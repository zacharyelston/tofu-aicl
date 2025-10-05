# State File Structure

## Complete DNA Format

```json
{
  "version": "1.0",
  "experiment_id": "rag_experiment_001",
  "created_at": "2025-10-05T10:00:00Z",
  "updated_at": "2025-10-05T10:05:43Z",
  
  "lineage": [
    {
      "timestamp": "2025-10-05T10:00:01Z",
      "sequence": 1,
      "action": "provision",
      "resource_type": "pinecone_index",
      "resource_name": "embeddings",
      "result": {
        "id": "embeddings-1a2b3c",
        "status": "ready",
        "dimension": 1536
      }
    },
    {
      "timestamp": "2025-10-05T10:00:05Z",
      "sequence": 2,
      "action": "execute",
      "pipeline": "ingest_docs",
      "step": "load_files",
      "result": {
        "documents": 23,
        "bytes": 145000
      }
    }
  ],
  
  "infrastructure": {
    "pinecone_index.embeddings": {
      "id": "embeddings-1a2b3c",
      "type": "pinecone_index",
      "provider": "pinecone",
      "attributes": {
        "dimension": 1536,
        "metric": "cosine"
      },
      "status": "ready"
    }
  },
  
  "outputs": {
    "total_vectors": 147,
    "pipeline_duration_ms": 6543,
    "index_url": "https://embeddings-1a2b3c.pinecone.io"
  },
  
  "metadata": {
    "config_file": "experiment_001.aicl",
    "git_commit": "abc123def",
    "runtime_version": "0.1.0"
  }
}
```

## Key Sections

### Lineage (append-only)
- Complete sequence of actions
- Timestamped
- Includes results
- Never modified, only appended

### Infrastructure (current)
- What exists right now
- Updated as resources change
- Used for destroy operations

### Outputs (results)
- Final results
- Computed values
- Summary metrics

### Metadata (tracking)
- Context information
- Versioning
- Debugging data
