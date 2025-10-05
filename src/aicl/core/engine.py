import hcl2
import docker
import grpc
import time
import os
from typing import Dict, Any
from pathlib import Path
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import MessageToDict

from aicl.state.manager import StateManager, ResourceState
from aicl.parser import HCLParser
from aicl.planner import Planner
from aicl.executor import Executor
import proto.provider_pb2 as provider_pb2
import proto.provider_pb2_grpc as provider_pb2_grpc

class ProviderContainer:
    def __init__(self, name, container, grpc_stub):
        self.name = name
        self.container = container
        self.stub = grpc_stub

    def stop(self):
        print(f"Stopping provider container: {self.name}")
        self.container.stop()

class AICLEngine:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.docker_client = docker.from_env()
        self.provider_containers: Dict[str, ProviderContainer] = {}
        self.state_manager = StateManager()
        self.parsed_config = self._parse_config()


    def _parse_config(self):
        parser = HCLParser(self.config_path)
        return parser.parse()

    def _start_providers(self):
        print("Starting provider containers...")
        providers = self.parsed_config.get('terraform', [{}])[0].get('required_providers', [{}])[0]
        for name, config in providers.items():
            image = config['container']['image']
            print(f"Starting container for provider '{name}' with image '{image}'...")
            try:
                env_vars = {}
                env_file_path = self.config_path.parent / '.env'
                if env_file_path.exists():
                    with open(env_file_path, 'r') as f:
                        for line in f:
                            if '=' in line:
                                key, value = line.strip().split('=', 1)
                                env_vars[key] = value

                container = self.docker_client.containers.run(
                    image=image,
                    detach=True,
                    auto_remove=True,
                    ports={'50051/tcp': None},
                    environment=env_vars
                )
                time.sleep(5) # Wait for container to be ready
                container.reload()
                
                # Check container status
                print(f"Container status: {container.status}")
                print(f"Container logs: {container.logs().decode('utf-8')[-500:]}")
                
                host_port = container.ports['50051/tcp'][0]['HostPort']
                print(f"Connecting to provider on 127.0.0.1:{host_port}")
                channel = grpc.insecure_channel(f'127.0.0.1:{host_port}')
                stub = provider_pb2_grpc.ProviderStub(channel)
                
                # Retry connection with exponential backoff
                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        # Configure the provider
                        provider_config = self.parsed_config.get('provider', [{}])[0].get(name, {})
                        config_struct = self._dict_to_struct(provider_config)
                        configure_req = provider_pb2.ConfigureRequest(config=config_struct)
                        stub.Configure(configure_req)
                        break
                    except grpc.RpcError as e:
                        if attempt < max_retries - 1:
                            time.sleep(2 ** attempt)  # Exponential backoff
                        else:
                            raise

                self.provider_containers[name] = ProviderContainer(name, container, stub)
                print(f"Provider '{name}' is running on port {host_port}")
            except Exception as e:
                print(f"Error starting provider {name}: {e}")
                self.destroy()
                raise

    def _dict_to_struct(self, d: dict) -> Struct:
        s = Struct()
        s.update(d)
        return s


    def _handle_diagnostics(self, diagnostics):
        for diag in diagnostics:
            severity = provider_pb2.Diagnostic.Severity.Name(diag.severity)
            print(f"  [{severity}] {diag.summary}: {diag.detail}")

    def apply(self):
        self.state_manager.load(self.parsed_config.get('variable', [{}])[0].get('experiment_id', {}).get('default', 'default-exp'))
        self._start_providers()
        print("\nApplying changes...")
        
        planner = Planner(self.parsed_config)
        sorted_nodes, resource_map = planner.build_graph()
        
        executor = Executor(self.provider_containers, self.state_manager)
        for node_id in sorted_nodes:
            executor.execute_node(node_id, resource_map)

        self.state_manager.save()
        print("Apply complete.")

    def destroy(self):
        print("\nDestroying resources and stopping containers...")
        if self.state_manager.current_state:
            for res_id, res_state in self.state_manager.current_state.resources.items():
                provider = self.provider_containers.get(res_state.provider)
                if provider:
                    try:
                        req = provider_pb2.DeleteResourceRequest(id=res_id, type_name=res_state.type)
                        response = provider.stub.DeleteResource(req)
                        self._handle_diagnostics(response.diagnostics)
                        print(f"  - Resource '{res_id}' deleted.")
                    except grpc.RpcError as e:
                        print(f"Error deleting resource {res_id}: {e.details()}")

        for name, container in self.provider_containers.items():
            container.stop()
        self.provider_containers = {}
        print("Destroy complete.")

    def run(self):
        try:
            self.apply()
        finally:
            self.destroy()

    def test(self, test_config_path: str):
        print(f"--- Running Tests from {test_config_path} ---")
        self.config_path = Path(test_config_path)
        self.parsed_config = self._parse_config()
        self._start_providers()

        try:
            resources = self.parsed_config.get('resource', [])
            for res_config in resources:
                for res_type, res_details in res_config.items():
                    provider_name = res_type.split('_')[0]
                    for res_name, config_attrs in res_details.items():
                        print(f"\n- Running test: '{res_name}' ({res_type})")
                        provider = self.provider_containers.get(provider_name)
                        if not provider:
                            raise Exception(f"Assertion provider '{provider_name}' not found.")

                        input_struct = self._dict_to_struct({
                            'command': config_attrs.get('command'),
                            'input': config_attrs.get('input')
                        })
                        req = provider_pb2.ValidateRequest(input=input_struct)
                        
                        response = provider.stub.Validate(req)
                        self._handle_diagnostics(response.diagnostics)

                        if not response.success:
                            print("  [FAIL] Provider validation failed.")
                            continue

                        # Evaluate the HCL assert block against the provider's output
                        assertion = config_attrs.get('assert', {})
                        condition = assertion.get('condition')
                        error_message = assertion.get('error_message', "Assertion failed.")

                        if condition:
                            eval_context = {'self': {'output': dict(response.output)}}
                            # WARNING: Using eval is insecure with untrusted input.
                            # For this PoC, we trust the .test-cl files.
                            result = eval(condition, {}, eval_context)
                            if result:
                                print("  [PASS] Assertion passed.")
                            else:
                                print(f"  [FAIL] {error_message}")
                        else:
                            print("  [WARN] No 'assert' block found for this test.")
        finally:
            self.destroy()
