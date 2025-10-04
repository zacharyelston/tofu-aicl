import grpc
import os
from concurrent import futures
from google.protobuf.struct_pb2 import Struct

import proto.provider_pb2 as provider_pb2
import proto.provider_pb2_grpc as provider_pb2_grpc

class TextSplitterProvider(provider_pb2_grpc.ProviderServicer):

    def _create_diagnostic(self, severity, summary, detail=""):
        return provider_pb2.Diagnostic(severity=severity, summary=summary, detail=detail)

    def _split_text(self, text, chunk_size, chunk_overlap):
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - chunk_overlap
        return chunks

    def ApplyResourceChange(self, request, context):
        config = dict(request.config)
        documents = config.get('documents', [])
        chunk_size = int(config.get('chunk_size', 1000))
        chunk_overlap = int(config.get('chunk_overlap', 200))

        all_chunks = []
        for doc in documents:
            text = doc.get('content', '')
            chunks = self._split_text(text, chunk_size, chunk_overlap)
            for chunk in chunks:
                all_chunks.append({'content': chunk, 'source': doc.get('path')})

        output_struct = Struct()
        output_struct.update(output_attributes)

        new_state = provider_pb2.ResourceState(
            id="text-splitter",
            type=request.type_name,
            attributes=output_struct
        )
        return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)

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
    provider_pb2_grpc.add_ProviderServicer_to_server(TextSplitterProvider(), server)
    port = os.getenv("PORT", "50051")
    server.add_insecure_port(f'[::]:{port}')
    print(f"Text Splitter provider listening on port {port}...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
