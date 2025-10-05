# Git-Based State Backend

## Why Git is Perfect for tofu-aicl

### The Default Choice

Git should be the **primary state backend** for tofu-aicl because:

✅ **Experimentation is the primary use case**
- AI workflows are exploratory
- Need to run many experiments
- Compare results is critical

✅ **State files are artifacts**
- Want them version controlled
- Complete history matters
- Reviewable in PRs

✅ **Team coordination through git**
- Natural workflow for developers
- PR reviews show exact changes
- Git history = experiment log

✅ **Infrastructure is often ephemeral**
- Spin up → use → destroy
- Not managing long-lived infrastructure
- State is the valuable output

✅ **Comparing experiments is essential**
- `git diff experiment_001.tfstate experiment_002.tfstate`
- See exactly what changed between runs
- Track parameter impact

## Git Workflows

### Single User Local Development

```bash
# Run experiment
tofu apply experiment.aicl

# State automatically saved to git-tracked file
# terraform.tfstate.d/experiment_001.tfstate

# Commit when ready
git add terraform.tfstate.d/experiment_001.tfstate
git commit -m "Experiment 001: baseline with chunk_size=500"
```

### Team Collaboration

```bash
# Developer A
git pull  # Get latest
tofu apply experiment.aicl
git add terraform.tfstate.d/shared.tfstate
git commit && git push

# Developer B (concurrent)
git pull
tofu apply experiment.aicl
git add terraform.tfstate.d/shared.tfstate
git commit && git push  # CONFLICT!

# Conflict resolution
git pull  # Shows state file conflict
# Either merge or rerun experiment
```

### Experiment Comparison

```bash
# Compare two experiments
git diff experiment_001.tfstate experiment_002.tfstate

# See what changed
# - Different parameters
# - Different results
# - Performance differences
```

## "Locking" Through Git

Git provides natural conflict resolution:

- **Explicit conflicts** - Git shows you when states diverge
- **Visible history** - `git log` shows who did what
- **PR reviews** - Team reviews changes before merge
- **State versioned with code** - Config and state stay in sync

This is **better than S3 locking** for experimentation:
- Conflicts are learning opportunities
- History provides context
- Reviews catch issues early
- No hidden state changes

## When Git Works Best

Perfect for:
- 📊 Research experiments
- 🧪 A/B testing variations
- 📈 Parameter tuning
- 🔬 Model comparisons
- 👥 Small team collaboration
- 📚 Educational projects
- 🎯 Reproducible research

## When to Use Remote Backend Instead

Only use S3/DynamoDB when:
- ⚠️ CI/CD needs atomic operations (can't wait for git)
- ⚠️ Many concurrent automated processes  
- ⚠️ State files are huge (>100MB, git becomes slow)
- ⚠️ Production systems where conflicts are unacceptable

For tofu-aicl, these are **edge cases only**.

## Benefits Summary

1. **Version Control** - Complete history of all experiments
2. **Diff-able** - Easy comparison between runs
3. **Reviewable** - PR reviews show exact changes
4. **Portable** - Clone repo = get all experiments
5. **Simple** - No external dependencies
6. **Secure** - Standard git authentication
7. **Offline** - Works without network

## Implementation Priority

**Phase 1: Git-only (MVP)**
- State files in `terraform.tfstate.d/`
- Git tracks them
- Users commit/push manually or via script
- **Perfect for 90% of use cases**

**Phase 2: Optional Remote (if needed)**
- Add S3/DynamoDB backend option
- Only for production/shared infrastructure
- Most experiments still use git
- Configurable per-project

## Next Steps

See `03-state-structure.md` for the state file format that enables this.
