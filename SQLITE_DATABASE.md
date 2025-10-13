# SQLite Experiment Database

## Overview
The AICL framework now includes a lightweight SQLite database for persistent experiment tracking. No server setup required—just run your experiments and query the results!

## Why SQLite?
- ✅ **Lightweight** - File-based, no server needed
- ✅ **Built-in** - No extra dependencies (part of Python)
- ✅ **SQL Queries** - Powerful analysis with standard SQL
- ✅ **Easy Backup** - Just copy the .db file
- ✅ **Perfect for Local** - Ideal for single-user experiment tracking

## Database Schema

### 📋 `experiments` table
Stores experiment metadata:
```sql
- id (auto-increment primary key)
- experiment_id (unique identifier, e.g., "smoke_test_1")
- timestamp (when experiment ran)
- config_file (path to .aicl file)
- description (experiment description)
- status (pending/running/completed/failed)
```

### ⚙️ `configurations` table
Stores experiment parameters:
```sql
- experiment_id (foreign key)
- chat_model (e.g., "gpt-4o-2024-08-06")
- embedding_model (e.g., "text-embedding-3-large")
- temperature (0.0-2.0)
- max_tokens (token limit)
- top_k (retrieval count)
- provider (naga/openai/openrouter)
- rerank (boolean)
- other_params (JSON blob for additional params)
```

### 📊 `results` table
Stores performance metrics:
```sql
- experiment_id (foreign key)
- total_cost_usd, embedding_cost_usd, chat_cost_usd
- total_tokens, prompt_tokens, completion_tokens
- latency_ms (chat latency)
- end_to_end_ms (total time)
- chunks_retrieved (vector DB hits)
- success (boolean)
- error_message (if failed)
```

### 🏆 `quality_scores` table
Stores LLM-as-Judge evaluation:
```sql
- experiment_id (foreign key)
- judge_model (e.g., "mistralai/mistral-large")
- judge_score (overall 0-10 score)
- accuracy_score (0-10)
- completeness_score (0-10)
- clarity_score (0-10)
- relevance_score (0-10)
- judge_feedback (text explanation)
```

## Performance Optimizations
- **Indexes** on `experiment_id` in all child tables for fast joins
- **Indexes** on common query fields (timestamp, cost, quality)
- **Upsert behavior** ensures one row per experiment (no duplicates)
- **Atomic transactions** with proper rollback on errors

## CLI Commands

### Show Statistics
```bash
python -m src.aicl.experiment_db stats
```
Output:
```
📊 Experiment Database Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Experiments: 27
  
  Quality Scores:
    Average: 7.85/10
    Best:    9.20/10
    Worst:   5.50/10
  
  Costs:
    Total Spent:  $0.0347
    Average/Exp:  $0.0013
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### List All Experiments
```bash
python -m src.aicl.experiment_db list
```

### Find Best Configurations
```bash
python -m src.aicl.experiment_db best
```
Shows experiments with quality ≥7 and cost ≤$0.01, sorted by quality then cost.

### Compare Model Performance
```bash
python -m src.aicl.experiment_db models
```
Shows average quality, cost, and latency grouped by model.

### Export to JSON
```bash
python -m src.aicl.experiment_db export backup.json
```

## Python API

### Basic Usage
```python
from src.aicl.experiment_db import ExperimentDB

# Initialize database
db = ExperimentDB()  # Creates experiments/results.db

# Save experiment
db.save_experiment(
    experiment_id="test_1",
    config={
        'chat_model': 'gpt-4o-2024-08-06',
        'embedding_model': 'text-embedding-3-large',
        'temperature': 0.7,
        'top_k': 5
    },
    results={
        'total_cost_usd': 0.00125,
        'total_tokens': 500,
        'latency_ms': 1250
    },
    quality={
        'judge_model': 'mistralai/mistral-large',
        'judge_score': 8.5,
        'judge_feedback': 'Excellent answer'
    }
)

