#!/usr/bin/env python3
"""
Performance Analysis Tool - Extract and compare metrics from experiments
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

def load_summary(results_dir):
    """Load matrix summary"""
    summary_path = Path(results_dir) / 'matrix_summary.json'
    with open(summary_path) as f:
        return json.load(f)

def load_config(config_path):
    """Load AICL config to extract parameters"""
    try:
        with open(config_path) as f:
            content = f.read()
            
            # Extract model
            model_match = re.search(r'model\s*=\s*"([^"]+)"', content)
            model = model_match.group(1) if model_match else 'unknown'
            
            # Extract prompt
            content_match = re.search(r'content\s*=\s*"([^"]+)"', content)
            prompt = content_match.group(1) if content_match else 'unknown'
            
            # Extract max_tokens
            tokens_match = re.search(r'max_tokens\s*=\s*(\d+)', content)
            max_tokens = int(tokens_match.group(1)) if tokens_match else None
            
            return {
                'model': model,
                'prompt': prompt,
                'max_tokens': max_tokens
            }
    except:
        return {'model': 'unknown', 'prompt': 'unknown', 'max_tokens': None}

def extract_response_from_stdout(stdout):
    """Extract response from stdout logs"""
    # The response might be in the logs - look for patterns
    # For now, return None - we'd need to enhance the runner to capture this
    return None

def parse_experiment_metrics(exp_data):
    """Parse metrics from experiment data"""
    config_data = load_config(exp_data['config_path'])
    
    metrics = {
        'experiment_id': exp_data['experiment_id'],
        'model': config_data['model'],
        'prompt': config_data['prompt'],
        'max_tokens': config_data['max_tokens'],
        'success': exp_data['returncode'] == 0,
        'stdout_lines': len(exp_data.get('stdout', '').split('\n')),
        'stderr_lines': len(exp_data.get('stderr', '').split('\n')),
        'resources_created': exp_data.get('metrics', {}).get('resources_created', 0),
        'timestamp': exp_data.get('timestamp', '')
    }
    
    # Try to extract response if available
    metrics['response'] = extract_response_from_stdout(exp_data.get('stdout', ''))
    
    return metrics

def compare_performance(results_dir="experiments/matrix-results"):
    """Compare performance across all experiments"""
    results_dir = Path(results_dir)
    
    print("=" * 80)
    print("🔬 PERFORMANCE ANALYSIS & COMPARISON")
    print("=" * 80)
    
    # Load summary
    summary = load_summary(results_dir)
    
    # Analyze each experiment
    analyses = []
    for exp_data in summary['experiments']:
        metrics = parse_experiment_metrics(exp_data)
        analyses.append(metrics)
    
    # Display configuration comparison
    print("\n📊 EXPERIMENT CONFIGURATIONS\n")
    print("┌─" + "─" * 78 + "┐")
    print("│ Experiment          │ Model              │ Prompt Summary         │ Tokens │")
    print("├─" + "─" * 78 + "┤")
    
    for analysis in analyses:
        exp_id = analysis['experiment_id'][:18]
        model = analysis['model'].split('/')[-1][:16]
        prompt = (analysis['prompt'][:20] + '..') if len(analysis['prompt']) > 20 else analysis['prompt']
        tokens = str(analysis['max_tokens'])[:6]
        
        print(f"│ {exp_id:<20}│ {model:<19}│ {prompt:<24}│ {tokens:<7}│")
    
    print("└─" + "─" * 78 + "┘")
    
    # Show detailed parameters
    print("\n📋 DETAILED EXPERIMENT PARAMETERS\n")
    
    for analysis in analyses:
        print("─" * 80)
        print(f"🧪 {analysis['experiment_id'].upper()}")
        print(f"   Model: {analysis['model']}")
        print(f"   Prompt: \"{analysis['prompt']}\"")
        print(f"   Max Tokens: {analysis['max_tokens']}")
        print(f"   Status: {'✅ SUCCESS' if analysis['success'] else '❌ FAILED'}")
        print(f"   Completed: {analysis['timestamp']}")
    
    print("\n" + "─" * 80)
    
    # Model comparison
    print("\n🏆 MODEL COMPARISON\n")
    
    # Group by model
    by_model = {}
    for analysis in analyses:
        model = analysis['model']
        if model not in by_model:
            by_model[model] = []
        by_model[model].append(analysis)
    
    for model, experiments in by_model.items():
        print(f"📌 {model}")
        print(f"   Experiments: {len(experiments)}")
        print(f"   Success Rate: {sum(1 for e in experiments if e['success'])}/{len(experiments)}")
        prompts = set(e['prompt'] for e in experiments)
        print(f"   Prompts Tested: {', '.join(prompts)}")
        print()
    
    # Prompt complexity analysis
    print("📝 PROMPT COMPLEXITY ANALYSIS\n")
    
    by_prompt_length = sorted(analyses, key=lambda x: len(x['prompt']))
    for analysis in by_prompt_length:
        complexity = "Simple" if len(analysis['prompt']) < 30 else "Medium" if len(analysis['prompt']) < 60 else "Complex"
        print(f"  • {analysis['experiment_id']}: {len(analysis['prompt'])} chars ({complexity})")
    
    # Success metrics
    print("\n✅ SUCCESS METRICS\n")
    
    total = len(analyses)
    successful = sum(1 for a in analyses if a['success'])
    print(f"  Overall Success Rate: {successful}/{total} ({100*successful/total:.1f}%)")
    
    if successful == total:
        print("  🎉 All experiments completed successfully!")
    
    print("\n" + "=" * 80)
    
    # Suggestions for next steps
    print("\n💡 INSIGHTS & RECOMMENDATIONS\n")
    
    models_tested = len(by_model)
    prompts_tested = len(set(a['prompt'] for a in analyses))
    
    print(f"  • Tested {models_tested} different models")
    print(f"  • Tested {prompts_tested} different prompts")
    print(f"  • All experiments used OpenRouter provider")
    
    print("\n  📈 To get performance metrics (response time, quality, tokens):")
    print("     1. Enhance the provider to return usage statistics")
    print("     2. Capture response content in state files")
    print("     3. Add timing measurements to the executor")
    
    print("\n  🔬 Suggested next experiments:")
    print("     • Test with different temperature settings")
    print("     • Compare response quality across models")
    print("     • Measure end-to-end latency")
    print("     • Track token usage and costs")
    
    print("\n" + "=" * 80)
    
    return analyses

def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "experiments/matrix-results"
    compare_performance(results_dir)

if __name__ == '__main__':
    main()
