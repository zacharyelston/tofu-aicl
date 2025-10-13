# AICL CLI Usage Guide

## Output Destination Controls

The AICL engine now supports flexible output configuration via command-line switches:

### Basic Usage

```bash
# Default behavior (JSON state file + stdout)
python run.py experiments/rag-demo/rag-demo-live.aicl

# Save to PostgreSQL DocDB
python run.py experiments/rag-demo/rag-demo-live.aicl --output-docdb

# Save to DocDB with custom experiment ID and tags
python run.py experiments/rag-demo/rag-demo-live.aicl \
  --output-docdb \
  --experiment-id rag-v2 \
  --tags rag,demo,production

# Quiet mode (minimal output)
python run.py experiments/rag-demo/rag-demo-live.aicl --quiet

# Disable stdout output
python run.py experiments/rag-demo/rag-demo-live.aicl --no-stdout
```

## Available Flags

### Output Destinations

| Flag | Default | Description |
|------|---------|-------------|
| `--output-file` | enabled | Save state to `.tfstate` JSON files |
| `--output-docdb` | disabled | Save results to PostgreSQL DocDB |
| `--output-stdout` | enabled | Print results to stdout |
| `--no-stdout` | - | Disable stdout output |

### Experiment Configuration

| Flag | Description |
|------|-------------|
| `--experiment-id ID` | Custom experiment identifier |
| `--tags TAGS` | Comma-separated tags (e.g., `rag,demo,v1`) |
| `--quiet` / `-q` | Minimal console output (errors only) |

### Experimental Features

| Flag | Status | Description |
|------|--------|-------------|
| `--parallel` | 🚧 Planned | Enable parallel execution for independent resources |

## Output Destinations Explained

### 1. **JSON State Files** (default)
Location: `./terraform.tfstate.d/{experiment_id}.tfstate`

```json
{
  "version": "1.0",
  "experiment_id": "default-exp",
  "resources": {...},
  "outputs": {...},
  "metadata": {
    "created_at": "2025-10-13T15:00:00",
    "last_modified": "2025-10-13T15:05:00"
  }
}
```

### 2. **PostgreSQL DocDB** (--output-docdb)
Structured storage in `experiment_outputs` table with JSONB columns for:
- Full experiment outputs
- Resource states and attributes
- Configuration snapshot
- Metadata and tags

**Query saved experiments:**
```bash
# List all experiments
python experiments/query_results.py --list

# Get specific experiment
python experiments/query_results.py --experiment-id rag-v2

# Compare multiple runs
python experiments/query_results.py --compare exp1,exp2,exp3
```

### 3. **Stdout** (default)
Real-time console output showing:
- Resource provisioning progress
- Execution traces (OpenTelemetry)
- Final experiment outputs (formatted)

## Examples

### Production RAG Experiment with Full Tracking

```bash
python run.py experiments/rag-demo/rag-demo-live.aicl \
  --output-file \
  --output-docdb \
  --experiment-id rag-prod-20251013 \
  --tags rag,production,pinecone,gpt4
```

This saves:
- ✅ State file for version control
- ✅ DocDB entry for querying/comparison
- ✅ Console output for monitoring

### Silent Background Execution

```bash
python run.py experiments/rag-demo/rag-demo-live.aicl \
  --quiet \
  --no-stdout \
  --output-docdb \
  --experiment-id background-exp > /dev/null 2>&1
```

### Development Mode (Fast Iteration)

```bash
# Skip file/DB saving, just show results
python run.py experiments/rag-demo/rag-demo-live.aicl \
  --output-stdout
```

## Parallel Execution (Coming Soon)

### Current: Sequential Execution
```
Resources execute one-by-one in topological order:
  knowledge_base → validation_query → main_question → ...
```

### Planned: Parallel Execution
```bash
python run.py experiment.aicl --parallel
```

**How it will work:**
- Group resources by **dependency level**
- Execute **same-level resources in parallel**
- Maintain **sequential execution between levels**

**Example Parallelization:**
```
Level 0:  knowledge_base (sequential - no deps)
Level 1:  validation_query, main_question (PARALLEL - no interdependency)
Level 2:  doc_chunks (sequential - depends on knowledge_base)
Level 3:  doc_vectors (sequential - depends on doc_chunks)
Level 4:  vector_index (sequential - depends on doc_vectors)
Level 5:  validation_results, rag_context (PARALLEL)
Level 6:  answer_gpt4o_mini, answer_claude, answer_gemini (PARALLEL)
Level 7:  judge_evaluation (sequential - depends on all answers)
```

**Safety Mechanisms:**
- Thread-safe state management with locks
- Per-resource error isolation
- Rollback on any failure

## Environment Variables

```bash
# Required for DocDB output
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"

# Optional: Control subprocess mode
export AICL_SUBPROCESS_MODE="true"  # default

# Optional: OpenTelemetry
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
```

## Help

```bash
python run.py --help
```
