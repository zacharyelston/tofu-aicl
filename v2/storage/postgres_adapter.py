"""
PostgreSQL storage adapter for production/team usage

Supports Replit managed PostgreSQL or external PostgreSQL databases.
Connection via DATABASE_URL or individual parameters.
"""

import psycopg2
import psycopg2.extras
import json
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

from .base import ExperimentStorage, ExperimentIdentifier, StorageResult


class PostgreSQLStorage(ExperimentStorage):
    """
    PostgreSQL storage for production and team environments
    
    Supports:
    - Replit managed PostgreSQL (reads DATABASE_URL)
    - External PostgreSQL (connection params)
    - Connection pooling
    - Multi-user access
    
    Usage:
        # Replit managed (auto-detects DATABASE_URL)
        storage = PostgreSQLStorage()
        
        # External database
        storage = PostgreSQLStorage(
            host="localhost",
            port=5432,
            database="experiments",
            user="aicl",
            password="secret"
        )
    """
    
    def __init__(
        self, 
        database_url: Optional[str] = None,
        host: Optional[str] = None,
        port: int = 5432,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        create_if_missing: bool = False
    ):
        """
        Initialize PostgreSQL storage
        
        Args:
            database_url: Full PostgreSQL connection URL (e.g., from Replit)
            host: Database host (if not using database_url)
            port: Database port (default: 5432)
            database: Database name
            user: Database user
            password: Database password
            create_if_missing: If True, create schema if it doesn't exist
        """
        # Load SQL configuration
        config_path = Path(__file__).parent / "sql-config.yaml"
        with open(config_path) as f:
            self.sql_config = yaml.safe_load(f)
        
        self.SCHEMA_VERSION = self.sql_config['schema']['version']
        
        # Determine connection method
        self.database_url = database_url or os.getenv('DATABASE_URL')
        
        if not self.database_url:
            if not all([host, database, user, password]):
                raise ValueError(
                    "Either provide database_url or all of (host, database, user, password)"
                )
            self.database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        # Test connection
        self._test_connection()
        
        # Initialize schema
        if create_if_missing:
            self._init_db()
        
        self._check_schema_version()
    
    def _test_connection(self):
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version()")
                version_row = cursor.fetchone()
                if version_row:
                    print(f"✅ Connected to PostgreSQL: {version_row[0].split(',')[0]}")
        except Exception as e:
            raise ValueError(f"❌ Failed to connect to PostgreSQL: {e}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = psycopg2.connect(self.database_url)
        conn.autocommit = False
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
            
            # Create tables from config (convert SQLite to PostgreSQL syntax)
            for table_name, create_sql in self.sql_config['tables'].items():
                # Convert SQLite to PostgreSQL syntax
                pg_sql = create_sql.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
                pg_sql = pg_sql.replace('DATETIME', 'TIMESTAMP')
                pg_sql = pg_sql.replace('BOOLEAN', 'BOOLEAN')
                cursor.execute(pg_sql)
            
            # Create indexes from config
            for index_sql in self.sql_config['indexes']:
                cursor.execute(index_sql)
            
            # Insert initial schema version if not exists
            cursor.execute("SELECT COUNT(*) FROM schema_version")
            count_row = cursor.fetchone()
            if count_row and count_row[0] == 0:
                cursor.execute(
                    "INSERT INTO schema_version (version, description) VALUES (%s, %s)",
                    (self.SCHEMA_VERSION, self.sql_config['schema']['description'])
                )
    
    def _check_schema_version(self):
        """Verify schema version matches"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                if row is not None and row[0] != self.SCHEMA_VERSION:
                    print(f"⚠️  Schema version mismatch: DB={row[0]}, Code={self.SCHEMA_VERSION}")
                    print(f"   Database may need migration.")
            except psycopg2.errors.UndefinedTable:
                print("⚠️  Schema not initialized. Set create_if_missing=True or run migrations.")
    
    def save_metadata(self, experiment_id: str, config_file: str, 
                     description: str, timestamp: str) -> ExperimentIdentifier:
        
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # PostgreSQL uses ON CONFLICT for upsert
            cursor.execute("""
                INSERT INTO experiments 
                (experiment_id, timestamp, config_file, description, status)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (experiment_id) DO UPDATE SET
                    timestamp = EXCLUDED.timestamp,
                    config_file = EXCLUDED.config_file,
                    description = EXCLUDED.description,
                    status = EXCLUDED.status
            """, (experiment_id, timestamp, config_file, description, 'completed'))
            
            cursor.execute(
                "SELECT experiment_id, timestamp, version FROM experiments WHERE experiment_id = %s",
                (experiment_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                raise ValueError(f"Experiment {experiment_id} not found after save")
            
            return ExperimentIdentifier(
                experiment_id=row[0],
                created_at=row[1].isoformat() if hasattr(row[1], 'isoformat') else str(row[1]),
                version=row[2] or 1
            )
    
    def save_configuration(self, experiment_id: str, config: Dict[str, Any]) -> StorageResult:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute("SELECT id FROM configurations WHERE experiment_id = %s", (experiment_id,))
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
                cursor.execute("DELETE FROM configurations WHERE experiment_id = %s", (experiment_id,))
            
            cursor.execute("""
                INSERT INTO configurations 
                (experiment_id, chat_model, embedding_model, temperature, max_tokens, 
                 top_k, provider, rerank, other_params)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, params)
            
            return StorageResult.UPDATED if exists else StorageResult.CREATED
    
    def save_results(self, experiment_id: str, results: Dict[str, Any]) -> StorageResult:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM results WHERE experiment_id = %s", (experiment_id,))
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
                cursor.execute("DELETE FROM results WHERE experiment_id = %s", (experiment_id,))
            
            cursor.execute("""
                INSERT INTO results 
                (experiment_id, total_cost_usd, embedding_cost_usd, chat_cost_usd,
                 total_tokens, prompt_tokens, completion_tokens, latency_ms, 
                 end_to_end_ms, chunks_retrieved, success, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, params)
            
            return StorageResult.UPDATED if exists else StorageResult.CREATED
    
    def save_quality_scores(self, experiment_id: str, quality: Dict[str, Any]) -> StorageResult:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM quality_scores WHERE experiment_id = %s", (experiment_id,))
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
                cursor.execute("DELETE FROM quality_scores WHERE experiment_id = %s", (experiment_id,))
            
            cursor.execute("""
                INSERT INTO quality_scores 
                (experiment_id, judge_model, judge_score, accuracy_score, 
                 completeness_score, clarity_score, relevance_score, judge_feedback)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, params)
            
            return StorageResult.UPDATED if exists else StorageResult.CREATED
    
    def get_experiment(self, experiment_id: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            # Convert SQLite ? to PostgreSQL %s
            query = self.sql_config['queries']['get_full_experiment'].replace('?', '%s')
            cursor.execute(query, (experiment_id,))
            row = cursor.fetchone()
            if row:
                return {k: v for k, v in row.items()}
            return None
    
    def get_all_experiments(self, limit: int = 100) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            # Convert SQLite ? to PostgreSQL %s
            query = self.sql_config['queries']['get_all_experiments'].replace('?', '%s')
            cursor.execute(query, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_best_configs(self, min_quality: float = 7.0, max_cost: float = 0.01, 
                        limit: int = 10) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            # Convert SQLite ? to PostgreSQL %s
            query = self.sql_config['queries']['get_best_configs'].replace('?', '%s')
            cursor.execute(query, (min_quality, max_cost, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_cost_analysis(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(self.sql_config['queries']['get_cost_analysis'])
            row = cursor.fetchone()
            if row:
                return {k: v for k, v in row.items()}
            return {}
    
    def get_model_performance(self) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(self.sql_config['queries']['get_model_performance'])
            return [dict(row) for row in cursor.fetchall()]
    
    def get_schema_version(self) -> str:
        return self.SCHEMA_VERSION
    
    def export_data(self, format: str = "json") -> str:
        experiments = self.get_all_experiments(limit=10000)
        
        if format == "json":
            db_location = 'hidden'
            if self.database_url and '@' in self.database_url:
                db_location = self.database_url.split('@')[1]
            
            return json.dumps({
                'schema_version': self.SCHEMA_VERSION,
                'exported_at': datetime.now().isoformat(),
                'storage_type': 'postgresql',
                'database_url': db_location,
                'total_experiments': len(experiments),
                'experiments': experiments
            }, indent=2, default=str)
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
        db_info = 'configured'
        if self.database_url and '@' in self.database_url:
            db_info = self.database_url.split('@')[1]
        return f"<PostgreSQLStorage db={db_info} version={self.SCHEMA_VERSION}>"
