# Three Layer Architecture

## Separation of Concerns

tofu-aicl has three distinct layers with different semantics:

```
┌─────────────────────────────────┐
│  Layer 1: Infrastructure        │  Persistent resources
│  (Provisioning)                 │  Create → Update → Destroy
└─────────────────────────────────┘
           ↓ provides endpoints
┌─────────────────────────────────┐
│  Layer 2: Services              │  Provider containers
│  (Container Management)         │  Start → Configure → Stop
└─────────────────────────────────┘
           ↓ enables execution
┌─────────────────────────────────┐
│  Layer 3: Pipelines             │  Data workflows
│  (Execution)                    │  Run → Complete
└─────────────────────────────────┘
```

## Layer 1: Infrastructure

**Purpose:** Persistent resources that outlive individual executions

**Syntax:** `resource` blocks
```hcl
resource "pinecone_index" "embeddings" {
  name = "my-embeddings"
  dimension = 1536
  metric = "cosine"
}
```

**Protocol:** `ApplyResourceChange`, `DeleteResource`  
**State:** Tracked in infrastructure section  
**Properties:** Idempotent, persistent, stateful

## Layer 2: Services

**Purpose:** Provider containers that expose capabilities

**Syntax:** `provider` blocks
```hcl
provider "pinecone" {
  api_key = var.pinecone_key
  environment = "production"
}
```

**Protocol:** `Configure`, `HealthCheck`  
**State:** Runtime only (not persisted)  
**Properties:** Ephemeral containers, configurable

## Layer 3: Pipelines

**Purpose:** Data transformations and workflows

**Syntax:** `pipeline` blocks (NEW)
```hcl
pipeline "ingest_docs" {
  step "load" {
    provider = file_loader
    path = "./docs"
  }
  
  step "split" {
    provider = text_splitter
    input = step.load.output
  }
}
```

**Protocol:** `Execute`  
**State:** Execution history (lineage)  
**Properties:** NOT idempotent, data flow

## How They Interact

```hcl
# Infrastructure provides endpoints
resource "pinecone_index" "main" { ... }

# Services enable operations  
provider "pinecone" { ... }

# Pipelines use infrastructure via services
pipeline "process" {
  step "store" {
    provider = pinecone
    index = resource.pinecone_index.main.id  # Reference
  }
}
```
