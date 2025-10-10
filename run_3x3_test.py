#!/usr/bin/env python3
"""
3x3 Matrix Test: Validate framework with 3 models x 3 tasks
"""
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Test matrix: 3 models x 3 tasks
MODELS = [
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4",
    "openai/gpt-4o-mini"
]

TASKS = [
    {"task": "Explain in 2 sentences", "topic": "declarative infrastructure"},
    {"task": "List 3 benefits of", "topic": "HCL configuration syntax"},
    {"task": "Write a haiku about", "topic": "AI orchestration"}
]

def substitute_template(template_content: str, variables: dict) -> str:
    """Replace {{ variable }} placeholders with actual values."""
    result = template_content
    for key, value in variables.items():
        result = result.replace(f"{{{{ {key} }}}}", value)
    return result

def run_experiment(model: str, task_vars: dict, experiment_id: str):
    """Run single experiment configuration."""
    # Read template
    with open('test_3x3_template.aicl', 'r') as f:
        template = f.read()
    
    # Substitute variables including model
    all_vars = task_vars.copy()
    all_vars['model'] = model
    config_content = substitute_template(template, all_vars)
    
    # Write config file
    config_file = f"experiments/{experiment_id}.aicl"
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    # Run experiment
    print(f"🔧 Running: {model} | {task_vars['task'][:20]}...")
    start_time = time.time()
    
    cmd = f"python run.py {config_file}"
    result = os.system(cmd + " > /dev/null 2>&1")
    
    elapsed = time.time() - start_time
    
    # Read state file (engine uses 'default-exp' by default)
    state_file = f"terraform.tfstate.d/default-exp.tfstate"
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            state = json.load(f)
            resource = state['resources'].get('chat-test_response', {})
            response_text = resource.get('attributes', {}).get('response', '')
            usage = resource.get('attributes', {}).get('usage', {})
            perf = resource.get('attributes', {}).get('performance', {})
            cost = resource.get('attributes', {}).get('cost', {})
            
            return {
                'model': model,
                'task': task_vars['task'],
                'topic': task_vars['topic'],
                'success': result == 0 and len(response_text) > 0,
                'elapsed': round(elapsed, 2),
                'response_length': len(response_text),
                'response_preview': response_text[:100] + '...' if len(response_text) > 100 else response_text,
                'tokens': int(usage.get('total_tokens', 0)),
                'latency_ms': int(perf.get('latency_ms', 0)),
                'cost_usd': round(cost.get('total_usd', 0), 6)
            }
    
    return {
        'model': model,
        'task': task_vars['task'],
        'topic': task_vars['topic'],
        'success': False,
        'elapsed': round(elapsed, 2),
        'error': 'No state file generated'
    }

def main():
    """Run 3x3 matrix test."""
    print("\n" + "="*70)
    print("🧪 AICL FRAMEWORK 3x3 MATRIX TEST")
    print("="*70)
    print(f"📊 Testing {len(MODELS)} models x {len(TASKS)} tasks = {len(MODELS) * len(TASKS)} experiments\n")
    
    # Create experiments directory
    Path('experiments').mkdir(exist_ok=True)
    
    results = []
    experiment_num = 1
    total_experiments = len(MODELS) * len(TASKS)
    
    for model in MODELS:
        for task_vars in TASKS:
            experiment_id = f"test_3x3_{experiment_num}"
            print(f"[{experiment_num}/{total_experiments}] ", end="")
            
            result = run_experiment(model, task_vars, experiment_id)
            results.append(result)
            
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['elapsed']}s | {result.get('response_length', 0)} chars")
            
            experiment_num += 1
    
    # Summary report
    print("\n" + "="*70)
    print("📈 TEST SUMMARY")
    print("="*70 + "\n")
    
    successful = sum(1 for r in results if r['success'])
    total_tokens = sum(r.get('tokens', 0) for r in results if r['success'])
    total_cost = sum(r.get('cost_usd', 0) for r in results if r['success'])
    
    print(f"✅ Success Rate: {successful}/{total_experiments} ({100*successful//total_experiments}%)")
    print(f"⏱️  Total Time: {sum(r['elapsed'] for r in results):.2f}s")
    print(f"📊 Average Time: {sum(r['elapsed'] for r in results)/len(results):.2f}s per experiment")
    print(f"🔢 Total Tokens: {total_tokens:,}")
    print(f"💰 Total Cost: ${total_cost:.4f}\n")
    
    # Model comparison
    print("🤖 BY MODEL:")
    for model in MODELS:
        model_results = [r for r in results if r['model'] == model and r['success']]
        if model_results:
            avg_time = sum(r['elapsed'] for r in model_results) / len(model_results)
            avg_tokens = sum(r.get('tokens', 0) for r in model_results) / len(model_results)
            total_cost_model = sum(r.get('cost_usd', 0) for r in model_results)
            avg_latency = sum(r.get('latency_ms', 0) for r in model_results) / len(model_results)
            
            print(f"  {model.split('/')[-1]}:")
            print(f"    ⏱️  Avg time: {avg_time:.2f}s")
            print(f"    🔢 Avg tokens: {avg_tokens:.0f}")
            print(f"    ⚡ Avg latency: {avg_latency:.0f}ms")
            print(f"    💰 Total cost: ${total_cost_model:.4f}")
    
    print("\n📝 BY TASK:")
    for i, task_vars in enumerate(TASKS, 1):
        task_results = [r for r in results if r['task'] == task_vars['task'] and r['success']]
        if task_results:
            avg_time = sum(r['elapsed'] for r in task_results) / len(task_results)
            avg_length = sum(r.get('response_length', 0) for r in task_results) / len(task_results)
            print(f"  Task {i} - {task_vars['task'][:40]}:")
            print(f"    ⏱️  Avg time: {avg_time:.2f}s | 📝 Avg response: {avg_length:.0f} chars")
    
    # Save results
    report_file = f"experiments/3x3_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_experiments': total_experiments,
            'success_rate': f"{successful}/{total_experiments}",
            'results': results
        }, f, indent=2)
    
    print(f"\n💾 Full report saved: {report_file}")
    print("\n" + "="*70 + "\n")
    
    return successful == total_experiments

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
