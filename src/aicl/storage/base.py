"""
Abstract storage interface for experiment data

Defines the contract that all storage backends must implement.
Supports idempotent operations and stable identifiers across backends.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class StorageResult(Enum):
    """Result of a storage operation"""
    CREATED = "created"
    UPDATED = "updated"
    ERROR = "error"


@dataclass
class ExperimentIdentifier:
    """Stable experiment identifier across all storage backends"""
    experiment_id: str
    created_at: str
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'experiment_id': self.experiment_id,
            'created_at': self.created_at,
            'version': self.version
        }


class ExperimentStorage(ABC):
    """
    Abstract interface for experiment storage
    
    All storage backends (in-memory, SQLite, PostgreSQL) must implement this interface.
    Methods are designed to be idempotent where possible.
    """
    
    @abstractmethod
    def save_metadata(self, experiment_id: str, config_file: str, 
                     description: str, timestamp: str) -> ExperimentIdentifier:
        """
        Save experiment metadata (idempotent)
        
        Args:
            experiment_id: Unique experiment identifier
            config_file: Path to AICL config file
            description: Experiment description
            timestamp: ISO format timestamp
            
        Returns:
            ExperimentIdentifier with stable ID and metadata
        """
        pass
    
    @abstractmethod
    def save_configuration(self, experiment_id: str, config: Dict[str, Any]) -> StorageResult:
        """
        Save experiment configuration (idempotent upsert)
        
        Args:
            experiment_id: Experiment to save config for
            config: Configuration dictionary (models, parameters, etc.)
            
        Returns:
            StorageResult indicating created or updated
        """
        pass
    
    @abstractmethod
    def save_results(self, experiment_id: str, results: Dict[str, Any]) -> StorageResult:
        """
        Save performance metrics (idempotent upsert)
        
        Args:
            experiment_id: Experiment to save results for
            results: Metrics dictionary (cost, tokens, latency, etc.)
            
        Returns:
            StorageResult indicating created or updated
        """
        pass
    
    @abstractmethod
    def save_quality_scores(self, experiment_id: str, quality: Dict[str, Any]) -> StorageResult:
        """
        Save quality evaluation scores (idempotent upsert)
        
        Args:
            experiment_id: Experiment to save quality for
            quality: Quality scores from LLM-as-Judge
            
        Returns:
            StorageResult indicating created or updated
        """
        pass
    
    def save_experiment(self, experiment_id: str, config: Dict, 
                       results: Dict, quality: Optional[Dict] = None) -> ExperimentIdentifier:
        """
        Convenience method to save complete experiment
        
        Calls individual save methods in sequence. Override for batch optimization.
        
        Args:
            experiment_id: Unique experiment identifier
            config: Configuration dictionary
            results: Results/metrics dictionary
            quality: Optional quality scores dictionary
            
        Returns:
            ExperimentIdentifier for the saved experiment
        """
        timestamp = results.get('timestamp') or datetime.now().isoformat()
        
        exp_id = self.save_metadata(
            experiment_id, 
            config.get('config_file', ''), 
            config.get('description', ''),
            timestamp
        )
        
        self.save_configuration(experiment_id, config)
        self.save_results(experiment_id, results)
        
        if quality:
            self.save_quality_scores(experiment_id, quality)
        
        return exp_id
    
    @abstractmethod
    def get_experiment(self, experiment_id: str) -> Optional[Dict]:
        """
        Retrieve complete experiment by ID
        
        Args:
            experiment_id: Experiment to retrieve
            
        Returns:
            Dictionary with all experiment data, or None if not found
        """
        pass
    
    @abstractmethod
    def get_all_experiments(self, limit: int = 100) -> List[Dict]:
        """
        Get all experiments (most recent first)
        
        Args:
            limit: Maximum number of experiments to return
            
        Returns:
            List of experiment dictionaries
        """
        pass
    
    @abstractmethod
    def get_best_configs(self, min_quality: float = 7.0, max_cost: float = 0.01, 
                        limit: int = 10) -> List[Dict]:
        """
        Find best configurations meeting quality and cost criteria
        
        Args:
            min_quality: Minimum quality score (0-10)
            max_cost: Maximum cost in USD
            limit: Maximum number of results
            
        Returns:
            List of experiment dictionaries sorted by quality desc, cost asc
        """
        pass
    
    @abstractmethod
    def get_cost_analysis(self) -> Dict[str, Any]:
        """
        Analyze costs across all experiments
        
        Returns:
            Dictionary with cost statistics (total, avg, min, max)
        """
        pass
    
    @abstractmethod
    def get_model_performance(self) -> List[Dict]:
        """
        Compare performance across different models
        
        Returns:
            List of model performance statistics
        """
        pass
    
    @abstractmethod
    def get_schema_version(self) -> str:
        """
        Get storage schema version
        
        Returns:
            Version string (e.g., "1.0.0")
        """
        pass
    
    @abstractmethod
    def export_data(self, format: str = "json") -> str:
        """
        Export all data in specified format
        
        Args:
            format: Export format ("json", "csv", etc.)
            
        Returns:
            Serialized data string
        """
        pass
    
    @abstractmethod
    def clear_all(self):
        """
        Clear all stored data (use with caution!)
        
        Mainly for testing and development.
        """
        pass
