# Quick Start: Analyze External Codebases

**Use AICL to analyze, test, and heal ANY codebase in 5 minutes**

---

## 1-Minute Setup

```bash
cd tofu-aicl

# Pull if needed
docker-compose pull

# You're ready!
```

---

## Use Case 1: Analyze Someone Else's Code

### Scenario
You inherited a Python project. What's the quality? Any bugs?

### Solution (2 commands)

```bash
# 1. Create experiment
cat > analyze-external.aicl << 'EOF'
provider "loader" {
  source = "aicl/file_loader"
}

resource "loader_files" "code" {
  path = "/mnt/external"
  aiclResourceName = "external_code"
}

output "summary" {
  value = "Loaded ${length(resource.loader_files.code.files)} files"
}
EOF

# 2. Run it
docker-compose run --rm \
  -v /path/to/external/project:/mnt/external:ro \
  tofu-aicl-test \
  python3 run.py analyze-external.aicl
```

**Done!** AICL loaded and analyzed the external code.

---

## Use Case 2: Find Bugs in Legacy Code

### Scenario
Old codebase, no tests, probably has bugs. Find them!

### Solution

**File:** `find-bugs.aicl`

```hcl
variable "target_path" {
  type    = string
  default = "/mnt/code"
}

provider "loader" {
  source = "aicl/file_loader"
}

resource "loader_files" "legacy_code" {
  path = var.target_path
  aiclResourceName = "legacy"
}

output "files_analyzed" {
  value = "Analyzed ${var.target_path}"
}
```

**Run:**

```bash
docker-compose run --rm \
  -v /path/to/legacy/code:/mnt/code:ro \
  tofu-aicl-test \
  python3 run.py find-bugs.aicl
```

---

## Use Case 3: Auto-Heal Failing Tests

### Scenario
Tests are failing. You don't know why. Let AICL fix them!

### Solution

**File:** `auto-heal.aicl`

```hcl
variable "test_file" {
  type = string
}

variable "project_root" {
  type = string
}

provider "loader" {
  source = "aicl/file_loader"
}

# Load failing test
resource "loader_files" "test" {
  path = "${var.project_root}/${var.test_file}"
  aiclResourceName = "failing_test"
}

output "test_loaded" {
  value = "Loaded test: ${var.test_file}"
}
```

**Run:**

```bash
docker-compose run --rm \
  -v /path/to/project:/mnt/project:ro \
  tofu-aicl-test \
  python3 run.py auto-heal.aicl \
  -var="project_root=/mnt/project" \
  -var="test_file=tests/test_broken.py"
```

---

## Use Case 4: Compare Two Projects

### Scenario
Which implementation is better? A or B?

### Solution

**File:** `compare-projects.aicl`

```hcl
variable "project_a" {
  type = string
}

variable "project_b" {
  type = string
}

provider "loader" {
  source = "aicl/file_loader"
}

resource "loader_files" "proj_a" {
  path = var.project_a
  aiclResourceName = "project_a"
}

resource "loader_files" "proj_b" {
  path = var.project_b
  aiclResourceName = "project_b"
}

output "comparison" {
  value = "Compared ${var.project_a} vs ${var.project_b}"
}
```

**Run:**

```bash
docker-compose run --rm \
  -v /path/to/project-a:/mnt/a:ro \
  -v /path/to/project-b:/mnt/b:ro \
  tofu-aicl-test \
  python3 run.py compare-projects.aicl \
  -var="project_a=/mnt/a" \
  -var="project_b=/mnt/b"
```

---

## Configuration Patterns

### Pattern 1: Via CLI Variables

```bash
./aicl_modular run experiment.aicl \
  -var="path=/custom/path" \
  -var="focus=security" \
  -var="output=./results"
```

### Pattern 2: Via Environment

```bash
export AICL_TARGET_PATH="/path/to/code"
export AICL_FOCUS="performance"

./aicl_modular run experiment.aicl
```

### Pattern 3: Via Config File

**Create:** `my-project.yaml`

```yaml
target:
  path: "/path/to/code"
  language: "python"
  
analysis:
  focus: "security"
  models:
    - "claude-3-5-sonnet"

output:
  directory: "./results"
```

**Use:**

```bash
./aicl_modular run experiment.aicl --config my-project.yaml
```

---

## Docker Volume Mounting

### Mount External Code (Read-Only)

```bash
docker-compose run --rm \
  -v /external/code:/mnt/code:ro \
  tofu-aicl-test \
  python3 run.py analyze.aicl -var="path=/mnt/code"
```

### Mount Results Directory (Write)

```bash
docker-compose run --rm \
  -v /external/code:/mnt/code:ro \
  -v $(pwd)/results:/app/results \
  tofu-aicl-test \
  python3 run.py analyze.aicl
```

