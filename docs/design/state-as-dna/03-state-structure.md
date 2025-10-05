# State File Structure

## Complete State File Format

```json
{
  "version": "1.0",
  "experiment_id": "rag_experiment_001",
  "created_at": "2025-10-05T10:00:00Z",
  "updated_at": "2025-10-05T10:00:15Z",
  
  "metadata": {
    "user": "researcher@example.com",
    "host": "macbook-pro.local",
    "tofu_version": "0.1.0",
    "config_file": "experiments/rag_001.aicl",
    "git_commit": "a1b2c3d4"
  },
  
  "lineage": [
    {
      "timestamp": "2025-10-05T10:00:01Z",
      "action": "provision",
      "resource_type": "pinecone_index",
      "resource_name": "embeddings",
      "provider": "pinecone",
      "input": {
        "name": "my-embeddings",
        "dimension": 1536,
        "metric": "cosine"
      },
      "result": {
        "id": "embeddings-1a2b3c",
        "status": "ready",
        "host": "us-west-2.pinecone.io"
      },
      "duration_ms": 2340
    },
    {
      "timestamp": "2025-10-05T10:00:05Z",
      "action": "execute",
      "pipeline": "ingest_docs",
      "step": "load_files",
      "provider": "file_loader",
      "input": {
        "path": "./data/documents"
      },
      "result": {
        "documents": 23,
        "total_bytes": 145000,
        "file_types": ["md", "txt", "pdf"]
      },
      "duration_ms": 1250
    },
    {
      "timestamp": "2025-10-05T10:00:07Z",
      "action": "execute",
      "pipeline": "ingest_docs",
      "step": "split_text",
      "provider": "text_splitter",
      "input": {
        "chunk_size": 500,
        "chunk_overlap": 50
      },
      "result": {
        "chunks": 147,
        "avg_chunk_size": 487
      },
      "duration_ms": 890
    },
    {
      "timestamp": "2025-10-05T10:00:12Z",
      "action": "execute",
      "pipeline": "ingest_docs",
      "step": "generate_embeddings",
      "provider": "openrouter",
      "input": {
        "model": "text-embedding-3-small",
        "chunks": 147
      },
      "result": {
        "embeddings": 147,
        "total_tokens": 15234
      },
      "duration_ms": 4123,
      "cost_usd": 0.00305
    },
    {
      "timestamp": "2025-10-05T10:00:15Z",
      "action": "execute",
      "pipeline": "ingest_docs",
      "step": "upsert_vectors",
      "provider": "pinecone",
      "input": {
        "index_id": "embeddings-1a2b3c",
        "vectors": 147
      },
      "result": {
        "upserted": 147
      },
      "duration_ms": 876
    }
  ],
  
  "current_state": {
    "infrastructure": {
      "pinecone_index.embeddings": {
        "id": "embeddings-1a2b3c",
        "provider": "pinecone",
        "attributes": {
          "name": "my-embeddings",
          "dimension": 1536,
          "metric": "cosine",
          "host": "us-west-2.pinecone.io",
          "vector_count": 147,
          "status": "ready"
        },
        "dependencies": []
      }
    },
    
    "outputs": {
      "total_documents": 23,
      "total_chunks": 147,
      "total_vectors": 147,
      "total_tokens": 15234,
      "total_cost_usd": 0.00305,
      "pipeline_duration_ms": 7139
    }
  },
  
  "diagnostics": [
    {
      "severity": "info",
      "message": "Processing 23 documents",
      "timestamp": "2025-10-05T10:00:05Z"
    },
    {
      "severity": "warning",
      "message": "3 chunks exceeded max size, truncated",
      "timestamp": "2025-10-05T10:00:07Z"
    }
  ]
}
```

## Key Sections

### 1. Metadata
Captures context of the run:
- Who ran it
- Where it ran
- What version of tofu
- Git commit for reproducibility

### 2. Lineage
Append-only log of **every action**:
- Timestamps for timeline
- Full input/output for each step
- Duration for performance analysis
- Costs for budget tracking
- Errors and warnings

### 3. Current State
Point-in-time snapshot:
- **Infrastructure**: Persistent resources
- **Outputs**: Computed values available for reference
- Clean separation from lineage

### 4. Diagnostics
All warnings, errors, info messages
- Searchable debug information
- Helps troubleshooting

## State Properties

### Append-Only Lineage
```python
# New entries are ADDED, never modified
state.lineage.append({
    "timestamp": now(),
    "action": "execute",
    "result": {...}
})
```

### Current State Updates
```python
# Infrastructure state gets UPDATED
state.current_state.infrastructure[resource_id] = new_attributes
```

## File Organization

```
terraform.tfstate.d/
├── experiment_001_baseline.tfstate
├── experiment_002_large_chunks.tfstate
├── experiment_003_small_chunks.tfstate
└── shared_infrastructure.tfstate
```

Each experiment gets its own state file, tracked in git.

## Comparison Example

```bash
$ git diff experiment_001.tfstate experiment_002.tfstate

# Shows:
- Lineage differences (what changed between runs)
- Parameter changes (chunk_size: 500 -> 1000)
- Result differences (chunks: 147 -> 87)
- Performance differences (duration_ms)
```

## Next Steps

See `04-lifecycle.md` for how state evolves through execution phases.
