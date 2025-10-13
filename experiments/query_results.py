#!/usr/bin/env python3
"""
Query and compare experiment results from DocDB

Usage:
    python experiments/query_results.py --experiment-id azure_security
    python experiments/query_results.py --best --by cost
    python experiments/query_results.py --list
    python experiments/query_results.py --compare exp1,exp2,exp3
"""

import argparse
import json
import sys
from datetime import datetime
from experiments.storage import ExperimentDocDB


def main():
    parser = argparse.ArgumentParser(description='Query experiment results')
    
    parser.add_argument('--experiment-id', help='Get specific experiment by ID')
    parser.add_argument('--list', action='store_true', help='List all experiments')
    parser.add_argument('--best', action='store_true', help='Get best experiments')
    parser.add_argument('--by', choices=['cost', 'tokens', 'quality'], default='cost', help='Metric to sort by')
    parser.add_argument('--compare', help='Compare experiments (comma-separated IDs)')
    parser.add_argument('--provider', help='Filter by provider')
    parser.add_argument('--limit', type=int, default=10, help='Max results')
    parser.add_argument('--export', help='Export to JSON file')
    
    args = parser.parse_args()
    
    try:
        db = ExperimentDocDB()
    except ValueError as e:
        print(f"❌ Database not configured: {e}")
        print("💡 Set DATABASE_URL environment variable or use Replit PostgreSQL")
        sys.exit(1)
    
    # List all experiments
    if args.list:
        experiments = db.list_all(limit=args.limit)
        print(f"\n📊 Experiments (last {args.limit}):")
        print("="*70)
        for exp in experiments:
            print(f"\n  ID: {exp['experiment_id']}")
            print(f"  Timestamp: {exp['run_timestamp']}")
            print(f"  Provider: {exp.get('provider', 'N/A')}")
            print(f"  Tokens: {exp.get('total_tokens', 'N/A')}")
            if exp.get('tags'):
                print(f"  Tags: {exp['tags']}")
        return
    
    # Get specific experiment
    if args.experiment_id:
        doc = db.get_by_id(args.experiment_id)
        if doc:
            print(f"\n📄 Experiment: {args.experiment_id}")
            print("="*70)
            print(json.dumps(doc, indent=2, default=str))
            
            if args.export:
                db.export_to_json(args.experiment_id, args.export)
                print(f"\n✅ Exported to {args.export}")
        else:
            print(f"❌ Experiment '{args.experiment_id}' not found")
        return
    
    # Compare experiments
    if args.compare:
        exp_ids = [eid.strip() for eid in args.compare.split(',')]
        comparison = db.compare(exp_ids)
        
        print(f"\n🔍 Comparing {len(exp_ids)} experiments:")
        print("="*70)
        
        for exp in comparison['experiments']:
            print(f"\n  {exp['experiment_id']} ({exp['provider']})")
            print(f"    Timestamp: {exp['run_timestamp']}")
            print(f"    Cost: ${exp.get('total_cost', 'N/A')}")
            print(f"    Tokens: {exp.get('total_tokens', 'N/A')}")
            print(f"    Quality: {exp.get('quality_score', 'N/A')}/100")
        
        print(f"\n📈 Metrics Summary:")
        for metric, stats in comparison['metrics'].items():
            print(f"\n  {metric}:")
            print(f"    Min: {stats['min']}")
            print(f"    Max: {stats['max']}")
            print(f"    Avg: {stats['avg']:.2f}")
        return
    
    # Get best experiments
    if args.best:
        metric_map = {
            'cost': 'total_cost',
            'tokens': 'total_tokens',
            'quality': 'quality_score'
        }
        
        metric = metric_map[args.by]
        ascending = args.by != 'quality'  # Quality: higher is better
        
        results = db.get_best(
            by_metric=metric,
            ascending=ascending,
            provider=args.provider,
            limit=args.limit
        )
        
        print(f"\n🏆 Best experiments by {args.by}:")
        print("="*70)
        
        for i, exp in enumerate(results, 1):
            metadata = exp.get('metadata', {})
            outputs = exp.get('outputs', {})
            
            print(f"\n  {i}. {exp['experiment_id']}")
            print(f"     Provider: {metadata.get('provider', 'N/A')}")
            print(f"     Timestamp: {exp['run_timestamp']}")
            
            if args.by == 'cost':
                print(f"     Cost: ${metadata.get('total_cost', 'N/A')}")
            elif args.by == 'tokens':
                print(f"     Tokens: {outputs.get('total_tokens', 'N/A')}")
            elif args.by == 'quality':
                print(f"     Quality Score: {metadata.get('quality_score', 'N/A')}/100")
        return
    
    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    main()
