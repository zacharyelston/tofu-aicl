# AICL CLI Architecture Specification

**Version:** 2.0.0  
**Purpose:** Define the modular architecture for AI-powered CLI tool  
**For:** AI model implementation and comparison

## Overview

A command-line interface for declarative AI infrastructure management with:
- Modular architecture (9+ small focused files)
- Configuration management (Dynaconf)
- Multiple execution modes (local/Docker)
- Beautiful output (Rich)
- Structured logging (Loguru)

## Directory Structure

```
aicl_modular                 # Entry point (80-100 lines)
cli/
├── __init__.py              # Package marker
├── config.py                # Configuration (50 lines)
├── logging_setup.py         # Logging (30 lines)
├── commands/                # Command implementations
│   ├── __init__.py
│   ├── run.py              # Run command (40 lines)
│   ├── validate.py         # Validation (35 lines)
│   └── state.py            # State management (60 lines)
├── runners/                 # Execution strategies
│   ├── __init__.py
│   ├── docker.py           # Docker runner (70 lines)
│   └── local.py            # Local runner (45 lines)
└── utils/                   # Shared utilities
    ├── __init__.py
    └── output.py           # Rich formatting (50 lines)
```

## Architectural Principles

### 1. Single Responsibility
Each file does ONE thing:
- `config.py` - Only configuration loading
- `docker.py` - Only Docker execution
- `validate.py` - Only validation logic

### 2. Small Files
- Maximum 100 lines per file
- Average 45 lines per file
- Easy to understand in one screen

### 3. Clear Structure by Placement
- `commands/` - User-facing commands
- `runners/` - Execution strategies
- `utils/` - Reusable helpers

### 4. Easy to Test
- Each file independently importable
- Minimal dependencies between modules
- Clear interfaces

## Key Dependencies

```python
typer>=0.9.0           # CLI framework
dynaconf>=3.2.0        # Configuration
rich>=13.0.0           # Terminal output
loguru>=0.7.0          # Logging
pydantic>=2.0.0        # Validation
```

## Success Criteria

Implementation must:
1. ✅ Pass all unit tests (see `test_criteria.md`)
2. ✅ Each file < 100 lines
3. ✅ Imports work independently
4. ✅ Configuration precedence correct (CLI > ENV > File > Defaults)
5. ✅ All commands execute without errors

## Grading Rubric

| Criterion | Weight | Points |
|-----------|--------|--------|
| Modular structure | 20% | 0-20 |
| File size compliance | 15% | 0-15 |
| Functionality | 30% | 0-30 |
| Code quality | 20% | 0-20 |
| Error handling | 15% | 0-15 |

**Total:** 100 points

## Implementation Order

1. Configuration (`config.py`)
2. Logging (`logging_setup.py`)
3. Output utilities (`utils/output.py`)
4. Runners (`runners/docker.py`, `runners/local.py`)
5. Commands (`commands/*.py`)
6. Entry point (`aicl_modular`)
7. Integration testing

## Reference Implementation

See: `/Users/zacelston/code/tofu-aicl/cli/`
