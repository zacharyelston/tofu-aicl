"""
Storage abstraction layer for AICL experiments

Provides pluggable storage backends:
- InMemoryStorage: Session-only storage for free CLI
- SQLiteStorage: User-configured SQLite database
- PostgreSQLStorage: Production/team storage with PostgreSQL
"""

from .base import ExperimentStorage, ExperimentIdentifier, StorageResult
from .memory import InMemoryStorage
from .sqlite_adapter import SQLiteStorage
from .postgres_adapter import PostgreSQLStorage

__all__ = [
    'ExperimentStorage',
    'ExperimentIdentifier', 
    'StorageResult',
    'InMemoryStorage',
    'SQLiteStorage',
    'PostgreSQLStorage',
]
