import grpc
import os
import requests
from concurrent import futures
from dotenv import load_dotenv
from google.protobuf.struct_pb2 import Struct

import proto.provider_pb2 as provider_pb2
import proto.provider_pb2_grpc as provider_pb2_grpc

load_dotenv()

class PineconeProvider(provider_pb2_grpc.ProviderServicer):
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.host_url = os.getenv("PINECONE_HOST_URL")

    def _create_diagnostic(self, severity, summary, detail=""):
        return provider_pb2.Diagnostic(severity=severity, summary=summary, detail=detail)

    def Configure(self, request, context):
        # Configuration is now handled by environment variables
        return provider_pb2.ConfigureResponse()

    def ApplyResourceChange(self, request, context):
        if not self.api_key or not self.host_url:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "PINECONE_API_KEY and PINECONE_HOST_URL must be set.")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

        if request.type_name != "pinecone_index":
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"Unsupported resource type: {request.type_name}")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

        config = dict(request.config)
        index_name = config.get('name')
        dimension = int(config.get('dimension'))
        metric = config.get('metric', 'cosine')

        payload = {
            "name": index_name,
            "dimension": dimension,
            "metric": metric,
            "spec": {
                "serverless": {
                    "cloud": config.get('cloud', 'aws'),
                    "region": config.get('region', 'us-east-1')
                }
            }
        }

        try:
            # Create is a special case that goes to the controller host
            controller_host = "https://api.pinecone.io"
            response = requests.post(
                f"{controller_host}/indexes",
                headers={"Api-Key": self.api_key, "Content-Type": "application/json"},
                json=payload
            )
            response.raise_for_status()

            new_state_struct = Struct()
            new_state_struct.update(config)
            new_state = provider_pb2.ResourceState(
                id=index_name,
                type=request.type_name,
                attributes=new_state_struct,
                status='ready'
            )
            return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)

        except requests.exceptions.RequestException as e:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"Failed to create Pinecone index: {e.response.text}", str(e))
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

    def DeleteResource(self, request, context):
        index_name = request.id
        try:
            controller_host = "https://api.pinecone.io"
            response = requests.delete(
                f"{controller_host}/indexes/{index_name}",
                headers={"Api-Key": self.api_key}
            )
            if response.status_code not in [204, 404]:
                response.raise_for_status()
            return provider_pb2.DeleteResourceResponse()

        except requests.exceptions.RequestException as e:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "Failed to delete Pinecone index", str(e))
            return provider_pb2.DeleteResourceResponse(diagnostics=[diag])

    # Other methods remain the same...

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    provider_pb2_grpc.add_ProviderServicer_to_server(PineconeProvider(), server)
    port = os.getenv("PORT", "50051")
    server.add_insecure_port(f'[::]:{port}')
    print(f"Pinecone provider listening on port {port}...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
