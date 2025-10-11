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

class RagieProvider(provider_pb2_grpc.ProviderServicer):
    def __init__(self):
        self.api_key = os.getenv("RAGIE_API_KEY")
        self.base_url = "https://api.ragie.ai"
        self.resources: Dict[str, Dict[str, Any]] = {}

    def _create_diagnostic(self, severity, summary, detail=""):
        return provider_pb2.Diagnostic(severity=severity, summary=summary, detail=detail)

    def GetSchema(self, request, context):
        schema = Struct()
        schema.update({
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to file to upload"},
                "query": {"type": "string", "description": "Natural language query"},
                "top_k": {"type": "integer", "description": "Number of results", "default": 8},
                "rerank": {"type": "boolean", "description": "Enable reranking", "default": True},
            }
        })
        resource_schema = provider_pb2.GetSchemaResponse.ResourceSchema(
            type_name="ragie_resource",
            schema=schema
        )
        return provider_pb2.GetSchemaResponse(resources=[resource_schema])

    def ValidateConfig(self, request, context):
        # API key is read from RAGIE_API_KEY environment variable
        # No validation needed in config
        return provider_pb2.ValidateConfigResponse()

    def Configure(self, request, context):
        if not self.api_key:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "RAGIE_API_KEY environment variable not set")
            return provider_pb2.ConfigureResponse(diagnostics=[diag])
        return provider_pb2.ConfigureResponse()

    def ApplyResourceChange(self, request, context):
        config = MessageToDict(request.config)
        
        resource_name = config.get('aiclResourceName', '')
        
        if request.prior_state and request.prior_state.id:
            resource_id = request.prior_state.id
        elif resource_name:
            resource_id = f"{request.type_name}-{resource_name}"
        else:
            resource_id = f"ragie-{uuid.uuid4().hex[:8]}"

        # Handle document upload
        if request.type_name in ["ragie_upload", "ragie_document"]:
            return self._upload_document(resource_id, config, request.type_name)
        
        # Handle retrieval/query
        elif request.type_name in ["ragie_retrieval", "ragie_query"]:
            return self._retrieve(resource_id, config, request.type_name)
        
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

    def _upload_document(self, resource_id, config, type_name):
        """Upload a document to Ragie for indexing"""
        file_path = config.get('file_path') or config.get('path')
        metadata = config.get('metadata', {})
        name = config.get('name')
        partition = config.get('partition')
        mode = config.get('mode', 'fast')  # 'fast' or 'hi_res'
        external_id = config.get('external_id')
        
        if not file_path:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "file_path is required for ragie_upload")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
        
        if not os.path.exists(file_path):
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"File not found: {file_path}")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
        
        try:
            # Prepare multipart upload
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'mode': mode}
                
                if metadata:
                    data['metadata'] = json.dumps(metadata)
                if name:
                    data['name'] = name
                if partition:
                    data['partition'] = partition
                if external_id:
                    data['external_id'] = external_id
                
                response = requests.post(
                    f"{self.base_url}/documents",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files=files,
                    data=data,
                    timeout=120
                )
            
            if response.status_code in [200, 201]:
                result = response.json()
                attributes = {
                    "document_id": result.get('id'),
                    "status": result.get('status'),
                    "name": result.get('name'),
                    "chunk_count": result.get('chunk_count'),
                    "page_count": result.get('page_count'),
                    "partition": result.get('partition'),
                    "created_at": result.get('created_at'),
                    "metadata": result.get('metadata', {}),
                    "file_path": file_path
                }
                
                self.resources[resource_id] = {
                    "id": resource_id,
                    "type_name": type_name,
                    "attributes": attributes
                }
                
                new_state_struct = Struct()
                ParseDict(attributes, new_state_struct)
                
                new_state = provider_pb2.ResourceState(
                    id=resource_id,
                    type=type_name,
                    attributes=new_state_struct,
                    status='ready'
                )
                return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)
            else:
                error_detail = response.text[:500]
                diag = self._create_diagnostic(
                    provider_pb2.Diagnostic.ERROR,
                    f"Ragie upload failed: {response.status_code}",
                    error_detail
                )
                return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
                
        except Exception as e:
            diag = self._create_diagnostic(
                provider_pb2.Diagnostic.ERROR,
                "Ragie upload error",
                str(e)
            )
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

    def _retrieve(self, resource_id, config, type_name):
        """Retrieve relevant chunks from Ragie"""
        query = config.get('query')
        top_k = config.get('top_k', config.get('topK', 8))
        rerank = config.get('rerank', True)
        recency_bias = config.get('recency_bias', config.get('recencyBias', False))
        filter_obj = config.get('filter')
        partition = config.get('partition')
        
        if not query:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "query is required for ragie_retrieval")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
        
        try:
            payload = {
                "query": query,
                "topK": top_k,
                "rerank": rerank,
                "recencyBias": recency_bias
            }
            
            if filter_obj:
                payload["filter"] = filter_obj
            if partition:
                payload["partition"] = partition
            
            response = requests.post(
                f"{self.base_url}/retrievals",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                chunks = result.get('scored_chunks', result.get('chunks', []))
                
                attributes = {
                    "query": query,
                    "chunks": chunks,
                    "top_k": top_k,
                    "num_results": len(chunks),
                    "rerank": rerank,
                    "recency_bias": recency_bias
                }
                
                self.resources[resource_id] = {
                    "id": resource_id,
                    "type_name": type_name,
                    "attributes": attributes
                }
                
                new_state_struct = Struct()
                ParseDict(attributes, new_state_struct)
                
                new_state = provider_pb2.ResourceState(
                    id=resource_id,
                    type=type_name,
                    attributes=new_state_struct,
                    status='ready'
                )
                return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)
            else:
                error_detail = response.text[:500]
                diag = self._create_diagnostic(
                    provider_pb2.Diagnostic.ERROR,
                    f"Ragie retrieval failed: {response.status_code}",
                    error_detail
                )
                return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
                
        except Exception as e:
            diag = self._create_diagnostic(
                provider_pb2.Diagnostic.ERROR,
                "Ragie retrieval error",
                str(e)
            )
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

    def RefreshResourceState(self, request, context):
        resource_id = request.current_state.id
        resource = self.resources.get(resource_id)
        
        if not resource:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"Resource not found: {resource_id}")
            return provider_pb2.RefreshResourceStateResponse(diagnostics=[diag])
        
        state_struct = Struct()
        ParseDict(resource['attributes'], state_struct)
        
        new_state = provider_pb2.ResourceState(
            id=resource_id,
            type=resource['type_name'],
            attributes=state_struct,
            status='ready'
        )
        return provider_pb2.RefreshResourceStateResponse(new_state=new_state)

    def DeleteResource(self, request, context):
        # Get resource ID from request (not current_state which may be empty)
        resource_id = request.id or (request.current_state.id if request.current_state else None)
        
        if resource_id and resource_id in self.resources:
            resource = self.resources[resource_id]
            
            # If it's a document, optionally delete from Ragie
            if resource['type_name'] in ["ragie_upload", "ragie_document"]:
                document_id = resource['attributes'].get('document_id')
                if document_id:
                    try:
                        requests.delete(
                            f"{self.base_url}/documents/{document_id}",
                            headers={"Authorization": f"Bearer {self.api_key}"},
                            timeout=30
                        )
                    except:
                        pass  # Best effort cleanup
            
            del self.resources[resource_id]
        
        return provider_pb2.DeleteResourceResponse()

if __name__ == '__main__':
    from v2.runtime import create_provider_server
    create_provider_server(RagieProvider())
