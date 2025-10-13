# Architecture Refactor Plan - CLI/Web Split

## Business Model Requirements

### Free Tier (CLI)
- ✅ Core AICL engine (HCL parsing, execution, providers)
- ✅ API layer for running experiments
- ❌ **No database included** (but schema + stub data provided)
- ✅ In-memory result storage (session only)
- ✅ Users can set up their own SQLite using provided schema

### Paid Tier (Web)
- ✅ Full web UI + API
- ✅ Persistent database (PostgreSQL/SQLite)
- ✅ Multi-user support
- ✅ Advanced analytics and dashboards

## Current Architecture Issues

### ❌ Problems
1. **Tight Coupling**: `experiment_db.py` directly imports SQLite, assumes DB exists
2. **No Abstraction**: Experiment runners directly instantiate `ExperimentDB()`
3. **Mixed Concerns**: Storage logic mixed with experiment logic
4. **Hard to Test**: Can't easily mock storage for tests
5. **Not Pluggable**: Can't swap storage backends

### Current Structure
```
src/aicl/
├── core/engine.py          # Core execution (good - reusable)
├── experiment_db.py        # ❌ Tightly coupled to SQLite
├── executor.py, parser.py  # Core components (good)
└── state/manager.py        # State persistence (good)

Root level:
├── run_rag_graded_matrix.py  # ❌ Directly uses ExperimentDB
├── llm_grader.py             # Judge logic (good - reusable)
└── run.py                    # Entry point (good)
```

## Proposed Architecture

### ✅ New Structure
```
src/aicl/
├── core/                    # Core engine (FREE - no changes)
│   ├── engine.py           # Orchestration engine
│   └── __init__.py
│
├── storage/                 # NEW: Storage abstraction
│   ├── __init__.py
│   ├── base.py             # Abstract storage interface
│   ├── memory.py           # In-memory storage (FREE tier)
│   ├── sqlite_adapter.py   # SQLite adapter (user sets up)
│   ├── postgres_adapter.py # PostgreSQL (WEB tier)
│   └── schema.py           # Schema export utilities
│
├── api/                     # NEW: Shared API layer
│   ├── __init__.py
│   ├── experiments.py      # Experiment running logic
│   └── grading.py          # LLM-as-Judge logic
│
├── state/                   # Existing (no changes)
│   └── manager.py
│
└── ... (executor, parser, etc - no changes)

cli/                         # NEW: Free CLI tool
├── __init__.py
├── main.py                 # CLI entry point
├── commands/               # CLI commands
│   ├── run.py             # Run experiments
│   ├── export.py          # Export results
│   └── schema.py          # Export DB schema
└── config.py              # CLI configuration

web/                        # FUTURE: Web tier
├── app.py                 # FastAPI/Flask application
├── api/                   # REST API endpoints
│   ├── experiments.py
│   ├── models.py
│   └── analytics.py
├── ui/                    # Frontend (React/Vue)
└── config.py              # Web configuration

providers/                  # No changes
└── ... (existing providers)

scripts/                    # NEW: Migration scripts
├── export_schema.py       # Export DB schema for users
└── generate_stubs.py      # Generate stub data
```

### Storage Abstraction Layer

#### Base Interface (`storage/base.py`)
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class ExperimentStorage(ABC):
    """Abstract interface for experiment storage"""
    
    @abstractmethod
    def save_experiment(self, experiment_id: str, config: Dict, 
                       results: Dict, quality: Optional[Dict] = None) -> int:
        """Save experiment data"""
        pass
    
    @abstractmethod
    def get_experiment(self, experiment_id: str) -> Optional[Dict]:
        """Retrieve experiment by ID"""
        pass
    
    @abstractmethod
    def get_all_experiments(self, limit: int = 100) -> List[Dict]:
        """Get all experiments"""
        pass
    
    @abstractmethod
    def get_best_configs(self, min_quality: float, 
                        max_cost: float, limit: int) -> List[Dict]:
        """Find best configurations"""
        pass
    
    @abstractmethod
    def export_schema(self, output_path: str):
        """Export schema definition"""
        pass
```

#### In-Memory Storage (`storage/memory.py`) - FREE
```python
class InMemoryStorage(ExperimentStorage):
    """In-memory storage for CLI (session only)"""
    
    def __init__(self):
        self.experiments = {}
        self.configs = {}
        self.results = {}
        self.quality_scores = {}
    
    # Implements all abstract methods
    # Data only persists during session
```

#### SQLite Adapter (`storage/sqlite_adapter.py`) - User Sets Up
```python
class SQLiteStorage(ExperimentStorage):
    """SQLite storage adapter (user provides db_path)"""
    
    def __init__(self, db_path: str):
        if not os.path.exists(db_path):
            raise ValueError(
                "Database not found. Run 'aicl setup-db' to create it."
            )
        self.db_path = db_path
        # Connect to existing DB
    
    # Implements all abstract methods
    # Uses existing experiment_db.py logic
```

#### Schema Export (`storage/schema.py`)
```python
def export_schema(output_format: str = "sql"):
    """Export database schema for user setup"""
    
    if output_format == "sql":
        return SQLITE_SCHEMA_SQL
    elif output_format == "python":
        return ALEMBIC_MIGRATION
    elif output_format == "stub":
        return generate_stub_data()
```

### API Layer (`api/experiments.py`)

```python
from src.aicl.storage.base import ExperimentStorage
from src.aicl.storage.memory import InMemoryStorage

