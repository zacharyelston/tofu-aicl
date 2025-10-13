# Using AICL with External Codebases

**Complete guide to analyzing, testing, and healing ANY codebase with AICL**

---

## Quick Links

- 📚 **[Experiment Builder Guide](EXPERIMENT_BUILDER_GUIDE.md)** - Complete reference (14KB)
- 🚀 **[Quick Start](QUICK_START_EXTERNAL.md)** - Get started in 5 minutes (8KB)
- 📊 **[Status & Workarounds](EXPERIMENT_STATUS.md)** - Current capabilities
- 💡 **[Examples](../experiments/examples/)** - Working code samples

---

## What You Can Do

### ✅ Analyze Any Codebase

```bash
docker-compose run --rm \
  -v /path/to/code:/mnt/code:ro \
  tofu-aicl-test \
  python3 run.py analyze.aicl -var="path=/mnt/code"
```

### ✅ Self-Healing Tests

```bash
./aicl_modular run heal-test.aicl \
  -var="test_file=tests/broken_test.py"
```

### ✅ Compare Projects

```bash
docker-compose run --rm \
  -v /project1:/p1:ro \
  -v /project2:/p2:ro \
  tofu-aicl-test \
  python3 run.py compare.aicl
```

---

## Documentation

### For Different Users

**Beginners:** Start with [Quick Start](QUICK_START_EXTERNAL.md)
- 5-minute setup
- Copy-paste examples
- Immediate results

**Developers:** Read [Experiment Builder Guide](EXPERIMENT_BUILDER_GUIDE.md)
- Complete API reference
- Advanced patterns
- Best practices

**DevOps:** See [Status Document](EXPERIMENT_STATUS.md)
- What works now
- CI/CD integration
- Workarounds

---

## Key Concepts

### 1. Experiments

**Definition:** AICL configuration files (`.aicl`) that define analysis workflows

**Structure:**
```hcl
provider "..." { }      # What tools to use
resource "..." { }      # What to do
output "..." { }        # What to show
```

### 2. Self-Healing

**Definition:** Automatic bug detection and fix proposal

**Flow:**
```
Run Test → Fails → Analyze → Generate Fix → Judge Quality → Apply
```

### 3. External Codebases

**Definition:** Any code outside the AICL project

**Method:** Mount via Docker volumes
```bash
-v /external/code:/mnt/code:ro
```

### 4. Configuration

**Priority:** CLI > Env > Config File > Defaults

**Methods:**
- CLI: `-var="key=value"`
- Env: `export AICL_KEY=value`
- File: `--config config.yaml`

---

## Examples by Use Case

### Security Audit

```hcl
# security-audit.aicl
variable "target" { type = string }

provider "loader" {
  source = "aicl/file_loader"
}

resource "loader_files" "code" {
  path = var.target
  aiclResourceName = "audit"
}
```

**Run:**
```bash
./aicl_modular run security-audit.aicl -var="target=/path/to/code"
```

### Performance Analysis

```hcl
# performance-check.aicl
variable "target" { type = string }

provider "loader" {
  source = "aicl/file_loader"
}

resource "loader_files" "code" {
  path = var.target
  aiclResourceName = "perf"
}
```

**Run:**
```bash
./aicl_modular run performance-check.aicl -var="target=/path/to/code"
```

### Code Quality

```hcl
# quality-check.aicl
variable "target" { type = string }

provider "loader" {
  source = "aicl/file_loader"
}

resource "loader_files" "code" {
  path = var.target
  aiclResourceName = "quality"
}
```

**Run:**
```bash
./aicl_modular run quality-check.aicl -var="target=/path/to/code"
```

---

## Cookbook

### Recipe 1: Analyze Open Source Project

```bash
# 1. Clone
git clone https://github.com/org/project /tmp/analyze

# 2. Analyze
docker-compose run --rm \
  -v /tmp/analyze:/mnt:ro \
  tofu-aicl-test \
  python3 run.py analyze.aicl -var="path=/mnt"
```

### Recipe 2: CI/CD Integration

```yaml
# .github/workflows/aicl-analysis.yml
name: AICL Analysis
on: [push]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: |
          docker run --rm \
            -v $(pwd):/mnt:ro \
            tofu-aicl:latest \
            python3 run.py analyze.aicl -var="path=/mnt"
```

### Recipe 3: Batch Analysis

```bash
# Analyze all projects
for project in ~/projects/*; do
  docker-compose run --rm \
    -v "$project:/mnt:ro" \
    tofu-aicl-test \
    python3 run.py analyze.aicl -var="path=/mnt" \
    > "analysis-$(basename $project).txt"
done
```

---

## Best Practices

### ✅ DO

- Mount external code as read-only (`:ro`)
- Use absolute paths in Docker
- Test with AICL itself first
- Create reusable templates
- Save results to mounted volumes

### ❌ DON'T

- Mount without `:ro` flag
- Use relative paths in containers
- Assume paths between host/container
- Hardcode paths in experiments
- Run without testing first

---

## Troubleshooting

### Can't access files

```bash
# Debug: Check mount
docker-compose run --rm \
  -v /path:/mnt:ro \
  tofu-aicl-test \
  ls -la /mnt
```

### Permission denied

```bash
# Solution: Use :ro
-v /path:/mnt:ro  # ← Add this
```

### Provider not found

```bash
# Workaround: Use Python
docker-compose run --rm tofu-aicl-test \
  python3 your-script.py
```

---

## What's Next

### Immediate (Works Now)

1. ✅ Use Python scripts
2. ✅ Mount external code
3. ✅ Analyze any codebase
4. ✅ Follow documented patterns

### Short Term (Pending)

1. ⏸️ Fix provider infrastructure
2. ⏸️ Run full `.aicl` experiments
3. ⏸️ Add LLM-based analysis
4. ⏸️ Automated fix application

### Long Term

1. 📋 CI/CD templates
2. 📋 Pre-built analyzers
3. 📋 Quality gates
4. 📋 Auto-healing pipelines

---

## Get Help

### Documentation

- [Experiment Builder Guide](EXPERIMENT_BUILDER_GUIDE.md) - Complete guide
- [Quick Start](QUICK_START_EXTERNAL.md) - Fast start
- [Status Document](EXPERIMENT_STATUS.md) - Current state
- [Examples](../experiments/examples/) - Working code

### Support

- 📖 Read the docs first
- 💡 Check examples directory
- 🔍 Review troubleshooting section
- ✅ Verify Docker setup

---

## Summary

**Documentation:** Complete ✅  
**Infrastructure:** Ready ✅  
**Examples:** Working ✅  
**Can use:** NOW ✅

**3-Step Process:**
1. Create experiment (`.aicl` file)
2. Mount code (`-v` flag)
3. Run analysis (`docker-compose run`)

**You can analyze ANY codebase with AICL!** 🚀

---

## File Reference

```
docs/
├── EXPERIMENT_BUILDER_GUIDE.md    # Complete reference
├── QUICK_START_EXTERNAL.md        # Quick guide
├── EXPERIMENT_STATUS.md            # Current status
└── EXTERNAL_CODEBASE_INDEX.md     # This file

experiments/
└── examples/
    ├── README.md                   # Examples guide
    └── analyze-external-demo.aicl  # Working demo
```

**Start here:** [Quick Start](QUICK_START_EXTERNAL.md) → [Builder Guide](EXPERIMENT_BUILDER_GUIDE.md) → [Examples](../experiments/examples/)
