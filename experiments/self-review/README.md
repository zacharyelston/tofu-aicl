# AICL Self-Review: Dockerized

Use AICL to review and analyze the AICL codebase in isolated Docker containers.

## Quick Start

```bash
cd /Users/zacelston/code/tofu-aicl/experiments/self-review

# Build the review image
docker-compose -f docker-compose.review.yml build

# Run specific reviews
docker-compose -f docker-compose.review.yml --profile code up review-code
docker-compose -f docker-compose.review.yml --profile tests up review-tests
docker-compose -f docker-compose.review.yml --profile arch up review-architecture

# Interactive shell
docker-compose -f docker-compose.review.yml --profile shell run review-shell
```

---

## Available Reviews

### 1. Code Quality Review
**Command:** `docker-compose -f docker-compose.review.yml --profile code up review-code`

**Analyzes:**
- Code cleanliness and readability
- Design pattern usage
- Error handling robustness
- Documentation completeness
- Maintainability

**Output:** Code quality score + recommendations

---

### 2. Test Coverage Review
**Command:** `docker-compose -f docker-compose.review.yml --profile tests up review-tests`

**Analyzes:**
- Which modules have tests
- Which modules lack tests
- Test quality (unit vs integration)
- Edge case coverage
- Mock usage

**Output:** Coverage estimate + priority areas

---

### 3. Architecture Review
**Command:** `docker-compose -f docker-compose.review.yml --profile arch up review-architecture`

**Analyzes:**
- Separation of concerns
- Modularity and reusability
- Extensibility (plugins, providers)
- Consistency (naming, patterns)
- Documentation quality

**Output:** Architecture score + refactoring suggestions

---

## Review Files

Each review is an AICL configuration:

- `review-code-quality.aicl` - Code quality analysis
- `review-tests.aicl` - Test coverage analysis  
- `review-architecture.aicl` - Architecture evaluation

**They use AICL to analyze AICL!**

---

## Customization

### Target Different Modules

```bash
# Review specific directory
docker-compose -f docker-compose.review.yml run review-shell
# Inside container:
export TARGET_DIR="cli"
aicl run review-code-quality.aicl
```

### Change Review Focus

Edit the `.aicl` files:
```hcl
variable "review_focus" {
  default = "error_handling"  # or "performance", "security", etc.
}
```

---

## Results

Results are saved to `./results/` directory:
```
results/
├── code-quality-report.md
├── test-coverage-report.md
└── architecture-report.md
```

---

## Example Workflow

```bash
cd /Users/zacelston/code/tofu-aicl/experiments/self-review

# 1. Build image once
docker-compose -f docker-compose.review.yml build

# 2. Run all reviews
docker-compose -f docker-compose.review.yml --profile code up
docker-compose -f docker-compose.review.yml --profile tests up
docker-compose -f docker-compose.review.yml --profile arch up

# 3. Review results
cat results/*.md

# 4. Interactive exploration
docker-compose -f docker-compose.review.yml --profile shell run review-shell
```

---

## Why Dockerized?

**Benefits:**
- ✅ Isolated environment (no conflicts)
- ✅ Reproducible (same results every time)
- ✅ Clean (no local dependency pollution)
- ✅ Shareable (others can run same reviews)
- ✅ Secure (sandboxed execution)

**Simple:**
```
Docker → AICL → Loads AICL Code → LLM Reviews → Report
```

---

## Architecture

```
┌─────────────────────────────────────┐
│     Docker Container                │
│  ┌───────────────────────────────┐  │
│  │   AICL Engine                 │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  file_loader provider   │  │  │
│  │  │  Loads: src/aicl/*.py   │  │  │
│  │  └─────────────────────────┘  │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  naga provider          │  │  │
│  │  │  Analyzes code          │  │  │
│  │  └─────────────────────────┘  │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  Output: Review Report  │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

The tool reviews itself! 🔄
