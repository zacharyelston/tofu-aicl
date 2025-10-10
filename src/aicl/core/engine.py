import hcl2
import grpc
import time
import os
import subprocess
import sys
from typing import Dict, Any, Optional
from pathlib import Path
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import MessageToDict, ParseDict

from aicl.state.manager import StateManager, ResourceState
from aicl.parser import HCLParser
from aicl.planner import Planner
from aicl.executor import Executor
from aicl.provider_registry import get_registry
from aicl.observability import get_tracer, get_meter, initialize_observability, shutdown_observability
import proto.provider_pb2 as provider_pb2
import proto.provider_pb2_grpc as provider_pb2_grpc

USE_SUBPROCESS_MODE = os.getenv("AICL_SUBPROCESS_MODE", "true").lower() == "true"

class ProviderContainer:
    def __init__(self, name, process_or_container, grpc_stub, is_subprocess=False):
        self.name = name
        self.process_or_container = process_or_container
        self.stub = grpc_stub
        self.is_subprocess = is_subprocess

    def stop(self):
        print(f"Stopping provider: {self.name}")
        if self.is_subprocess:
            if hasattr(self.process_or_container, 'terminate'):
                self.process_or_container.terminate()
                try:
                    self.process_or_container.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process_or_container.kill()
        else:
            self.process_or_container.stop()

