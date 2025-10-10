from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.struct_pb2 import Struct
import grpc
import proto.provider_pb2 as provider_pb2
from aicl.state.manager import ResourceState
from aicl.evaluator import HCLEvaluator
from aicl.observability import get_tracer

class Executor:
    def __init__(self, providers, state_manager, parsed_config=None):
        self.providers = providers
        self.state_manager = state_manager
        self.parsed_config = parsed_config or {}
        self.evaluator = HCLEvaluator(state_manager, parsed_config)
        self.tracer = get_tracer(__name__)

        # Map resource types to provider names
        self.resource_to_provider = {
            'file_loader': 'file_loader',
            'text_splitter': 'text_splitter',
            'embedding': 'openai',
            'azure_openai_embedding': 'azure_openai',
            'chat': 'openrouter',
            'upsert': 'pinecone',
            'query': 'pinecone',
        }

    def execute_node(self, node_id, resource_map):
        with self.tracer.start_as_current_span(f"provision_resource.{node_id}") as span:
            res_type, res_name, config_attrs = resource_map[node_id]
            span.set_attribute("resource.type", res_type)
            span.set_attribute("resource.name", res_name)

            # Map resource type to provider name
            provider_name = self.resource_to_provider.get(res_type)
            if not provider_name:
                # Fallback to old behavior for backward compatibility
                provider_name = res_type.split('_')[0]

            span.set_attribute("resource.provider", provider_name)
            provider = self.providers.get(provider_name)
            if not provider:
                raise Exception(f"Provider '{provider_name}' not found for resource '{res_name}'")

            # Build evaluation context from current state
            with self.tracer.start_as_current_span("evaluate_config"):
                context = self.evaluator.build_context()
                resolved_config = self.evaluator.resolve_config(config_attrs, context)

            # Add resource metadata for provider to use in ID generation
            resolved_config['aiclResourceName'] = res_name
            resolved_config['aiclResourceType'] = res_type

            config_struct = self._dict_to_struct(resolved_config)
            req = provider_pb2.ApplyResourceChangeRequest(type_name=res_type, config=config_struct)

            try:
                with self.tracer.start_as_current_span("provider_apply"):
                    response = provider.stub.ApplyResourceChange(req)
                    state = response.new_state

                    attributes = MessageToDict(state.attributes)
                    metadata = MessageToDict(state.metadata)
                    resource_state = ResourceState(
                        id=state.id, type=state.type, provider=provider_name,
                        attributes=attributes, metadata=metadata, status=state.status
                    )
                    self.state_manager.add_resource(resource_state)
                    
                    # Set success attributes after successful completion
                    span.set_attribute("resource.id", state.id)
                    span.set_attribute("resource.status", "created")
                    print(f"  + Resource '{res_name}' ({state.id}) created successfully.")
            except grpc.RpcError as e:
                span.set_attribute("resource.status", "failed")
                span.record_exception(e)
                print(f"Error applying resource {res_name}: {e.details()}")
                raise

    def _dict_to_struct(self, d: dict) -> Struct:
        s = Struct()
        ParseDict(d, s)
        return s
    
    def _handle_diagnostics(self, diagnostics):
        """Handle and print diagnostics from provider responses."""
        for diag in diagnostics:
            severity = provider_pb2.Diagnostic.Severity.Name(diag.severity)
            print(f"  [{severity}] {diag.summary}: {diag.detail}")
    
    def destroy_all(self):
        """Destroy all resources in current state."""
        with self.tracer.start_as_current_span("destroy_all_resources") as span:
            if not self.state_manager.current_state:
                return
            
            resources = list(self.state_manager.current_state.resources.items())
            span.set_attribute("resource.count", len(resources))
            
            for res_id, res_state in resources:
                with self.tracer.start_as_current_span(f"destroy_resource.{res_id}") as res_span:
                    res_span.set_attribute("resource.id", res_id)
                    res_span.set_attribute("resource.type", res_state.type)
                    
                    provider = self.providers.get(res_state.provider)
                    if provider:
                        try:
                            req = provider_pb2.DeleteResourceRequest(id=res_id, type_name=res_state.type)
                            response = provider.stub.DeleteResource(req)
                            self._handle_diagnostics(response.diagnostics)
                            res_span.set_attribute("resource.status", "deleted")
                            print(f"  - Resource '{res_id}' deleted.")
                        except grpc.RpcError as e:
                            res_span.set_attribute("resource.status", "failed")
                            res_span.record_exception(e)
                            print(f"Error deleting resource {res_id}: {e.details()}")