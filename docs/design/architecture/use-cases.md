# Common Use Cases

## Case 1: Pure Provisioning → Use

Provision infrastructure, then execute against it.

```hcl
# Phase 1: Provision (persistent)
resource "pinecone_index" "embeddings" {
  name = "my-index"
  dimension = 1536
}

# Phase 2: Execute (ephemeral)
pipeline "ingest" {
  step "upsert" {
    provider = pinecone
    index = resource.pinecone_index.embeddings.id
    vectors = step.embed.output
  }
}
```

**State:**
- Infrastructure persists
- Execution logged in lineage

## Case 2: Ephemeral Everything

Spin up, execute, tear down.

```hcl
provider "file_loader" { }
provider "text_splitter" { }

pipeline "one_off" {
  step "load" { provider = file_loader, path = "./data" }
  step "split" { provider = text_splitter, input = step.load.output }
}
```

**State:**
- No persistent infrastructure
- Only execution history

## Case 3: Multi-Experiment

Shared infrastructure, multiple experiments.

```hcl
# Provision once
resource "pinecone_index" "experiments" { ... }

# Run multiple times
pipeline "exp_a" {
  params { chunk_size = 500 }
  step "process" { ... }
}

pipeline "exp_b" {
  params { chunk_size = 1000 }
  step "process" { ... }
}
```

**State:**
- Infrastructure persists
- Multiple lineage entries (one per execution)

## Case 4: Agent Awaiting Resources

```hcl
resource "vector_db" "ready" { ... }

pipeline "agent_workflow" {
  step "wait" {
    provider = vector_db
    action = "wait_until_ready"
    target = resource.vector_db.ready.id
  }
  
  step "use" {
    # Agent uses ready resource
  }
}
```

**State:**
- Infrastructure shows "ready" status
- Pipeline waits for it

## Case 5: Long-Running Service

```hcl
resource "llm_server" "inference" {
  model = "claude-3.5-sonnet"
  container = "llm-server:1.0"
}

# Service stays up, multiple executions
pipeline "query_1" {
  step "ask" {
    provider = llm
    server = resource.llm_server.inference.endpoint
  }
}

pipeline "query_2" { ... }
```

**State:**
- Server infrastructure persists
- Each query logged separately
