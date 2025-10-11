# Architecture Refactor - Implementation Guide

## Executive Summary

**Goal**: Separate storage from core engine to support CLI (free, DB-optional) and Web (paid, persistent DB) tiers.

**Architect Approval**: ✅ Approved with targeted adjustments to storage interface and migration strategy.

## Refined Storage Interface

### Base Interface (`storage/base.py`)

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class StorageResult(Enum):
    """Result of storage operation"""
    CREATED = "created"
    UPDATED = "updated"
    ERROR = "error"

@dataclass
class ExperimentIdentifier:
    """Stable experiment identifier across all backends"""
    experiment_id: str
    created_at: str
    version: int = 1

class ExperimentStorage(ABC):
    """Abstract interface for experiment storage"""
    
    @abstractmethod
    def save_metadata(self, experiment_id: str, config_file: str, 
                     description: str, timestamp: str) -> ExperimentIdentifier:
        """Save experiment metadata (idempotent)"""
        pass
    
    @abstractmethod
    def save_configuration(self, experiment_id: str, config: Dict[str, Any]) -> StorageResult:
        """Save experiment configuration (idempotent upsert)"""
        pass
    
    @abstractmethod
    def save_results(self, experiment_id: str, results: Dict[str, Any]) -> StorageResult:
        """Save performance metrics (idempotent upsert)"""
        pass
    
    @abstractmethod
    def save_quality_scores(self, experiment_id: str, quality: Dict[str, Any]) -> StorageResult:
        """Save quality evaluation (idempotent upsert)"""
        pass
    
    # Convenience method (calls above in sequence)
    def save_experiment(self, experiment_id: str, config: Dict, 
                       results: Dict, quality: Optional[Dict] = None) -> ExperimentIdentifier:
        """Save complete experiment (calls individual save methods)"""
        exp_id = self.save_metadata(experiment_id, config.get('config_file', ''), 
                                    config.get('description', ''), 
                                    results.get('timestamp', ''))
        self.save_configuration(experiment_id, config)
        self.save_results(experiment_id, results)
        if quality:
            self.save_quality_scores(experiment_id, quality)
        return exp_id
    
    @abstractmethod
    def get_experiment(self, experiment_id: str) -> Optional[Dict]:
        """Retrieve complete experiment by ID"""
        pass
    
    @abstractmethod
    def get_all_experiments(self, limit: int = 100) -> List[Dict]:
        """Get all experiments (most recent first)"""
        pass
    
    @abstractmethod
    def get_best_configs(self, min_quality: float, max_cost: float, 
                        limit: int = 10) -> List[Dict]:
        """Find best configurations meeting criteria"""
        pass
    
    @abstractmethod
    def get_schema_version(self) -> str:
        """Get storage schema version"""
        pass
    
    @abstractmethod
    def export_data(self, format: str = "json") -> str:
        """Export all data in specified format"""
        pass
```

### In-Memory Storage (`storage/memory.py`)

```python
from datetime import datetime
from .base import ExperimentStorage, ExperimentIdentifier, StorageResult