class ExperimentRunner:
    """Shared experiment running logic"""
    
    def __init__(self, storage: ExperimentStorage = None):
        # Default to in-memory for CLI
        self.storage = storage or InMemoryStorage()
    
    def run_experiments(self, configs: List[str], **kwargs):
        """Run experiments and store results"""
        for config in configs:
            # Run experiment
            results = self._execute_experiment(config)
            
            # Store results
            self.storage.save_experiment(...)
        
        return self.storage.get_all_experiments()
```

### CLI Tool (`cli/main.py`)

```python
import argparse
from src.aicl.api.experiments import ExperimentRunner
from src.aicl.storage.memory import InMemoryStorage
from src.aicl.storage.sqlite_adapter import SQLiteStorage

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', help='Path to SQLite database (optional)')
    parser.add_argument('--export-schema', help='Export DB schema')
    
    args = parser.parse_args()
    
    # User can optionally provide their own DB
    if args.db:
        storage = SQLiteStorage(args.db)
    else:
        storage = InMemoryStorage()
        print("💡 Using in-memory storage (session only)")
        print("   To persist results, set up SQLite: aicl setup-db")
    
    runner = ExperimentRunner(storage=storage)
    runner.run_experiments(...)
```

## Migration Plan

### Phase 1: Storage Abstraction (Week 1)
1. ✅ Create `storage/` module with base interface
2. ✅ Implement `InMemoryStorage` for free CLI
3. ✅ Refactor existing `experiment_db.py` → `SQLiteStorage`
4. ✅ Create schema export utilities

### Phase 2: API Layer (Week 2)
1. ✅ Extract experiment logic from `run_rag_graded_matrix.py`
2. ✅ Create `api/experiments.py` with storage injection
3. ✅ Move LLM grading to `api/grading.py`
4. ✅ Update all experiment runners to use new API

### Phase 3: CLI Tool (Week 2-3)
1. ✅ Create `cli/` module with commands
2. ✅ Implement schema export command
3. ✅ Add setup wizard for DB configuration
4. ✅ Package as standalone CLI tool

### Phase 4: Provider Connectors (Week 3-4)
1. ✅ Build Azure OpenAI connector
2. ✅ Build AWS Bedrock connector
3. ✅ Update provider registry
4. ✅ Add to test suites

### Phase 5: Web Preparation (Week 4+)
1. ✅ Design web API endpoints
2. ✅ Set up FastAPI/Flask scaffold
3. ✅ Implement PostgreSQL adapter
4. ✅ Build authentication layer

## File Organization

### What Stays Free (CLI)
```
src/aicl/core/        # Core engine
src/aicl/state/       # State management
src/aicl/api/         # Shared API layer
src/aicl/storage/     # Storage abstractions
  ├── base.py        # Interface (all tiers)
  ├── memory.py      # Free tier
  ├── schema.py      # Schema export (free)
providers/            # All providers
cli/                  # CLI tool
```

### What Requires Setup (User)
```
src/aicl/storage/
  └── sqlite_adapter.py    # User runs setup command
  
schemas/                   # Exported schemas
  ├── sqlite_schema.sql   # SQL DDL
  ├── stub_data.json      # Sample data
  └── README.md           # Setup instructions
```

### What's Paid (Web)
```
web/                       # Full web application
src/aicl/storage/
  └── postgres_adapter.py  # PostgreSQL for web
```

## User Experience

### Free Tier (CLI)
```bash
# Default: in-memory storage
$ aicl run experiments/*.aicl
✅ Ran 5 experiments (in-memory, session only)

# Optional: Set up SQLite
$ aicl setup-db
📁 Created experiments/results.db
📄 Schema: schemas/sqlite_schema.sql
💡 Use --db flag to persist results

$ aicl run experiments/*.aicl --db experiments/results.db
✅ Ran 5 experiments (saved to SQLite)

# Export schema for custom setup
$ aicl export-schema --format sql > my_schema.sql
```

### Paid Tier (Web)
```bash
# Web app with PostgreSQL
$ aicl-web serve
🚀 Starting web server on http://localhost:8000
🗄️  Connected to PostgreSQL
👤 Multi-user support enabled
📊 Analytics dashboard available
```

## Benefits

### ✅ Clean Separation
- Core engine is storage-agnostic
- Easy to test (mock storage)
- Pluggable backends

### ✅ Business Model Support
- Free: CLI + in-memory + schema export
- Paid: Web + persistent DB + analytics

### ✅ Future-Proof
- Easy to add new storage backends
- Web tier builds on same API
- Provider ecosystem unchanged

### ✅ User-Friendly
- Free users get full engine + schema
- Clear upgrade path to paid tier
- Self-hosted option available

## Next Steps

1. **Get Approval**: Review this architecture plan
2. **Phase 1**: Implement storage abstraction
3. **Phase 2**: Refactor experiment runners
4. **Phase 3**: Build CLI tool
5. **Phase 4**: Add Azure/Bedrock providers
6. **Phase 5**: Prepare for web tier

## Open Questions

1. **CLI Packaging**: PyPI package or standalone binary?
2. **Schema Versioning**: Alembic migrations or simple SQL?
3. **Web Framework**: FastAPI or Flask?
4. **Frontend**: React, Vue, or server-side templates?
5. **Authentication**: OAuth, API keys, or both?