# Retrieve experiment
exp = db.get_experiment("test_1")
print(f"Score: {exp['judge_score']}/10, Cost: ${exp['total_cost_usd']}")
```

### Query Best Configs
```python
# Find configs meeting quality and cost thresholds
best = db.get_best_configs(min_quality=7.0, max_cost=0.01, limit=10)

for config in best:
    print(f"{config['experiment_id']}: {config['judge_score']}/10 @ ${config['total_cost_usd']}")
```

### Cost Analysis
```python
stats = db.get_cost_analysis()
print(f"Total spent: ${stats['total_spent']:.4f}")
print(f"Average cost: ${stats['avg_cost']:.4f}")
```

### Model Performance Comparison
```python
models = db.get_model_performance()

for m in models:
    print(f"{m['chat_model']}: {m['avg_quality']:.1f}/10 @ ${m['avg_cost']:.4f}")
```

## Advanced SQL Queries

### Compare Embedding Models
```sql
SELECT 
    embedding_model,
    AVG(judge_score) as avg_quality,
    AVG(total_cost_usd) as avg_cost,
    COUNT(*) as experiments
FROM configurations c
JOIN quality_scores q ON c.experiment_id = q.experiment_id
JOIN results r ON c.experiment_id = r.experiment_id
GROUP BY embedding_model
ORDER BY avg_quality DESC;
```

### Find Best Temperature Settings
```sql
SELECT 
    temperature,
    AVG(judge_score) as avg_quality,
    COUNT(*) as experiments
FROM configurations c
JOIN quality_scores q ON c.experiment_id = q.experiment_id
GROUP BY temperature
ORDER BY avg_quality DESC;
```

### Cost by Provider
```sql
SELECT 
    provider,
    SUM(total_cost_usd) as total_cost,
    AVG(total_cost_usd) as avg_cost,
    COUNT(*) as experiments
FROM configurations c
JOIN results r ON c.experiment_id = r.experiment_id
GROUP BY provider
ORDER BY total_cost DESC;
```

### Quality Trends Over Time
```sql
SELECT 
    DATE(timestamp) as date,
    AVG(judge_score) as avg_quality,
    COUNT(*) as experiments
FROM experiments e
JOIN quality_scores q ON e.experiment_id = q.experiment_id
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

## Integration with Experiment Runner

The database automatically saves results when you run experiments:

```bash
# Run experiments with grading (auto-saves to DB)
python run_rag_graded_matrix.py experiments/suites/smoke_test/*.aicl

# Query results
python -m src.aicl.experiment_db best
```

## Database Location
Default: `experiments/results.db`

Custom location:
```python
db = ExperimentDB(db_path="custom/path/experiments.db")
```

## Backup & Migration

### Backup Database
```bash
# Copy SQLite file
cp experiments/results.db backups/results_$(date +%Y%m%d).db

# Or export to JSON
python -m src.aicl.experiment_db export backups/export_$(date +%Y%m%d).json
```

### Migrate to New Database
```bash
# SQLite dump and restore
sqlite3 experiments/results.db .dump > backup.sql
sqlite3 new_database.db < backup.sql
```

## Benefits

### 🎯 Track Progress
- Historical record of all experiments
- Compare current vs past performance
- Identify improving/degrading trends

### 💰 Optimize Costs
- Find cheapest configs meeting quality bar
- Track total spending across experiments
- Identify cost outliers

### 🏆 Quality Assurance
- Track quality scores over time
- Compare judge models
- Ensure consistent quality

### 🔬 Scientific Method
- Reproducible experiments
- Statistical analysis
- A/B test validation

## Troubleshooting

### Database locked error
If you get "database is locked" errors:
```python
# Increase timeout
conn = sqlite3.connect(db_path, timeout=30.0)
```

### Reset database
```bash
# Delete and recreate
rm experiments/results.db
python -m src.aicl.experiment_db stats  # Recreates schema
```

### View schema
```bash
sqlite3 experiments/results.db .schema
```

## Future Enhancements

Potential additions:
- Time-series visualization (quality/cost trends)
- Statistical significance testing (A/B comparison)
- Automated regression detection
- Cost forecasting
- Multi-database aggregation (compare across projects)
