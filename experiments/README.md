# AICL Experiment System

**Organized experiment management with document database storage**

## Directory Structure

```
experiments/
├── configs/        # AICL configuration files (.aicl)
├── variables/      # Variable files for experiments (.tfvars, .json)
├── outputs/        # Raw experiment outputs (JSON, logs)
├── states/         # Terraform state files (.tfstate)
├── results/        # Processed results and reports
└── README.md       # This file
```

## Document Database

All experiment outputs are stored in PostgreSQL as structured documents with:
- **Experiment ID** - Unique identifier for each run
- **Timestamp** - When the experiment was executed
- **Config** - The AICL configuration used
- **Outputs** - All generated outputs and results
- **Metadata** - Tags, provider info, costs, tokens

## Quick Start

### Run an Experiment
```bash
# 1. Create config in experiments/configs/
cat > experiments/configs/my-experiment.aicl << 'EOF'
experiment "my_test" {
  description = "Test experiment"
}

resource "azure_openai_chat" "test" {
  deployment = "gpt-35-turbo"
  prompt = "Hello, Azure!"
}
EOF

# 2. Run it
python run.py experiments/configs/my-experiment.aicl

# 3. Results are automatically saved to DocDB
python experiments/query_results.py --experiment-id my_test
```

### Compare Experiments
```bash
# Compare multiple runs
python experiments/compare.py --ids exp1,exp2,exp3

# Find best performing
python experiments/query_results.py --best --by cost
python experiments/query_results.py --best --by quality
```

## Storage Details

### PostgreSQL Schema

**Table: `experiment_outputs`**
```sql
CREATE TABLE experiment_outputs (
    id SERIAL PRIMARY KEY,
    experiment_id VARCHAR(255) NOT NULL,
    run_timestamp TIMESTAMP NOT NULL,
    config_file TEXT,
    config_content JSONB,
    outputs JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_experiment_id ON experiment_outputs(experiment_id);
CREATE INDEX idx_run_timestamp ON experiment_outputs(run_timestamp);
```

### Document Format

```json
{
  "experiment_id": "azure_security_2025_10_13",
  "run_timestamp": "2025-10-13T13:19:43Z",
  "config_file": "experiments/configs/azure_security.aicl",
  "config_content": {...},
  "outputs": {
    "step_1": {
      "description": "Generate code",
      "output": "...",
      "tokens": 453
    },
    "step_2": {...},
    "total_tokens": 1080
  },
  "metadata": {
    "provider": "azure_openai",
    "deployment": "gpt-35-turbo",
    "total_cost": 0.0006,
    "tags": ["security", "self-build"]
  }
}
```

## Query Examples

### Python API
```python
from experiments.storage import ExperimentDB

db = ExperimentDB()

# Get experiment by ID
result = db.get_by_id("azure_security_2025_10_13")

# Query by date range
results = db.query(
    start_date="2025-10-01",
    end_date="2025-10-31",
    provider="azure_openai"
)

# Compare performance
comparison = db.compare(
    experiment_ids=["exp1", "exp2", "exp3"],
    metrics=["cost", "tokens", "quality_score"]
)
```

### CLI
```bash
# List all experiments
experiments list

# Show specific experiment
experiments show azure_security_2025_10_13

# Compare experiments
experiments compare exp1 exp2 exp3 --metric cost

# Find best by criteria
experiments best --by cost --limit 5
experiments best --by quality --provider azure_openai
```

## File Organization

### Configuration Files (`configs/`)
- Store all `.aicl` experiment definitions
- Use descriptive names: `azure_security_analyzer.aicl`
- Version control recommended

### Variables (`variables/`)
- Store variable files for parameterized experiments
- Formats: `.tfvars`, `.json`, `.env`
- Example: `azure_credentials.tfvars`

### Outputs (`outputs/`)
- Raw experiment outputs before processing
- JSON format with full details
- Automatically generated

### States (`states/`)
- Terraform state files for resource tracking
- One `.tfstate` per experiment
- Used for cleanup and debugging

### Results (`results/`)
- Processed results and reports
- Charts, comparisons, summaries
- Human-readable formats (Markdown, HTML, PDF)

## Best Practices

1. **Use descriptive experiment IDs**
   ```bash
   # Good
   azure_security_v2_2025_10_13
   
   # Bad
   test1
   ```

2. **Tag your experiments**
   ```python
   metadata = {
       "tags": ["security", "azure", "self-build"],
       "version": "2.0",
       "author": "team_name"
   }
   ```

3. **Document configuration changes**
   - Update README when adding new experiment types
   - Comment complex AICL configurations

4. **Clean up old experiments**
   ```bash
   # Archive experiments older than 90 days
   experiments archive --older-than 90d
   ```

## Migration

Existing experiments can be migrated to the new system:

```bash
# Migrate Azure experiment
python experiments/migrate.py \
  --source azure_experiment_results.json \
  --experiment-id azure_security_2025_10_13
```

## Integration

### With V2 Storage Layer
The experiment DocDB uses the existing v2/storage layer:
- In-memory: Development/testing
- SQLite: Local persistence
- PostgreSQL: Production/team sharing

### With OpenTelemetry
All experiments automatically export traces and metrics to configured OTEL endpoint.

## Security

- Secrets are never stored in outputs
- Config files should use environment variables for credentials
- Database access requires authentication
- Query results can be scoped by user/team

## Support

For help:
- Check `experiments/examples/` for sample experiments
- Run `experiments --help` for CLI usage
- See AICL docs at `docs/EXPERIMENT_BUILDER_GUIDE.md`
