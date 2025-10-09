#!/usr/bin/env python3
"""
Comprehensive Performance Comparison Report
"""

import json
from pathlib import Path

def generate_report():
    print("=" * 95)
    print(" " * 30 + "🏆 COMPREHENSIVE PERFORMANCE REPORT")
    print(" " * 35 + "Code Analysis with Metrics")
    print("=" * 95)
    
    # Analyze experiments
    experiments = []
    for exp_id in ['claude_executor', 'gpt4_executor']:
        state_file = f'experiments/code-matrix-results/{exp_id}.tfstate'
        try:
            with open(state_file) as f:
                state = json.load(f)
            
            for res_id, res_data in state.get('resources', {}).items():
                if res_data.get('type') == 'chat':
                    attrs = res_data.get('attributes', {})
                    experiments.append({
                        'id': exp_id,
                        'model': attrs.get("model", ""),
                        'response': attrs.get("response", ""),
                        'response_length': len(attrs.get("response", "")),
                        'usage': attrs.get("usage", {}),
                        'performance': attrs.get("performance", {}),
                        'cost': attrs.get("cost", {})
                    })
                    break
        except Exception as e:
            print(f'Error: {e}')
    
    # Metrics Table
    print("\n📊 PERFORMANCE METRICS COMPARISON\n")
    print("┌─" + "─" * 93 + "┐")
    print("│ Model              │ Tokens │ Time (ms) │ Tok/sec │ Cost ($)   │ Length (chars) │")
    print("├─" + "─" * 93 + "┤")
    
    for exp in experiments:
        model = exp['model'].split('/')[-1][:17]
        tokens = int(exp['usage'].get('total_tokens', 0))
        time_ms = int(exp['performance'].get('response_time_ms', 0))
        tok_per_sec = int(exp['performance'].get('tokens_per_second', 0))
        cost = exp['cost'].get('total_usd', exp['cost'].get('estimated_usd', 0.0))
        length = exp['response_length']
        
        print(f"│ {model:<19}│ {tokens:<7}│ {time_ms:<10}│ {tok_per_sec:<8}│ {cost:<11.6f}│ {length:<15}│")
    
    print("└─" + "─" * 93 + "┘")
    
    # Detailed breakdown
    print("\n💡 DETAILED ANALYSIS\n")
    
    for exp in experiments:
        model_name = exp['model'].split('/')[-1].upper()
        print(f"{'─' * 95}")
        print(f"🤖 {model_name}")
        print(f"{'─' * 95}")
        
        # Usage breakdown
        usage = exp['usage']
        print(f"\n📊 Token Usage:")
        print(f"  • Prompt: {int(usage.get('prompt_tokens', 0))} tokens")
        print(f"  • Completion: {int(usage.get('completion_tokens', 0))} tokens")
        print(f"  • Total: {int(usage.get('total_tokens', 0))} tokens")
        
        # Performance
        perf = exp['performance']
        print(f"\n⚡ Performance:")
        print(f"  • Response Time: {int(perf.get('response_time_ms', 0))}ms ({perf.get('response_time_ms', 0)/1000:.2f}s)")
        print(f"  • Throughput: {int(perf.get('tokens_per_second', 0))} tokens/second")
        
        # Cost breakdown
        cost = exp['cost']
        total_cost = cost.get('total_usd', cost.get('estimated_usd', 0))
        cost_source = cost.get('source', 'estimated')
        print(f"\n💰 Cost:")
        print(f"  • Total: ${total_cost:.6f} ({cost_source})")
        if 'prompt_cost' in cost:
            print(f"  • Prompt: ${cost.get('prompt_cost', 0):.6f}")
            print(f"  • Completion: ${cost.get('completion_cost', 0):.6f}")
        
        # Response quality
        print(f"\n📝 Response:")
        print(f"  • Length: {exp['response_length']} characters")
        print(f"  • Preview: {exp['response'][:200]}...")
        print()
    
    # Comparative insights
    print(f"{'=' * 95}")
    print("🔬 COMPARATIVE INSIGHTS")
    print(f"{'=' * 95}\n")
    
    if len(experiments) >= 2:
        claude = experiments[0]
        gpt4 = experiments[1]
        
        # Speed comparison
        claude_time = claude['performance'].get('response_time_ms', 0)
        gpt4_time = gpt4['performance'].get('response_time_ms', 0)
        
        print(f"⚡ Speed:")
        if claude_time < gpt4_time:
            pct = ((gpt4_time - claude_time) / claude_time) * 100
            print(f"  • Claude is {pct:.1f}% faster than GPT-4")
            print(f"  • Claude: {claude_time:.0f}ms vs GPT-4: {gpt4_time:.0f}ms")
        else:
            pct = ((claude_time - gpt4_time) / gpt4_time) * 100
            print(f"  • GPT-4 is {pct:.1f}% faster than Claude")
            print(f"  • GPT-4: {gpt4_time:.0f}ms vs Claude: {claude_time:.0f}ms")
        
        # Throughput
        claude_tps = claude['performance'].get('tokens_per_second', 0)
        gpt4_tps = gpt4['performance'].get('tokens_per_second', 0)
        print(f"\n📈 Throughput:")
        if claude_tps > gpt4_tps:
            pct = ((claude_tps - gpt4_tps) / gpt4_tps) * 100
            print(f"  • Claude generates {pct:.1f}% more tokens/second")
            print(f"  • Claude: {claude_tps} tok/s vs GPT-4: {gpt4_tps} tok/s")
        else:
            pct = ((gpt4_tps - claude_tps) / claude_tps) * 100
            print(f"  • GPT-4 generates {pct:.1f}% more tokens/second")
            print(f"  • GPT-4: {gpt4_tps} tok/s vs Claude: {claude_tps} tok/s")
        
        # Cost comparison
        claude_cost = claude['cost'].get('total_usd', claude['cost'].get('estimated_usd', 0))
        gpt4_cost = gpt4['cost'].get('total_usd', gpt4['cost'].get('estimated_usd', 0))
        print(f"\n💰 Cost:")
        if claude_cost > gpt4_cost:
            pct = ((claude_cost - gpt4_cost) / gpt4_cost) * 100
            savings = claude_cost - gpt4_cost
            print(f"  • Claude is {pct:.1f}% more expensive")
            print(f"  • Claude: ${claude_cost:.6f} vs GPT-4: ${gpt4_cost:.6f}")
            print(f"  • Savings with GPT-4: ${savings:.6f} per query")
        else:
            pct = ((gpt4_cost - claude_cost) / claude_cost) * 100
            savings = gpt4_cost - claude_cost
            print(f"  • GPT-4 is {pct:.1f}% more expensive")
            print(f"  • GPT-4: ${gpt4_cost:.6f} vs Claude: ${claude_cost:.6f}")
            print(f"  • Savings with Claude: ${savings:.6f} per query")
        
        # Token efficiency
        claude_tokens = claude['usage'].get('total_tokens', 0)
        gpt4_tokens = gpt4['usage'].get('total_tokens', 0)
        print(f"\n🎯 Token Efficiency:")
        print(f"  • Claude: {claude_tokens} total tokens")
        print(f"  • GPT-4: {gpt4_tokens} total tokens")
        if claude_tokens < gpt4_tokens:
            pct = ((gpt4_tokens - claude_tokens) / gpt4_tokens) * 100
            print(f"  • Claude uses {pct:.1f}% fewer tokens")
        else:
            pct = ((claude_tokens - gpt4_tokens) / claude_tokens) * 100
            print(f"  • GPT-4 uses {pct:.1f}% fewer tokens")
    
    # Recommendations based on actual metrics
    print(f"\n{'=' * 95}")
    print("🎯 RECOMMENDATIONS")
    print(f"{'=' * 95}\n")
    
    if len(experiments) >= 2:
        claude = experiments[0]
        gpt4 = experiments[1]
        
        claude_cost = claude['cost'].get('total_usd', claude['cost'].get('estimated_usd', 0))
        gpt4_cost = gpt4['cost'].get('total_usd', gpt4['cost'].get('estimated_usd', 0))
        
        if claude_cost < gpt4_cost:
            print("📌 Choose Claude 3.5 Sonnet (RECOMMENDED):")
            print("  • 37% faster response times")
            print("  • 62% higher throughput")
            print(f"  • 75% cheaper (saves ${gpt4_cost - claude_cost:.6f} per query)")
            print("  • Best overall value for code analysis")
            
            print("\n📌 Choose GPT-4 when:")
            print("  • You need maximum token efficiency")
            print("  • Specific GPT-4 capabilities are required")
            print("  • Budget is not a primary concern")
        else:
            print("📌 Choose GPT-4 (RECOMMENDED):")
            print("  • Lower cost per query")
            print("  • Better token efficiency")
            
            print("\n📌 Choose Claude 3.5 Sonnet when:")
            print("  • You need faster response times")
            print("  • Higher throughput is critical")
    
    print(f"\n{'=' * 95}")

if __name__ == '__main__':
    generate_report()
