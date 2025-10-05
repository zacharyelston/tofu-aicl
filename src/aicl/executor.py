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
            
            # Merge config with attributes for metadata display (config has original values)
            display_attrs = {**resolved_config, **attributes}
            
            # Display output abstract
            self._display_output_abstract(res_type, res_name, display_attrs)
        except grpc.RpcError as e:
            print(f"Error applying resource {res_name}: {e.details()}")
            # self.destroy() # This should be handled in the engine
            raise

    def _display_output_abstract(self, res_type, res_name, attributes):
        """Display a summary of resource output with metadata"""
        
        # Chat responses
        if res_type == 'chat':
            response = attributes.get('response', '')
            model = attributes.get('model', 'unknown')
            usage = attributes.get('usage', {})
            
            if response:
                preview = response[:150] + '...' if len(response) > 150 else response
                print(f"    → Response: {preview}")
            
            # Show model and token usage if available
            if model:
                print(f"    → Model: {model}")
            if usage:
                prompt_tokens = usage.get('prompt_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)
                total_tokens = usage.get('total_tokens', prompt_tokens + completion_tokens)
                if total_tokens > 0:
                    print(f"    → Tokens: {total_tokens} total ({prompt_tokens} prompt + {completion_tokens} completion)")
        
        # Query results
        elif res_type == 'query':
            matches = attributes.get('matches', [])
            results = attributes.get('results', [])
            count = attributes.get('count', len(matches))
            namespace = attributes.get('namespace', 'default')
            
            if count > 0:
                print(f"    → Retrieved {count} document(s) from namespace '{namespace}'")
                
                # Show top matches with scores
                if results and len(results) > 0:
                    for i, result in enumerate(results[:3]):  # Show top 3
                        score = result.get('score', 0)
                        source = result.get('source', 'unknown')
                        # Truncate long source paths
                        if len(source) > 60:
                            source = '...' + source[-57:]
                        print(f"    → Match #{i+1}: {source} (score: {score:.3f})")
        
        # Embeddings
        elif res_type == 'embedding':
            embeddings = attributes.get('embeddings', [])
            vector = attributes.get('vector', [])
            model = attributes.get('model', 'unknown')
            count = attributes.get('count', len(embeddings))
            
            if count > 0:
                print(f"    → Generated {count} embedding(s)")
                print(f"    → Model: {model}")
                if embeddings and len(embeddings) > 0:
                    dims = len(embeddings[0].get('vector', []))
                    if dims > 0:
                        print(f"    → Dimensions: {dims}")
            elif vector:
                print(f"    → Generated 1 embedding vector")
                print(f"    → Model: {model}")
                print(f"    → Dimensions: {len(vector)}")
        
        # File loader
        elif res_type == 'loader_files':
            documents = attributes.get('documents', [])
            path = attributes.get('path', 'unknown')
            total_chars = sum(len(doc.get('content', '')) for doc in documents)
            
            if documents:
                print(f"    → Loaded {len(documents)} document(s) from '{path}'")
                print(f"    → Total size: {total_chars:,} characters")
                # Show sample filenames
                if len(documents) > 0:
                    sources = [doc.get('source', '') for doc in documents[:3]]
                    for src in sources:
                        if src:
                            print(f"    → File: {src}")
        
        # Text splitter
        elif res_type == 'text_splitter':
            chunks = attributes.get('chunks', [])
            chunk_size = attributes.get('chunk_size', 'unknown')
            overlap = attributes.get('chunk_overlap', 'unknown')
            
            if chunks:
                total_chars = sum(len(chunk.get('content', '')) for chunk in chunks)
                print(f"    → Created {len(chunks)} chunk(s)")
                print(f"    → Chunk size: {chunk_size}, overlap: {overlap}")
                print(f"    → Total size: {total_chars:,} characters")
        
        # Upsert
        elif res_type == 'upsert':
            upserted_count = attributes.get('upserted_count', 0)
            namespace = attributes.get('namespace', 'default')
            dimension = attributes.get('dimension', 'unknown')
            
            if upserted_count > 0:
                print(f"    → Upserted {upserted_count} vector(s) to namespace '{namespace}'")
                if dimension != 'unknown':
                    print(f"    → Vector dimension: {dimension}")
    
    def _dict_to_struct(self, d: dict) -> Struct:
        s = Struct()
        ParseDict(d, s)
        return s