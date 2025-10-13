# AICL Experiment Builder Guide

**How to use AICL to analyze, test, and self-heal any codebase**

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Building an Experiment](#building-an-experiment)
3. [Self-Healing Tests](#self-healing-tests)
4. [Applying to Other Codebases](#applying-to-other-codebases)
5. [Configuration Methods](#configuration-methods)
6. [Examples](#examples)

---

## Quick Start

### Analyze Any Codebase in 3 Steps

```bash
# 1. Create experiment file
cat > my-experiment.aicl << 'EOF'
provider "loader" {
  source = "aicl/file_loader"
}

resource "loader_files" "code" {
  path = "/path/to/your/codebase"
  aiclResourceName = "mycode"
}
EOF

# 2. Run in Docker
docker-compose run --rm tofu-aicl-test python3 run.py my-experiment.aicl

# 3. Review results
```

---

## Building an Experiment

### 1. Basic Experiment Structure

Every AICL experiment has 3 parts:

```hcl
# Part 1: Declare providers
provider "loader" {
  source = "aicl/file_loader"
}

# Part 2: Define resources (what to do)
resource "loader_files" "code" {
  path = "src/"
  aiclResourceName = "code"
}

# Part 3: Outputs (what to show)
output "files_loaded" {
  value = "Loaded ${resource.loader_files.code.path}"
}
```

### 2. Add Variables for Reusability

```hcl
variable "target_path" {
  type    = string
  default = "src/"
}

variable "file_pattern" {
  type    = string
  default = "*.py"
}

resource "loader_files" "code" {
  path    = var.target_path
  pattern = var.file_pattern
  aiclResourceName = "code"
}
```

### 3. Chain Resources

```hcl
# Load code
resource "loader_files" "source" {
  path = var.code_path
  aiclResourceName = "source"
}

# Analyze with LLM
resource "naga_completion" "analysis" {
  model = "claude-3-5-sonnet"
  prompt = <<-EOT
    Analyze this code:
    ${resource.loader_files.source.files}
    
    Find potential bugs and improvements.
  EOT
}

# Output results
output "analysis_result" {
  value = resource.naga_completion.analysis.response
}
```

---

## Self-Healing Tests

### Concept

```
Test Fails → Analyze Error → Generate Fix → Verify Fix → Apply if Good
```

### Example: Self-Healing Unit Test

**File:** `self-healing-test.aicl`

```hcl
provider "loader" {
  source = "aicl/file_loader"
}

provider "naga" {
  source = "aicl/naga"
}

provider "command" {
  source = "aicl/command"
}

variable "test_file" {
  type    = string
  default = "tests/test_mymodule.py"
}

# Step 1: Load failing test
resource "loader_files" "test_code" {
  path = var.test_file
  aiclResourceName = "failing_test"
}

# Step 2: Run test and capture error
resource "command_exec" "run_test" {
  command = "pytest ${var.test_file} -v"
  aiclResourceName = "test_result"
}

# Step 3: Analyze failure
resource "naga_completion" "analyze_failure" {
  model = "claude-3-5-sonnet"
  
  prompt = <<-EOT
    A test failed. Analyze and fix it.
    
    TEST CODE:
    ${resource.loader_files.test_code.content}
    
    ERROR OUTPUT:
    ${resource.command_exec.run_test.stderr}
    
    EXIT CODE: ${resource.command_exec.run_test.exit_code}
    
    TASK:
    1. Identify root cause
    2. Generate fix
    3. Return ONLY the fixed test code
  EOT
  
  max_tokens = 2000
}

# Step 4: Judge fix quality
resource "naga_completion" "judge_fix" {
  model = "gpt-4"
  
  prompt = <<-EOT
    Evaluate this fix:
    
    ORIGINAL ERROR: ${resource.command_exec.run_test.stderr}
    PROPOSED FIX: ${resource.naga_completion.analyze_failure.response}
    
    Score (0-100):
    - Correctness (40 pts): Fixes the issue?
    - Quality (30 pts): Clean code?
    - Safety (30 pts): No side effects?
    
    Return JSON: {"score": 0-100, "decision": "ACCEPT|REJECT", "reasoning": "..."}
  EOT
}

# Outputs
output "fix_proposal" {
  value = resource.naga_completion.analyze_failure.response
}

output "fix_quality" {
  value = resource.naga_completion.judge_fix.response
}

output "recommendation" {
  value = "Review fix and apply if score >= 80"
}
```

### Run Self-Healing Test

```bash
# Set target test file
export TEST_FILE="tests/test_broken.py"

# Run healing experiment
docker-compose run --rm tofu-aicl-test python3 run.py \
  self-healing-test.aicl \
  -var="test_file=$TEST_FILE"

# Review output and apply fix manually
```

---

## Applying to Other Codebases

### Method 1: Config File

**Create:** `~/.aicl/my-project-config.yaml`

```yaml
target:
  codebase: "/path/to/other/project"
  language: "python"
  test_dir: "tests"
  src_dir: "src"

analysis:
  focus: "bugs"
  models:
    - "claude-3-5-sonnet"
    - "gpt-4"

output:
  directory: "./analysis-results"
  format: "markdown"
```

**Use in experiment:**

```hcl
variable "config_file" {
  type    = string
  default = "~/.aicl/my-project-config.yaml"
}

resource "loader_files" "external_code" {
  path = file(var.config_file).target.codebase
  aiclResourceName = "external"
}
```

### Method 2: CLI Arguments

```bash
# Via environment variables
export AICL_TARGET_PATH="/path/to/other/project"
export AICL_ANALYSIS_FOCUS="security"

# Via CLI flags
./aicl_modular run analysis.aicl \
  -var="target_path=/path/to/other/project" \
  -var="focus=security" \
  -var="output_dir=./results"

# Via Docker volume mount
docker-compose run --rm \
  -v /path/to/other/project:/mnt/target:ro \
  tofu-aicl-test \
  python3 run.py analysis.aicl \
  -var="target_path=/mnt/target"
```

### Method 3: Experiment Template

**Create reusable template:**

`analyze-project.aicl.template`

```hcl
variable "project_path" {
  type = string
  description = "Path to project to analyze"
}

variable "project_name" {
  type = string
  description = "Project name for reporting"
}

variable "analysis_type" {
  type    = string
  default = "code_quality"
  description = "Type: code_quality, security, performance"
}

provider "loader" {
  source = "aicl/file_loader"
}

provider "naga" {
  source = "aicl/naga"
}

# Load project code
resource "loader_files" "project" {
  path = var.project_path
  aiclResourceName = var.project_name
}

# Analyze based on type
resource "naga_completion" "analysis" {
  model = "claude-3-5-sonnet"
  
  prompt = <<-EOT
    Analyze ${var.project_name} for ${var.analysis_type}.
    
    CODE:
    ${resource.loader_files.project.files}
    
    Provide detailed report with:
    1. Summary
    2. Issues found (high/medium/low severity)
    3. Recommendations
    4. Priority actions
  EOT
  
  max_tokens = 4000
}

output "analysis_report" {
  value = resource.naga_completion.analysis.response
}
```

**Use template:**

```bash
# Analyze different projects with same template
./aicl_modular run analyze-project.aicl.template \
  -var="project_path=/home/user/webapp" \
  -var="project_name=MyWebApp" \
  -var="analysis_type=security"

./aicl_modular run analyze-project.aicl.template \
  -var="project_path=/home/user/api" \
  -var="project_name=MyAPI" \
  -var="analysis_type=performance"
```

---

## Configuration Methods

### Priority Order

```
CLI Arguments > Environment Variables > Config File > Defaults
```

### 1. CLI Arguments (Highest Priority)

```bash
./aicl_modular run experiment.aicl \
  -var="path=/custom/path" \
  -var="model=gpt-4" \
  -var="focus=security"
```

### 2. Environment Variables

```bash
export AICL_TARGET_PATH="/custom/path"
export AICL_MODEL="gpt-4"
export AICL_FOCUS="security"

./aicl_modular run experiment.aicl
```

### 3. Config File

**Create:** `experiment-config.yaml`

```yaml
variables:
  path: "/custom/path"
  model: "gpt-4"
  focus: "security"

providers:
  naga:
    api_key_env: "ANTHROPIC_API_KEY"
  
output:
  directory: "./results"
  format: "json"
```

**Use:**

```bash
./aicl_modular run experiment.aicl --config experiment-config.yaml
```

### 4. Defaults (In Experiment)

```hcl
variable "path" {
  type    = string
  default = "./src"  # Lowest priority
}
```

---

## Examples

### Example 1: Analyze External Project

**Scenario:** Analyze a React app you didn't write

```hcl
# analyze-react-app.aicl

variable "app_path" {
  type = string
}

provider "loader" {
  source = "aicl/file_loader"
}

provider "naga" {
  source = "aicl/naga"
}

resource "loader_files" "react_code" {
  path    = "${var.app_path}/src"
  pattern = "*.{js,jsx,ts,tsx}"
  aiclResourceName = "react_app"
}

resource "naga_completion" "react_analysis" {
  model = "claude-3-5-sonnet"
  
  prompt = <<-EOT
    Analyze this React application:
    
    ${resource.loader_files.react_code.files}
    
    Focus on:
    1. Component structure
    2. State management
    3. Performance issues
    4. Security vulnerabilities
    5. Best practices violations
    
    Provide actionable recommendations.
  EOT
  
  max_tokens = 4000
}

output "analysis" {
  value = resource.naga_completion.react_analysis.response
}
```

**Run:**

```bash
docker run --rm \
  -v /path/to/react-app:/mnt/app:ro \
  -v $(pwd):/workspace \
  -w /workspace \
  tofu-aicl:latest \
  python3 run.py analyze-react-app.aicl \
  -var="app_path=/mnt/app"
```

### Example 2: Self-Healing Django Tests

```hcl
# heal-django-tests.aicl

variable "django_project" {
  type = string
}

variable "failing_test" {
  type = string
}

provider "loader" {
  source = "aicl/file_loader"
}

provider "command" {
  source = "aicl/command"
}

provider "naga" {
  source = "aicl/naga"
}

# Load test file
resource "loader_files" "test" {
  path = "${var.django_project}/${var.failing_test}"
  aiclResourceName = "django_test"
}

# Load related models/views
resource "loader_files" "context" {
  path = "${var.django_project}/models.py"
  aiclResourceName = "context"
}

# Run test
resource "command_exec" "run_test" {
  command = "cd ${var.django_project} && python manage.py test ${var.failing_test}"
  aiclResourceName = "test_run"
}

# Analyze and fix
resource "naga_completion" "fix_test" {
  model = "claude-3-5-sonnet"
  
  prompt = <<-EOT
    Fix this Django test.
    
    TEST CODE:
    ${resource.loader_files.test.content}
    
    CONTEXT (Models):
    ${resource.loader_files.context.content}
    
    ERROR:
    ${resource.command_exec.run_test.stderr}
    
    Generate fixed test that:
    1. Follows Django best practices
    2. Uses proper fixtures
    3. Tests the right behavior
    4. Will pass
  EOT
}

# Judge quality
resource "naga_completion" "judge" {
  model = "gpt-4"
  
  prompt = <<-EOT
    Score this Django test fix (0-100):
    
    ${resource.naga_completion.fix_test.response}
    
    Criteria:
    - Django best practices (30 pts)
    - Test coverage (30 pts)
    - Code quality (20 pts)
    - Will it pass? (20 pts)
    
    JSON: {"score": X, "decision": "ACCEPT|REJECT"}
  EOT
}

output "proposed_fix" {
  value = resource.naga_completion.fix_test.response
}

output "quality_score" {
  value = resource.naga_completion.judge.response
}
```

**Run:**

```bash
./aicl_modular run heal-django-tests.aicl \
  -var="django_project=/path/to/myproject" \
  -var="failing_test=myapp.tests.TestUserModel.test_create_user"
```

### Example 3: Multi-Project Comparison

```hcl
# compare-projects.aicl

variable "project_a_path" {
  type = string
}

variable "project_b_path" {
  type = string
}

provider "loader" {
  source = "aicl/file_loader"
}

provider "naga" {
  source = "aicl/naga"
}

resource "loader_files" "project_a" {
  path = var.project_a_path
  aiclResourceName = "project_a"
}

resource "loader_files" "project_b" {
  path = var.project_b_path
  aiclResourceName = "project_b"
}

resource "naga_completion" "comparison" {
  model = "claude-3-5-sonnet"
  
  prompt = <<-EOT
    Compare these two codebases:
    
    PROJECT A:
    ${resource.loader_files.project_a.files}
    
    PROJECT B:
    ${resource.loader_files.project_b.files}
    
    Compare:
    1. Architecture approaches
    2. Code quality
    3. Test coverage
    4. Best practices
    5. Performance patterns
    
    Which is better and why?
    What can each learn from the other?
  EOT
  
  max_tokens = 5000
}

output "comparison_report" {
  value = resource.naga_completion.comparison.response
}
```

**Run:**

```bash
docker-compose run --rm \
  -v /path/to/project1:/mnt/proj1:ro \
  -v /path/to/project2:/mnt/proj2:ro \
  tofu-aicl-test \
  python3 run.py compare-projects.aicl \
  -var="project_a_path=/mnt/proj1" \
  -var="project_b_path=/mnt/proj2"
```

---

## Best Practices

### 1. Use Variables for Reusability

```hcl
variable "target" { type = string }
variable "model" { type = string, default = "claude-3-5-sonnet" }
variable "output_dir" { type = string, default = "./results" }
```

### 2. Mount External Code as Read-Only

```bash
docker run -v /external/code:/mnt/code:ro ...
```

### 3. Save Results to Mounted Volume

```yaml
volumes:
  - ./results:/app/results  # Save here
```

### 4. Chain Experiments

```bash
# Run analysis
./aicl_modular run analyze.aicl > results.json

# Use results in next experiment
./aicl_modular run fix.aicl -var="issues=$(cat results.json)"
```

### 5. Use Templates for Common Tasks

Create library of templates:
```
templates/
├── analyze-python.aicl
├── analyze-javascript.aicl
├── security-audit.aicl
├── performance-check.aicl
└── test-healer.aicl
```

---

## Quick Reference

### Analyze Any Codebase

```bash
docker run --rm \
  -v /path/to/code:/mnt/code:ro \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  tofu-aicl:latest \
  python3 run.py analyze.aicl -var="path=/mnt/code"
```

### Self-Heal Tests

```bash
./aicl_modular run heal-test.aicl \
  -var="test_file=tests/test_broken.py" \
  -var="model=claude-3-5-sonnet"
```

### Compare Projects

```bash
docker-compose run --rm \
  -v $PROJECT1:/p1:ro \
  -v $PROJECT2:/p2:ro \
  tofu-aicl-test \
  python3 run.py compare.aicl \
  -var="project_a=/p1" \
  -var="project_b=/p2"
```

---

## Summary

**Build Experiments:**
1. Define providers
2. Create resources
3. Add outputs

**Self-Healing:**
1. Run test → Capture error
2. Analyze error → Generate fix
3. Judge quality → Apply if good

**Other Codebases:**
1. Mount via Docker volume
2. Pass path via variable
3. Run experiment

**Configuration:**
- CLI args (highest priority)
- Environment variables
- Config files
- Defaults (lowest priority)

**Simple and powerful!** 🚀