class InMemoryStorage(ExperimentStorage):
    """In-memory storage for free CLI (session only)"""
    
    SCHEMA_VERSION = "1.0.0"
    
    def __init__(self):
        self.experiments = {}  # experiment_id -> metadata
        self.configs = {}      # experiment_id -> config
        self.results = {}      # experiment_id -> results
        self.quality = {}      # experiment_id -> quality
        
    def save_metadata(self, experiment_id: str, config_file: str, 
                     description: str, timestamp: str) -> ExperimentIdentifier:
        self.experiments[experiment_id] = {
            'experiment_id': experiment_id,
            'config_file': config_file,
            'description': description,
            'timestamp': timestamp or datetime.now().isoformat()
        }
        return ExperimentIdentifier(
            experiment_id=experiment_id,
            created_at=self.experiments[experiment_id]['timestamp'],
            version=1
        )
    
    def save_configuration(self, experiment_id: str, config: Dict) -> StorageResult:
        if experiment_id in self.configs:
            self.configs[experiment_id].update(config)
            return StorageResult.UPDATED
        else:
            self.configs[experiment_id] = config.copy()
            return StorageResult.CREATED
    
    # ... implement other methods
    
    def get_schema_version(self) -> str:
        return self.SCHEMA_VERSION
    
    def export_data(self, format: str = "json") -> str:
        if format == "json":
            return json.dumps({
                'schema_version': self.SCHEMA_VERSION,
                'experiments': self.experiments,
                'configurations': self.configs,
                'results': self.results,
                'quality_scores': self.quality
            }, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
```

### SQLite Adapter (`storage/sqlite_adapter.py`)

```python
from .base import ExperimentStorage, ExperimentIdentifier, StorageResult

class SQLiteStorage(ExperimentStorage):
    """SQLite storage adapter (user provides db_path)"""
    
    SCHEMA_VERSION = "1.0.0"
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_exists()
        self._check_schema_version()
    
    def _ensure_db_exists(self):
        """Check if DB exists, provide helpful error if not"""
        if not os.path.exists(self.db_path):
            raise ValueError(
                f"Database not found: {self.db_path}\n"
                f"To set up SQLite:\n"
                f"  1. Run: aicl export-schema --format sql > schema.sql\n"
                f"  2. Run: sqlite3 {self.db_path} < schema.sql\n"
                f"  3. Or use: aicl setup-db --path {self.db_path}"
            )
    
    def _check_schema_version(self):
        """Verify schema version matches"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if not row:
                raise ValueError("Schema version not found. Run migrations.")
            if row[0] != self.SCHEMA_VERSION:
                raise ValueError(
                    f"Schema version mismatch: DB={row[0]}, Code={self.SCHEMA_VERSION}\n"
                    f"Run migrations: aicl migrate"
                )
    
    def save_metadata(self, experiment_id: str, config_file: str, 
                     description: str, timestamp: str) -> ExperimentIdentifier:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO experiments 
                (experiment_id, config_file, description, timestamp)
                VALUES (?, ?, ?, ?)
            """, (experiment_id, config_file, description, timestamp))
            
            # Return stable identifier
            cursor.execute("""
                SELECT experiment_id, timestamp, version 
                FROM experiments WHERE experiment_id = ?
            """, (experiment_id,))
            row = cursor.fetchone()
            
            return ExperimentIdentifier(
                experiment_id=row[0],
                created_at=row[1],
                version=row[2] or 1
            )
    
    # ... implement other methods similar to current experiment_db.py
```

## Compatibility Layer

### Shim for Backward Compatibility (`storage/compat.py`)

```python
"""
Compatibility wrapper for existing code using ExperimentDB
Allows gradual migration without breaking current scripts
"""

from .sqlite_adapter import SQLiteStorage

