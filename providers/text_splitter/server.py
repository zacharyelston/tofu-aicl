import grpc
import os
from concurrent import futures
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import MessageToDict, ParseDict

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
        try:
            print(f"DEBUG: Raw config type: {type(request.config)}")
            config = MessageToDict(request.config)
            print(f"DEBUG: Config after MessageToDict: {type(config)}")
            print(f"DEBUG: Config keys: {config.keys() if isinstance(config, dict) else 'NOT A DICT'}")
            documents = config.get('documents', [])
            print(f"DEBUG: Documents type: {type(documents)}, length: {len(documents) if hasattr(documents, '__len__') else 'N/A'}")
            chunk_size = int(config.get('chunk_size', 1000))
            chunk_overlap = int(config.get('chunk_overlap', 200))
            
            # Get resource name from AICL config for consistent ID generation
            resource_name = config.get('aiclResourceName', 'default')
            resource_id = f"{request.type_name}-{resource_name}"

            all_chunks = []
            for i, doc in enumerate(documents):
                print(f"DEBUG: Doc {i} type: {type(doc)}")
                text = doc.get('content', '') if isinstance(doc, dict) else ''
                chunks = self._split_text(text, chunk_size, chunk_overlap)
                for chunk in chunks:
                    all_chunks.append({'content': chunk, 'source': doc.get('path') if isinstance(doc, dict) else ''})
        except Exception as e:
            import traceback
            print(f"ERROR in text_splitter: {e}")
            print(f"TRACEBACK: {traceback.format_exc()}")
            raise

        output_attributes = {'chunks': all_chunks}
        output_struct = Struct()
        ParseDict(output_attributes, output_struct)

        new_state = provider_pb2.ResourceState(
            id=resource_id,
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

if __name__ == '__main__':
    from v2.runtime import create_provider_server
    create_provider_server(TextSplitterProvider())