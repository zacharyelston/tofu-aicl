# Matrix Experiment Results

This directory contains state files and results from matrix experiments.

## Files

- `*.tfstate` - Terraform state files for each experiment
- `*.aicl` - AICL configuration files used for each experiment
- `matrix_summary.json` - Summary of all experiments with metadata (when generated)

## Usage

### Run Experiments

Use the main CLI to run experiments:

```bash
# Run single experiment
python run.py experiments/rag-demo/rag-demo-live.aicl

# With output options
python run.py experiments/rag-demo/rag-demo-live.aicl \
  --output-docdb \
  --experiment-id matrix-test-001 \
  --tags matrix,comparison
```

### View Results

Results are saved in:
- **JSON state files**: `terraform.tfstate.d/{experiment_id}.tfstate`
- **PostgreSQL DocDB**: Query with experiment_id (if `--output-docdb` used)
- **Stdout**: Formatted console output (if `--output-stdout`)

## State Files

Each experiment produces:
- Configuration file: `{experiment_id}.aicl`
- State file: `terraform.tfstate.d/{experiment_id}.tfstate`

State files contain complete resource information and can be used for detailed analysis.

See `docs/CLI_USAGE.md` for output options.
