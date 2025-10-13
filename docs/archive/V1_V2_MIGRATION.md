# v1 to v2 Migration Guide

## Directory Structure

### v1 (Current - Legacy)
```
src/aicl/
├── core/           # Core engine (reused in v2)
├── experiment_db.py # OLD: Tightly coupled SQLite
└── ...

run_rag_graded_matrix.py  # v1 experiment runner
llm_grader.py             # v1 grading logic
```

### v2 (New - Modular)
```
v2/
├── storage/        # NEW: Storage abstraction
│   ├── base.py
│   ├── memory.py
│   ├── sqlite_adapter.py
│   └── postgres_adapter.py
│
├── api/            # NEW: Shared logic
│   ├── experiments.py
│   └── grading.py
│
├── cli/            # NEW: Free CLI tool
│   └── main.py
│
└── schemas/        # NEW: DB schemas for users
    └── sqlite_schema.sql

src/aicl/
├── core/           # UNCHANGED: Core engine
├── experiment_db.py # COMPATIBILITY: Wraps v2
└── ...
```

## What's Where

### Core Engine (Unchanged)
These components stay in `src/aicl/` and work with both v1 and v2:
- `core/engine.py` - Orchestration
- `parser.py` - HCL parsing
- `evaluator.py` - Expression evaluation
- `executor.py` - Resource provisioning
- `planner.py` - Dependency resolution
- `state/manager.py` - State management

### Storage (v2 Only)
All storage logic moves to `v2/storage/`:
- `v2/storage/base.py` - Abstract interface
- `v2/storage/memory.py` - In-memory (free CLI)
- `v2/storage/sqlite_adapter.py` - SQLite (user setup)
- `v2/storage/postgres_adapter.py` - PostgreSQL (web)

### API Layer (v2 Only)
Shared experiment logic in `v2/api/`:
- `v2/api/experiments.py` - Experiment runner
- `v2/api/grading.py` - LLM-as-Judge

### CLI (v2 Only)
Free CLI tool in `v2/cli/`:
- `v2/cli/main.py` - Entry point
- `v2/cli/commands/` - CLI commands

### Backward Compatibility
- `src/aicl/experiment_db.py` - Wraps v2 storage, shows deprecation warning

## Code Migration

### Before (v1)
```python
from src.aicl.experiment_db import ExperimentDB

db = ExperimentDB()
db.save_experiment(
    experiment_id="test_1",
    config={...},
    results={...},
    quality={...}
)
```

### After (v2 - In-Memory)
```python
from v2.storage import InMemoryStorage

storage = InMemoryStorage()
storage.save_experiment(
    experiment_id="test_1",
    config={...},
    results={...},
    quality={...}
)
```

### After (v2 - SQLite)
```python
from v2.storage import SQLiteStorage

storage = SQLiteStorage("experiments/results.db")
storage.save_experiment(
    experiment_id="test_1",
    config={...},
    results={...},
    quality={...}
)
```

## Import Paths

### v1 Imports (Legacy)
```python
from src.aicl.experiment_db import ExperimentDB  # ⚠️ Deprecated
```

### v2 Imports (New)
```python
# Storage
from v2.storage import InMemoryStorage, SQLiteStorage, PostgreSQLStorage
from v2.storage import ExperimentStorage, ExperimentIdentifier, StorageResult

# API
from v2.api import ExperimentRunner
from v2.api import LLMGrader

# CLI
from v2.cli import main as cli_main
```

## File Location Reference

| Component | v1 Location | v2 Location | Status |
|-----------|-------------|-------------|--------|
| Core Engine | `src/aicl/core/` | `src/aicl/core/` | Unchanged |
| Storage | `src/aicl/experiment_db.py` | `v2/storage/` | Refactored |
| Experiment Runner | `run_rag_graded_matrix.py` | `v2/api/experiments.py` | Moved |
| LLM Grading | `llm_grader.py` | `v2/api/grading.py` | Moved |
| CLI | N/A | `v2/cli/` | New |
| Schemas | N/A | `v2/schemas/` | New |
| Providers | `providers/` | `providers/` | Unchanged |

## Backward Compatibility

### v1 Code Still Works
The old `experiment_db.py` now wraps v2 storage:

```python
# This still works (with deprecation warning)
from src.aicl.experiment_db import ExperimentDB
db = ExperimentDB()

# Behind the scenes it uses:
from v2.storage import SQLiteStorage
storage = SQLiteStorage()
```

### Deprecation Timeline
- **v2.0.0-alpha**: Both v1 and v2 available
- **v2.0.0-beta**: v1 shows warnings, v2 recommended
- **v2.0.0**: v1 deprecated, v2 default
- **v3.0.0**: v1 removed completely

## Migration Checklist

### Phase 1: Setup (Done ✅)
- [x] Create v2/ directory structure
- [x] Move storage abstraction to v2/
- [x] Create backward compatibility wrapper
- [x] Document v1/v2 differences

### Phase 2: API Layer (Next)
- [ ] Move experiment logic to v2/api/
- [ ] Move grading logic to v2/api/
- [ ] Update experiment runners to use v2
- [ ] Add tests for v2 API

### Phase 3: CLI Tool
- [ ] Build v2/cli/ command structure
- [ ] Implement schema export
- [ ] Add setup wizard
- [ ] Package as standalone tool

### Phase 4: Provider Connectors
- [ ] Azure OpenAI connector
- [ ] AWS Bedrock connector
- [ ] Update provider registry

### Phase 5: Web Tier
- [ ] PostgreSQL adapter
- [ ] Web API endpoints
- [ ] Authentication layer
- [ ] Frontend UI

## Testing Strategy

### Test Both Versions
```python
# Test v1 compatibility
def test_v1_compatibility():
    from src.aicl.experiment_db import ExperimentDB
    db = ExperimentDB()
    # Should work with deprecation warning

# Test v2 storage
def test_v2_storage():
    from v2.storage import InMemoryStorage
    storage = InMemoryStorage()
    # Should work without warnings
```

### Regression Tests
Ensure v1 code continues working during migration:
```bash
# Run existing tests
pytest tests/ -v

# Should pass with deprecation warnings
```

## FAQ

**Q: Do I need to change my existing code?**
A: No, v1 code continues to work with deprecation warnings.

**Q: When should I migrate to v2?**
A: Migrate when you need:
- In-memory storage (no DB setup)
- Multiple storage backends
- Better testability
- CLI/Web separation

**Q: Can I use both v1 and v2 together?**
A: Yes, they can coexist. v1 actually uses v2 under the hood.

**Q: What about my existing database?**
A: v2 SQLiteStorage is compatible with v1 databases. Just change the import.

**Q: Where do providers go?**
A: Providers stay in `providers/` and work with both v1 and v2.
