#!/usr/bin/env python3
"""
Minimal AICL Engine - Simplified version for easy understanding
"""
import json
import subprocess
import time
import grpc
from pathlib import Path
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import ParseDict, MessageToDict

import sys
sys.path.insert(0, '/home/runner/tofu-aicl')

import proto.provider_pb2 as provider_pb2
import proto.provider_pb2_grpc as provider_pb2_grpc

from core.parser import HCLParser
from core.state_manager import StateManager, ResourceState
from core.evaluator import HCLEvaluator
from core.planner import Planner
from core.executor import Executor

class MinimalEngine:
    """Simplified AICL engine with just the essentials"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.provider_processes = {}
        self.provider_stubs = {}
        self.state_manager = StateManager()
        
        # Parse config
        parser = HCLParser(self.config_path)
        self.parsed_config = parser.parse()
        
    def _start_provider(self, name: str, port: int, script_path: str):
        """Start a provider as subprocess"""
        print(f"Starting {name} provider on port {port}...")
        
        process = subprocess.Popen(
            ['python', script_path],
            env={**subprocess.os.environ},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for provider to be ready
        time.sleep(2)
        
        # Connect to provider
        channel = grpc.insecure_channel(f'localhost:{port}')
        stub = provider_pb2_grpc.ProviderStub(channel)
        
        # Configure provider
        stub.Configure(provider_pb2.ConfigureRequest(config={}))
        
        self.provider_processes[name] = process
        self.provider_stubs[name] = stub
        
        print(f"✓ {name} provider ready")
    
    def apply(self):
        """Run the AICL experiment"""
        print("\n" + "="*60)
        print("MINIMAL AICL ENGINE - APPLY")
        print("="*60 + "\n")
        
        # 1. Start providers
        providers = self.parsed_config.get('terraform', [{}])[0].get('required_providers', [{}])[0]
        
        for name, config in providers.items():
            if name == 'naga':
                self._start_provider(
                    'naga', 
                    50052, 
                    'versions/minimal/providers/naga/server.py'
                )
        
        # 2. Create plan
        planner = Planner(self.parsed_config)
        sorted_resources, resource_map = planner.build_graph()
        
        print(f"\n📋 Execution Plan: {len(sorted_resources)} resources\n")
        
        # 3. Execute resources
        evaluator = HCLEvaluator(self.state_manager, self.parsed_config)
        executor = Executor(self.provider_stubs, self.state_manager)
        
        for resource_id in sorted_resources:
            res_type, res_name, config_attrs = resource_map[resource_id]
            
            # Resolve variables
            context = evaluator.build_context()
            resolved_config = evaluator.resolve_config(config_attrs, context)
            
            print(f"→ Creating {res_type}.{res_name}")
            
            # Execute
            new_state = executor.apply_resource_change(
                resource_id=resource_id,
                resource_type=res_type,
                resource_name=res_name,
                config=resolved_config
            )
            
            # Update state
            self.state_manager.update_resource(new_state)
            
            print(f"  ✓ {new_state.status}")
        
        # 4. Save state
        state_file = Path("terraform.tfstate.d/default-minimal.tfstate")
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        state_data = {
            "version": 1,
            "resources": {
                rid: {
                    "id": rstate.id,
                    "type": rstate.type,
                    "attributes": rstate.attributes,
                    "status": rstate.status
                }
                for rid, rstate in self.state_manager.current_state.resources.items()
            }
        }
        
        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
        
        print(f"\n💾 State saved to {state_file}")
        print("\n" + "="*60)
        print("✅ APPLY COMPLETE")
        print("="*60 + "\n")
    
    def destroy(self):
        """Clean up providers"""
        print("\n🧹 Cleaning up...")
        for name, process in self.provider_processes.items():
            process.terminate()
            process.wait(timeout=5)
            print(f"  ✓ Stopped {name} provider")
        print("✅ Cleanup complete\n")
    
    def run(self):
        """Run the full lifecycle"""
        try:
            self.apply()
        finally:
            self.destroy()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python engine.py <config.aicl>")
        sys.exit(1)
    
    engine = MinimalEngine(sys.argv[1])
    engine.run()
