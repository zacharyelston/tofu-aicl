import hcl2
import docker
import grpc
import time
import os
from typing import Dict, Any
from pathlib import Path
from google.protobuf.struct_pb2 import Struct
from collections import defaultdict
from google.protobuf.json_format import MessageToDict

from aicl.state.manager import StateManager, ResourceState
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
        self.parsed_config: Dict[str, Any] = {}
        self.experiment_id = ""
        self.state_manager = StateManager()

    def _parse_config(self):
        print(f"Parsing config file: {self.config_path}")
        with open(self.config_path, 'r') as f:
            self.parsed_config = hcl2.load(f)
        self.experiment_id = self.parsed_config.get('variable', [{}])[0].get('experiment_id', {}).get('default', 'default-exp')
        self.state_manager.load(self.experiment_id)

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
                time.sleep(3) # Simple wait for container to be ready
                container.reload()
                host_port = container.ports['50051/tcp'][0]['HostPort']
                channel = grpc.insecure_channel(f'localhost:{host_port}')
                stub = provider_pb2_grpc.ProviderStub(channel)
                
                # Configure the provider
                provider_config = self.parsed_config.get('provider', [{}])[0].get(name, {})
                config_struct = self._dict_to_struct(provider_config)
                configure_req = provider_pb2.ConfigureRequest(config=config_struct)
                stub.Configure(configure_req)

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

    def _resolve_dependencies(self, config):
        if isinstance(config, dict):
            for key, value in config.items():
                config[key] = self._resolve_dependencies(value)
        elif isinstance(config, list):
            for i, value in enumerate(config):
                config[i] = self._resolve_dependencies(value)
        elif isinstance(config, str) and config.startswith('resource.'):
            parts = config.split('.')
            if len(parts) == 5:
                _, ref_type, ref_name, ref_attr, ref_key = parts
                ref_resource_state = self.state_manager.get_resource_by_name(ref_name)
                if ref_resource_state:
                    return ref_resource_state.attributes.get(ref_key)
        return config

    def _handle_diagnostics(self, diagnostics):
        for diag in diagnostics:
            severity = provider_pb2.Diagnostic.Severity.Name(diag.severity)
            print(f"  [{severity}] {diag.summary}: {diag.detail}")

    def apply(self):
        self._start_providers()
        print("\nApplying changes...")
        
        adj = defaultdict(list)
        in_degree = defaultdict(int)
        resource_map = {}
        all_resource_ids = []

        resources = self.parsed_config.get('resource', [])
        for res_config in resources:
            for res_type, res_details in res_config.items():
                for res_name, config_attrs in res_details.items():
                    node_id = f"{res_type}.{res_name}"
                    resource_map[node_id] = (res_type, res_name, config_attrs)
                    all_resource_ids.append(node_id)
                    in_degree[node_id]  # Initialize

                    for value in config_attrs.values():
                        if isinstance(value, str) and value.startswith('resource.'):
                            parts = value.split('.')
                            dep_id = f"{parts[1]}.{parts[2]}"
                            adj[dep_id].append(node_id)
                            in_degree[node_id] += 1
        
        queue = [node for node in all_resource_ids if in_degree[node] == 0]
        sorted_order = []
        while queue:
            node = queue.pop(0)
            sorted_order.append(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_order) != len(all_resource_ids):
            raise Exception("Cycle detected in resource dependencies!")

        for node_id in sorted_order:
            res_type, res_name, config_attrs = resource_map[node_id]
            provider_name = res_type.split('_')[0]
            provider = self.provider_containers.get(provider_name)
            if not provider:
                raise Exception(f"Provider '{provider_name}' not found for resource '{res_name}'")

            # Re-parse with the current state to resolve dependencies
            with open(self.config_path, 'r') as f:
                hcl_context = {'resource': self.state_manager.get_all_resources_as_dict()}
                resolved_config = hcl2.load(f, context=hcl_context)['resource'][0][res_type][res_name]

            config_struct = self._dict_to_struct(resolved_config)
            req = provider_pb2.ApplyResourceChangeRequest(type_name=res_type, config=config_struct)
            
            try:
                response = provider.stub.ApplyResourceChange(req)
                self._handle_diagnostics(response.diagnostics)
                state = response.new_state
                attributes = MessageToDict(state.attributes)
                metadata = MessageToDict(state.metadata)
                resource_state = ResourceState(
                    id=state.id, type=state.type, provider=provider_name,
                    attributes=attributes, metadata=metadata, status=state.status
                )
                self.state_manager.add_resource(resource_state)
                print(f"  + Resource '{res_name}' ({state.id}) created successfully.")
            except grpc.RpcError as e:
                print(f"Error applying resource {res_name}: {e.details()}")
                self.destroy()

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
            self._parse_config()
            self.apply()
        finally:
            self.destroy()

    def test(self, test_config_path: str):
        print(f"--- Running Tests from {test_config_path} ---")
        self.config_path = Path(test_config_path)
        self._parse_config()
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
