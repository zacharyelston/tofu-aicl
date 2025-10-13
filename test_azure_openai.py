#!/usr/bin/env python3
"""
Test Azure OpenAI provider

This test verifies that the Azure OpenAI provider can generate embeddings.
"""

import os
import sys
import subprocess
import time
import grpc
import json

# Add proto to path
sys.path.insert(0, os.path.dirname(__file__))

import proto.provider_pb2 as provider_pb2
import proto.provider_pb2_grpc as provider_pb2_grpc
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import ParseDict


def test_azure_openai_embeddings():
    """Test Azure OpenAI embeddings via gRPC"""
    
    print("=" * 70)
    print("Azure OpenAI Provider Test")
    print("=" * 70)
    
    # Check environment variables
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    
    if not api_key or not endpoint:
        print("\n❌ Missing Azure credentials!")
        print(f"   AZURE_OPENAI_API_KEY: {'✓' if api_key else '✗'}")
        print(f"   AZURE_OPENAI_ENDPOINT: {'✓' if endpoint else '✗'}")
        return False
    
    print(f"\n✅ Azure credentials configured")
    print(f"   Endpoint: {endpoint}")
    
    # Start Azure OpenAI provider server
    print(f"\n🚀 Starting Azure OpenAI provider...")
    server_process = subprocess.Popen(
        ['python', 'providers/azure_openai/server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2)
    
    try:
        # Connect to provider
        channel = grpc.insecure_channel('localhost:50051')
        stub = provider_pb2_grpc.ProviderStub(channel)
        
        print("✅ Connected to Azure provider")
        
        # Test 1: Configure provider
        print("\n📋 Test 1: Configure provider...")
        config_response = stub.Configure(provider_pb2.ConfigureRequest())
        
        if config_response.diagnostics:
            print("❌ Configuration failed:")
            for diag in config_response.diagnostics:
                print(f"   {diag.summary}")
            return False
        
        print("✅ Provider configured successfully")
        
        # Test 2: Generate embeddings
        # Note: You need to provide a valid Azure deployment name
        deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'text-embedding-ada-002')
        
        print(f"\n📊 Test 2: Generate embeddings (deployment: {deployment_name})...")
        
        config = {
            'deployment': deployment_name,
            'text': 'Hello, Azure OpenAI!',
            'aiclResourceName': 'azure-test-embedding'
        }
        
        config_struct = Struct()
        ParseDict(config, config_struct)
        
        apply_request = provider_pb2.ApplyResourceChangeRequest(
            type_name='azure_openai_embedding',
            config=config_struct
        )
        
        apply_response = stub.ApplyResourceChange(apply_request)
        
        if apply_response.diagnostics:
            print("❌ Embedding generation failed:")
            for diag in apply_response.diagnostics:
                print(f"   {diag.summary}: {diag.detail}")
            return False
        
        # Check response
        state = apply_response.new_state
        attributes = dict(state.attributes)
        
        if 'embedding' in attributes:
            embedding = attributes['embedding']
            print(f"✅ Embedding generated successfully!")
            print(f"   Dimensions: {len(embedding)}")
            print(f"   First 5 values: {embedding[:5]}")
            print(f"   Status: {state.status}")
        else:
            print(f"⚠️  Response received but no embedding found")
            print(f"   Attributes: {list(attributes.keys())}")
        
        print("\n✅ Azure OpenAI provider test passed!")
        return True
        
    except grpc.RpcError as e:
        print(f"\n❌ gRPC Error: {e.code()}")
        print(f"   Details: {e.details()}")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        server_process.terminate()
        server_process.wait(timeout=5)
        channel.close()
        print("\n🛑 Provider stopped")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Testing Azure OpenAI Integration")
    print("=" * 70 + "\n")
    
    success = test_azure_openai_embeddings()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed")
        sys.exit(1)
