#!/usr/bin/env python3
"""
Test PostgreSQL storage adapter

This test demonstrates PostgreSQL storage usage and verifies the implementation.
Requires a PostgreSQL database (Replit managed or external).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from v2.storage import PostgreSQLStorage


def test_postgres_storage():
    """Test PostgreSQL storage with Replit database or external PostgreSQL"""
    
    print("=" * 70)
    print("PostgreSQL Storage Test")
    print("=" * 70)
    
    # Check for DATABASE_URL (Replit managed)
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("\n⚠️  No DATABASE_URL found.")
        print("\nTo test PostgreSQL storage:")
        print("  1. Replit managed: Create database in Replit UI")
        print("  2. External: Set DATABASE_URL environment variable")
        print("\nExample:")
        print("  export DATABASE_URL='postgresql://user:pass@host:5432/db'")
        print("  python v2/storage/test_postgres.py")
        return
    
    try:
        # Initialize storage (create schema)
        print(f"\n📡 Connecting to PostgreSQL...")
        storage = PostgreSQLStorage(create_if_missing=True)
        print(f"✅ Storage initialized: {storage}")
        
        # Save test experiment
        print(f"\n💾 Saving test experiment...")
        storage.save_experiment(
            experiment_id="postgres-test-001",
            config={
                "chat_model": "gpt-4o",
                "embedding_model": "text-embedding-3-small",
                "temperature": 0.7,
                "provider": "openai"
            },
            results={
                "total_cost_usd": 0.0042,
                "total_tokens": 1380,
                "latency_ms": 2100,
                "success": True
            },
            quality={
                "judge_model": "gpt-4o",
                "judge_score": 8.7,
                "judge_feedback": "Excellent accuracy and completeness"
            }
        )
        print("✅ Experiment saved successfully")
        
        # Retrieve experiment
        print(f"\n🔍 Retrieving experiment...")
        experiment = storage.get_experiment("postgres-test-001")
        if experiment:
            print(f"  Model: {experiment.get('chat_model')}")
            print(f"  Quality: {experiment.get('judge_score'):.1f}/10")
            print(f"  Cost: ${experiment.get('total_cost_usd'):.4f}")
        
        # Cost analysis
        print(f"\n📊 Cost Analysis:")
        cost_analysis = storage.get_cost_analysis()
        print(f"  Total experiments: {cost_analysis.get('total_experiments', 0)}")
        print(f"  Average cost: ${cost_analysis.get('avg_cost', 0):.4f}")
        print(f"  Total spent: ${cost_analysis.get('total_spent', 0):.4f}")
        
        # Export data
        print(f"\n💾 Export capability:")
        export_data = storage.export_data(format="json")
        import json
        export_json = json.loads(export_data)
        print(f"  Schema version: {export_json['schema_version']}")
        print(f"  Storage type: {export_json['storage_type']}")
        print(f"  Total experiments: {export_json['total_experiments']}")
        
        print(f"\n✅ PostgreSQL storage working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check DATABASE_URL is correct")
        print("  2. Verify PostgreSQL is running")
        print("  3. Check database credentials")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_postgres_storage()
