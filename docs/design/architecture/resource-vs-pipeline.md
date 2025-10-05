# Resource vs Pipeline: Clear Separation

## The Problem

Current code treats everything as a "resource" using Terraform-like Apply/Destroy:

```hcl
# This LOOKS like provisioning but is actually execution
resource "loader_files" "docs" {
  path = "./docs"
}

resource "splitter_text" "chunks" {
  documents = resource.loader_files.docs.attributes.documents
}
```

This creates confusion:
- Is this infrastructure or data processing?
- What does "destroy" mean for loaded files?
- Is it idempotent?

## The Solution

### Resources = Infrastructure (Persistent)

```hcl
resource "pinecone_index" "embeddings" {
  name = "my-index"
  dimension = 1536
}
```

**Semantics:**
- Creates infrastructure
- Idempotent (run twice = same result)
- Has persistent state
- Can be destroyed
- Uses `ApplyResourceChange` RPC

### Pipelines = Execution (Ephemeral)

```hcl
pipeline "process_docs" {
  step "load" {
    provider = file_loader
    path = "./docs"
  }
  
  step "split" {
    input = step.load.output
    chunk_size = 500
  }
}
```

**Semantics:**
- Processes data
- NOT idempotent (run twice = two executions)
- Results in lineage, not state
- No "destroy" concept
- Uses `Execute` RPC

## Decision Matrix

| Aspect | Resource | Pipeline |
|--------|----------|----------|
| Purpose | Infrastructure | Data processing |
| Lifecycle | Create/Update/Destroy | Run/Complete |
| Idempotent | Yes | No |
| State | Persistent | History only |
| Protocol | ApplyResourceChange | Execute |
| Example | Pinecone index | Load files |

## Refactoring Example

**Before (confused):**
```hcl
resource "loader_files" "docs" {
  path = "./docs"
}
```

**After (clear):**
```hcl
pipeline "ingest" {
  step "load" {
    provider = file_loader
    path = "./docs"
  }
}
```

The file_loader provider still exists, but it's used for execution, not provisioning.
