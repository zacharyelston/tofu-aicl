# RAG Query Context Passing Issue

## Problem Statement

The RAG (Retrieval-Augmented Generation) query pipeline is functional end-to-end, but retrieved context is not being passed to the chat completion step, resulting in answers without grounded information.

## Current Behavior

1. **Indexing Pipeline** (`rag_index.aicl`) - ✅ WORKS
   - Loads source code → splits into chunks → generates embeddings → stores in Pinecone
   - All resources create successfully with proper IDs

2. **Query Pipeline** (`rag_query.aicl`) - ⚠️ PARTIAL FAILURE
   - Generates question embedding ✅
   - Queries Pinecone for relevant chunks ✅
   - Passes results to chat ❌ (context is empty)

## Root Cause

Resources created by certain providers (embedding, query) are being stored in state with **empty IDs and types**, preventing the HCL evaluator from building proper context for interpolation resolution.

**Evidence from state file:**
```json
"": {
  "id": "",
  "type": "",
  "provider": "pinecone",
  "attributes": {},
  ...
}
```

**Expected interpolation:**
```hcl
content = "Context: ${resource.query.relevant_chunks.attributes.results}\n\nQuestion: ..."
```

**Actual resolution:** `${resource.query.relevant_chunks.attributes.results}` → `None` (resource not found in context)

## Technical Details

### Evaluator Context Building (`src/aicl/evaluator.py:14-29`)
```python
for resource_id, resource_state in self.state_manager.current_state.resources.items():
    res_type = resource_state.type
    res_name = resource_id.split('-', 1)[1] if '-' in resource_id else resource_id

    if res_type not in context['resource']:
        context['resource'][res_type] = {}

    context['resource'][res_type][res_name] = {
        'attributes': resource_state.attributes,
        ...
    }
```

**Problem:** When `resource_id = ""` and `res_type = ""`, the context structure becomes invalid.

### Attempted Fixes

1. ✅ Added `aiclResourceName` field to executor config
2. ✅ Updated providers to use resource name for ID generation
3. ❌ Providers still return empty IDs for embedding/query resources

### Provider ID Generation Pattern

**OpenRouter** (`providers/openrouter/server.py:65-73`):
```python
resource_name = config.get('aiclResourceName', '')
if request.prior_state and request.prior_state.id:
    resource_id = request.prior_state.id
elif resource_name:
    resource_id = f"{request.type_name}-{resource_name}"
else:
    resource_id = f"or-{uuid.uuid4().hex[:8]}"
```

**Pinecone** (`providers/pinecone/server.py:34,205`):
```python
resource_name = config.get('aiclResourceName', '')
# ...in _query_vectors:
resource_id = f"{type_name}-{resource_name}" if resource_name else f"query-{namespace or 'default'}"
```

## Hypothesis

The `aiclResourceName` field may not be reaching the providers due to:
1. Protobuf field name transformation (camelCase → snake_case)
2. Struct serialization filtering out unknown fields
3. MessageToDict not preserving all fields

## Success Criteria

1. Query resource stored in state with proper ID: `query-relevant_chunks`
2. Embedding resource stored with proper ID: `embedding-question_vector`
3. Context interpolation resolves to actual retrieved chunks
4. Chat response contains grounded information from retrieved context

## Files to Review

- `src/aicl/executor.py` - Adds aiclResourceName to config
- `providers/openrouter/server.py` - Embedding and chat providers
- `providers/pinecone/server.py` - Query provider
- `src/aicl/evaluator.py` - Context building and interpolation
- `rag_query.aicl` - Query pipeline configuration

## Test Command

```bash
python run.py rag_query.aicl
```

**Check state:**
```bash
python3 -c "
import json
with open('terraform.tfstate.d/default-exp.tfstate', 'r') as f:
    state = json.load(f)
    for rid, res in state['resources'].items():
        if res.get('type') in ['query', 'embedding']:
            print(f'{rid} | {res.get(\"type\")} | {list(res.get(\"attributes\", {}).keys())}')
"
```

## Expected Output

After fix, the chat response should contain actual information from the AICL codebase instead of "I cannot provide information..."