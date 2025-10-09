#!/usr/bin/env python3
"""
RAG Performance Analysis - Compare code analysis quality with metrics
"""

import json
import sys
from pathlib import Path

def load_state_file(path):
    """Load state file"""
    with open(path) as f:
        return json.load(f)

def load_summary(results_dir):
    """Load summary"""
    with open(Path(results_dir) / 'rag_matrix_summary.json') as f:
        return json.load(f)

def extract_metrics(state):
    """Extract all metrics from state"""
    metrics = {
        'experiment_id': state.get('experiment_id', 'unknown'),
        'response': None,
        'response_length': 0,
        'model': None,
        'usage': {},
        'performance': {},
        'cost': {}
    }
    
    # Find chat resource
    for res_id, res_data in state.get('resources', {}).items():
        if res_data.get('type') == 'chat':
            attrs = res_data.get('attributes', {})
            
            metrics['response'] = attrs.get('response', '')
            metrics['response_length'] = len(metrics['response'])
            metrics['model'] = attrs.get('model', 'unknown')
            metrics['usage'] = attrs.get('usage', {})
            metrics['performance'] = attrs.get('performance', {})
            metrics['cost'] = attrs.get('cost', {})
            break
    
    return metrics

def analyze_rag_performance(results_dir="experiments/rag-matrix-results"):
    """Analyze RAG experiment performance"""
    results_dir = Path(results_dir)
    
    print("=" * 90)
    print(" " * 25 + "🔬 RAG PERFORMANCE ANALYSIS")
    print("=" * 90)
    
    summary = load_summary(results_dir)
    
    # Load all experiments
    analyses = []
    for exp in summary['experiments']:
        if exp.get('state_file'):
            state = load_state_file(exp['state_file'])
            metrics = extract_metrics(state)
            metrics['question'] = exp['experiment_id'].split('_', 1)[1] if '_' in exp['experiment_id'] else 'unknown'
            analyses.append(metrics)
    
    # Display metrics table
    print("\n📊 PERFORMANCE METRICS\n")
    print("┌─" + "─" * 88 + "┐")
    print("│ Experiment       │ Tokens  │ Time (ms) │ Cost ($)  │ Tok/sec │ Response Length │")
    print("├─" + "─" * 88 + "┤")
    
    for analysis in analyses:
        exp_id = analysis['experiment_id'][:15]
        total_tokens = analysis['usage'].get('total_tokens', 0)
        response_time = analysis['performance'].get('response_time_ms', 0)
        cost = analysis['cost'].get('estimated_usd', 0.0)
        tok_per_sec = analysis['performance'].get('tokens_per_second', 0)
        resp_len = analysis['response_length']
        
        print(f"│ {exp_id:<17}│ {total_tokens:<8}│ {response_time:<10}│ {cost:<10.6f}│ {tok_per_sec:<8}│ {resp_len:<16}│")
    
    print("└─" + "─" * 88 + "┘")
    
    # Show responses
    print("\n💬 CODE ANALYSIS RESPONSES\n")
    
    for analysis in analyses:
        print("─" * 90)
        print(f"🧪 {analysis['experiment_id'].upper()}")
        print(f"Model: {analysis['model']}")
        print(f"Question: {analysis['question']}")
        print(f"\nResponse ({analysis['response_length']} chars):")
        print(f"{analysis['response'][:500]}..." if len(analysis['response']) > 500 else analysis['response'])
        
        print(f"\n📈 Metrics:")
        print(f"  • Tokens: {analysis['usage'].get('total_tokens', 0)} (prompt: {analysis['usage'].get('prompt_tokens', 0)}, completion: {analysis['usage'].get('completion_tokens', 0)})")
        print(f"  • Time: {analysis['performance'].get('response_time_ms', 0)}ms")
        print(f"  • Speed: {analysis['performance'].get('tokens_per_second', 0)} tok/sec")
        print(f"  • Cost: ${analysis['cost'].get('estimated_usd', 0.0):.6f}")
    
    print("\n" + "─" * 90)
    
    # Comparative analysis
    print("\n🏆 COMPARATIVE ANALYSIS\n")
    
    # Group by model
    by_model = {}
    for analysis in analyses:
        model = analysis['model']
        if model not in by_model:
            by_model[model] = []
        by_model[model].append(analysis)
    
    for model, experiments in by_model.items():
        model_name = model.split('/')[-1]
        avg_tokens = sum(e['usage'].get('total_tokens', 0) for e in experiments) / len(experiments)
        avg_time = sum(e['performance'].get('response_time_ms', 0) for e in experiments) / len(experiments)
        avg_cost = sum(e['cost'].get('estimated_usd', 0) for e in experiments) / len(experiments)
        avg_length = sum(e['response_length'] for e in experiments) / len(experiments)
        
        print(f"📌 {model_name.upper()}")
        print(f"   Avg Tokens: {avg_tokens:.1f}")
        print(f"   Avg Time: {avg_time:.0f}ms")
        print(f"   Avg Cost: ${avg_cost:.6f}")
        print(f"   Avg Response Length: {avg_length:.1f} chars")
        print()
    
    # Efficiency metrics
    print("💰 COST & EFFICIENCY COMPARISON\n")
    
    if len(by_model) >= 2:
        models = list(by_model.items())
        model1_name, model1_data = models[0]
        model2_name, model2_data = models[1]
        
        model1_avg_cost = sum(e['cost'].get('estimated_usd', 0) for e in model1_data) / len(model1_data)
        model2_avg_cost = sum(e['cost'].get('estimated_usd', 0) for e in model2_data) / len(model2_data)
        
        if model1_avg_cost > model2_avg_cost:
            diff = ((model1_avg_cost - model2_avg_cost) / model2_avg_cost) * 100
            print(f"  • {model1_name.split('/')[-1]} is {diff:.1f}% more expensive than {model2_name.split('/')[-1]}")
        else:
            diff = ((model2_avg_cost - model1_avg_cost) / model1_avg_cost) * 100
            print(f"  • {model2_name.split('/')[-1]} is {diff:.1f}% more expensive than {model1_name.split('/')[-1]}")
        
        model1_avg_time = sum(e['performance'].get('response_time_ms', 0) for e in model1_data) / len(model1_data)
        model2_avg_time = sum(e['performance'].get('response_time_ms', 0) for e in model2_data) / len(model2_data)
        
        if model1_avg_time < model2_avg_time:
            print(f"  • {model1_name.split('/')[-1]} is faster ({model1_avg_time:.0f}ms vs {model2_avg_time:.0f}ms)")
        else:
            print(f"  • {model2_name.split('/')[-1]} is faster ({model2_avg_time:.0f}ms vs {model1_avg_time:.0f}ms)")
    
    print("\n" + "=" * 90)

def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "experiments/rag-matrix-results"
    analyze_rag_performance(results_dir)

if __name__ == '__main__':
    main()
