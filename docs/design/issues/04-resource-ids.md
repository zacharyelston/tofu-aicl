# Issue 04: Resource ID Generation Inconsistent

**Priority:** CRITICAL  
**Week:** 1

## Problem

Providers generate IDs differently:

```python
# file_loader
id=f"loader-{Path(path).name}"

# text_splitter  
id="text-splitter"  # Hardcoded!
```

**Issues:**
1. Collisions if multiple text_splitter resources
2. No standard format
3. State uses IDs as dict keys (collisions overwrite!)

## Example Failure

```hcl
resource "splitter_text" "small" {
  chunk_size = 500
}

resource "splitter_text" "large" {
  chunk_size = 1000
}
```

Both get ID `"text-splitter"` → second overwrites first in state!

## Solution

Standardize ID generation:

```python
class ResourceIDGenerator:
    @staticmethod
    def generate(provider: str, resource_type: str, resource_name: str) -> str:
        # Format: provider_type_name
        return f"{provider}_{resource_type}_{resource_name}"

# Examples:
# pinecone_index_embeddings
# file_loader_files_docs
# text_splitter_text_chunks
```

**Or use UUIDs:**

```python
import uuid

def generate_id(provider: str, resource_type: str, resource_name: str):
    # Deterministic UUID from components
    namespace = uuid.NAMESPACE_DNS
    name = f"{provider}.{resource_type}.{resource_name}"
    return str(uuid.uuid5(namespace, name))
```

## Provider Updates

All providers must use standard ID:

```python
# In ApplyResourceChange
config = dict(request.config)
resource_name = config['_resource_name']  # Passed by engine

resource_id = ResourceIDGenerator.generate(
    provider="text_splitter",
    resource_type=request.type_name,
    resource_name=resource_name
)

return ApplyResourceChangeResponse(
    new_state=ResourceState(
        id=resource_id,  # Standardized!
        ...
    )
)
```

## Tests Needed

- Unique IDs for same type
- Consistent format
- No collisions
- Deterministic (same inputs = same ID)
