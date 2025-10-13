# AICL CLI Specifications

**Purpose:** Formal specifications for AI model implementation and comparison

## Files

| Spec | Component | Points |
|------|-----------|--------|
| `00-architecture.md` | Overall structure | - |
| `01-config.md` | Configuration | 30 |
| `02-logging.md` | Logging | 20 |
| `03-docker-runner.md` | Docker execution | 30 |
| `04-local-runner.md` | Local execution | 20 |
| `05-run-command.md` | Run orchestration | 15 |
| `06-output-utils.md` | Rich formatting | 20 |
| `07-entry-point.md` | Main CLI | 30 |

**Total:** 165 points

## Using These Specs

1. Read `00-architecture.md` first
2. Implement each component independently
3. Follow interface specs exactly
4. Run tests after each file
5. Grade using point system

## AI Model Comparison

Test different models:
```bash
# Implementation
claude "Implement from docs/spec/"
gpt4 "Implement from docs/spec/"

# Grading
pytest tests/spec/ --grade
```

Compare:
- Functionality (does it work?)
- Compliance (follows spec?)
- Quality (clean code?)
- Speed (time to complete?)
