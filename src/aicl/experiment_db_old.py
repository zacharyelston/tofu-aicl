"""
AICL Experiment Results Database (SQLite)
Stores experiment configurations, results, and metrics for analysis
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

class ExperimentDB:
    def __init__(self, db_path: str = "experiments/results.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Experiments table - metadata about each experiment
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id TEXT UNIQUE NOT NULL,
                    timestamp DATETIME NOT NULL,
                    config_file TEXT,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Configurations table - experiment parameters
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
                    other_params TEXT,  -- JSON blob for additional params
                    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
                )
            """)
            
            # Results table - cost and performance metrics
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
            
            # Quality scores table - judge evaluation
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
            
            # Create indexes for common queries and joins
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_exp_timestamp ON experiments(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_config_exp_id ON configurations(experiment_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_config_model ON configurations(chat_model)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_exp_id ON results(experiment_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_cost ON results(total_cost_usd)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality_exp_id ON quality_scores(experiment_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality_score ON quality_scores(judge_score)")
    
    def save_experiment(self, 
                       experiment_id: str, 
                       config: Dict[str, Any],
                       results: Dict[str, Any],
                       quality: Optional[Dict[str, Any]] = None) -> int:
        """Save complete experiment data"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Save experiment metadata
            cursor.execute("""
                INSERT OR REPLACE INTO experiments (experiment_id, timestamp, config_file, description, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                experiment_id,
                datetime.now().isoformat(),
                config.get('config_file', ''),
                config.get('description', ''),
                results.get('status', 'completed')
            ))
            
            # 2. Save configuration (delete existing if updating)
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
            
            # 3. Save results/metrics (delete existing if updating)
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
            
            # 4. Save quality scores (if available, delete existing if updating)
            if quality:
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
            
            return cursor.lastrowid
    
    def get_experiment(self, experiment_id: str) -> Optional[Dict]:
        """Retrieve complete experiment data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Join all tables
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
        """Get all experiments (most recent first)"""
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
    
    def get_best_configs(self, 
                        min_quality: float = 7.0,
                        max_cost: float = 0.01,
                        limit: int = 10) -> List[Dict]:
        """Find best configurations meeting quality and cost constraints"""
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
        """Analyze costs across experiments"""
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
        """Compare performance across different models"""
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
    
    def export_to_json(self, output_file: str):
        """Export all data to JSON for backup/analysis"""
        experiments = self.get_all_experiments(limit=10000)
        
        with open(output_file, 'w') as f:
            json.dump({
                'exported_at': datetime.now().isoformat(),
                'total_experiments': len(experiments),
                'experiments': experiments
            }, f, indent=2)
        
        print(f"✅ Exported {len(experiments)} experiments to {output_file}")
    
    def get_stats_summary(self) -> str:
        """Get a formatted summary of database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM experiments")
            total_exp = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(judge_score), MAX(judge_score), MIN(judge_score) FROM quality_scores")
            quality_stats = cursor.fetchone()
            
            cursor.execute("SELECT SUM(total_cost_usd), AVG(total_cost_usd) FROM results")
            cost_stats = cursor.fetchone()
            
            avg_qual = f"{quality_stats[0]:.2f}/10" if quality_stats[0] else 'N/A'
            best_qual = f"{quality_stats[1]:.2f}/10" if quality_stats[1] else 'N/A'
            worst_qual = f"{quality_stats[2]:.2f}/10" if quality_stats[2] else 'N/A'
            total_cost = f"${cost_stats[0]:.4f}" if cost_stats[0] else '$0.00'
            avg_cost = f"${cost_stats[1]:.4f}" if cost_stats[1] else '$0.00'
            
            return f"""
📊 Experiment Database Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Experiments: {total_exp}
  
  Quality Scores:
    Average: {avg_qual}
    Best:    {best_qual}
    Worst:   {worst_qual}
  
  Costs:
    Total Spent:  {total_cost}
    Average/Exp:  {avg_cost}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """.strip()


# CLI for database queries
if __name__ == "__main__":
    import sys
    
    db = ExperimentDB()
    
    if len(sys.argv) < 2:
        print(db.get_stats_summary())
        print("\nUsage:")
        print("  python -m src.aicl.experiment_db stats          # Show statistics")
        print("  python -m src.aicl.experiment_db list           # List all experiments")
        print("  python -m src.aicl.experiment_db best           # Show best configs")
        print("  python -m src.aicl.experiment_db models         # Model performance")
        print("  python -m src.aicl.experiment_db export <file>  # Export to JSON")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "stats":
        print(db.get_stats_summary())
    
    elif command == "list":
        experiments = db.get_all_experiments()
        print(f"\n📋 Recent Experiments ({len(experiments)})\n")
        for exp in experiments[:20]:
            score = f"{exp['judge_score']}" if exp['judge_score'] is not None else 'N/A'
            print(f"  {exp['experiment_id']:<30} | Score: {score:<5} | Cost: ${exp['total_cost_usd'] or 0:.4f}")
    
    elif command == "best":
        best = db.get_best_configs()
        print(f"\n🏆 Best Configurations (Quality ≥7, Cost ≤$0.01)\n")
        for cfg in best:
            print(f"  {cfg['experiment_id']:<30}")
            print(f"    Model: {cfg['chat_model']}, Embedding: {cfg['embedding_model']}")
            print(f"    Score: {cfg['judge_score']:.1f}/10, Cost: ${cfg['total_cost_usd']:.4f}, Latency: {cfg['latency_ms']:.0f}ms")
            print()
    
    elif command == "models":
        models = db.get_model_performance()
        print(f"\n📊 Model Performance Comparison\n")
        print(f"{'Chat Model':<30} {'Embedding':<30} {'Experiments':<12} {'Avg Quality':<12} {'Avg Cost':<12} {'Avg Latency'}")
        print("-" * 120)
        for m in models:
            print(f"{m['chat_model']:<30} {m['embedding_model']:<30} {m['num_experiments']:<12} {m['avg_quality'] or 'N/A':<12} ${m['avg_cost'] or 0:<11.4f} {m['avg_latency'] or 'N/A':<12.0f}ms")
    
    elif command == "export":
        output = sys.argv[2] if len(sys.argv) > 2 else "experiments/export.json"
        db.export_to_json(output)
    
    else:
        print(f"❌ Unknown command: {command}")
