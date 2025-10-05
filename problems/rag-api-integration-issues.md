# RAG API Integration Issues

## Discovery (October 5, 2025)

The AICL RAG framework architecture is **WORKING CORRECTLY**. The empty resource IDs were a red herring caused by API call failures returning error diagnostics instead of ResourceState objects.

## Actual Issues

### 1. OpenRouter Embeddings API Call Failing

**Error**: `Embeddings generation failed: Expecting value: line 1 column 1 (char 0)`

**Root Cause**: JSON parsing error when calling OpenRouter's embeddings endpoint

**Possible Reasons**:
- OpenRouter may not support embeddings API (only chat completions)
- Wrong model identifier for embeddings
- API response is not JSON (could be HTML error page)
- Missing or incorrect API endpoint

**Current Code** (`providers/openrouter/server.py:126-135`):
```python
response = requests.post(
    f"{self.base_url}/embeddings",  # May not exist!
    headers={
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": model,  # "openai/text-embedding-3-small"
        "input": text_list
    }
)
```

**Fix Options**:
1. Use OpenAI directly for embeddings (not through OpenRouter)
2. Use a different embedding provider (Cohere, Voyage AI)
3. Check OpenRouter docs to see if embeddings are supported

### 2. Pinecone Query API Call Failing

**Error**: `Query failed: 400 Bad Request for url: https://aicl-docs-nby1j17.svc.aped-4627-b74a.pinecone.io/query`

**Root Cause**: Pinecone rejecting the query request

**Possible Reasons**:
- Vector passed is empty (because embedding failed!)
- Vector dimensionality mismatch
- Invalid query payload format
- Namespace doesn't exist

**Current Code** (`providers/pinecone/server.py:160-165`):
```python
payload = {
    'vector': vector,  # Likely empty or wrong format
    'topK': top_k,
    'includeMetadata': include_metadata
}
if namespace:
    payload['namespace'] = namespace
```

**Dependency Chain**:
The query DEPENDS on the embedding working first:
1. Generate embedding for question → **FAILS**
2. Pass empty/invalid vector to Pinecone → **FAILS**

## Framework Validation

### ✅ What's Working
- Provider architecture and gRPC communication
- Resource dependency resolution
- State management
- HCL interpolation (when resources exist)
- Chat completion (proven by successful chat-answer resource)
- Resource ID generation with aiclResourceName

### ❌ What's Broken
- OpenRouter embeddings API integration
- Pinecone query (cascading failure from embedding)

## Solution Path

### Immediate Fix: Use OpenAI Directly for Embeddings

```python
# In providers/openrouter/server.py or create new openai provider
response = requests.post(
    "https://api.openai.com/v1/embeddings",  # Direct OpenAI
    headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",  # Need separate key
        "Content-Type": "application/json"
    },
    json={
        "model": "text-embedding-3-small",  # No "openai/" prefix
        "input": text_list
    }
)
```

### Alternative: Different Embedding Provider

Consider using:
- **Voyage AI** - Specialized for RAG
- **Cohere** - Has embed endpoint
- **Together AI** - Supports embeddings

## Test Commands

**Check OpenRouter API capabilities**:
```bash
curl https://openrouter.ai/api/v1/embeddings \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/text-embedding-3-small", "input": ["test"]}'
```

**Check what actually happened**:
```bash
python run.py rag_query.aicl 2>&1 | grep -E "(diagnostic|ERROR)"
```

## Files to Fix

1. `providers/openrouter/server.py` - Fix embeddings API call or remove embeddings support
2. `rag_query.aicl` - May need to use different provider for embeddings
3. Consider creating separate `providers/openai/server.py` for embeddings

## Success Criteria

1. Embedding generation completes without JSON parse error
2. Vector is properly formatted and passed to Pinecone
3. Query returns relevant chunks
4. Chat receives context and generates grounded answer