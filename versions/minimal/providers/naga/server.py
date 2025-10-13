#!/usr/bin/env python3
import grpc
import os
import json
import requests
from concurrent import futures
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import MessageToDict, ParseDict

import sys
sys.path.insert(0, '/home/runner/tofu-aicl')

import proto.provider_pb2 as provider_pb2
import proto.provider_pb2_grpc as provider_pb2_grpc

class NagaProvider(provider_pb2_grpc.ProviderServicer):
    """Minimal Naga.ai provider - chat and embeddings only"""
    
    def __init__(self):
        self.api_key = os.getenv("NAGA_API_KEY")
        self.base_url = "https://api.naga.ac/v1"
    
    def Configure(self, request, context):
        if not self.api_key:
            diag = provider_pb2.Diagnostic(
                severity=provider_pb2.Diagnostic.ERROR,
                summary="NAGA_API_KEY not set"
            )
            return provider_pb2.ConfigureResponse(diagnostics=[diag])
        return provider_pb2.ConfigureResponse()
    
    def ApplyResourceChange(self, request, context):
        config = MessageToDict(request.config)
        resource_name = config.get('aiclResourceName', 'default')
        resource_id = f"{request.type_name}-{resource_name}"
        
        # Handle chat
        if request.type_name in ["naga_chat", "chat"]:
            return self._chat(resource_id, config, request.type_name)
        
        # Handle embeddings
        elif request.type_name in ["naga_embedding", "embedding"]:
            return self._embedding(resource_id, config, request.type_name)
        
        # Unknown type
        diag = provider_pb2.Diagnostic(
            severity=provider_pb2.Diagnostic.ERROR,
            summary=f"Unknown resource type: {request.type_name}"
        )
        return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
    
    def _chat(self, resource_id, config, type_name):
        """Execute chat completion"""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.get('model', 'gpt-4o-mini'),
                    "messages": config.get('messages', []),
                    "temperature": config.get('temperature', 0.7),
                    "max_tokens": config.get('max_tokens', 1024)
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract response
            choice = result['choices'][0]
            content = choice['message']['content']
            usage = result.get('usage', {})
            
            output = {
                'content': content,
                'usage': usage,
                'model': config.get('model'),
                'finish_reason': choice.get('finish_reason')
            }
            
            output_struct = Struct()
            ParseDict(output, output_struct)
            
            new_state = provider_pb2.ResourceState(
                id=resource_id,
                type=type_name,
                attributes=output_struct,
                status='ready'
            )
            return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)
            
        except Exception as e:
            diag = provider_pb2.Diagnostic(
                severity=provider_pb2.Diagnostic.ERROR,
                summary=f"Chat failed: {str(e)}"
            )
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
    
    def _embedding(self, resource_id, config, type_name):
        """Generate embeddings"""
        try:
            text = config.get('text', '')
            if not text:
                raise ValueError("No text provided")
            
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": config.get('model', 'text-embedding-3-small'),
                    "input": [text]
                }
            )
            response.raise_for_status()
            result = response.json()
            
            vector = result['data'][0]['embedding']
            
            output = {
                'vector': vector,
                'model': config.get('model'),
                'dimensions': len(vector)
            }
            
            output_struct = Struct()
            ParseDict(output, output_struct)
            
            new_state = provider_pb2.ResourceState(
                id=resource_id,
                type=type_name,
                attributes=output_struct,
                status='ready'
            )
            return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)
            
        except Exception as e:
            diag = provider_pb2.Diagnostic(
                severity=provider_pb2.Diagnostic.ERROR,
                summary=f"Embedding failed: {str(e)}"
            )
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    provider_pb2_grpc.add_ProviderServicer_to_server(NagaProvider(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Naga provider listening on port 50052")
    server.wait_for_termination()
