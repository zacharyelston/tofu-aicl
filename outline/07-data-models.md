# Data Models and Schemas

## Model Catalog Schema

### models.yaml Structure

```yaml
chat_models:
  - id: string                    # Unique identifier (e.g., "gpt-4o")
    name: string                  # Display name
    provider: string              # Provider name (e.g., "openai")
    type: "chat"                  # Model type
    cost_per_1k_input: float      # Cost per 1K input tokens (USD)
    cost_per_1k_output: float     # Cost per 1K output tokens (USD)
    quality_score: float          # 1-10 rating
    context_window: int           # Max context tokens
    capabilities: string[]        # Features (e.g., ["streaming", "function_calling"])
    
embedding_models:
  - id: string
    name: string
    provider: string
    type: "embedding"
    cost_per_1k_tokens: float
    quality_score: float
    dimensions: int               # Embedding size
    max_input_tokens: int
    
judge_models:
  - id: string
    name: string
    provider: string
    type: "judge"
    cost_per_1k_input: float
    cost_per_1k_output: float
    reliability_score: float      # Judging accuracy (1-10)
    context_window: int
```

### Example Model Definitions

```yaml
chat_models:
  - id: gpt-4o
    name: GPT-4o
    provider: openai
    type: chat
    cost_per_1k_input: 0.0025
    cost_per_1k_output: 0.01
    quality_score: 9.5
    context_window: 128000
    capabilities: [streaming, function_calling, vision]
  
  - id: gpt-4o-mini
    name: GPT-4o Mini
    provider: openai
    type: chat
    cost_per_1k_input: 0.00015
    cost_per_1k_output: 0.0006
    quality_score: 8.5
    context_window: 128000
    capabilities: [streaming, function_calling]

embedding_models:
  - id: text-embedding-3-small
    name: Text Embedding 3 Small
    provider: openai
    type: embedding
    cost_per_1k_tokens: 0.00002
    quality_score: 7.0
    dimensions: 1536
    max_input_tokens: 8191
  
  - id: text-embedding-3-large
    name: Text Embedding 3 Large
    provider: openai
    type: embedding
    cost_per_1k_tokens: 0.00013
    quality_score: 9.0
    dimensions: 3072
    max_input_tokens: 8191
```

---

## State File Schema

### Format: JSON

```json
{
  "version": 1,
  "timestamp": "ISO-8601",
  "config_hash": "sha256",
  "resources": [
    {
      "id": "string",
      "type": "string",
      "provider": "string",
      "name": "string",
      "attributes": {},
      "dependencies": [],
      "metadata": {}
    }
  ],
  "outputs": {},
  "metadata": {}
}
```

### Example State File

```json
{
  "version": 1,
  "timestamp": "2025-10-11T12:00:00Z",
  "config_hash": "a1b2c3d4",
  "resources": [
    {
      "id": "resource.llm_completion.answer",
      "type": "llm_completion",
      "provider": "openai",
      "name": "answer",
      "attributes": {
        "model": "gpt-4o-mini",
        "prompt": "What is AI?",
        "content": "Artificial Intelligence is...",
        "usage.total_tokens": 150,
        "cost": 0.0015
      },
      "dependencies": ["provider.openai"],
      "metadata": {
        "created_at": "2025-10-11T12:00:00Z",
        "updated_at": "2025-10-11T12:00:00Z",
        "execution_time_ms": 2100
      }
    }
  ],
  "outputs": {
    "answer_text": "Artificial Intelligence is...",
    "total_cost": 0.0015
  },
  "metadata": {
    "engine_version": "1.0.0",
    "execution_id": "exec-123"
  }
}
```

---

## Experiment Database Schema

### SQLite/PostgreSQL Tables

#### Table: experiments

```sql
CREATE TABLE experiments (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  config_template TEXT,              -- Base AICL template
  variables_config TEXT,              -- YAML variables definition
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status TEXT CHECK(status IN ('pending', 'running', 'completed', 'failed'))
);
```

#### Table: configurations

```sql
CREATE TABLE configurations (
  id TEXT PRIMARY KEY,
  experiment_id TEXT REFERENCES experiments(id),
  config_text TEXT NOT NULL,         -- Full AICL config
  variables JSON,                     -- Variable values used
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_config_experiment ON configurations(experiment_id);
```

#### Table: results

```sql
CREATE TABLE results (
  id TEXT PRIMARY KEY,
  experiment_id TEXT REFERENCES experiments(id),
  configuration_id TEXT REFERENCES configurations(id),
  
  -- Execution metadata
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  duration_ms INTEGER,
  status TEXT CHECK(status IN ('success', 'failed', 'timeout')),
  error_message TEXT,
  
  -- Resource usage
  total_tokens INTEGER,
  prompt_tokens INTEGER,
  completion_tokens INTEGER,
  estimated_cost REAL,
  
  -- Output
  output_text TEXT,
  output_json JSON,
  
  -- Context
  context_retrieved TEXT,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_results_experiment ON results(experiment_id);
CREATE INDEX idx_results_config ON results(configuration_id);
```

