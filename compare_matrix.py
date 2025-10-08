#!/usr/bin/env python3
"""
Matrix Comparison Tool - Analyze experiment results
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def load_state_file(path):
    """Load and parse a state file"""
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None

def load_summary(results_dir):
    """Load matrix summary"""
    summary_path = Path(results_dir) / 'matrix_summary.json'
    if summary_path.exists():
        with open(summary_path) as f:
            return json.load(f)
    return None

def compare_experiments(results_dir="experiments/matrix-results"):
    """Compare all experiments in results directory"""
    results_dir = Path(results_dir)
    
    print("=" * 80)
    print("📊 MATRIX EXPERIMENT COMPARISON")
    print("=" * 80)
    
    # Load summary
    summary = load_summary(results_dir)
    if summary:
        print(f"\n📈 Summary Statistics:")
        print(f"  Total Experiments: {summary['total_experiments']}")
        print(f"  Successful: {summary['successful']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Timestamp: {summary['timestamp']}")
    
    # Load all state files
    print(f"\n🔍 Analyzing State Files:")
    print(f"  Location: {results_dir}/")
    
    state_files = list(results_dir.glob("*.tfstate"))
    print(f"  Found: {len(state_files)} state files\n")
    
    # Analyze each state file
    comparisons = []
    
    for state_file in sorted(state_files):
        exp_id = state_file.stem
        state = load_state_file(state_file)
        
        if state:
            analysis = {
                'id': exp_id,
                'file': state_file.name,
                'version': state.get('version'),
                'lineage': state.get('lineage'),
                'serial': state.get('serial'),
                'resources_count': len(state.get('resources', {})),
                'resources': state.get('resources', {})
            }
            comparisons.append(analysis)
    
    # Display comparison
    print("┌─" + "─" * 78 + "┐")
    print("│ " + "EXPERIMENT RESULTS".center(78) + " │")
    print("├─" + "─" * 78 + "┤")
    
    for comp in comparisons:
        serial = comp.get('serial', 'N/A') or 'N/A'
        print(f"│ 🧪 {comp['id']:<30} │ Resources: {comp['resources_count']:<10} │ Serial: {str(serial):<10} │")
        
        # Show resource details
        for res_id, res_data in list(comp['resources'].items())[:3]:  # Show first 3
            res_type = res_data.get('type', 'unknown')
            provider = res_data.get('provider', 'unknown')
            print(f"│    └─ {res_id[:40]:<40} │ {res_type}/{provider:<20} │")
    
    print("└─" + "─" * 78 + "┘")
    
    # Variables comparison
    if summary and 'experiments' in summary:
        print(f"\n📋 Variable Matrix:")
        print("┌─" + "─" * 78 + "┐")
        
        for exp in summary['experiments']:
            exp_id = exp.get('experiment_id', 'unknown')
            metrics = exp.get('metrics', {})
            print(f"│ {exp_id:<20} │ Status: {'✅' if exp.get('returncode') == 0 else '❌':<3} │ Resources: {metrics.get('resources_created', 0):<5} │")
        
        print("└─" + "─" * 78 + "┘")
    
    # Generate insights
    print(f"\n💡 Insights:")
    total_resources = sum(c['resources_count'] for c in comparisons)
    avg_resources = total_resources / len(comparisons) if comparisons else 0
    print(f"  • Average resources per experiment: {avg_resources:.1f}")
    print(f"  • Total state files collected: {len(state_files)}")
    print(f"  • All experiments stored in: {results_dir}/")
    
    print(f"\n✨ Next Steps:")
    print(f"  1. State files are ready for detailed analysis")
    print(f"  2. Use these files to compare provider performance")
    print(f"  3. Build dashboards or reports from this data")
    
    return comparisons

def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "experiments/matrix-results"
    compare_experiments(results_dir)

if __name__ == '__main__':
    main()
