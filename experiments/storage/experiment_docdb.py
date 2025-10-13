"""
Experiment Document Database
Stores all experiment outputs as structured documents in PostgreSQL
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor, Json


class ExperimentDocDB:
    """PostgreSQL-backed document storage for experiments"""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize experiment document database
        
        Args:
            connection_string: PostgreSQL connection string (default: from DATABASE_URL env var)
        """
        self.connection_string = connection_string or os.getenv('DATABASE_URL')
        if not self.connection_string:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self._ensure_schema()
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.connection_string)
    
    def _ensure_schema(self):
        """Create tables if they don't exist"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS experiment_outputs (
            id SERIAL PRIMARY KEY,
            experiment_id VARCHAR(255) NOT NULL,
            run_timestamp TIMESTAMP NOT NULL,
            config_file TEXT,
            config_content JSONB,
            outputs JSONB NOT NULL,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_experiment_id ON experiment_outputs(experiment_id);
        CREATE INDEX IF NOT EXISTS idx_run_timestamp ON experiment_outputs(run_timestamp);
        CREATE INDEX IF NOT EXISTS idx_metadata_gin ON experiment_outputs USING GIN(metadata);
        """
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            conn.commit()
    
    def save_experiment(
        self,
        experiment_id: str,
        outputs: Dict[str, Any],
        config_file: Optional[str] = None,
        config_content: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        run_timestamp: Optional[datetime] = None
    ) -> int:
        """
        Save experiment outputs as a document
        
        Args:
            experiment_id: Unique identifier for the experiment
            outputs: All experiment outputs (steps, results, etc.)
            config_file: Path to config file used
            config_content: Full config content as dict
            metadata: Additional metadata (provider, cost, tokens, tags)
            run_timestamp: When experiment was run (default: now)
        
        Returns:
            Database ID of saved document
        """
        run_timestamp = run_timestamp or datetime.now()
        
        sql = """
        INSERT INTO experiment_outputs 
        (experiment_id, run_timestamp, config_file, config_content, outputs, metadata)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (
                    experiment_id,
                    run_timestamp,
                    config_file,
                    Json(config_content) if config_content else None,
                    Json(outputs),
                    Json(metadata) if metadata else None
                ))
                doc_id = cur.fetchone()[0]
            conn.commit()
        
        return doc_id
    
    def get_by_id(self, experiment_id: str, run_timestamp: Optional[datetime] = None) -> Optional[Dict]:
        """
        Get experiment output by ID
        
        Args:
            experiment_id: Experiment identifier
            run_timestamp: Specific run timestamp (default: latest)
        
        Returns:
            Experiment document or None
        """
        if run_timestamp:
            sql = """
            SELECT * FROM experiment_outputs 
            WHERE experiment_id = %s AND run_timestamp = %s
            """
            params = (experiment_id, run_timestamp)
        else:
            sql = """
            SELECT * FROM experiment_outputs 
            WHERE experiment_id = %s 
            ORDER BY run_timestamp DESC 
            LIMIT 1
            """
            params = (experiment_id,)
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
        
        return dict(row) if row else None
    
    def get_all_runs(self, experiment_id: str) -> List[Dict]:
        """
        Get all runs of an experiment
        
        Args:
            experiment_id: Experiment identifier
        
        Returns:
            List of all runs, sorted by timestamp (newest first)
        """
        sql = """
        SELECT * FROM experiment_outputs 
        WHERE experiment_id = %s 
        ORDER BY run_timestamp DESC
        """
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (experiment_id,))
                rows = cur.fetchall()
        
        return [dict(row) for row in rows]
    
    def query(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        provider: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query experiments with filters
        
        Args:
            start_date: Filter by start date
            end_date: Filter by end date
            provider: Filter by provider (e.g., 'azure_openai')
            tags: Filter by tags (any match)
            limit: Maximum results
        
        Returns:
            List of matching experiment documents
        """
        conditions = []
        params = []
        
        if start_date:
            conditions.append("run_timestamp >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("run_timestamp <= %s")
            params.append(end_date)
        
        if provider:
            conditions.append("metadata->>'provider' = %s")
            params.append(provider)
        
        if tags:
            conditions.append("metadata->'tags' ?| %s::text[]")
            params.append(tags)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f"""
        SELECT * FROM experiment_outputs 
        WHERE {where_clause}
        ORDER BY run_timestamp DESC 
        LIMIT %s
        """
        params.append(limit)
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
        
        return [dict(row) for row in rows]
    
    def compare(self, experiment_ids: List[str], metrics: List[str] = None) -> Dict:
        """
        Compare multiple experiments
        
        Args:
            experiment_ids: List of experiment IDs to compare
            metrics: Metrics to compare (default: cost, tokens, quality)
        
        Returns:
            Comparison data structure
        """
        metrics = metrics or ['total_cost', 'total_tokens', 'quality_score']
        
        placeholders = ','.join(['%s'] * len(experiment_ids))
        sql = f"""
        SELECT 
            experiment_id,
            run_timestamp,
            metadata->>'provider' as provider,
            (metadata->>'total_cost')::float as total_cost,
            (outputs->>'total_tokens')::int as total_tokens,
            (metadata->>'quality_score')::int as quality_score
        FROM experiment_outputs 
        WHERE experiment_id IN ({placeholders})
        ORDER BY run_timestamp DESC
        """
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, experiment_ids)
                rows = cur.fetchall()
        
        comparison = {
            'experiments': [dict(row) for row in rows],
            'metrics': {}
        }
        
        for metric in metrics:
            values = [row.get(metric) for row in rows if row.get(metric) is not None]
            if values:
                comparison['metrics'][metric] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'values': values
                }
        
        return comparison
    
    def get_best(
        self,
        by_metric: str = 'total_cost',
        ascending: bool = True,
        provider: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get best experiments by metric
        
        Args:
            by_metric: Metric to sort by (cost, tokens, quality_score)
            ascending: True for lowest first, False for highest
            provider: Filter by provider
            limit: Max results
        
        Returns:
            List of best experiments
        """
        order = "ASC" if ascending else "DESC"
        
        if by_metric in ['total_cost', 'quality_score']:
            metric_field = f"(metadata->>'{by_metric}')::float"
        else:
            metric_field = f"(outputs->>'{by_metric}')::int"
        
        provider_filter = "AND metadata->>'provider' = %s" if provider else ""
        params = [limit]
        if provider:
            params.insert(0, provider)
        
        sql = f"""
        SELECT * FROM experiment_outputs 
        WHERE {metric_field} IS NOT NULL {provider_filter}
        ORDER BY {metric_field} {order}
        LIMIT %s
        """
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
        
        return [dict(row) for row in rows]
    
    def export_to_json(self, experiment_id: str, output_file: str):
        """Export experiment to JSON file"""
        doc = self.get_by_id(experiment_id)
        if doc:
            # Convert datetime to string for JSON serialization
            doc['run_timestamp'] = doc['run_timestamp'].isoformat()
            doc['created_at'] = doc['created_at'].isoformat()
            
            with open(output_file, 'w') as f:
                json.dump(doc, f, indent=2)
    
    def list_all(self, limit: int = 50) -> List[Dict]:
        """List all experiments (summary view)"""
        sql = """
        SELECT 
            experiment_id,
            run_timestamp,
            metadata->>'provider' as provider,
            (outputs->>'total_tokens')::int as total_tokens,
            metadata->>'tags' as tags
        FROM experiment_outputs 
        ORDER BY run_timestamp DESC 
        LIMIT %s
        """
        
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (limit,))
                rows = cur.fetchall()
        
        return [dict(row) for row in rows]