#### Table: quality_scores

```sql
CREATE TABLE quality_scores (
  id TEXT PRIMARY KEY,
  result_id TEXT REFERENCES results(id),
  
  -- Grading metadata
  judge_model TEXT NOT NULL,
  grading_prompt TEXT,
  graded_at TIMESTAMP,
  
  -- Scores
  overall_score REAL,              -- 0-10
  relevance_score REAL,
  accuracy_score REAL,
  completeness_score REAL,
  
  -- Judge output
  judge_reasoning TEXT,
  judge_raw_output TEXT,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quality_result ON quality_scores(result_id);
```

---

## Test Variables Schema

### test-variables.yaml Structure

```yaml
# Chat models to test
chat_models:
  models:
    - name: string                # Model catalog ID
      # Additional model-specific overrides (optional)
  
  # Model parameters
  temperature:
    min: float
    max: float
    step: float
  
  max_tokens:
    values: [int, int, ...]
  
  top_p:
    values: [float, float, ...]

# Embedding models to test
embedding_models:
  models:
    - name: string                # Model catalog ID
      dimensions: int             # Auto-populated from catalog

# RAG-specific variables
rag:
  retrieval:
    top_k:
      values: [int, int, ...]
    rerank: [bool, bool]
  
  chunking:
    chunk_size:
      values: [int, int, ...]
    overlap:
      values: [int, int, ...]

# Prompts/templates
prompts:
  - string
  - string

# Custom variables
custom:
  key: value
```

### Example Test Variables

```yaml
chat_models:
  models:
    - name: "gpt-4o-2024-08-06"
    - name: "gpt-4o-mini"
    - name: "openrouter-claude-sonnet"
  
  temperature:
    min: 0.0
    max: 1.0
    step: 0.5
  
  max_tokens:
    values: [100, 500, 1000]

embedding_models:
  models:
    - name: "text-embedding-3-small"
    - name: "text-embedding-3-large"

rag:
  retrieval:
    top_k:
      values: [3, 5, 10]
    rerank: [false, true]
  
  chunking:
    chunk_size:
      values: [500, 1000, 1500]
    overlap:
      values: [50, 100]

prompts:
  - "What is machine learning?"
  - "Explain neural networks simply."
```

---

## Provider Config Schema

### config.yaml Structure

```yaml
provider:
  # Identity
  name: string                    # Unique ID (lowercase, underscores)
  display_name: string            # Human-readable
  version: string                 # Semantic version
  source: string                  # Registry path
  description: string
  
  # Runtime
  runtime:
    entrypoint: string            # Executable file
    default_port: int             # gRPC port (50001-60000)
    mode: enum                    # subprocess | docker | both
    args: [string]                # CLI arguments (optional)
    env: {string: string}         # Environment vars (optional)
  
  # Environment
  environment:
    required_vars: [string]       # Must be set
    optional_vars: [string]       # Optional
  
  # Capabilities
  capabilities:
    types: [string]               # Resource types
    operations: [string]          # Supported operations
  
  # Models (references to catalog)
  model_ids: [string]             # Catalog IDs
```

### Validation Rules

```yaml
# Schema using JSON Schema format
{
  "type": "object",
  "required": ["provider"],
  "properties": {
    "provider": {
      "type": "object",
      "required": ["name", "display_name", "version", "runtime", "capabilities"],
      "properties": {
        "name": {
          "type": "string",
          "pattern": "^[a-z][a-z0-9_]*$"
        },
        "runtime": {
          "properties": {
            "default_port": {
              "type": "integer",
              "minimum": 50001,
              "maximum": 60000
            },
            "mode": {
              "enum": ["subprocess", "docker", "both"]
            }
          }
        }
      }
    }
  }
}
```

---

## Metrics Schema

### Collected Metrics

```json
{
  "execution_id": "string",
  "timestamp": "ISO-8601",
  "resource_id": "string",
  "resource_type": "string",
  
  "performance": {
    "duration_ms": int,
    "queue_time_ms": int,
    "execution_time_ms": int
  },
  
  "usage": {
    "input_tokens": int,
    "output_tokens": int,
    "total_tokens": int
  },
  
  "cost": {
    "input_cost_usd": float,
    "output_cost_usd": float,
    "total_cost_usd": float
  },
  
  "quality": {
    "score": float,              // 0-10
    "judge_model": "string",
    "dimensions": {
      "relevance": float,
      "accuracy": float,
      "completeness": float
    }
  }
}
```

---

## OpenTelemetry Traces

### Span Attributes

```json
{
  "service.name": "aicl-engine",
  "aicl.resource.id": "resource.llm_completion.answer",
  "aicl.resource.type": "llm_completion",
  "aicl.provider": "openai",
  "aicl.model": "gpt-4o-mini",
  "aicl.execution_id": "exec-123",
  
  "llm.usage.input_tokens": 50,
  "llm.usage.output_tokens": 100,
  "llm.usage.total_tokens": 150,
  "llm.cost.total_usd": 0.0015,
  
  "http.status_code": 200,
  "error": false
}
```
