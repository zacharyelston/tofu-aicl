# Remote State Backend (Optional)

## When Git is NOT Enough

While git is the **default and recommended** backend for tofu-aicl, there are edge cases where remote state (S3 + DynamoDB) makes sense.

## Use Remote Backend When:

### 1. CI/CD Requires Atomic Operations
```yaml
# GitHub Actions workflow
- name: Deploy Infrastructure
  run: tofu apply --auto-approve
  # Can't wait for git pull/push/merge
  # Needs immediate atomic lock
```

**Problem with Git:**
- CI jobs can't resolve merge conflicts
- Race conditions between parallel jobs
- Need instant lock acquisition

**Solution:**
```hcl
terraform {
  backend "s3" {
    bucket         = "tofu-aicl-state"
    key            = "ci/main.tfstate"
    region         = "us-west-2"
    dynamodb_table = "tofu-aicl-locks"
    encrypt        = true
  }
}
```

### 2. Many Concurrent Automated Processes

**Scenario:**
- 10+ automated experiments running simultaneously
- Distributed system with many agents
- High-frequency state updates

**Problem with Git:**
- Constant merge conflicts
- Git not designed for high-frequency writes
- Coordination overhead

**Solution:** S3 with DynamoDB locking provides instant coordination.

### 3. State Files Are Huge (>100MB)

**Scenario:**
- Experiments with massive datasets
- Storing large output artifacts in state
- Binary data in results

**Problem with Git:**
- Git performance degrades with large files
- Repo size grows quickly
- Slow clone/pull operations

**Solution:** S3 handles large files efficiently.

### 4. Production Systems with Zero Tolerance for Conflicts

**Scenario:**
- Production infrastructure management
- Multiple teams managing shared resources
- Downtime is unacceptable

**Problem with Git:**
- Merge conflicts require manual resolution
- Not acceptable in production
- Need immediate failure on conflict

**Solution:** DynamoDB lock fails immediately on conflict.

## Configuration

### Git Backend (Default)
```hcl
terraform {
  backend "local" {
    path = "terraform.tfstate.d/${var.experiment_id}.tfstate"
  }
}
```

### S3 Backend (Opt-in)
```hcl
terraform {
  backend "s3" {
    bucket         = "tofu-aicl-state"
    key            = "prod/main.tfstate"
    region         = "us-west-2"
    dynamodb_table = "tofu-aicl-locks"
    encrypt        = true
  }
}
```

## Comparison

| Feature | Git Backend | S3 Backend |
|---------|-------------|------------|
| **Setup** | ✅ None (built-in) | ⚠️ AWS account + config |
| **Cost** | ✅ Free | 💰 AWS costs |
| **Conflicts** | ⚠️ Manual merge | ✅ Automatic lock |
| **History** | ✅ Git log | ⚠️ S3 versioning |
| **Diff** | ✅ `git diff` | ❌ Manual |
| **Review** | ✅ PR workflow | ❌ None |
| **Offline** | ✅ Works offline | ❌ Needs network |
| **Speed (small)** | ✅ Fast | ⚠️ Network latency |
| **Speed (large)** | ❌ Slow | ✅ Fast |
| **Concurrent** | ⚠️ Conflicts | ✅ Locked |
| **Audit** | ✅ Git history | ⚠️ CloudTrail |
| **Experimentation** | ✅✅✅ Ideal | ⚠️ Overkill |
| **Production** | ⚠️ Risky | ✅ Safer |

## Recommendation

### For 90% of Use Cases: Use Git
- **Research & experiments**
- **A/B testing**
- **Parameter tuning**
- **Small teams (<10 people)**
- **Educational projects**
- **Reproducible research**

### For 10% of Use Cases: Use S3
- **Production infrastructure**
- **CI/CD pipelines**
- **Large-scale distributed systems**
- **High-frequency automation**
- **Very large state files (>100MB)**

## Hybrid Approach

You can mix backends per-project:

```
repo/
  experiments/         # Git-backed
    001_baseline/
      experiment.tfstate
    002_variation/
      experiment.tfstate
  
  production/          # S3-backed
    config.aicl
    # State in S3, not git
```

## Setup Instructions

### S3 Backend Setup

1. **Create S3 Bucket:**
```bash
aws s3 mb s3://tofu-aicl-state --region us-west-2
aws s3api put-bucket-versioning \
  --bucket tofu-aicl-state \
  --versioning-configuration Status=Enabled
```

2. **Create DynamoDB Table:**
```bash
aws dynamodb create-table \
  --table-name tofu-aicl-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

3. **Configure Backend:**
```hcl
terraform {
  backend "s3" {
    bucket         = "tofu-aicl-state"
    key            = "path/to/state.tfstate"
    region         = "us-west-2"
    dynamodb_table = "tofu-aicl-locks"
    encrypt        = true
  }
}
```

## Cost Estimation

### Git Backend
- **Cost:** $0 (free)
- **Storage:** Repo size (typically <100MB)
- **Bandwidth:** Only for git push/pull

### S3 Backend
- **Storage:** ~$0.023/GB/month
- **Requests:** ~$0.005 per 1000 requests
- **DynamoDB:** ~$0.25 per million requests
- **Typical:** <$5/month for moderate use

## Migration

### Git → S3
```bash
# 1. Configure S3 backend in config
# 2. Migrate state
tofu init -migrate-state

# 3. Verify
tofu state list
```

### S3 → Git
```bash
# 1. Pull state from S3
tofu state pull > terraform.tfstate.d/migrated.tfstate

# 2. Configure git backend
# 3. Reinit
tofu init

# 4. Commit state
git add terraform.tfstate.d/
git commit -m "Migrated state to git"
```

## Key Takeaway

> Use git by default. Only reach for S3/DynamoDB when you have a specific problem that git can't solve.

The "State as DNA" model works **best** with git for tofu-aicl's primary use case: AI experimentation and research.

## Next Steps

See `06-implementation.md` for how to implement the state backend system.
