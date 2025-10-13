"""
SQLite storage adapter (user provides database)

Users must set up their own SQLite database using exported schema.
This adapter connects to existing databases and enforces schema versioning.
"""

import sqlite3
import json
import os
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
    
    SCHEMA_VERSION = "1.0.0"
    
    def __init__(self, db_path: str = "experiments/results.db"):
        self.db_path = db_path
        self._ensure_db_exists()
        self._init_db()
        self._check_schema_version()
    
    def _ensure_db_exists(self):
        """Provide helpful error if DB doesn't exist"""
        if not os.path.exists(self.db_path):
            raise ValueError(
                f"❌ Database not found: {self.db_path}\n\n"
                f"To set up SQLite storage:\n"
                f"  1. Export schema: aicl export-schema --format sql > schema.sql\n"
                f"  2. Create database: sqlite3 {self.db_path} < schema.sql\n\n"
                f"Or use the setup command:\n"
                f"  aicl setup-db --path {self.db_path}\n"
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
            
            # Schema version table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT NOT NULL,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            """)
            
            # Experiments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id TEXT UNIQUE NOT NULL,
                    timestamp DATETIME NOT NULL,
                    config_file TEXT,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    version INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Configurations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configurations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id TEXT NOT NULL,
                    chat_model TEXT,
                    embedding_model TEXT,
                    temperature REAL,
                    max_tokens INTEGER,
                    top_k INTEGER,
                    provider TEXT,
                    rerank BOOLEAN,
                    other_params TEXT,
                    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
                )
            """)
            
            # Results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id TEXT NOT NULL,
                    total_cost_usd REAL,
                    embedding_cost_usd REAL,
                    chat_cost_usd REAL,
                    total_tokens INTEGER,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    latency_ms REAL,
                    end_to_end_ms REAL,
                    chunks_retrieved INTEGER,
                    success BOOLEAN,
                    error_message TEXT,
                    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
                )
            """)
            
            # Quality scores table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quality_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id TEXT NOT NULL,
                    judge_model TEXT,
                    judge_score REAL,
                    accuracy_score REAL,
                    completeness_score REAL,
                    clarity_score REAL,
                    relevance_score REAL,
                    judge_feedback TEXT,
                    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_exp_timestamp ON experiments(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_config_exp_id ON configurations(experiment_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_config_model ON configurations(chat_model)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_exp_id ON results(experiment_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_cost ON results(total_cost_usd)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality_exp_id ON quality_scores(experiment_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality_score ON quality_scores(judge_score)")
            
            # Insert initial schema version if not exists
            cursor.execute("SELECT COUNT(*) FROM schema_version")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO schema_version (version, description) VALUES (?, ?)",
                    (self.SCHEMA_VERSION, "Initial schema with experiments, configurations, results, quality_scores")
                )
    
    def _check_schema_version(self):
        """Verify schema version matches (skip if no version table yet)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
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
            cursor.execute("""
                INSERT OR REPLACE INTO experiments 
                (experiment_id, timestamp, config_file, description, status)
                VALUES (?, ?, ?, ?, ?)
            """, (experiment_id, timestamp, config_file, description, 'completed'))
            
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
    
    def save_configuration(self, experiment_id: str, config: Dict[str, Any]) -> StorageResult:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute("SELECT id FROM configurations WHERE experiment_id = ?", (experiment_id,))
            exists = cursor.fetchone()
            
            # Delete existing for upsert
            if exists:
                cursor.execute("DELETE FROM configurations WHERE experiment_id = ?", (experiment_id,))
            
            other_params = {k: v for k, v in config.items() 
                          if k not in ['chat_model', 'embedding_model', 'temperature', 'max_tokens', 'top_k', 'provider', 'rerank']}
            
            cursor.execute("""
                INSERT INTO configurations 
                (experiment_id, chat_model, embedding_model, temperature, max_tokens, top_k, provider, rerank, other_params)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                experiment_id,
                config.get('chat_model'),
                config.get('embedding_model'),
                config.get('temperature'),
                config.get('max_tokens'),
                config.get('top_k'),
                config.get('provider'),
                config.get('rerank'),
                json.dumps(other_params)
            ))
            
            return StorageResult.UPDATED if exists else StorageResult.CREATED
    
    def save_results(self, experiment_id: str, results: Dict[str, Any]) -> StorageResult:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM results WHERE experiment_id = ?", (experiment_id,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute("DELETE FROM results WHERE experiment_id = ?", (experiment_id,))
            
            cursor.execute("""
                INSERT INTO results 
                (experiment_id, total_cost_usd, embedding_cost_usd, chat_cost_usd, 
                 total_tokens, prompt_tokens, completion_tokens, latency_ms, end_to_end_ms,
                 chunks_retrieved, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
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
            ))
            
            return StorageResult.UPDATED if exists else StorageResult.CREATED
    
    def save_quality_scores(self, experiment_id: str, quality: Dict[str, Any]) -> StorageResult:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM quality_scores WHERE experiment_id = ?", (experiment_id,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute("DELETE FROM quality_scores WHERE experiment_id = ?", (experiment_id,))
            
            cursor.execute("""
                INSERT INTO quality_scores 
                (experiment_id, judge_model, judge_score, accuracy_score, 
                 completeness_score, clarity_score, relevance_score, judge_feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                experiment_id,
                quality.get('judge_model'),
                quality.get('judge_score'),
                quality.get('accuracy_score'),
                quality.get('completeness_score'),
                quality.get('clarity_score'),
                quality.get('relevance_score'),
                quality.get('judge_feedback')
            ))
            
            return StorageResult.UPDATED if exists else StorageResult.CREATED
    
    def get_experiment(self, experiment_id: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    e.*,
                    c.chat_model, c.embedding_model, c.temperature, c.max_tokens, c.top_k, c.provider, c.rerank, c.other_params,
                    r.total_cost_usd, r.embedding_cost_usd, r.chat_cost_usd, r.total_tokens, r.prompt_tokens, r.completion_tokens,
                    r.latency_ms, r.end_to_end_ms, r.chunks_retrieved, r.success, r.error_message,
                    q.judge_model, q.judge_score, q.accuracy_score, q.completeness_score, q.clarity_score, q.relevance_score, q.judge_feedback
                FROM experiments e
                LEFT JOIN configurations c ON e.experiment_id = c.experiment_id
                LEFT JOIN results r ON e.experiment_id = r.experiment_id
                LEFT JOIN quality_scores q ON e.experiment_id = q.experiment_id
                WHERE e.experiment_id = ?
            """, (experiment_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_experiments(self, limit: int = 100) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    e.*,
                    c.chat_model, c.embedding_model, c.temperature, c.top_k,
                    r.total_cost_usd, r.total_tokens,
                    q.judge_score
                FROM experiments e
                LEFT JOIN configurations c ON e.experiment_id = c.experiment_id
                LEFT JOIN results r ON e.experiment_id = r.experiment_id
                LEFT JOIN quality_scores q ON e.experiment_id = q.experiment_id
                ORDER BY e.timestamp DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_best_configs(self, min_quality: float = 7.0, max_cost: float = 0.01, 
                        limit: int = 10) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    e.experiment_id,
                    c.chat_model, c.embedding_model, c.temperature, c.max_tokens, c.top_k,
                    r.total_cost_usd, r.total_tokens, r.latency_ms,
                    q.judge_score
                FROM experiments e
                JOIN configurations c ON e.experiment_id = c.experiment_id
                JOIN results r ON e.experiment_id = r.experiment_id
                JOIN quality_scores q ON e.experiment_id = q.experiment_id
                WHERE q.judge_score >= ? AND r.total_cost_usd <= ?
                ORDER BY q.judge_score DESC, r.total_cost_usd ASC
                LIMIT ?
            """, (min_quality, max_cost, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_cost_analysis(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_experiments,
                    AVG(total_cost_usd) as avg_cost,
                    MIN(total_cost_usd) as min_cost,
                    MAX(total_cost_usd) as max_cost,
                    SUM(total_cost_usd) as total_spent
                FROM results
            """)
            
            return dict(cursor.fetchone())
    
    def get_model_performance(self) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    c.chat_model,
                    c.embedding_model,
                    COUNT(*) as num_experiments,
                    AVG(r.total_cost_usd) as avg_cost,
                    AVG(q.judge_score) as avg_quality,
                    AVG(r.latency_ms) as avg_latency
                FROM configurations c
                JOIN results r ON c.experiment_id = r.experiment_id
                LEFT JOIN quality_scores q ON c.experiment_id = q.experiment_id
                GROUP BY c.chat_model, c.embedding_model
                ORDER BY avg_quality DESC, avg_cost ASC
            """)
            
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
