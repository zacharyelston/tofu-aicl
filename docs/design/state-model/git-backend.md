# Git-Based State Backend

## Why Git?

For tofu-aicl's experimentation focus, git is the perfect state backend:

✅ State files are experiment reports (want them versioned)  
✅ Comparison is critical (git diff)  
✅ Collaboration through PRs  
✅ Audit trail built-in (git blame, log)  
✅ Simple (no separate infrastructure)

## Git as Default

```hcl
terraform {
  backend "local" {
    path = "terraform.tfstate.d/${var.experiment_id}.tfstate"
  }
}
```

State files are git-tracked by default.

## Locking Through Git

Git provides implicit locking through merge conflicts:

```bash
# Developer A
git pull
tofu apply
git add state.tfstate
git commit && git push

# Developer B (concurrent)
git pull
tofu apply  
git add state.tfstate
git commit && git push  # FAILS - merge conflict
```

This is **better for experimentation** because:
- Conflicts are explicit
- Changes can be reviewed in PRs
- History is preserved

## Workflows

### Experiment Comparison
```bash
git diff experiment_001.tfstate experiment_002.tfstate
```

### Experiment History
```bash
git log -- terraform.tfstate.d/exp_001.tfstate
git show abc123:terraform.tfstate.d/exp_001.tfstate
```

### Collaboration
```bash
git checkout -b experiment_003
# run experiment
git add terraform.tfstate.d/experiment_003.tfstate
git commit -m "Experiment 003: larger chunks"
# Create PR for review
```

## When NOT to Use Git

Only use remote state (S3/DynamoDB) when:
- ⚠️ CI/CD needs atomic operations
- ⚠️ Many concurrent automated processes
- ⚠️ State files are huge (>100MB)
- ⚠️ Production systems with strict requirements

For tofu-aicl: **This is edge cases only.**

## Optional Remote Backend

```hcl
# Can opt-in for specific cases
terraform {
  backend "s3" {
    bucket = "tofu-aicl-state"
    key    = "production/service.tfstate"
    dynamodb_table = "tofu-aicl-locks"
  }
}
```
