import re
from typing import Any, Dict
from aicl.state.manager import StateManager

class HCLEvaluator:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.interpolation_pattern = re.compile(r'\$\{([^}]+)\}')
    
    def build_context(self) -> Dict[str, Any]:
        context = {'resource': {}}
        
        if self.state_manager.current_state:
            for resource_id, resource_state in self.state_manager.current_state.resources.items():
                parts = resource_id.split('.')
                if len(parts) >= 2:
                    res_type = parts[0]
                    res_name = parts[1]
                    
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
        
        def replace_interpolation(match):
            expr = match.group(1).strip()
            return str(self._evaluate_expression(expr, context))
        
        if '${' in value:
            resolved = self.interpolation_pattern.sub(replace_interpolation, value)
            if resolved == value:
                return value
            if resolved.replace('${', '').replace('}', '') == value.replace('${', '').replace('}', ''):
                return resolved
            return resolved
        
        return value
    
    def _evaluate_expression(self, expr: str, context: Dict[str, Any]) -> Any:
        parts = expr.split('.')
        current = context
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
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
