import re
from collections import defaultdict
from typing import Any, Set

class Planner:
    def __init__(self, parsed_config):
        self.parsed_config = parsed_config
        # Pattern to match resource references: resource.TYPE.NAME
        # Captures the TYPE and NAME groups
        self.resource_pattern = re.compile(r'resource\.([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)')

    def _extract_interpolation_blocks(self, text: str) -> list[str]:
        """
        Extract ${...} interpolation blocks from a string.
        Uses a simplified greedy approach - finds nearest } for each ${.
        Good enough for dependency detection (not perfect evaluation).
        """
        blocks = []
        i = 0
        while i < len(text):
            # Look for ${
            start_idx = text.find('${', i)
            if start_idx == -1:
                break
                
            # Find the nearest } after ${
            # This is greedy and won't handle all nested cases perfectly,
            # but it's sufficient for dependency detection
            end_idx = text.find('}', start_idx + 2)
            if end_idx == -1:
                break
            
            # Extract the block content (between ${ and })
            block = text[start_idx + 2:end_idx]
            blocks.append(block)
            
            # Continue searching after this block
            i = end_idx + 1
        
        return blocks

    def _extract_resource_references(self, value: Any) -> Set[str]:
        """
        Extract all resource references from a value.
        
        Searches for 'resource.TYPE.NAME' ONLY within ${...} interpolation blocks.
        This prevents false dependencies from plain documentation strings.
        """
        references = set()
        
        if isinstance(value, str):
            # Extract all ${...} interpolation blocks
            blocks = self._extract_interpolation_blocks(value)
            
            # Search for resource references only within these blocks
            for block in blocks:
                for match in self.resource_pattern.finditer(block):
                    resource_type = match.group(1)
                    resource_name = match.group(2)
                    dep_id = f"{resource_type}.{resource_name}"
                    references.add(dep_id)
        
        elif isinstance(value, list):
            for item in value:
                references.update(self._extract_resource_references(item))
        
        elif isinstance(value, dict):
            for v in value.values():
                references.update(self._extract_resource_references(v))
        
        return references

    def build_graph(self):
        adj = defaultdict(list)
        in_degree = defaultdict(int)
        resource_map = {}
        all_resource_ids = []

        # First pass: build resource map
        resources = self.parsed_config.get('resource', [])
        for res_config in resources:
            for res_type, res_details in res_config.items():
                for res_name, config_attrs in res_details.items():
                    node_id = f"{res_type}.{res_name}"
                    resource_map[node_id] = (res_type, res_name, config_attrs)
                    all_resource_ids.append(node_id)
                    in_degree[node_id]  # Initialize

        # Second pass: extract dependencies and validate they exist
        for node_id in all_resource_ids:
            _, _, config_attrs = resource_map[node_id]
            
            # Extract all resource dependencies from config
            dependencies = self._extract_resource_references(config_attrs)
            for dep_id in dependencies:
                # Only add dependency edge if the referenced resource actually exists
                if dep_id in resource_map:
                    adj[dep_id].append(node_id)
                    in_degree[node_id] += 1
                # Silently ignore references to non-existent resources
                # (they might be in comments, string literals, etc.)

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