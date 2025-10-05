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

class OpenAIProvider(provider_pb2_grpc.ProviderServicer):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        self.resources: Dict[str, Dict[str, Any]] = {}

    def _create_diagnostic(self, severity, summary, detail=""):
        return provider_pb2.Diagnostic(severity=severity, summary=summary, detail=detail)

    def GetSchema(self, request, context):
        schema = Struct()
        schema.update({
            "type": "object",
            "properties": {
                "model": {"type": "string", "description": "Model identifier", "default": "text-embedding-3-small"},
                "dimensions": {"type": "integer", "description": "Number of dimensions (optional)"}
            }
        })
        resource_schema = provider_pb2.GetSchemaResponse.ResourceSchema(
            type_name="openai_embedding",
            schema=schema
        )
        return provider_pb2.GetSchemaResponse(resources=[resource_schema])

    def ValidateConfig(self, request, context):
        return provider_pb2.ValidateConfigResponse()

    def Configure(self, request, context):
        if not self.api_key:
            diag = self._create_diagnostic(
                provider_pb2.Diagnostic.ERROR,
                "OPENAI_API_KEY environment variable not set"
            )
            return provider_pb2.ConfigureResponse(diagnostics=[diag])
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
            resource_id = f"openai-{uuid.uuid4().hex[:8]}"

        # Handle embeddings
        if request.type_name in ["embedding", "openai_embedding"]:
            return self._generate_embeddings(resource_id, config, request.type_name)

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
        """Generate embeddings using OpenAI API"""
        # Handle both single text and array of texts
        single_text = config.get('text')
        texts = config.get('texts', [])

        if single_text:
            texts = [single_text]

        model = config.get('model', 'text-embedding-3-small')
        dimensions = config.get('dimensions')

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

            # Prepare request payload
            payload = {
                "model": model,
                "input": text_list
            }
            if dimensions:
                payload["dimensions"] = dimensions

            # Call OpenAI API
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
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
                'model': model,
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
                f"Embeddings generation failed: {str(e)}",
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

def serve(port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    provider_pb2_grpc.add_ProviderServicer_to_server(OpenAIProvider(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"OpenAI Provider started on port {port}")
    server.wait_for_termination()

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50051
    serve(port)