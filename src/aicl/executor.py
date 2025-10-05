from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.struct_pb2 import Struct
import grpc
import proto.provider_pb2 as provider_pb2
from aicl.state.manager import ResourceState
from aicl.evaluator import HCLEvaluator

class Executor:
    def __init__(self, providers, state_manager):
        self.providers = providers
        self.state_manager = state_manager
        self.evaluator = HCLEvaluator(state_manager)

        # Map resource types to provider names (using aliases from HCL config)
        self.resource_to_provider = {
            'loader_files': 'loader',
            'text_splitter': 'text_splitter',
            'embedding': 'openrouter',
            'chat': 'openrouter',
            'upsert': 'pinecone',
            'query': 'pinecone',
        }

    def execute_node(self, node_id, resource_map):
        res_type, res_name, config_attrs = resource_map[node_id]

        # Map resource type to provider name
        provider_name = self.resource_to_provider.get(res_type)
        if not provider_name:
            # Fallback to old behavior for backward compatibility
            provider_name = res_type.split('_')[0]

        provider = self.providers.get(provider_name)
        if not provider:
            raise Exception(f"Provider '{provider_name}' not found for resource '{res_name}'")

        # Build evaluation context from current state
        context = self.evaluator.build_context()

        # Resolve all interpolations in config
        resolved_config = self.evaluator.resolve_config(config_attrs, context)

        # Add resource metadata for provider to use in ID generation
        # Use camelCase to avoid Protobuf field name transformation issues
        resolved_config['aiclResourceName'] = res_name
        resolved_config['aiclResourceType'] = res_type

        config_struct = self._dict_to_struct(resolved_config)
        req = provider_pb2.ApplyResourceChangeRequest(type_name=res_type, config=config_struct)

        try:
            response = provider.stub.ApplyResourceChange(req)
            state = response.new_state

            attributes = MessageToDict(state.attributes)
            metadata = MessageToDict(state.metadata)
            resource_state = ResourceState(
                id=state.id, type=state.type, provider=provider_name,
                attributes=attributes, metadata=metadata, status=state.status
            )
            self.state_manager.add_resource(resource_state)
            print(f"  + Resource '{res_name}' ({state.id}) created successfully.")
            
            # Display output abstract
            self._display_output_abstract(res_type, res_name, attributes)
        except grpc.RpcError as e:
            print(f"Error applying resource {res_name}: {e.details()}")
            # self.destroy() # This should be handled in the engine
            raise

    def _display_output_abstract(self, res_type, res_name, attributes):
        """Display a summary of resource output"""
        
        # Chat responses
        if res_type == 'chat':
            response = attributes.get('response', '')
            if response:
                preview = response[:150] + '...' if len(response) > 150 else response
                print(f"    → Response: {preview}")
        
        # Query results
        elif res_type == 'query':
            matches = attributes.get('matches', [])
            results = attributes.get('results', [])
            count = attributes.get('count', len(matches))
            if count > 0:
                print(f"    → Retrieved {count} document(s)")
                if results and len(results) > 0:
                    top_result = results[0]
                    score = top_result.get('score', 0)
                    source = top_result.get('source', 'unknown')[:50]
                    print(f"    → Top match: {source} (score: {score:.3f})")
        
        # Embeddings
        elif res_type == 'embedding':
            embeddings = attributes.get('embeddings', [])
            vector = attributes.get('vector', [])
            count = attributes.get('count', len(embeddings))
            if count > 0:
                print(f"    → Generated {count} embedding(s)")
            elif vector:
                print(f"    → Generated 1 embedding vector ({len(vector)} dimensions)")
        
        # File loader
        elif res_type == 'loader_files':
            documents = attributes.get('documents', [])
            if documents:
                print(f"    → Loaded {len(documents)} document(s)")
        
        # Text splitter
        elif res_type == 'text_splitter':
            chunks = attributes.get('chunks', [])
            if chunks:
                print(f"    → Created {len(chunks)} chunk(s)")
        
        # Upsert
        elif res_type == 'upsert':
            upserted_count = attributes.get('upserted_count', 0)
            namespace = attributes.get('namespace', 'default')
            if upserted_count > 0:
                print(f"    → Upserted {upserted_count} vector(s) to namespace '{namespace}'")
    
    def _dict_to_struct(self, d: dict) -> Struct:
        s = Struct()
        ParseDict(d, s)
        return s