class ExperimentDB:
    """
    DEPRECATED: Use SQLiteStorage directly
    This class provides backward compatibility during migration
    """
    
    def __init__(self, db_path: str = "experiments/results.db"):
        import warnings
        warnings.warn(
            "ExperimentDB is deprecated. Use SQLiteStorage instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self._storage = SQLiteStorage(db_path)
    
    def save_experiment(self, experiment_id, config, results, quality=None):
        """Delegate to new storage interface"""
        return self._storage.save_experiment(experiment_id, config, results, quality)
    
    # Delegate all methods to storage
    def __getattr__(self, name):
        return getattr(self._storage, name)
```

## Schema Versioning

### Schema Version Table
```sql
CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Initial version
INSERT INTO schema_version (version, description) 
VALUES ('1.0.0', 'Initial schema with experiments, configurations, results, quality_scores');
```

### Migration Script (`scripts/migrate_db.py`)
```python
"""Database migration tool"""

import sqlite3
from pathlib import Path

MIGRATIONS = {
    '1.0.0': """
        CREATE TABLE experiments (...);
        CREATE TABLE configurations (...);
        CREATE TABLE results (...);
        CREATE TABLE quality_scores (...);
        CREATE INDEX idx_config_exp_id ON configurations(experiment_id);
        -- etc.
    """,
    '1.1.0': """
        ALTER TABLE results ADD COLUMN end_to_end_ms REAL;
        -- Future migrations
    """
}

def migrate(db_path: str, target_version: str = None):
    conn = sqlite3.connect(db_path)
    current = get_schema_version(conn)
    
    # Apply migrations in order
    for version in sorted(MIGRATIONS.keys()):
        if version > current:
            print(f"Applying migration {version}...")
            conn.executescript(MIGRATIONS[version])
            record_migration(conn, version)
            if target_version and version == target_version:
                break
```

## Migration Plan - Detailed

### Phase 1: Storage Abstraction (Week 1)

**Day 1-2: Create Base Interface**
```bash
# Create storage module
mkdir -p src/aicl/storage
touch src/aicl/storage/{__init__.py,base.py,memory.py}

# Implement abstract interface
# - ExperimentStorage base class
# - StorageResult enum
# - ExperimentIdentifier dataclass
```

**Day 3-4: Refactor ExperimentDB → SQLiteStorage**
```bash
# Move and refactor
mv src/aicl/experiment_db.py src/aicl/storage/sqlite_adapter.py

# Create compatibility shim
touch src/aicl/storage/compat.py

# Update imports in experiment_db.py
cat > src/aicl/experiment_db.py << EOF
# DEPRECATED: Import from new location
from .storage.compat import ExperimentDB
EOF
```

**Day 5: Testing & Schema Export**
```bash
# Add regression tests
pytest tests/storage/ -v

# Create schema export
python scripts/export_schema.py --format sql > schemas/sqlite_schema.sql
python scripts/export_schema.py --format stub > schemas/stub_data.json
```

### Phase 2: API Layer (Week 2)

**Refactor Experiment Runners**
```python
# Before (run_rag_graded_matrix.py)
from src.aicl.experiment_db import ExperimentDB
db = ExperimentDB()

# After
from src.aicl.api.experiments import ExperimentRunner
from src.aicl.storage.memory import InMemoryStorage

runner = ExperimentRunner(storage=InMemoryStorage())
# Or with user's DB:
# runner = ExperimentRunner(storage=SQLiteStorage("my.db"))
```

### Phase 3: CLI Tool (Week 2-3)

**CLI Structure**
```bash
cli/
├── __init__.py
├── main.py              # Entry point
├── commands/
│   ├── run.py          # Run experiments
│   ├── export.py       # Export results/schema
│   ├── setup.py        # Setup database
│   └── migrate.py      # Run migrations
└── config.py           # CLI configuration

# Entry point (cli/main.py)
def main():
    parser = argparse.ArgumentParser(prog='aicl')
    subparsers = parser.add_subparsers()
    
    # aicl run
    run_parser = subparsers.add_parser('run')
    run_parser.add_argument('configs', nargs='+')
    run_parser.add_argument('--db', help='SQLite database path')
    
    # aicl setup-db
    setup_parser = subparsers.add_parser('setup-db')
    setup_parser.add_argument('--path', default='experiments/results.db')
    
    # aicl export-schema
    export_parser = subparsers.add_parser('export-schema')
    export_parser.add_argument('--format', choices=['sql', 'python', 'stub'])
```

### Phase 4: Provider Connectors (Week 3-4)

**Azure OpenAI Provider**
```python
# providers/azure_openai/server.py
# Similar to existing OpenAI provider
# Uses Azure-specific endpoint format
```

**AWS Bedrock Provider**
```python
# providers/bedrock/server.py
# Integrates with AWS Bedrock API
# Supports Claude, Titan, etc.
```

### Phase 5: Web Preparation (Week 4+)

**FastAPI Application**
```python
# web/app.py
from fastapi import FastAPI
from src.aicl.storage.postgres_adapter import PostgreSQLStorage

app = FastAPI()
storage = PostgreSQLStorage(DATABASE_URL)

@app.post("/api/experiments")
async def run_experiment(config: dict):
    runner = ExperimentRunner(storage=storage)
    return runner.run_experiments([config])
```

## Directory Structure After Refactor

```
src/aicl/
├── core/                   # Core engine (no changes)
│   └── engine.py
│
├── storage/                # NEW: Storage abstraction
│   ├── __init__.py
│   ├── base.py            # Abstract interface
│   ├── memory.py          # In-memory (free CLI)
│   ├── sqlite_adapter.py  # SQLite adapter
│   ├── postgres_adapter.py # PostgreSQL (web)
│   └── compat.py          # Backward compatibility
│
├── api/                    # NEW: Shared API layer
│   ├── __init__.py
│   ├── experiments.py     # Experiment runner
│   └── grading.py         # LLM-as-Judge
│
├── experiment_db.py        # DEPRECATED: Re-exports compat layer
└── ... (other files)

cli/                        # NEW: Free CLI tool
├── main.py
├── commands/
└── config.py

web/                        # FUTURE: Web application
├── app.py
├── api/
└── ui/

schemas/                    # NEW: Exported schemas
├── sqlite_schema.sql
├── stub_data.json
└── README.md

scripts/                    # NEW: Utilities
├── export_schema.py
├── generate_stubs.py
└── migrate_db.py
```

## Testing Strategy

### Unit Tests
```python
# tests/storage/test_memory.py
def test_in_memory_storage():
    storage = InMemoryStorage()
    exp_id = storage.save_experiment(...)
    assert exp_id.experiment_id == "test_1"
    
# tests/storage/test_sqlite.py
def test_sqlite_upsert():
    storage = SQLiteStorage(":memory:")
    # Test idempotent upsert
    result1 = storage.save_configuration("exp1", {...})
    result2 = storage.save_configuration("exp1", {...})
    assert result1 == StorageResult.CREATED
    assert result2 == StorageResult.UPDATED
```

### Integration Tests
```python
# tests/integration/test_api.py
def test_experiment_runner_with_storage():
    storage = InMemoryStorage()
    runner = ExperimentRunner(storage=storage)
    results = runner.run_experiments([...])
    assert len(results) > 0
```

### Regression Tests
```python
# tests/regression/test_compat.py
def test_backward_compatibility():
    # Old way should still work
    from src.aicl.experiment_db import ExperimentDB
    db = ExperimentDB()
    db.save_experiment(...)
```

## Documentation for Free Users

### schemas/README.md
```markdown
# Setting Up SQLite for AICL

The free CLI version of AICL uses in-memory storage by default.
To persist experiment results, set up SQLite:

## Quick Setup
```bash
# 1. Create database
aicl setup-db --path experiments/results.db

# 2. Run experiments with persistence
aicl run experiments/*.aicl --db experiments/results.db
```

## Manual Setup
```bash
# 1. Export schema
aicl export-schema --format sql > schema.sql

# 2. Create database
sqlite3 experiments/results.db < schema.sql

# 3. Use it
aicl run experiments/*.aicl --db experiments/results.db
```

## Upgrading
Web version includes PostgreSQL with advanced analytics.
Your SQLite data can be imported.
```

## Open Questions - Decisions Needed

1. **CLI Packaging**:
   - [ ] PyPI package (`pip install aicl-cli`)
   - [ ] Standalone binary (PyInstaller)
   - [ ] Both?

2. **Schema Versioning**:
   - [ ] Alembic for migrations
   - [ ] Simple SQL scripts
   - [ ] Both (Alembic for web, SQL for CLI)

3. **Web Framework**:
   - [ ] FastAPI (modern, async)
   - [ ] Flask (simpler, more mature)

4. **Authentication**:
   - [ ] OAuth (Google, GitHub)
   - [ ] API keys
   - [ ] Both

5. **Frontend**:
   - [ ] React (component-based)
   - [ ] Vue (simpler learning curve)
   - [ ] Server-side templates (Jinja2)

## Next Steps

1. ✅ Get user approval on this implementation plan
2. Start Phase 1: Create storage abstraction
3. Run regression tests to ensure compatibility
4. Document setup process for free users
5. Plan Azure/Bedrock provider integration
