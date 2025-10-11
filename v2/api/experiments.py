"""
Experiment Runner - Storage-agnostic experiment execution

Separates experiment logic from storage backend.
Supports any storage implementation (in-memory, SQLite, PostgreSQL).
"""

from typing import List, Dict, Optional, Any
from pathlib import Path
import subprocess
import json
from datetime import datetime

from v2.storage.base import ExperimentStorage
from v2.storage.memory import InMemoryStorage


class ExperimentRunner:
    """
    Storage-agnostic experiment runner
    
    Usage:
        # Free CLI (in-memory)
        runner = ExperimentRunner()
        
        # User's SQLite
        runner = ExperimentRunner(storage=SQLiteStorage("my.db"))
        
        # Web tier (PostgreSQL)
        runner = ExperimentRunner(storage=PostgreSQLStorage(url))
    """
    
    def __init__(self, storage: Optional[ExperimentStorage] = None):
        """
        Initialize experiment runner
        
        Args:
            storage: Storage backend (defaults to InMemoryStorage)
        """
        self.storage = storage or InMemoryStorage()
    
    def run_experiment(self, config_file: str, **kwargs) -> Dict[str, Any]:
        """
        Run a single experiment
        
        Args:
            config_file: Path to AICL config file
            **kwargs: Additional experiment parameters
            
        Returns:
            Experiment results dictionary
        """
        # TODO: Implement experiment execution logic
        # This will integrate with existing src/aicl/core/engine.py
        raise NotImplementedError("Experiment execution will be implemented in Phase 2")
    
    def run_experiments(self, config_files: List[str], **kwargs) -> List[Dict]:
        """
        Run multiple experiments
        
        Args:
            config_files: List of AICL config files
            **kwargs: Additional parameters (parallel, max_workers, etc.)
            
        Returns:
            List of experiment results
        """
        results = []
        
        for config_file in config_files:
            try:
                result = self.run_experiment(config_file, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"❌ Failed to run {config_file}: {e}")
        
        return results
    
    def get_all_results(self, limit: int = 100) -> List[Dict]:
        """Get all experiment results from storage"""
        return self.storage.get_all_experiments(limit=limit)
    
    def get_best_configs(self, min_quality: float = 7.0, 
                        max_cost: float = 0.01) -> List[Dict]:
        """Find best configurations meeting criteria"""
        return self.storage.get_best_configs(min_quality, max_cost)
    
    def analyze_costs(self) -> Dict[str, Any]:
        """Analyze costs across experiments"""
        return self.storage.get_cost_analysis()
    
    def compare_models(self) -> List[Dict]:
        """Compare performance across models"""
        return self.storage.get_model_performance()
    
    def __repr__(self):
        return f"<ExperimentRunner storage={type(self.storage).__name__}>"
