# Issue 01: Dependency Resolution is Broken

**Priority:** CRITICAL  
**Week:** 1

## Problem

Current dependency resolution makes dangerous assumptions:

```python
# In executor.py
ref_type, ref_name, ref_attr, ref_key = parts[1], parts[2], parts[3], parts[4]
# Assumes: resource.loader_files.docs.attributes.documents
#          parts:  [0]     [1]        [2]    [3]        [4]
```

**Issues:**
1. Assumes exactly 5 parts (what about `resource.foo.bar.id`?)
2. Hardcodes `attributes` as part[3]
3. Uses fuzzy matching: `if name in res.id`
4. No validation that reference exists

## Example Failure

```hcl
resource "splitter_text" "chunks" {
  documents = resource.loader_files.docs.id  # 4 parts, not 5!
}
```

Current code will crash with IndexError.

## Solution

Build a proper reference parser:

```python
class ReferenceResolver:
    def parse(self, ref: str) -> Reference:
        # resource.{type}.{name}.{attribute_path}
        parts = ref.split('.')
        
        if parts[0] != "resource":
            raise ValueError(f"Invalid reference: {ref}")
        
        return Reference(
            type=parts[1],
            name=parts[2],
            path=parts[3:]  # Remaining parts are attribute path
        )
    
    def resolve(self, ref: Reference) -> Any:
        # Find resource by exact (type, name) match
        resource = self.state.get_resource_exact(ref.type, ref.name)
        
        if not resource:
            raise ValueError(f"Resource not found: {ref.type}.{ref.name}")
        
        # Navigate attribute path
        value = resource.attributes
        for key in ref.path:
            if key not in value:
                raise ValueError(f"Attribute not found: {'.'.join(ref.path)}")
            value = value[key]
        
        return value
```

## Tests Needed

- Reference with 3 parts: `resource.foo.bar`
- Reference with 4 parts: `resource.foo.bar.id`
- Reference with 5+ parts: `resource.foo.bar.attributes.documents`
- Nested attributes: `resource.foo.bar.meta.count`
- Non-existent resource
- Non-existent attribute
