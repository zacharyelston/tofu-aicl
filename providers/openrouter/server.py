import grpc
import os
import json
import uuid
import requests
from concurrent import futures
from typing import Dict, Any
from dotenv import load_dotenv
from google.protobuf.struct_pb2 import Struct

import proto.provider_pb2 as provider_pb2
import proto.provider_pb2_grpc as provider_pb2_grpc

# Load API keys from .env file
load_dotenv()

class OpenRouterProvider(provider_pb2_grpc.ProviderServicer):
    def __init__(self):
        self.api_key = None
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
        self.api_key = request.config.get('api_key')
        if not self.api_key:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "Missing 'api_key' in provider configuration")
            return provider_pb2.ConfigureResponse(diagnostics=[diag])

        try:
            response = requests.get(f"{self.base_url}/models", headers={"Authorization": f"Bearer {self.api_key}"})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"API key validation failed: {e}")
            return provider_pb2.ConfigureResponse(diagnostics=[diag])
        
        return provider_pb2.ConfigureResponse()

    # --- Resource Management ---
    def ApplyResourceChange(self, request, context):
        resource_id = request.prior_state.id if request.prior_state and request.prior_state.id else f"or-model-{uuid.uuid4().hex[:8]}"
        config = dict(request.config)
        
        self.resources[resource_id] = {
            "id": resource_id,
            "type_name": request.type_name,
            "attributes": config
        }

        new_state_struct = Struct()
        new_state_struct.update(config)

        new_state = provider_pb2.ResourceState(
            id=resource_id,
            type=request.type_name,
            attributes=new_state_struct,
            status='ready'
        )
        return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)

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
