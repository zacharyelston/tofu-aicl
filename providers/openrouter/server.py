import grpc
import os
import json
import uuid
import requests
from concurrent import futures
from typing import Dict, Any
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import MessageToDict, ParseDict

import proto.provider_pb2 as provider_pb2
import proto.provider_pb2_grpc as provider_pb2_grpc

class OpenRouterProvider(provider_pb2_grpc.ProviderServicer):
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.resources: Dict[str, Dict[str, Any]] = {}  # In-memory state

    # --- Helper Methods ---
    def _create_diagnostic(self, severity, summary, detail=""):
        return provider_pb2.Diagnostic(severity=severity, summary=summary, detail=detail)

    # --- Lifecycle Management ---
    def GetSchema(self, request, context):
        schema = Struct()
        schema.update({
            "type": "object",
            "properties": {
                "model": {"type": "string", "description": "Model identifier (e.g., anthropic/claude-3.5-sonnet)"},
                "temperature": {"type": "number", "description": "Sampling temperature 0.0-2.0", "default": 0.7},
                "max_tokens": {"type": "integer", "description": "Maximum tokens to generate", "default": 1024},
            },
            "required": ["model"]
        })
        resource_schema = provider_pb2.GetSchemaResponse.ResourceSchema(
            type_name="openrouter_model",
            schema=schema
        )
        return provider_pb2.GetSchemaResponse(resources=[resource_schema])

    def ValidateConfig(self, request, context):
        # This provider only needs the api_key
        if 'api_key' not in request.config:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "Missing 'api_key' in provider configuration")
            return provider_pb2.ValidateConfigResponse(diagnostics=[diag])
        return provider_pb2.ValidateConfigResponse()

    def Configure(self, request, context):
        # API key is already set from environment in __init__
        if not self.api_key:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "OPENROUTER_API_KEY environment variable not set")
            return provider_pb2.ConfigureResponse(diagnostics=[diag])
        
        return provider_pb2.ConfigureResponse()

    # --- Resource Management ---
    def ApplyResourceChange(self, request, context):
        config = MessageToDict(request.config)
        
        # Use resource name from AICL config for consistent IDs
        resource_name = config.get('aiclResourceName', '')
        
        if request.prior_state and request.prior_state.id:
            resource_id = request.prior_state.id
        elif resource_name:
            resource_id = f"{request.type_name}-{resource_name}"
        else:
            resource_id = f"or-{uuid.uuid4().hex[:8]}"
        
        # Handle embeddings generation
        if request.type_name in ["embedding", "openrouter_embeddings"]:
            return self._generate_embeddings(resource_id, config, request.type_name)
        
        # Handle chat/query
        elif request.type_name in ["chat", "openrouter_query"]:
            return self._execute_chat(resource_id, config, request.type_name)
        
        # Default: just store config
        self.resources[resource_id] = {
            "id": resource_id,
            "type_name": request.type_name,
            "attributes": config
        }

        new_state_struct = Struct()
        ParseDict(config, new_state_struct)

        new_state = provider_pb2.ResourceState(
            id=resource_id,
            type=request.type_name,
            attributes=new_state_struct,
            status='ready'
        )
        return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)
    
    def _generate_embeddings(self, resource_id, config, type_name):
        """Generate embeddings for text chunks"""
        # Handle both single text and array of texts
        single_text = config.get('text')
        texts = config.get('texts', [])
        
        if single_text:
            texts = [single_text]
        
        model = config.get('model', 'openai/text-embedding-3-small')
        
        if not texts:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "No text or texts provided for embeddings")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
        
        embeddings = []
        try:
            # Extract text content from chunks
            text_list = []
            for item in texts:
                if isinstance(item, dict):
                    text_list.append(item.get('content', ''))
                else:
                    text_list.append(str(item))
            
            # Call OpenRouter embeddings API
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "input": text_list
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # Build embeddings with metadata
            for i, embedding_data in enumerate(result.get('data', [])):
                embeddings.append({
                    'id': f"{resource_id}-{i}",
                    'values': embedding_data['embedding'],
                    'metadata': texts[i] if isinstance(texts[i], dict) else {'content': texts[i]}
                })
            
            output_attributes = {
                'embeddings': embeddings,
                'model': model,
                'count': len(embeddings)
            }
            
            # For single text query, also include the vector directly
            if single_text and len(embeddings) > 0:
                output_attributes['vector'] = embeddings[0]['values']
            
            output_struct = Struct()
            ParseDict(output_attributes, output_struct)
            
            new_state = provider_pb2.ResourceState(
                id=resource_id,
                type=type_name,
                attributes=output_struct,
                status='ready'
            )
            return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)
            
        except Exception as e:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"Embeddings generation failed: {str(e)}")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
    
    def _execute_chat(self, resource_id, config, type_name):
        """Execute chat completion with messages"""
        messages = config.get('messages', [])
        model = config.get('model', 'anthropic/claude-3.5-sonnet')
        
        if not messages:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "No messages provided")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
        
        try:
            print(f"DEBUG OpenRouter: Executing chat with model {model}")
            print(f"DEBUG OpenRouter: Messages: {messages}")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": config.get('temperature', 0.7),
                    "max_tokens": config.get('max_tokens', 1024)
                }
            )
            response.raise_for_status()
            result = response.json()
            
            answer = result['choices'][0]['message']['content']
            
            output_attributes = {
                'response': answer,
                'model': model,
                'message_count': len(messages)
            }
            
            output_struct = Struct()
            ParseDict(output_attributes, output_struct)
            
            new_state = provider_pb2.ResourceState(
                id=resource_id,
                type=type_name,
                attributes=output_struct,
                status='ready'
            )
            return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)
            
        except Exception as e:
            import traceback
            print(f"ERROR OpenRouter chat: {e}")
            print(f"TRACEBACK: {traceback.format_exc()}")
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"Chat execution failed: {str(e)}")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
    
    def _execute_query(self, resource_id, config, type_name):
        """Execute RAG query with context"""
        query = config.get('query', '')
        context = config.get('context', [])
        model = config.get('model', 'anthropic/claude-3.5-sonnet')
        
        if not query:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "No query provided")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
        
        try:
            # Build context string from retrieved chunks
            context_str = "\n\n".join([
                f"Source: {chunk.get('source', 'unknown')}\n{chunk.get('content', '')}"
                for chunk in context
            ])
            
            # Create prompt with context
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer the question based on the provided context."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context_str}\n\nQuestion: {query}"
                }
            ]
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": config.get('temperature', 0.7),
                    "max_tokens": config.get('max_tokens', 1024)
                }
            )
            response.raise_for_status()
            result = response.json()
            
            answer = result['choices'][0]['message']['content']
            
            output_attributes = {
                'query': query,
                'answer': answer,
                'model': model,
                'context_count': len(context)
            }
            
            output_struct = Struct()
            ParseDict(output_attributes, output_struct)
            
            new_state = provider_pb2.ResourceState(
                id=resource_id,
                type=type_name,
                attributes=output_struct,
                status='ready'
            )
            return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)
            
        except Exception as e:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"Query execution failed: {str(e)}")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

    def ReadResource(self, request, context):
        resource = self.resources.get(request.id)
        if not resource:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"Resource with ID '{request.id}' not found.")
            return provider_pb2.ReadResourceResponse(diagnostics=[diag])

        state_struct = Struct()
        state_struct.update(resource['attributes'])
        state = provider_pb2.ResourceState(
            id=resource['id'],
            type=resource['type_name'],
            attributes=state_struct,
            status='ready'
        )
        return provider_pb2.ReadResourceResponse(state=state)

    def DeleteResource(self, request, context):
        if request.id in self.resources:
            del self.resources[request.id]
        return provider_pb2.DeleteResourceResponse()

    # --- AI & Testing Workflow ---
    def Execute(self, request, context):
        resource = self.resources.get(request.resource_id)
        if not resource:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"Resource not found: {request.resource_id}")
            context.abort(grpc.StatusCode.NOT_FOUND, json.dumps(diag))

        yield provider_pb2.ExecuteResponse(log="Executing OpenRouter chat completion...")

        payload = {
            "model": resource['attributes']['model'],
            "messages": list(request.input.get('messages', [])),
            "temperature": resource['attributes'].get('temperature', 0.7),
            "max_tokens": resource['attributes'].get('max_tokens', 1024),
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                stream=False # For simplicity in this example
            )
            response.raise_for_status()
            result = response.json()
            
            output_struct = Struct()
            output_struct.update(result)
            yield provider_pb2.ExecuteResponse(data=output_struct)

        except requests.exceptions.RequestException as e:
            yield provider_pb2.ExecuteResponse(log=f"Error during execution: {e}")
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "OpenRouter API request failed", str(e))
            context.abort(grpc.StatusCode.INTERNAL, json.dumps(diag))

    def Validate(self, request, context):
        # Placeholder implementation for the test-cl framework
        diag = self._create_diagnostic(provider_pb2.Diagnostic.WARNING, "Validation not implemented for this provider.")
        return provider_pb2.ValidateResponse(success=True, diagnostics=[diag])

    def HealthCheck(self, request, context):
        return provider_pb2.HealthCheckResponse(healthy=True, version="0.1.0")

    # --- Not Implemented Placeholders ---
    def PlanResourceChange(self, request, context):
        # A real implementation would compare prior_state and proposed_config
        planned_state = Struct()
        planned_state.update(request.proposed_config)
        return provider_pb2.PlanResourceChangeResponse(planned_state=planned_state)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    provider_pb2_grpc.add_ProviderServicer_to_server(OpenRouterProvider(), server)
    port = os.getenv("PORT", "50051")
    server.add_insecure_port(f'[::]:{port}')
    print(f"OpenRouter provider listening on port {port}...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    # Set the API key from environment for local testing
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set.")
    else:
        serve()
