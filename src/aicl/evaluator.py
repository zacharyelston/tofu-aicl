import re
from typing import Any, Dict
from aicl.state.manager import StateManager

class HCLEvaluator:
    def __init__(self, state_manager: StateManager, parsed_config: Dict[str, Any] = None):
        self.state_manager = state_manager
        self.parsed_config = parsed_config or {}
        self.interpolation_pattern = re.compile(r'\$\{([^}]+)\}')

    def build_context(self, variable_overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        context = {'resource': {}, 'var': {}}

        # Add variables from HCL config
        variables = self.parsed_config.get('variable', [])
        for var_block in variables:
            for var_name, var_config in var_block.items():
                # Use override value if provided, otherwise use default
                if variable_overrides and var_name in variable_overrides:
                    context['var'][var_name] = variable_overrides[var_name]
                elif isinstance(var_config, dict) and 'default' in var_config:
                    context['var'][var_name] = var_config['default']
                else:
                    # No default and no override - leave undefined
                    pass

        # Add resources from state
        if self.state_manager.current_state:
            for resource_id, resource_state in self.state_manager.current_state.resources.items():
                # Skip resources with empty types (invalid/failed resources)
                if not resource_state.type or resource_state.type.strip() == "":
                    continue
                
                # Resource type is stored in resource_state.type (e.g., "loader_files")
                # Resource name is extracted from ID (e.g., "loader-docs" -> "docs")
                res_type = resource_state.type
                res_name = resource_id.split('-', 1)[1] if '-' in resource_id else resource_id

                if res_type not in context['resource']:
                    context['resource'][res_type] = {}

                context['resource'][res_type][res_name] = {
                    'id': resource_state.id,
                    'type': resource_state.type,
                    'attributes': resource_state.attributes,
                    'metadata': resource_state.metadata,
                    'status': resource_state.status
                }

        return context

    def resolve_value(self, value: Any, context: Dict[str, Any]) -> Any:
        if not isinstance(value, str):
            return value

        # Check if the entire value is a single interpolation
        full_match = self.interpolation_pattern.fullmatch(value.strip())
        if full_match:
            expr = full_match.group(1).strip()
            # Return the actual value without converting to string
            return self._evaluate_expression(expr, context)

        # Handle partial interpolations (string with embedded ${...})
        if '${' in value:
            def replace_interpolation(match):
                expr = match.group(1).strip()
                result = self._evaluate_expression(expr, context)
                return str(result) if result is not None else ''

            resolved = self.interpolation_pattern.sub(replace_interpolation, value)
            return resolved

        return value

    def _evaluate_expression(self, expr: str, context: Dict[str, Any]) -> Any:
        parts = expr.split('.')
        current = context

        for i, part in enumerate(parts):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                # Debug: Show where resolution failed
                path_so_far = '.'.join(parts[:i])
                print(f"[EVALUATOR] Failed to resolve '{expr}' at part '{part}' (path so far: '{path_so_far}')")
                if isinstance(current, dict):
                    print(f"[EVALUATOR] Available keys at this level: {list(current.keys())[:10]}")
                return f"${{{expr}}}"

        return current

    def resolve_config(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        resolved = {}
        for key, value in config.items():
            if isinstance(value, dict):
                resolved[key] = self.resolve_config(value, context)
            elif isinstance(value, list):
                resolved[key] = [
                    self.resolve_config(item, context) if isinstance(item, dict)
                    else self.resolve_value(item, context)
                    for item in value
                ]
            else:
                resolved[key] = self.resolve_value(value, context)
        return resolved