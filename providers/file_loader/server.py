import grpc
import os
from concurrent import futures
from pathlib import Path
from google.protobuf.struct_pb2 import Struct

import proto.provider_pb2 as provider_pb2
import proto.provider_pb2_grpc as provider_pb2_grpc

class FileLoaderProvider(provider_pb2_grpc.ProviderServicer):

    def _create_diagnostic(self, severity, summary, detail=""):
        return provider_pb2.Diagnostic(severity=severity, summary=summary, detail=detail)

    def ApplyResourceChange(self, request, context):
        if request.type_name != "loader_files":
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"Unsupported resource type: {request.type_name}")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

        config = dict(request.config)
        path = config.get('path', '.')
        glob = config.get('glob', '**/*')

        documents = []
        try:
            for file_path in Path(path).rglob(glob):
                if file_path.is_file():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    documents.append({
                        'path': str(file_path),
                        'content': content
                    })
            
            output_attributes = {'documents': documents}
            output_struct = Struct()
            output_struct.update(output_attributes)

            new_state = provider_pb2.ResourceState(
                id=f"loader-{Path(path).name}",
                type=request.type_name,
                attributes=output_struct
            )
            return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)

        except Exception as e:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "Failed to load files", str(e))
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
    # --- Minimal Implementations for other required RPCs ---
    def Configure(self, request, context):
        return provider_pb2.ConfigureResponse()

    def GetSchema(self, request, context):
        return provider_pb2.GetSchemaResponse()

    def ReadResource(self, request, context):
        return provider_pb2.ReadResourceResponse()

    def DeleteResource(self, request, context):
        return provider_pb2.DeleteResourceResponse()

    def Execute(self, request, context):
        yield provider_pb2.ExecuteResponse(log="Execute is not applicable for this provider.")

    def Validate(self, request, context):
        return provider_pb2.ValidateResponse(success=True)
        
    def HealthCheck(self, request, context):
        return provider_pb2.HealthCheckResponse(healthy=True, version="0.1.0")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    provider_pb2_grpc.add_ProviderServicer_to_server(FileLoaderProvider(), server)
    port = os.getenv("PORT", "50051")
    server.add_insecure_port(f'[::]:{port}')
    print(f"File Loader provider listening on port {port}...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
