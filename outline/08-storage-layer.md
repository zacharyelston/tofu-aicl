# Storage Layer Specification

## Storage Abstraction

### Abstract Interface: StorageBackend

All storage implementations must implement this interface.

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class StorageBackend(ABC):
    """Abstract interface for experiment storage"""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize storage (create tables, etc)"""
        pass
    
    @abstractmethod
    def store_experiment(self, experiment: Experiment) -> str:
        """Store experiment metadata, return ID"""
        pass
    
    @abstractmethod
    def store_configuration(self, config: Configuration) -> str:
        """Store experiment configuration, return ID"""
        pass
    
    @abstractmethod
    def store_result(self, result: ExperimentResult) -> str:
        """Store execution result, return ID"""
        pass
    
    @abstractmethod
    def store_quality_score(self, score: QualityScore) -> str:
        """Store quality grading, return ID"""
        pass
    
    @abstractmethod
    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Retrieve experiment by ID"""
        pass
    
    @abstractmethod
    def list_experiments(self, limit: int = 100) -> List[Experiment]:
        """List all experiments"""
        pass
    
    @abstractmethod
    def get_results(self, experiment_id: str) -> List[ExperimentResult]:
        """Get all results for an experiment"""
        pass
    
    @abstractmethod
    def get_best_result(self, experiment_id: str, metric: str) -> Optional[ExperimentResult]:
        """Get best result by metric (cost, quality, latency)"""
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict:
        """Get aggregate statistics"""
        pass
```

---

## In-Memory Storage (Free Tier Default)

### Implementation: MemoryStorage

```python
class MemoryStorage(StorageBackend):
    """Non-persistent in-memory storage for testing/CLI"""
    
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.configurations: Dict[str, Configuration] = {}
        self.results: Dict[str, ExperimentResult] = {}
        self.quality_scores: Dict[str, QualityScore] = {}
    
    def initialize(self) -> None:
        # No-op for memory storage
        pass
    
    def store_experiment(self, experiment: Experiment) -> str:
        self.experiments[experiment.id] = experiment
        return experiment.id
    
    # ... other methods
```

### Characteristics
- **Pros**: Fast, no setup, zero dependencies
- **Cons**: Data lost on process exit
- **Use Case**: Quick testing, temporary experiments, CI/CD

---

## SQLite Storage (Free Tier Optional)

### Implementation: SQLiteAdapter

```python
import sqlite3

class SQLiteAdapter(StorageBackend):
    """SQLite storage (user-configured)"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
    
    def initialize(self) -> None:
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()
    
    def _create_tables(self) -> None:
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                config_template TEXT,
                variables_config TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT
            )
        """)
        
        # ... other tables (configurations, results, quality_scores)
        
        self.conn.commit()
    
    def store_experiment(self, experiment: Experiment) -> str:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO experiments (id, name, description, status)
            VALUES (?, ?, ?, ?)
        """, (experiment.id, experiment.name, experiment.description, experiment.status))
        self.conn.commit()
        return experiment.id
    
    # ... other methods
```

### Setup Command

```bash
# CLI command to initialize SQLite database
aicl setup-db --path ./experiments.db

# Creates database file with schema
# User can then run experiments with:
aicl run experiment.aicl --db ./experiments.db
```

### Characteristics
- **Pros**: Persistent, local, serverless, zero-cost
- **Cons**: Single-user, manual setup
- **Use Case**: Personal projects, local persistence

---

## PostgreSQL Storage (Paid Web Tier)

### Implementation: PostgresAdapter

```python
import psycopg2

class PostgresAdapter(StorageBackend):
    """PostgreSQL storage (managed SaaS)"""
    
    def __init__(self, connection_string: str):
        self.conn_string = connection_string
        self.conn = None
    
    def initialize(self) -> None:
        self.conn = psycopg2.connect(self.conn_string)
        self._create_tables()
    
    def _create_tables(self) -> None:
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,  -- Multi-tenant support
                name TEXT NOT NULL,
                description TEXT,
                config_template TEXT,
                variables_config JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                status TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Add indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_experiments_user 
            ON experiments(user_id)
        """)
        
        # ... other tables with multi-tenant support
        
        self.conn.commit()
    
    # ... other methods with user_id filtering
```

### Multi-Tenant Support

```python
class PostgresAdapter(StorageBackend):
    def __init__(self, connection_string: str, user_id: str):
        self.user_id = user_id
        # ... rest of init
    
    def list_experiments(self, limit: int = 100) -> List[Experiment]:
        """List experiments for current user only"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM experiments 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """, (self.user_id, limit))
        # ... parse results
