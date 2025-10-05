from collections import defaultdict

class Planner:
    def __init__(self, parsed_config):
        self.parsed_config = parsed_config

    def build_graph(self):
        adj = defaultdict(list)
        in_degree = defaultdict(int)
        resource_map = {}
        all_resource_ids = []

        resources = self.parsed_config.get('resource', [])
        for res_config in resources:
            for res_type, res_details in res_config.items():
                for res_name, config_attrs in res_details.items():
                    node_id = f"{res_type}.{res_name}"
                    resource_map[node_id] = (res_type, res_name, config_attrs)
                    all_resource_ids.append(node_id)
                    in_degree[node_id]  # Initialize

                    for value in config_attrs.values():
                        if isinstance(value, str) and 'resource.' in value:
                            # Strip ${} wrapper if present
                            clean_value = value.strip('${}').strip()
                            if clean_value.startswith('resource.'):
                                parts = clean_value.split('.')
                                if len(parts) >= 3:
                                    dep_id = f"{parts[1]}.{parts[2]}"
                                    adj[dep_id].append(node_id)
                                    in_degree[node_id] += 1

        queue = [node for node in all_resource_ids if in_degree[node] == 0]
        sorted_order = []
        while queue:
            node = queue.pop(0)
            sorted_order.append(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_order) != len(all_resource_ids):
            raise Exception("Cycle detected in resource dependencies!")

        return sorted_order, resource_map