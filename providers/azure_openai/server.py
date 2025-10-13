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

class AzureOpenAIProvider(provider_pb2_grpc.ProviderServicer):
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        self.resources: Dict[str, Dict[str, Any]] = {}

    def _create_diagnostic(self, severity, summary, detail=""):
        return provider_pb2.Diagnostic(severity=severity, summary=summary, detail=detail)

    def GetSchema(self, request, context):
        schema = Struct()
        schema.update({
            "type": "object",
            "properties": {
                "deployment": {"type": "string", "description": "Azure deployment name"},
                "dimensions": {"type": "integer", "description": "Number of dimensions (optional)"}
            },
            "required": ["deployment"]
        })
        resource_schema = provider_pb2.GetSchemaResponse.ResourceSchema(
            type_name="azure_openai_embedding",
            schema=schema
        )
        return provider_pb2.GetSchemaResponse(resources=[resource_schema])

    def ValidateConfig(self, request, context):
        diagnostics = []

        config = MessageToDict(request.config) if request.config else {}

        if not config.get('deployment'):
            diagnostics.append(self._create_diagnostic(
                provider_pb2.Diagnostic.ERROR,
                "Deployment name is required for Azure OpenAI resources"
            ))

        if diagnostics:
            return provider_pb2.ValidateConfigResponse(diagnostics=diagnostics)

        return provider_pb2.ValidateConfigResponse()

    def Configure(self, request, context):
        diagnostics = []

        if not self.api_key:
            diagnostics.append(self._create_diagnostic(
                provider_pb2.Diagnostic.ERROR,
                "AZURE_OPENAI_API_KEY environment variable not set"
            ))

        if not self.endpoint:
            diagnostics.append(self._create_diagnostic(
                provider_pb2.Diagnostic.ERROR,
                "AZURE_OPENAI_ENDPOINT environment variable not set"
            ))

        if diagnostics:
            return provider_pb2.ConfigureResponse(diagnostics=diagnostics)

        return provider_pb2.ConfigureResponse()

    def ApplyResourceChange(self, request, context):
        config = MessageToDict(request.config)

        # Use resource name from AICL config for consistent IDs
        resource_name = config.get('aiclResourceName', '')

        if request.prior_state and request.prior_state.id:
            resource_id = request.prior_state.id
        elif resource_name:
            resource_id = f"{request.type_name}-{resource_name}"
        else:
            resource_id = f"azure-{uuid.uuid4().hex[:8]}"

        # Handle embeddings
        if request.type_name in ["embedding", "azure_openai_embedding"]:
            return self._generate_embeddings(resource_id, config, request.type_name)
        
        # Handle chat completions
        if request.type_name in ["chat", "azure_openai_chat"]:
            return self._generate_chat_completion(resource_id, config, request.type_name)

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
        """Generate embeddings using Azure OpenAI API"""
        # Handle both single text and array of texts
        single_text = config.get('text')
        texts = config.get('texts', [])

        if single_text:
            texts = [single_text]

        deployment = config.get('deployment')
        dimensions = config.get('dimensions')

        if not deployment:
            diag = self._create_diagnostic(
                provider_pb2.Diagnostic.ERROR,
                "Deployment name is required for Azure OpenAI embeddings"
            )
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

        if not texts:
            diag = self._create_diagnostic(
                provider_pb2.Diagnostic.ERROR,
                "No text or texts provided for embeddings"
            )
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

        try:
            # Extract text content from chunks
            text_list = []
            for item in texts:
                if isinstance(item, dict):
                    text_list.append(item.get('content', ''))
                else:
                    text_list.append(str(item))

            # Build Azure OpenAI URL
            url = f"{self.endpoint}/openai/deployments/{deployment}/embeddings?api-version={self.api_version}"

            # Prepare request payload
            payload = {
                "input": text_list
            }
            if dimensions:
                payload["dimensions"] = dimensions

            # Call Azure OpenAI API
            response = requests.post(
                url,
                headers={
                    "api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            result = response.json()

            # Extract embeddings
            embeddings = []
            for i, item in enumerate(result.get('data', [])):
                embedding_data = {
                    'index': i,
                    'embedding': item.get('embedding', [])
                }
                # Preserve metadata from input if available
                if isinstance(texts[i], dict):
                    embedding_data['metadata'] = texts[i].get('metadata', {})
                embeddings.append(embedding_data)

            # Store result
            result_data = {
                'embeddings': embeddings,
                'deployment': deployment,
                'usage': result.get('usage', {})
            }

            # Handle single vs multiple embeddings
            if single_text and embeddings:
                result_data['embedding'] = embeddings[0]['embedding']

            self.resources[resource_id] = {
                "id": resource_id,
                "type_name": type_name,
                "attributes": result_data
            }

            # Create response
            new_state_struct = Struct()
            ParseDict(result_data, new_state_struct)

            new_state = provider_pb2.ResourceState(
                id=resource_id,
                type=type_name,
                attributes=new_state_struct,
                status='ready'
            )

            return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)

        except requests.exceptions.RequestException as e:
            diag = self._create_diagnostic(
                provider_pb2.Diagnostic.ERROR,
                f"Azure embeddings generation failed: {str(e)}",
                str(e)
            )
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
        except Exception as e:
            diag = self._create_diagnostic(
                provider_pb2.Diagnostic.ERROR,
                f"Unexpected error: {str(e)}",
                str(e)
            )
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

    def _generate_chat_completion(self, resource_id, config, type_name):
        """Generate chat completion using Azure OpenAI API"""
        deployment = config.get('deployment')
        messages = config.get('messages', [])
        prompt = config.get('prompt')
        
        # Support both prompt and messages format
        if prompt and not messages:
            messages = [{"role": "user", "content": prompt}]
        
        if not deployment:
            diag = self._create_diagnostic(
                provider_pb2.Diagnostic.ERROR,
                "Deployment name is required for Azure OpenAI chat"
            )
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
        
        if not messages:
            diag = self._create_diagnostic(
                provider_pb2.Diagnostic.ERROR,
                "No messages or prompt provided for chat completion"
            )
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
        
        try:
            # Build Azure OpenAI URL for chat completions
            url = f"{self.endpoint}/openai/deployments/{deployment}/chat/completions?api-version={self.api_version}"
            
            # Prepare request payload
            payload = {
                "messages": messages
            }
            
            # Add optional parameters
            if config.get('temperature') is not None:
                payload['temperature'] = config['temperature']
            if config.get('max_tokens'):
                payload['max_tokens'] = config['max_tokens']
            if config.get('top_p') is not None:
                payload['top_p'] = config['top_p']
            if config.get('frequency_penalty') is not None:
                payload['frequency_penalty'] = config['frequency_penalty']
            if config.get('presence_penalty') is not None:
                payload['presence_penalty'] = config['presence_penalty']
            
            # Call Azure OpenAI API
            response = requests.post(
                url,
                headers={
                    "api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract completion
            choice = result.get('choices', [{}])[0]
            message = choice.get('message', {})
            
            result_data = {
                'content': message.get('content', ''),
                'role': message.get('role', 'assistant'),
                'deployment': deployment,
                'model': result.get('model', deployment),
                'usage': result.get('usage', {}),
                'finish_reason': choice.get('finish_reason', 'stop')
            }
            
            self.resources[resource_id] = {
                "id": resource_id,
                "type_name": type_name,
                "attributes": result_data
            }
            
            # Create response
            new_state_struct = Struct()
            ParseDict(result_data, new_state_struct)
            
            new_state = provider_pb2.ResourceState(
                id=resource_id,
                type=type_name,
                attributes=new_state_struct,
                status='ready'
            )
            
            return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)
        
        except requests.exceptions.RequestException as e:
            diag = self._create_diagnostic(
                provider_pb2.Diagnostic.ERROR,
                f"Azure chat completion failed: {str(e)}",
                str(e)
            )
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
        except Exception as e:
            diag = self._create_diagnostic(
                provider_pb2.Diagnostic.ERROR,
                f"Unexpected error: {str(e)}",
                str(e)
            )
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
    
    def DeleteResource(self, request, context):
        resource_id = request.id
        if resource_id in self.resources:
            del self.resources[resource_id]
        return provider_pb2.DeleteResourceResponse()

if __name__ == '__main__':
    from v2.runtime import create_provider_server
    create_provider_server(AzureOpenAIProvider())