```

### Characteristics
- **Pros**: Multi-user, scalable, managed, ACID guarantees
- **Cons**: Requires server, paid hosting
- **Use Case**: SaaS platform, team collaboration

---

## Storage Strategy Pattern

### Tier Selection

```python
class StorageFactory:
    """Factory for creating storage backends"""
    
    @staticmethod
    def create(tier: str, **kwargs) -> StorageBackend:
        if tier == "memory":
            return MemoryStorage()
        
        elif tier == "sqlite":
            db_path = kwargs.get("db_path", "./experiments.db")
            return SQLiteAdapter(db_path)
        
        elif tier == "postgres":
            conn_string = kwargs.get("connection_string")
            user_id = kwargs.get("user_id")
            return PostgresAdapter(conn_string, user_id)
        
        else:
            raise ValueError(f"Unknown storage tier: {tier}")
```

### CLI Usage

```bash
# Default: in-memory (no persistence)
aicl run experiment.aicl

# SQLite: user-configured persistence
aicl run experiment.aicl --db ./my-experiments.db

# PostgreSQL: web tier (env-configured)
export DATABASE_URL="postgresql://user:pass@host/db"
aicl run experiment.aicl
```

### Web Tier Configuration

```python
# Automatic in web environment
if os.getenv("DATABASE_URL"):
    storage = StorageFactory.create(
        "postgres",
        connection_string=os.getenv("DATABASE_URL"),
        user_id=current_user.id
    )
else:
    # Fallback to memory for development
    storage = StorageFactory.create("memory")
```

---

## Migration Strategy

### From v1 to v2

```python
class MigrationTool:
    """Migrate experiments from v1 to v2 storage"""
    
    def migrate(self, source: StorageBackend, dest: StorageBackend):
        """Copy all data from source to destination"""
        
        # Migrate experiments
        experiments = source.list_experiments(limit=None)
        for exp in experiments:
            dest.store_experiment(exp)
            
            # Migrate related data
            configs = source.get_configurations(exp.id)
            for config in configs:
                dest.store_configuration(config)
            
            results = source.get_results(exp.id)
            for result in results:
                dest.store_result(result)
                
                # Migrate quality scores
                score = source.get_quality_score(result.id)
                if score:
                    dest.store_quality_score(score)
```

---

## State File Storage

### Local State Files (JSON)

```python
class StateManager:
    """Manage .tfstate files"""
    
    def __init__(self, state_path: str = "./terraform.tfstate"):
        self.state_path = state_path
        self.lock_path = f"{state_path}.lock"
    
    def save_state(self, state: State) -> None:
        """Save state to JSON file"""
        with self._acquire_lock():
            with open(self.state_path, 'w') as f:
                json.dump(state.to_dict(), f, indent=2)
    
    def load_state(self) -> State:
        """Load state from JSON file"""
        if not os.path.exists(self.state_path):
            return State.empty()
        
        with open(self.state_path, 'r') as f:
            data = json.load(f)
            return State.from_dict(data)
    
    def _acquire_lock(self):
        """File-based locking for concurrent access"""
        # Use fcntl.flock or similar
        pass
```

### State Locking

```python
import fcntl
import time

class StateLock:
    """File-based state lock"""
    
    def __init__(self, lock_path: str, timeout: int = 60):
        self.lock_path = lock_path
        self.timeout = timeout
        self.lock_file = None
    
    def __enter__(self):
        start = time.time()
        self.lock_file = open(self.lock_path, 'w')
        
        while True:
            try:
                fcntl.flock(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except IOError:
                if time.time() - start > self.timeout:
                    raise TimeoutError("Failed to acquire state lock")
                time.sleep(0.1)
    
    def __exit__(self, *args):
        fcntl.flock(self.lock_file, fcntl.LOCK_UN)
        self.lock_file.close()
        os.remove(self.lock_path)
```

---

## Query Patterns

### Common Queries

```python
# Get best performing configuration
best = storage.get_best_result(
    experiment_id="exp-123",
    metric="quality_score"  # or "cost", "latency"
)

# Compare configurations
results = storage.get_results(experiment_id="exp-123")
comparison = {
    r.configuration.variables: r.quality_score
    for r in results
}

# Aggregate statistics
stats = storage.get_statistics()
# {
#   "total_experiments": 10,
#   "total_executions": 150,
#   "total_cost": 1.25,
#   "avg_quality": 7.8
# }
```
