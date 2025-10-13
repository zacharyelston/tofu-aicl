#!/usr/bin/env python3
"""
Example usage of v2 storage layer

Demonstrates in-memory and SQLite storage for experiment tracking
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from v2.storage import InMemoryStorage, SQLiteStorage
import json


def example_in_memory():
    """Example: In-memory storage (free CLI default)"""
    print("=" * 70)
    print("EXAMPLE 1: In-Memory Storage (Free CLI)")
    print("=" * 70)
    
    storage = InMemoryStorage()
    
    # Save experiments
    experiments = [
        {
            "id": "gpt4o-test-001",
            "config": {
                "chat_model": "gpt-4o",
                "embedding_model": "text-embedding-3-small",
                "temperature": 0.7,
                "max_tokens": 500
            },
            "results": {
                "total_cost_usd": 0.0035,
                "total_tokens": 1250,
                "latency_ms": 2340,
                "success": True
            },
            "quality": {
                "judge_model": "gpt-4o",
                "judge_score": 8.5,
                "judge_feedback": "Excellent response, accurate and complete"
            }
        },
        {
            "id": "gpt4o-mini-test-001",
            "config": {
                "chat_model": "gpt-4o-mini",
                "embedding_model": "text-embedding-3-small",
                "temperature": 0.7,
                "max_tokens": 500
            },
            "results": {
                "total_cost_usd": 0.0008,
                "total_tokens": 1180,
                "latency_ms": 1850,
                "success": True
            },
            "quality": {
                "judge_model": "gpt-4o",
                "judge_score": 7.8,
                "judge_feedback": "Good response, slightly less detailed"
            }
        }
    ]
    
    for exp in experiments:
        storage.save_experiment(
            experiment_id=exp["id"],
            config=exp["config"],
            results=exp["results"],
            quality=exp["quality"]
        )
    
    print(f"\n✅ Saved {len(storage)} experiments\n")
    
    # Analyze
    print("📊 Cost Analysis:")
    cost_analysis = storage.get_cost_analysis()
    print(json.dumps(cost_analysis, indent=2))
    
    print("\n🏆 Best Configurations (quality >= 7.0, cost <= $0.01):")
    best_configs = storage.get_best_configs(min_quality=7.0, max_cost=0.01)
    for config in best_configs:
        print(f"  • {config['experiment_id']}: "
              f"Quality {config.get('judge_score', 0):.1f}, "
              f"Cost ${config.get('total_cost_usd', 0):.4f}")
    
    print("\n📈 Model Performance:")
    model_perf = storage.get_model_performance()
    for perf in model_perf:
        print(f"  • {perf['chat_model']}: "
              f"Quality {perf.get('avg_quality') or 0:.1f}/10, "
              f"Cost ${perf['avg_cost']:.4f}")
    
    print()


def example_sqlite():
    """Example: SQLite storage (user-configured persistence)"""
    print("=" * 70)
    print("EXAMPLE 2: SQLite Storage (Persistent)")
    print("=" * 70)
    
    db_path = "/tmp/test_experiments.db"
    
    # Create database
    storage = SQLiteStorage(db_path, create_if_missing=True)
    
    # Save experiment
    storage.save_experiment(
        experiment_id="claude-test-001",
        config={
            "chat_model": "claude-3-5-sonnet",
            "temperature": 0.5,
            "max_tokens": 1000
        },
        results={
            "total_cost_usd": 0.0045,
            "total_tokens": 1500,
            "latency_ms": 1200,
            "success": True
        },
        quality={
            "judge_model": "gpt-4o",
            "judge_score": 9.2,
            "judge_feedback": "Exceptional reasoning and accuracy"
        }
    )
    
    print(f"\n✅ Saved experiment to {db_path}")
    print(f"📁 Database: {storage}")
    
    # Retrieve
    experiment = storage.get_experiment("claude-test-001")
    if experiment:
        print(f"\n🔍 Retrieved Experiment:")
        print(f"  Model: {experiment.get('chat_model')}")
        print(f"  Quality: {experiment.get('judge_score'):.1f}/10")
        print(f"  Cost: ${experiment.get('total_cost_usd'):.4f}")
        print(f"  Feedback: {experiment.get('judge_feedback')}")
    
    # Export
    print(f"\n💾 Export to JSON:")
    export_data = storage.export_data(format="json")
    export_json = json.loads(export_data)
    print(f"  Total experiments: {export_json['total_experiments']}")
    print(f"  Storage type: {export_json['storage_type']}")
    print(f"  Schema version: {export_json['schema_version']}")
    
    print()


def example_comparison():
    """Example: Compare in-memory vs SQLite"""
    print("=" * 70)
    print("EXAMPLE 3: Storage Comparison")
    print("=" * 70)
    
    # In-memory
    mem_storage = InMemoryStorage()
    mem_storage.save_experiment(
        experiment_id="test-mem",
        config={"model": "gpt-4o"},
        results={"cost": 0.001}
    )
    
    # SQLite
    sql_storage = SQLiteStorage("/tmp/compare.db", create_if_missing=True)
    sql_storage.save_experiment(
        experiment_id="test-sql",
        config={"model": "gpt-4o"},
        results={"cost": 0.001}
    )
    
    print("\n📊 Feature Comparison:")
    print(f"{'Feature':<25} {'In-Memory':<15} {'SQLite':<15}")
    print("-" * 55)
    print(f"{'Setup Required':<25} {'No':<15} {'Yes':<15}")
    print(f"{'Persistent':<25} {'No':<15} {'Yes':<15}")
    print(f"{'Speed':<25} {'Very Fast':<15} {'Fast':<15}")
    print(f"{'Cost':<25} {'Free':<15} {'Free':<15}")
    print(f"{'Use Case':<25} {'Quick tests':<15} {'Long-term':<15}")
    print(f"{'Multi-user':<25} {'No':<15} {'No':<15}")
    
    print("\n💡 Recommendation:")
    print("  • Use in-memory for quick experiments and CI/CD")
    print("  • Use SQLite for personal projects needing history")
    print("  • Use PostgreSQL (future) for team/production")
    
    print()


if __name__ == "__main__":
    example_in_memory()
    example_sqlite()
    example_comparison()
    
    print("=" * 70)
    print("✅ Storage layer ready for SQL experiments!")
    print("=" * 70)
