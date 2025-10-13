"""
SQLite storage adapter (user provides database)

Users must set up their own SQLite database using exported schema.
This adapter connects to existing databases and enforces schema versioning.
"""

import sqlite3
import json
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

from .base import ExperimentStorage, ExperimentIdentifier, StorageResult


class SQLiteStorage(ExperimentStorage):
    """
    SQLite storage adapter for persistent experiment tracking
    
    Users must create database first using:
      1. aicl export-schema --format sql > schema.sql
      2. sqlite3 my.db < schema.sql
    Or:
      aicl setup-db --path my.db
    """
    
    def __init__(self, db_path: str = "experiments/results.db", create_if_missing: bool = False):
        """
        Initialize SQLite storage
        
        Args:
            db_path: Path to SQLite database file
            create_if_missing: If True, create DB if it doesn't exist (default: False)
        """
        self.db_path = db_path
        
        # Load SQL configuration
        config_path = Path(__file__).parent / "sql-config.yaml"
        with open(config_path) as f:
            self.sql_config = yaml.safe_load(f)
        
        self.SCHEMA_VERSION = self.sql_config['schema']['version']
        
        if create_if_missing:
            # Ensure parent directory exists
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            # _init_db will create the file and schema
        else:
            self._ensure_db_exists()
        
        self._init_db()
        
        if not create_if_missing:
            self._check_schema_version()
    
    def _ensure_db_exists(self):
        """Provide helpful error if DB doesn't exist"""
        if not os.path.exists(self.db_path):
            raise ValueError(
                f"❌ Database not found: {self.db_path}\n\n"
                f"To set up SQLite storage:\n"
                f"  python -m v2.cli.main setup-db --path {self.db_path}\n\n"
                f"Or create manually:\n"
                f"  1. Export schema: python -m v2.cli.main export-schema > schema.sql\n"
                f"  2. Create database: sqlite3 {self.db_path} < schema.sql\n"
            )
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database schema if needed"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create tables from config
            for table_name, create_sql in self.sql_config['tables'].items():
                cursor.execute(create_sql)
            
            # Create indexes from config
            for index_sql in self.sql_config['indexes']:
                cursor.execute(index_sql)
            
            # Insert initial schema version if not exists
            cursor.execute(self.sql_config['queries']['count_schema_versions'])
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    self.sql_config['queries']['insert_schema_version'],
                    (self.SCHEMA_VERSION, self.sql_config['schema']['description'])
                )
    
    def _check_schema_version(self):
        """Verify schema version matches (skip if no version table yet)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(self.sql_config['queries']['get_schema_version'])
                row = cursor.fetchone()
                if row and row[0] != self.SCHEMA_VERSION:
                    print(f"⚠️  Schema version mismatch: DB={row[0]}, Code={self.SCHEMA_VERSION}")
                    print(f"   Database may need migration. Run: aicl migrate")
            except sqlite3.OperationalError:
                pass
    
    def save_metadata(self, experiment_id: str, config_file: str, 
                     description: str, timestamp: str) -> ExperimentIdentifier:
        
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                self.sql_config['queries']['upsert_experiment'],
                (experiment_id, timestamp, config_file, description, 'completed')
            )
            
            cursor.execute(
                self.sql_config['queries']['get_experiment_metadata'],
                (experiment_id,)
            )
            row = cursor.fetchone()
            
            return ExperimentIdentifier(
                experiment_id=row[0],
                created_at=row[1],
                version=row[2] or 1
            )
    
    def save_configuration(self, experiment_id: str, config: Dict[str, Any]) -> StorageResult:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute(self.sql_config['queries']['check_config_exists'], (experiment_id,))
            exists = cursor.fetchone()
            
            # Prepare params
            other_params = {k: v for k, v in config.items() 
                          if k not in ['chat_model', 'embedding_model', 'temperature', 'max_tokens', 'top_k', 'provider', 'rerank']}
            
            params = (
                experiment_id,
                config.get('chat_model'),
                config.get('embedding_model'),
                config.get('temperature'),
                config.get('max_tokens'),
                config.get('top_k'),
                config.get('provider'),
                config.get('rerank'),
                json.dumps(other_params)
            )
            
            # Upsert: delete and insert
            if exists:
                cursor.execute("DELETE FROM configurations WHERE experiment_id = ?", (experiment_id,))
            
            cursor.execute(self.sql_config['queries']['insert_configuration'], params)
            
            return StorageResult.UPDATED if exists else StorageResult.CREATED
    
    def save_results(self, experiment_id: str, results: Dict[str, Any]) -> StorageResult:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(self.sql_config['queries']['check_results_exists'], (experiment_id,))
            exists = cursor.fetchone()
            
            params = (
                experiment_id,
                results.get('total_cost_usd'),
                results.get('embedding_cost_usd'),
                results.get('chat_cost_usd'),
                results.get('total_tokens'),
                results.get('prompt_tokens'),
                results.get('completion_tokens'),
                results.get('latency_ms'),
                results.get('end_to_end_ms'),
                results.get('chunks_retrieved'),
                results.get('success', True),
                results.get('error_message')
            )
            
            if exists:
                cursor.execute("DELETE FROM results WHERE experiment_id = ?", (experiment_id,))
            
            cursor.execute(self.sql_config['queries']['insert_results'], params)
            
            return StorageResult.UPDATED if exists else StorageResult.CREATED
    
    def save_quality_scores(self, experiment_id: str, quality: Dict[str, Any]) -> StorageResult:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(self.sql_config['queries']['check_quality_exists'], (experiment_id,))
            exists = cursor.fetchone()
            
            params = (
                experiment_id,
                quality.get('judge_model'),
                quality.get('judge_score'),
                quality.get('accuracy_score'),
                quality.get('completeness_score'),
                quality.get('clarity_score'),
                quality.get('relevance_score'),
                quality.get('judge_feedback')
            )
            
            if exists:
                cursor.execute("DELETE FROM quality_scores WHERE experiment_id = ?", (experiment_id,))
            
            cursor.execute(self.sql_config['queries']['insert_quality'], params)
            
            return StorageResult.UPDATED if exists else StorageResult.CREATED
    
    def get_experiment(self, experiment_id: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(self.sql_config['queries']['get_full_experiment'], (experiment_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_experiments(self, limit: int = 100) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(self.sql_config['queries']['get_all_experiments'], (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_best_configs(self, min_quality: float = 7.0, max_cost: float = 0.01, 
                        limit: int = 10) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(self.sql_config['queries']['get_best_configs'], (min_quality, max_cost, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_cost_analysis(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(self.sql_config['queries']['get_cost_analysis'])
            return dict(cursor.fetchone())
    
    def get_model_performance(self) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(self.sql_config['queries']['get_model_performance'])
            return [dict(row) for row in cursor.fetchall()]
    
    def get_schema_version(self) -> str:
        return self.SCHEMA_VERSION
    
    def export_data(self, format: str = "json") -> str:
        experiments = self.get_all_experiments(limit=10000)
        
        if format == "json":
            return json.dumps({
                'schema_version': self.SCHEMA_VERSION,
                'exported_at': datetime.now().isoformat(),
                'storage_type': 'sqlite',
                'database_path': self.db_path,
                'total_experiments': len(experiments),
                'experiments': experiments
            }, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def clear_all(self):
        """Clear all stored data (use with caution!)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM quality_scores")
            cursor.execute("DELETE FROM results")
            cursor.execute("DELETE FROM configurations")
            cursor.execute("DELETE FROM experiments")
    
    def __repr__(self):
        return f"<SQLiteStorage db={self.db_path} version={self.SCHEMA_VERSION}>"
