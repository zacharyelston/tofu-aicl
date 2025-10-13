"""
DEPRECATED: Backward compatibility wrapper for ExperimentDB

This module provides backward compatibility during the migration to the new storage abstraction.
New code should use storage classes directly from src.aicl.storage

Usage (old way - still works):
    from src.aicl.experiment_db import ExperimentDB
    db = ExperimentDB()

Usage (new way - recommended):
    from src.aicl.storage import SQLiteStorage
    storage = SQLiteStorage("experiments/results.db")
"""

import warnings
from pathlib import Path
from .storage.sqlite_adapter import SQLiteStorage


class ExperimentDB:
    """
    DEPRECATED: Use SQLiteStorage directly from src.aicl.storage
    
    This class provides backward compatibility for existing code.
    It will be removed in a future version.
    """
    
    def __init__(self, db_path: str = "experiments/results.db"):
        warnings.warn(
            "ExperimentDB is deprecated and will be removed in version 2.0. "
            "Use SQLiteStorage from src.aicl.storage instead:\n"
            "  from src.aicl.storage import SQLiteStorage\n"
            "  storage = SQLiteStorage('experiments/results.db')",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Ensure parent directory exists (for compatibility)
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Delegate to new storage implementation
        self._storage = SQLiteStorage(db_path)
    
    # Delegate all methods to the storage backend
    def __getattr__(self, name):
        return getattr(self._storage, name)
    
    def __repr__(self):
        return f"<ExperimentDB (deprecated, using {self._storage})>"


# Also provide direct module-level access for CLI compatibility
def get_stats_summary():
    """Module-level function for CLI backward compatibility"""
    from .storage import SQLiteStorage
    db = SQLiteStorage()
    return db.get_stats_summary() if hasattr(db, 'get_stats_summary') else "Statistics not available"
