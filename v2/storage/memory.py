"""
In-memory storage implementation for free CLI tier

Data only persists during the session. No database setup required.
Perfect for quick experiments and testing.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from .base import ExperimentStorage, ExperimentIdentifier, StorageResult


class InMemoryStorage(ExperimentStorage):
    """
    In-memory storage for free CLI (session only)
    
    Features:
    - Zero setup required
    - Fast operations (no I/O)
    - Data clears on exit
    - Perfect for testing and quick experiments
    """
    
    SCHEMA_VERSION = "1.0.0"
    
    def __init__(self):
        self.experiments = {}
        self.configs = {}
        self.results = {}
        self.quality = {}
    
    def save_metadata(self, experiment_id: str, config_file: str, 
                     description: str, timestamp: str) -> ExperimentIdentifier:
        
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        self.experiments[experiment_id] = {
            'experiment_id': experiment_id,
            'config_file': config_file,
            'description': description,
            'timestamp': timestamp,
            'status': 'completed'
        }
        
        return ExperimentIdentifier(
            experiment_id=experiment_id,
            created_at=timestamp,
            version=1
        )
    
    def save_configuration(self, experiment_id: str, config: Dict[str, Any]) -> StorageResult:
        if experiment_id in self.configs:
            self.configs[experiment_id].update(config)
            return StorageResult.UPDATED
        else:
            self.configs[experiment_id] = config.copy()
            return StorageResult.CREATED
    
    def save_results(self, experiment_id: str, results: Dict[str, Any]) -> StorageResult:
        if experiment_id in self.results:
            self.results[experiment_id].update(results)
            return StorageResult.UPDATED
        else:
            self.results[experiment_id] = results.copy()
            return StorageResult.CREATED
    
    def save_quality_scores(self, experiment_id: str, quality: Dict[str, Any]) -> StorageResult:
        if experiment_id in self.quality:
            self.quality[experiment_id].update(quality)
            return StorageResult.UPDATED
        else:
            self.quality[experiment_id] = quality.copy()
            return StorageResult.CREATED
    
    def get_experiment(self, experiment_id: str) -> Optional[Dict]:
        if experiment_id not in self.experiments:
            return None
        
        exp = self.experiments[experiment_id].copy()
        exp.update(self.configs.get(experiment_id, {}))
        exp.update(self.results.get(experiment_id, {}))
        exp.update(self.quality.get(experiment_id, {}))
        
        return exp
    
    def get_all_experiments(self, limit: int = 100) -> List[Dict]:
        all_exps = []
        
        for exp_id in sorted(self.experiments.keys(), 
                            key=lambda x: self.experiments[x].get('timestamp', ''), 
                            reverse=True):
            exp = self.get_experiment(exp_id)
            if exp:
                all_exps.append(exp)
            
            if len(all_exps) >= limit:
                break
        
        return all_exps
    
    def get_best_configs(self, min_quality: float = 7.0, max_cost: float = 0.01, 
                        limit: int = 10) -> List[Dict]:
        candidates = []
        
        for exp_id in self.experiments.keys():
            exp = self.get_experiment(exp_id)
            
            if exp and exp.get('judge_score', 0) >= min_quality and \
               exp.get('total_cost_usd', float('inf')) <= max_cost:
                candidates.append(exp)
        
        candidates.sort(
            key=lambda x: (-x.get('judge_score', 0), x.get('total_cost_usd', 0))
        )
        
        return candidates[:limit] if limit else candidates
    
    def get_cost_analysis(self) -> Dict[str, Any]:
        costs = [r.get('total_cost_usd', 0) for r in self.results.values() if r.get('total_cost_usd')]
        
        if not costs:
            return {
                'total_experiments': len(self.experiments),
                'avg_cost': 0,
                'min_cost': 0,
                'max_cost': 0,
                'total_spent': 0
            }
        
        return {
            'total_experiments': len(self.experiments),
            'avg_cost': sum(costs) / len(costs),
            'min_cost': min(costs),
            'max_cost': max(costs),
            'total_spent': sum(costs)
        }
    
    def get_model_performance(self) -> List[Dict]:
        model_stats = {}
        
        for exp_id in self.experiments.keys():
            config = self.configs.get(exp_id, {})
            results = self.results.get(exp_id, {})
            quality = self.quality.get(exp_id, {})
            
            chat_model = config.get('chat_model', 'unknown')
            embed_model = config.get('embedding_model', 'unknown')
            
            key = (chat_model, embed_model)
            
            if key not in model_stats:
                model_stats[key] = {
                    'chat_model': chat_model,
                    'embedding_model': embed_model,
                    'num_experiments': 0,
                    'total_cost': 0,
                    'total_quality': 0,
                    'total_latency': 0,
                    'count_quality': 0,
                    'count_latency': 0
                }
            
            stats = model_stats[key]
            stats['num_experiments'] += 1
            
            if results.get('total_cost_usd'):
                stats['total_cost'] += results['total_cost_usd']
            
            if quality.get('judge_score'):
                stats['total_quality'] += quality['judge_score']
                stats['count_quality'] += 1
            
            if results.get('latency_ms'):
                stats['total_latency'] += results['latency_ms']
                stats['count_latency'] += 1
        
        performance = []
        for key, stats in model_stats.items():
            performance.append({
                'chat_model': stats['chat_model'],
                'embedding_model': stats['embedding_model'],
                'num_experiments': stats['num_experiments'],
                'avg_cost': stats['total_cost'] / stats['num_experiments'] if stats['num_experiments'] > 0 else 0,
                'avg_quality': stats['total_quality'] / stats['count_quality'] if stats['count_quality'] > 0 else None,
                'avg_latency': stats['total_latency'] / stats['count_latency'] if stats['count_latency'] > 0 else None
            })
        
        performance.sort(key=lambda x: (-x.get('avg_quality') or 0, x['avg_cost']))
        return performance
    
    def get_schema_version(self) -> str:
        return self.SCHEMA_VERSION
    
    def export_data(self, format: str = "json") -> str:
        if format == "json":
            return json.dumps({
                'schema_version': self.SCHEMA_VERSION,
                'exported_at': datetime.now().isoformat(),
                'storage_type': 'in-memory',
                'experiments': self.experiments,
                'configurations': self.configs,
                'results': self.results,
                'quality_scores': self.quality
            }, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def clear_all(self):
        """Clear all stored data"""
        self.experiments.clear()
        self.configs.clear()
        self.results.clear()
        self.quality.clear()
    
    def __len__(self):
        """Return number of experiments"""
        return len(self.experiments)
    
    def __repr__(self):
        return f"<InMemoryStorage experiments={len(self.experiments)} version={self.SCHEMA_VERSION}>"
