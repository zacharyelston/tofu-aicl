# Matrix Experiment Results

This directory contains state files and results from matrix experiments.

## Files

- `*.tfstate` - Terraform state files for each experiment
- `*.aicl` - AICL configuration files used for each experiment
- `matrix_summary.json` - Summary of all experiments with metadata

## Usage

### Run Matrix Experiments
```bash
python run_matrix.py
```

### Compare Results
```bash
python compare_matrix.py
```

## State Files

Each experiment produces:
- Configuration file: `{experiment_id}.aicl`
- State file: `{experiment_id}.tfstate`

State files contain complete resource information and can be used for detailed analysis.
