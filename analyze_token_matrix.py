#!/usr/bin/env python3
"""Analyze 3x3 Token Size x Model Matrix Results"""

import json
from pathlib import Path
from tabulate import tabulate

def main():
    results_dir = Path("experiments/token-matrix-results")
    
    # Collect all metrics
    metrics = []
    
    for state_file in sorted(results_dir.glob("*.tfstate")):
        exp_id = state_file.stem
        parts = exp_id.split('_')
        model_name = parts[0]
        token_size = parts[1]
        
        with open(state_file) as f:
            state = json.load(f)
        
        # Extract resource data
        resources = state.get('resources', {})
        for resource_id, resource_data in resources.items():
            if resource_data.get('type') == 'chat':
                attrs = resource_data.get('attributes', {})
                usage = attrs.get('usage', {})
                perf = attrs.get('performance', {})
                cost_data = attrs.get('cost', {})
                
                metrics.append({
                    'model': model_name.upper(),
                    'token_limit': token_size,
                    'prompt_tokens': int(usage.get('prompt_tokens', 0)),
                    'completion_tokens': int(usage.get('completion_tokens', 0)),
                    'total_tokens': int(usage.get('total_tokens', 0)),
                    'cost': float(cost_data.get('total_usd', 0)),
                    'cost_source': cost_data.get('source', 'unknown'),
                    'response_time_ms': int(perf.get('response_time_ms', 0)),
                    'tokens_per_sec': int(perf.get('tokens_per_second', 0)),
                    'response_length': len(attrs.get('response', ''))
                })
    
    # Display results
    print("\n" + "="*100)
    print("🎯 3x3 TOKEN SIZE x CODE MODEL MATRIX RESULTS")
    print("="*100 + "\n")
    
    # Table data
    table_data = []
    for m in sorted(metrics, key=lambda x: (x['model'], ['small', 'medium', 'large'].index(x['token_limit']))):
        table_data.append([
            m['model'],
            m['token_limit'].capitalize(),
            m['token_limit'].replace('small', '500').replace('medium', '1500').replace('large', '3000'),
            m['completion_tokens'],
            f"${m['cost']:.6f}",
            m['cost_source'],
            f"{m['response_time_ms']:,}",
            m['tokens_per_sec'],
            m['response_length']
        ])
    
    headers = ['Model', 'Size', 'Limit', 'Tokens Used', 'Cost', 'Source', 'Time (ms)', 'Tok/sec', 'Chars']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Analysis by model
    print("\n" + "="*100)
    print("📊 PERFORMANCE BY MODEL")
    print("="*100 + "\n")
    
    for model in sorted(set(m['model'] for m in metrics)):
        model_metrics = [m for m in metrics if m['model'] == model]
        avg_cost = sum(m['cost'] for m in model_metrics) / len(model_metrics)
        avg_time = sum(m['response_time_ms'] for m in model_metrics) / len(model_metrics)
        avg_tokens = sum(m['completion_tokens'] for m in model_metrics) / len(model_metrics)
        avg_speed = sum(m['tokens_per_sec'] for m in model_metrics) / len(model_metrics)
        
        print(f"{model}:")
        print(f"  Average Cost:         ${avg_cost:.6f}")
        print(f"  Average Response Time: {avg_time:.0f}ms")
        print(f"  Average Tokens:        {avg_tokens:.0f}")
        print(f"  Average Speed:         {avg_speed:.0f} tokens/sec")
        print()
    
    # Token size impact
    print("="*100)
    print("📈 TOKEN SIZE IMPACT")
    print("="*100 + "\n")
    
    for size in ['small', 'medium', 'large']:
        size_metrics = [m for m in metrics if m['token_limit'] == size]
        avg_tokens = sum(m['completion_tokens'] for m in size_metrics) / len(size_metrics)
        avg_cost = sum(m['cost'] for m in size_metrics) / len(size_metrics)
        limit = size.replace('small', '500').replace('medium', '1500').replace('large', '3000')
        
        print(f"{size.upper()} ({limit} token limit):")
        print(f"  Average tokens used: {avg_tokens:.0f}")
        print(f"  Average cost:        ${avg_cost:.6f}")
        print(f"  Utilization:         {(avg_tokens/int(limit))*100:.1f}%")
        print()
    
    # Cost comparison
    print("="*100)
    print("💰 COST COMPARISON")
    print("="*100 + "\n")
    
    total_costs = {}
    for m in metrics:
        if m['model'] not in total_costs:
            total_costs[m['model']] = 0
        total_costs[m['model']] += m['cost']
    
    sorted_costs = sorted(total_costs.items(), key=lambda x: x[1])
    cheapest = sorted_costs[0]
    
    for model, total_cost in sorted_costs:
        vs_cheapest = ((total_cost - cheapest[1]) / cheapest[1] * 100) if cheapest[1] > 0 else 0
        print(f"{model}: ${total_cost:.6f} total", end="")
        if model != cheapest[0]:
            print(f" ({vs_cheapest:+.1f}% vs {cheapest[0]})", end="")
        print()

if __name__ == '__main__':
    main()