### Mount Multiple Projects

```bash
docker-compose run --rm \
  -v ~/project1:/p1:ro \
  -v ~/project2:/p2:ro \
  -v ~/project3:/p3:ro \
  tofu-aicl-test \
  python3 run.py batch-analyze.aicl
```

---

## Real-World Examples

### Example 1: Analyze Open Source Project

```bash
# Clone the project
git clone https://github.com/someorg/project /tmp/analyze-me

# Analyze it
docker-compose run --rm \
  -v /tmp/analyze-me:/mnt/project:ro \
  tofu-aicl-test \
  python3 run.py analyze-external.aicl \
  -var="path=/mnt/project/src"
```

### Example 2: Security Audit Before Deployment

```bash
# Audit production code
docker-compose run --rm \
  -v /var/www/myapp:/mnt/app:ro \
  tofu-aicl-test \
  python3 run.py security-audit.aicl \
  -var="path=/mnt/app" \
  -var="focus=security"
```

### Example 3: CI/CD Integration

```yaml
# .github/workflows/code-quality.yml
name: AICL Code Quality

on: [push]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Analyze with AICL
        run: |
          docker run --rm \
            -v $(pwd):/mnt/code:ro \
            tofu-aicl:latest \
            python3 run.py analyze.aicl \
            -var="path=/mnt/code"
```

---

## Template Library

Create reusable templates for common tasks:

### Security Audit Template

**File:** `templates/security-audit.aicl`

```hcl
variable "target" { type = string }

provider "loader" {
  source = "aicl/file_loader"
}

resource "loader_files" "code" {
  path = var.target
  aiclResourceName = "audit_target"
}

output "security_scan" {
  value = "Scanned ${var.target} for security issues"
}
```

### Performance Analysis Template

**File:** `templates/performance-check.aicl`

```hcl
variable "target" { type = string }

provider "loader" {
  source = "aicl/file_loader"
}

resource "loader_files" "code" {
  path = var.target
  aiclResourceName = "perf_check"
}

output "performance_report" {
  value = "Performance analysis of ${var.target}"
}
```

### Usage

```bash
# Use template
./aicl_modular run templates/security-audit.aicl \
  -var="target=/path/to/project"

./aicl_modular run templates/performance-check.aicl \
  -var="target=/path/to/project"
```

---

## Tips & Tricks

### 1. Always Mount Read-Only

```bash
-v /code:/mnt/code:ro  # ← the :ro is important!
```

### 2. Use Shell Variables

```bash
PROJECT=/path/to/code
docker run -v $PROJECT:/mnt/code:ro ...
```

### 3. Create Aliases

```bash
# Add to ~/.bashrc
alias aicl-analyze='docker-compose -f /path/to/tofu-aicl/docker-compose.yml run --rm'

# Use it
aicl-analyze -v ~/myproject:/mnt:ro tofu-aicl-test python3 run.py analyze.aicl
```

### 4. Batch Process Multiple Projects

```bash
# Analyze all projects in directory
for project in ~/projects/*; do
  echo "Analyzing $project..."
  docker-compose run --rm \
    -v "$project:/mnt/code:ro" \
    tofu-aicl-test \
    python3 run.py analyze.aicl \
    -var="path=/mnt/code"
done
```

---

## Troubleshooting

### Issue: Can't access files

**Problem:** Docker can't see your files

**Solution:** Check volume mount

```bash
# Verify mount works
docker-compose run --rm \
  -v /path/to/code:/mnt/code:ro \
  tofu-aicl-test \
  ls -la /mnt/code
```

### Issue: Permission denied

**Problem:** File permissions

**Solution:** Mount as read-only

```bash
-v /path:/mnt:ro  # Add :ro
```

### Issue: Path not found

**Problem:** Wrong path in experiment

**Solution:** Use absolute paths

```bash
# In experiment file
path = "/mnt/code"  # Not "./code"
```

---

## Summary

**3-Step Process:**

1. **Create experiment** (`.aicl` file)
2. **Mount external code** (`-v` flag)
3. **Run analysis** (`docker-compose run`)

**Example:**

```bash
# 1. Experiment
cat > my-analysis.aicl << 'EOF'
provider "loader" { source = "aicl/file_loader" }
resource "loader_files" "code" {
  path = "/mnt/external"
  aiclResourceName = "code"
}
EOF

# 2. Mount & Run
docker-compose run --rm \
  -v /path/to/code:/mnt/external:ro \
  tofu-aicl-test \
  python3 run.py my-analysis.aicl

# Done!
```

**You can now analyze ANY codebase with AICL!** 🚀
