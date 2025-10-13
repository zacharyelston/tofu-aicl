# AICL v2 Architecture

## Overview

v2 is a complete architectural refactor to support:
- **Free CLI**: No database required (in-memory storage by default)
- **Paid Web**: Persistent storage with PostgreSQL
- **User Setup**: Optional SQLite for free users who want persistence

## Directory Structure

```
v2/
├── storage/              # Storage abstraction layer
│   ├── base.py          # Abstract interface
│   ├── memory.py        # In-memory (FREE CLI default)
│   ├── sqlite_adapter.py # SQLite (user sets up)
│   └── postgres_adapter.py # PostgreSQL (WEB tier)
│
├── api/                  # Shared experiment logic
│   ├── experiments.py   # Experiment runner
│   └── grading.py       # LLM-as-Judge
│
├── cli/                  # Free CLI tool
│   ├── main.py          # Entry point
│   └── commands/        # CLI commands
│
└── schemas/             # Database schemas
    ├── sqlite_schema.sql
    └── migrations/
```

## Key Differences from v1

### v1 (Current)
- ❌ Tightly coupled to SQLite
- ❌ Always requires database setup
- ❌ Hard to test (no mocking)
- ❌ Can't support different storage backends

### v2 (New)
- ✅ Storage abstraction layer
- ✅ In-memory default (no setup)
- ✅ Pluggable backends (SQLite, PostgreSQL)
- ✅ Easy to test (mock storage)
- ✅ Supports CLI and Web tiers

## Usage

### Free CLI (In-Memory)
```python
from v2.storage import InMemoryStorage
from v2.api import ExperimentRunner

# Default: session-only storage
storage = InMemoryStorage()
runner = ExperimentRunner(storage=storage)
runner.run_experiments([...])
```

### Free CLI (User's SQLite)
```python
from v2.storage import SQLiteStorage
from v2.api import ExperimentRunner

# User sets up their own DB
storage = SQLiteStorage("my_experiments.db")
runner = ExperimentRunner(storage=storage)
runner.run_experiments([...])
```

### Paid Web (PostgreSQL)
```python
from v2.storage import PostgreSQLStorage
from v2.api import ExperimentRunner

# Managed PostgreSQL for web tier
storage = PostgreSQLStorage(DATABASE_URL)
runner = ExperimentRunner(storage=storage)
```

## Migration from v1

### Option 1: Keep Using v1
```python
# Old code continues to work
from src.aicl.experiment_db import ExperimentDB
db = ExperimentDB()  # Shows deprecation warning
```

### Option 2: Migrate to v2
```python
# New storage-agnostic approach
from v2.storage import SQLiteStorage
storage = SQLiteStorage("experiments/results.db")
storage.save_experiment(...)
```

## Business Model Support

### Free Tier
- Core AICL engine (unchanged in src/aicl/)
- v2 in-memory storage (default)
- Schema export for user setup
- All providers (OpenAI, Naga, Ragie, etc.)

### Paid Tier
- Web UI + API
- v2 PostgreSQL storage
- Multi-user support
- Advanced analytics

## Development Status

- ✅ Storage abstraction (base, memory, sqlite)
- ⏳ API layer (experiments, grading)
- ⏳ CLI tool
- ⏳ Schema export utilities
- ⏳ PostgreSQL adapter
- ⏳ Web application
