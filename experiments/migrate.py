#!/usr/bin/env python3
"""
Migrate existing experiment results to DocDB

Usage:
    python experiments/migrate.py --source azure_experiment_results.json --id azure_security_2025_10_13
"""

import argparse
import json
import sys
from datetime import datetime
from experiments.storage import ExperimentDocDB


def migrate_json_file(db: ExperimentDocDB, source_file: str, experiment_id: str):
    """Migrate a JSON results file to DocDB"""
    
    with open(source_file) as f:
        data = json.load(f)
    
    # Extract components
    outputs = {
        'steps': data.get('steps', []),
        'total_tokens': data.get('total_tokens', 0)
    }
    
    # Parse timestamp
    timestamp_str = data.get('timestamp', datetime.now().isoformat())
    run_timestamp = datetime.fromisoformat(timestamp_str)
    
    # Build metadata
    metadata = {
        'provider': 'azure_openai',
        'deployment': data.get('deployment', 'unknown'),
        'total_cost': outputs['total_tokens'] * 0.000001,  # Rough estimate
        'tags': ['migrated', 'azure', 'security']
    }
    
    # Calculate quality score from steps if available
    for step in outputs.get('steps', []):
        if 'grade' in step.get('description', '').lower():
            try:
                grade_output = step.get('output', '')
                if 'score' in grade_output:
                    import re
                    match = re.search(r'"score":\s*(\d+)', grade_output)
                    if match:
                        metadata['quality_score'] = int(match.group(1))
            except:
                pass
    
    # Save to DocDB
    doc_id = db.save_experiment(
        experiment_id=experiment_id,
        outputs=outputs,
        config_file=None,
        config_content=None,
        metadata=metadata,
        run_timestamp=run_timestamp
    )
    
    print(f"✅ Migrated {source_file} to DocDB")
    print(f"   Experiment ID: {experiment_id}")
    print(f"   Document ID: {doc_id}")
    print(f"   Timestamp: {run_timestamp}")
    print(f"   Tokens: {outputs['total_tokens']}")
    
    return doc_id


def main():
    parser = argparse.ArgumentParser(description='Migrate experiment results to DocDB')
    parser.add_argument('--source', required=True, help='Source JSON file')
    parser.add_argument('--id', dest='experiment_id', required=True, help='Experiment ID')
    
    args = parser.parse_args()
    
    try:
        db = ExperimentDocDB()
    except ValueError as e:
        print(f"❌ Database not configured: {e}")
        print("💡 Set DATABASE_URL environment variable")
        sys.exit(1)
    
    try:
        migrate_json_file(db, args.source, args.experiment_id)
    except FileNotFoundError:
        print(f"❌ File not found: {args.source}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
