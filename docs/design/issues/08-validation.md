# Issue 08: No Validation Layer

**Priority:** MEDIUM  
**Week:** 3

## Problem

No validation before operations:
- Config not validated against schema
- References not checked
- No type checking

## Solution

Implement schema validation:

```python
class Validator:
    def __init__(self, provider_schemas):
        self.schemas = provider_schemas
    
    def validate_resource(self, resource_type, config):
        schema = self.schemas.get(resource_type)
        if not schema:
            raise ValueError(f"Unknown resource type: {resource_type}")
        
        # Validate against JSON schema
        jsonschema.validate(config, schema)
    
    def validate_reference(self, ref: str, state):
        # Check reference exists
        parsed = ReferenceResolver.parse(ref)
        resource = state.get_resource_exact(parsed.type, parsed.name)
        
        if not resource:
            raise ValueError(f"Reference not found: {ref}")
```

## Engine Integration

```python
def apply(self):
    # Get schemas from providers
    for name, provider in self.providers.items():
        schema = provider.GetSchema()
        self.validator.register_schema(name, schema)
    
    # Validate all resources before applying
    for resource in self.resources:
        self.validator.validate_resource(
            resource.type,
            resource.config
        )
    
    # Then proceed with apply
    self._provision_resources()
```