class AICLEngine:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.docker_client = None
        if not USE_SUBPROCESS_MODE:
            try:
                import docker
                self.docker_client = docker.from_env()
            except Exception as e:
                print(f"Warning: Docker not available: {e}")
                print("Falling back to subprocess mode")
        self.provider_containers: Dict[str, ProviderContainer] = {}
        self.state_manager = StateManager()
        self.parsed_config = self._parse_config()
        self.next_port = 50051
        
        initialize_observability()
        self.tracer = get_tracer(__name__)
        self.meter = get_meter(__name__)
        
        self.provider_start_counter = self.meter.create_counter(
            "aicl.provider.starts",
            description="Number of provider starts"
        )
        self.resource_counter = self.meter.create_counter(
            "aicl.resources.operations",
            description="Resource operations (create/delete)"
        )


    def _parse_config(self):
        parser = HCLParser(self.config_path)
        return parser.parse()
    
    @staticmethod
    def _dict_to_struct(d: dict) -> Struct:
        """Utility to convert dict to Protobuf Struct."""
        s = Struct()
        ParseDict(d, s)
        return s

    def _start_providers(self):
        if USE_SUBPROCESS_MODE or self.docker_client is None:
            self._start_providers_subprocess()
        else:
            self._start_providers_docker()

    def _start_providers_subprocess(self):
        with self.tracer.start_as_current_span("start_providers_subprocess") as span:
            providers = self.parsed_config.get('terraform', [{}])[0].get('required_providers', [{}])[0]
            span.set_attribute("provider.count", len(providers))
            span.set_attribute("provider.mode", "subprocess")
            
            print("Starting providers in subprocess mode...")
            registry = get_registry()

            for name, config in providers.items():
                print(f"Starting subprocess for provider '{name}'...")
                with self.tracer.start_as_current_span(f"start_provider.{name}") as provider_span:
                    provider_span.set_attribute("provider.name", name)
                    try:
                        # Get provider metadata from registry
                        source = config.get('source', '')
                        provider_metadata = registry.get(source)

                        if not provider_metadata:
                            print(f"Warning: Provider '{source}' not found in registry, using source name directly")
                            provider_name = source.split('/')[-1] if '/' in source else name
                        else:
                            provider_name = provider_metadata.name

                        # Find the provider server script
                        provider_dir = Path(__file__).parent.parent.parent.parent / 'providers' / provider_name
                        server_script = provider_dir / 'server.py'

                        if not server_script.exists():
                            raise FileNotFoundError(f"Provider server script not found: {server_script}")

                        # Load environment variables
                        env_vars = os.environ.copy()

                        # Add workspace root to PYTHONPATH so providers can find proto files
                        workspace_root = str(Path(__file__).parent.parent.parent.parent)
                        if 'PYTHONPATH' in env_vars:
                            env_vars['PYTHONPATH'] = f"{workspace_root}:{env_vars['PYTHONPATH']}"
                        else:
                            env_vars['PYTHONPATH'] = workspace_root

                        env_file_path = self.config_path.parent / '.env'
                        if env_file_path.exists():
                            with open(env_file_path, 'r') as f:
                                for line in f:
                                    if '=' in line and not line.strip().startswith('#'):
                                        key, value = line.strip().split('=', 1)
                                        env_vars[key] = value

                        # Assign a port
                        port = self.next_port
                        self.next_port += 1
                        env_vars['PORT'] = str(port)

                        # Start the provider as a subprocess
                        process = subprocess.Popen(
                            [sys.executable, str(server_script)],
                            env=env_vars,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True
                        )

                        # Wait for the provider to start
                        time.sleep(2)

                        # Connect to the provider
                        print(f"Connecting to provider on 127.0.0.1:{port}")
                        channel = grpc.insecure_channel(f'127.0.0.1:{port}')
                        stub = provider_pb2_grpc.ProviderStub(channel)

                        # Retry connection with exponential backoff
                        max_retries = 5
                        for attempt in range(max_retries):
                            try:
                                # Configure the provider with variable evaluation
                                from aicl.evaluator import HCLEvaluator
                                provider_config = self.parsed_config.get('provider', [{}])[0].get(name, {})
                                
                                # Evaluate variables in provider config
                                evaluator = HCLEvaluator(self.state_manager, self.parsed_config)
                                context = evaluator.build_context()
                                resolved_provider_config = evaluator.resolve_config(provider_config, context)
                                
                                config_struct = self._dict_to_struct(resolved_provider_config) if resolved_provider_config else Struct()
                                configure_req = provider_pb2.ConfigureRequest(config=config_struct)
                                stub.Configure(configure_req)
                                break
                            except grpc.RpcError as e:
                                if attempt < max_retries - 1:
                                    time.sleep(2 ** attempt)  # Exponential backoff
                                else:
                                    raise

                        self.provider_containers[name] = ProviderContainer(name, process, stub, is_subprocess=True)
                        self.provider_start_counter.add(1, {"provider": name, "mode": "subprocess"})
                        provider_span.set_attribute("provider.port", port)
                        provider_span.set_attribute("provider.status", "running")
                        print(f"Provider '{name}' is running on port {port}")
                    except Exception as e:
                        provider_span.set_attribute("provider.status", "failed")
                        provider_span.record_exception(e)
                        print(f"Error starting provider {name}: {e}")
                        self.destroy()
                        raise

    def _start_providers_docker(self):
        print("Starting provider containers...")
        providers = self.parsed_config.get('terraform', [{}])[0].get('required_providers', [{}])[0]
        registry = get_registry()

        for name, config in providers.items():
            # Try to get image from registry first, fall back to HCL config
            source = config.get('source', '')
            provider_metadata = registry.get(source)

            if provider_metadata:
                image = provider_metadata.container_image
            elif 'container' in config and 'image' in config['container']:
                image = config['container']['image']
            else:
                raise ValueError(f"No container image found for provider '{name}' in registry or config")

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
                        # Configure the provider with variable evaluation
                        from aicl.evaluator import HCLEvaluator
                        provider_config = self.parsed_config.get('provider', [{}])[0].get(name, {})
                        
                        # Evaluate variables in provider config
                        evaluator = HCLEvaluator(self.state_manager, self.parsed_config)
                        context = evaluator.build_context()
                        resolved_provider_config = evaluator.resolve_config(provider_config, context)
                        
                        config_struct = self._dict_to_struct(resolved_provider_config) if resolved_provider_config else Struct()
                        configure_req = provider_pb2.ConfigureRequest(config=config_struct)
                        stub.Configure(configure_req)
                        break
                    except grpc.RpcError as e:
                        if attempt < max_retries - 1:
                            time.sleep(2 ** attempt)  # Exponential backoff
                        else:
                            raise

                self.provider_containers[name] = ProviderContainer(name, container, stub, is_subprocess=False)
                print(f"Provider '{name}' is running on port {host_port}")
            except Exception as e:
                print(f"Error starting provider {name}: {e}")
                self.destroy()
                raise


    def apply(self):
        with self.tracer.start_as_current_span("apply") as span:
            experiment_id = self.parsed_config.get('variable', [{}])[0].get('experiment_id', {}).get('default', 'default-exp')
            span.set_attribute("experiment.id", experiment_id)
            
            self.state_manager.load(experiment_id)
            self._start_providers()
            print("\nApplying changes...")

            planner = Planner(self.parsed_config)
            sorted_nodes, resource_map = planner.build_graph()
            span.set_attribute("resource.count", len(sorted_nodes))

            executor = Executor(self.provider_containers, self.state_manager, self.parsed_config)
            for node_id in sorted_nodes:
                with self.tracer.start_as_current_span(f"execute_resource.{node_id}"):
                    executor.execute_node(node_id, resource_map)
                    self.resource_counter.add(1, {"operation": "create", "resource": node_id})

            self.state_manager.save()
            print("Apply complete.")

    def destroy(self):
        with self.tracer.start_as_current_span("destroy") as span:
            print("\nDestroying resources and stopping containers...")
            
            resource_count = len(self.state_manager.current_state.resources) if self.state_manager.current_state else 0
            span.set_attribute("resource.count", resource_count)
            
            # Delegate resource destruction to Executor
            if self.state_manager.current_state and self.provider_containers:
                executor = Executor(self.provider_containers, self.state_manager, self.parsed_config)
                executor.destroy_all()
                self.resource_counter.add(resource_count, {"operation": "delete"})
            
            # Stop all provider containers/processes
            for name, container in self.provider_containers.items():
                with self.tracer.start_as_current_span(f"stop_provider.{name}"):
                    container.stop()
            self.provider_containers = {}
            print("Destroy complete.")

    def run(self):
        try:
            self.apply()
        finally:
            self.destroy()
            shutdown_observability()

    def test(self, test_config_path: str):
        print(f"--- Running Tests from {test_config_path} ---")
        self.config_path = Path(test_config_path)
        self.parsed_config = self._parse_config()
        self._start_providers()

        # Create executor for utility methods
        executor = Executor(self.provider_containers, self.state_manager, self.parsed_config)

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

                        # Use Executor's _dict_to_struct method
                        input_struct = executor._dict_to_struct({
                            'command': config_attrs.get('command'),
                            'input': config_attrs.get('input')
                        })
                        req = provider_pb2.ValidateRequest(input=input_struct)

                        response = provider.stub.Validate(req)
                        # Use Executor's _handle_diagnostics method
                        executor._handle_diagnostics(response.diagnostics)

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