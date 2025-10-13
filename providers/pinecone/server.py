import grpc
import os
import requests
from concurrent import futures
from google.protobuf.struct_pb2 import Struct
from google.protobuf.json_format import MessageToDict, ParseDict

import proto.provider_pb2 as provider_pb2
import proto.provider_pb2_grpc as provider_pb2_grpc

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

        config = MessageToDict(request.config)

        # Get resource name for consistent ID generation
        resource_name = config.get('aiclResourceName', '')

        # Handle upsert operation
        if request.type_name in ["upsert", "pinecone_upsert"]:
            return self._upsert_vectors(config, request.type_name, resource_name)

        # Handle query operation
        elif request.type_name in ["query", "pinecone_query"]:
            return self._query_vectors(config, request.type_name, resource_name)

        # Handle index creation (legacy)
        elif request.type_name == "pinecone_index":
            return self._create_index(config, request.type_name)

        else:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"Unsupported resource type: {request.type_name}")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

    def _create_index(self, config, type_name):
        """Create a new Pinecone index"""
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
            controller_host = "https://api.pinecone.io"
            response = requests.post(
                f"{controller_host}/indexes",
                headers={"Api-Key": self.api_key, "Content-Type": "application/json"},
                json=payload
            )
            response.raise_for_status()

            new_state_struct = Struct()
            ParseDict(config, new_state_struct)
            new_state = provider_pb2.ResourceState(
                id=index_name,
                type=type_name,
                attributes=new_state_struct,
                status='ready'
            )
            return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)

        except requests.exceptions.RequestException as e:
            error_msg = e.response.text if hasattr(e, 'response') else str(e)
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"Failed to create Pinecone index: {error_msg}")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

    def _upsert_vectors(self, config, type_name, resource_name=''):
        """Upsert vectors to Pinecone index"""
        vectors = config.get('vectors', [])
        namespace = config.get('namespace', '')

        print(f"[PINECONE UPSERT] Called with namespace: {namespace}")
        print(f"[PINECONE UPSERT] Number of vectors: {len(vectors)}")
        print(f"[PINECONE UPSERT] Config keys: {list(config.keys())}")

        if not vectors:
            print(f"[PINECONE UPSERT] ERROR: No vectors provided!")
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "No vectors provided for upsert")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

        try:
            print(f"[PINECONE UPSERT] Formatting {len(vectors)} vectors...")
            # Format vectors for Pinecone API
            formatted_vectors = []
            for vec in vectors:
                formatted_vectors.append({
                    'id': vec.get('id', ''),
                    'values': vec.get('values', []),
                    'metadata': vec.get('metadata', {})
                })

            payload = {'vectors': formatted_vectors}
            if namespace:
                payload['namespace'] = namespace

            print(f"[PINECONE UPSERT] Sending to: {self.host_url}/vectors/upsert")
            print(f"[PINECONE UPSERT] Payload has {len(formatted_vectors)} vectors")
            
            response = requests.post(
                f"{self.host_url}/vectors/upsert",
                headers={"Api-Key": self.api_key, "Content-Type": "application/json"},
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"[PINECONE UPSERT] SUCCESS! Upserted: {result.get('upsertedCount', 0)} vectors")
            print(f"[PINECONE UPSERT] Response: {result}")

            output_attributes = {
                'upserted_count': result.get('upsertedCount', len(vectors)),
                'namespace': namespace,
                'vectors': vectors
            }

            output_struct = Struct()
            ParseDict(output_attributes, output_struct)

            # Use resource name from AICL config for consistent IDs
            resource_id = f"{type_name}-{resource_name}" if resource_name else f"upsert-{namespace or 'default'}"

            new_state = provider_pb2.ResourceState(
                id=resource_id,
                type=type_name,
                attributes=output_struct,
                status='ready'
            )
            return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)

        except requests.exceptions.HTTPError as e:
            error_detail = f"Upsert failed: {str(e)}"
            if e.response is not None:
                try:
                    error_body = e.response.json()
                    error_detail += f" | Response: {error_body}"
                except:
                    error_detail += f" | Response text: {e.response.text[:500]}"
            print(f"[PINECONE UPSERT] ERROR: {error_detail}")
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, error_detail)
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
        except Exception as e:
            print(f"[PINECONE UPSERT] ERROR: {str(e)}")
            import traceback
            print(f"[PINECONE UPSERT] Traceback: {traceback.format_exc()}")
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"Upsert failed: {str(e)}")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

    def _query_vectors(self, config, type_name, resource_name=''):
        """Query vectors from Pinecone index"""
        vector = config.get('vector', [])
        top_k = config.get('top_k', 5)
        namespace = config.get('namespace', '')
        include_metadata = config.get('include_metadata', True)

        print(f"[PINECONE QUERY] Called with namespace: {namespace}, top_k: {top_k}")
        print(f"[PINECONE QUERY] Vector length: {len(vector) if vector else 0}")

        if not vector:
            print(f"[PINECONE QUERY] ERROR: No query vector provided!")
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, "No query vector provided")
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])

        try:
            print(f"[PINECONE QUERY] Querying {self.host_url}/query...")
            payload = {
                'vector': vector,
                'topK': top_k,
                'includeMetadata': include_metadata
            }
            if namespace:
                payload['namespace'] = namespace

            response = requests.post(
                f"{self.host_url}/query",
                headers={"Api-Key": self.api_key, "Content-Type": "application/json"},
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"[PINECONE QUERY] SUCCESS! Got {len(result.get('matches', []))} matches")
            if result.get('matches'):
                print(f"[PINECONE QUERY] Top match score: {result['matches'][0].get('score', 0)}")

            # Extract matches
            matches = []
            results = []
            for match in result.get('matches', []):
                metadata = match.get('metadata', {})
                matches.append({
                    'id': match.get('id'),
                    'score': match.get('score'),
                    'metadata': metadata
                })
                # Format for easy consumption by chat
                results.append({
                    'content': metadata.get('content', ''),
                    'source': metadata.get('source', ''),
                    'score': match.get('score', 0)
                })

            output_attributes = {
                'matches': matches,
                'results': results,  # Formatted for easy use
                'namespace': namespace,
                'count': len(matches)
            }

            output_struct = Struct()
            ParseDict(output_attributes, output_struct)

            # Use resource name from AICL config for consistent IDs
            resource_id = f"{type_name}-{resource_name}" if resource_name else f"query-{namespace or 'default'}"

            new_state = provider_pb2.ResourceState(
                id=resource_id,
                type=type_name,
                attributes=output_struct,
                status='ready'
            )
            return provider_pb2.ApplyResourceChangeResponse(new_state=new_state)

        except requests.exceptions.HTTPError as e:
            error_detail = f"Query failed: {str(e)}"
            if e.response is not None:
                try:
                    error_body = e.response.json()
                    error_detail += f" | Response: {error_body}"
                except:
                    error_detail += f" | Response text: {e.response.text[:500]}"
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, error_detail)
            return provider_pb2.ApplyResourceChangeResponse(diagnostics=[diag])
        except Exception as e:
            diag = self._create_diagnostic(provider_pb2.Diagnostic.ERROR, f"Query failed: {str(e)}")
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

if __name__ == '__main__':
    from v2.runtime import create_provider_server
    create_provider_server(PineconeProvider())