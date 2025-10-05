from google.protobuf.json_format import MessageToDict
from google.protobuf.struct_pb2 import Struct
import grpc
import proto.provider_pb2 as provider_pb2
from aicl.state.manager import ResourceState

class Executor:
    def __init__(self, providers, state_manager):
        self.providers = providers
        self.state_manager = state_manager

    def execute_node(self, node_id, resource_map):
        res_type, res_name, config_attrs = resource_map[node_id]
        provider_name = res_type.split('_')[0]
        provider = self.providers.get(provider_name)
        if not provider:
            raise Exception(f"Provider '{provider_name}' not found for resource '{res_name}'")

        # Manual dependency resolution
        for key, value in config_attrs.items():
            if isinstance(value, str) and 'resource.' in value:
                # Strip ${} wrapper if present
                clean_value = value.strip('${}').strip()
                if clean_value.startswith('resource.'):
                    parts = clean_value.split('.')
                    if len(parts) >= 5:
                        ref_type, ref_name, ref_attr, ref_key = parts[1], parts[2], parts[3], parts[4]
                        
                        ref_resource_state = self.state_manager.get_resource_by_name(ref_type, ref_name)
                        if ref_resource_state:
                            config_attrs[key] = ref_resource_state.attributes.get(ref_key)
                        else:
                            raise Exception(f"Referenced resource '{ref_type}.{ref_name}' not found in state")

        config_struct = self._dict_to_struct(config_attrs)
        req = provider_pb2.ApplyResourceChangeRequest(type_name=res_type, config=config_struct)
        
        try:
            response = provider.stub.ApplyResourceChange(req)
            # self._handle_diagnostics(response.diagnostics) # This should be handled in the engine
            state = response.new_state
            attributes = MessageToDict(state.attributes)
            metadata = MessageToDict(state.metadata)
            resource_state = ResourceState(
                id=state.id, type=state.type, provider=provider_name,
                attributes=attributes, metadata=metadata, status=state.status
            )
            self.state_manager.add_resource(resource_state)
            print(f"  + Resource '{res_name}' ({state.id}) created successfully.")
        except grpc.RpcError as e:
            print(f"Error applying resource {res_name}: {e.details()}")
            # self.destroy() # This should be handled in the engine
            raise

    def _dict_to_struct(self, d: dict) -> Struct:
        s = Struct()
        s.update(d)
        return s
