# Provider Protocol: Apply vs Execute

## Current Problem

The gRPC protocol supports BOTH provisioning and execution, but current code only uses `ApplyResourceChange` for everything.

```protobuf
service Provider {
  rpc ApplyResourceChange(...) returns (...);  // Used for everything
  rpc Execute(...) returns (stream ...);        // Defined but unused!
}
```

## Correct Usage

### ApplyResourceChange = Infrastructure

Used when creating/updating persistent resources:

```python
# In pinecone provider
def ApplyResourceChange(self, request, context):
    # Create Pinecone index
    index = pinecone.create_index(
        name=config['name'],
        dimension=config['dimension']
    )
    
    return ApplyResourceChangeResponse(
        new_state=ResourceState(
            id=index.id,
            status="ready",
            attributes={"dimension": 1536}
        )
    )
```

**Properties:**
- Returns `ResourceState` (persistent)
- Idempotent
- Tracked in state.infrastructure

### Execute = Data Processing

Used when processing data through a pipeline:

```python
# In file_loader provider
def Execute(self, request, context):
    path = request.input['path']
    
    for file in load_files(path):
        yield ExecuteResponse(
            data={
                'path': str(file.path),
                'content': file.content
            }
        )
```

**Properties:**
- Streams results
- NOT idempotent
- Tracked in state.lineage

## Provider Implementation

Providers can support BOTH:

```python
class PineconeProvider:
    def ApplyResourceChange(self, request, context):
        # Create index (infrastructure)
        ...
    
    def Execute(self, request, context):
        # Upsert vectors (data operation)
        ...
```

Same provider, different RPC for different purposes.

## Decision Guide

Use **ApplyResourceChange** when:
- Creating infrastructure (indices, configs)
- Resource will persist
- Want idempotency
- Need state tracking

Use **Execute** when:
- Processing data
- Transformation/workflow step
- Streaming results
- Execution is the goal

## Migration Example

**Before:**
```python
# file_loader incorrectly uses Apply
def ApplyResourceChange(self, request, context):
    documents = load_files(path)
    return ApplyResourceChangeResponse(
        new_state=ResourceState(
            attributes={'documents': documents}
        )
    )
```

**After:**
```python
# file_loader correctly uses Execute
def Execute(self, request, context):
    path = request.input['path']
    for doc in load_files(path):
        yield ExecuteResponse(data=doc)
```
