#!/usr/bin/env python3
"""
3x3 Matrix Test with LLM-as-Judge Quality Grading
Tests both infrastructure reliability AND response accuracy/quality
"""

import os
import sys
import json
import time
from datetime import datetime
from llm_grader import LLMGrader

# Test matrix configuration
MODELS = [
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4",
    "openai/gpt-4o-mini"
]

TASKS = [
    {
        'task': 'Explain in 2 sentences',
        'topic': 'declarative infrastructure',
        'expected_criteria': ['accuracy', 'clarity', 'completeness']
    },
    {
        'task': 'List 3 benefits of',
        'topic': 'HCL configuration syntax',
        'expected_criteria': ['accuracy', 'completeness', 'relevance']
    },
    {
        'task': 'Write a haiku about',
        'topic': 'AI orchestration',
        'expected_criteria': ['relevance', 'clarity', 'actionability']
    }
]

# Judge model for grading
JUDGE_MODEL = "openai/gpt-4"


def substitute_template(template: str, variables: dict) -> str:
    """Substitute template variables (lowercase with spaces)."""
    result = template
    for key, value in variables.items():
        # Only substitute string values
        if isinstance(value, str):
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
    print(f"🔧 Running: {model.split('/')[-1]} | {task_vars['task'][:20]}...")
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
                'response_text': response_text,
                'response_length': len(response_text),
                'response_preview': response_text[:100] + '...' if len(response_text) > 100 else response_text,
                'tokens': int(usage.get('total_tokens', 0)),
                'latency_ms': int(perf.get('latency_ms', 0)),
                'cost_usd': round(cost.get('total_usd', 0), 6),
                'expected_criteria': task_vars.get('expected_criteria', [])
            }
    
    return {
        'model': model,
        'task': task_vars['task'],
        'topic': task_vars['topic'],
        'success': False,
        'elapsed': round(elapsed, 2),
        'error': 'No state file generated'
    }


def grade_responses(results: list, judge_model: str) -> list:
    """Grade all successful responses using LLM-as-Judge."""
    print("\n" + "="*70)
    print("🎯 GRADING RESPONSES WITH LLM-AS-JUDGE")
    print("="*70)
    print(f"Judge Model: {judge_model}\n")
    
    grader = LLMGrader(judge_model=judge_model)
    graded_results = []
    
    for i, result in enumerate(results, 1):
        if not result.get('success'):
            graded_results.append(result)
            continue
        
        # Build question
        question = f"{result['task']}: {result['topic']}"
        response = result.get('response_text', '')
        
        print(f"[{i}/{len(results)}] Grading {result['model'].split('/')[-1]} response...", end=' ')
        
        try:
            # Use task-specific criteria
            criteria = result.get('expected_criteria', ['accuracy', 'relevance', 'clarity'])
            grades = grader.grade_response(question, response, criteria=criteria)
            
            result['quality'] = {
                'scores': grades.get('scores', {}),
                'overall_score': grades.get('overall_score', 0),
                'reasoning': grades.get('reasoning', ''),
                'judge_model': judge_model
            }
            
            score = result['quality']['overall_score']
            print(f"✅ Score: {score}/10")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            result['quality'] = {'error': str(e), 'overall_score': 0}
        
        graded_results.append(result)
    
    return graded_results


def main():
    """Run 3x3 matrix test with quality grading."""
    print("\n" + "="*70)
    print("🧪 AICL FRAMEWORK 3x3 MATRIX TEST WITH QUALITY GRADING")
    print("="*70)
    print(f"📊 Testing {len(MODELS)} models x {len(TASKS)} tasks = {len(MODELS) * len(TASKS)} experiments")
    print(f"👨‍⚖️ Judge Model: {JUDGE_MODEL}\n")
    
    results = []
    total_experiments = len(MODELS) * len(TASKS)
    experiment_num = 1
    
    # Run experiments
    for model in MODELS:
        for task_vars in TASKS:
            experiment_id = f"test_3x3_{experiment_num}"
            result = run_experiment(model, task_vars, experiment_id)
            results.append(result)
            
            status = "✅" if result['success'] else "❌"
            print(f"[{experiment_num}/{total_experiments}] {status} {result['elapsed']}s | {result.get('response_length', 0)} chars")
            
            experiment_num += 1
    
    # Grade responses
    graded_results = grade_responses(results, JUDGE_MODEL)
    
    # Summary report
    print("\n" + "="*70)
    print("📈 INFRASTRUCTURE TEST SUMMARY")
    print("="*70 + "\n")
    
    successful = sum(1 for r in graded_results if r['success'])
    total_tokens = sum(r.get('tokens', 0) for r in graded_results if r['success'])
    total_cost = sum(r.get('cost_usd', 0) for r in graded_results if r['success'])
    
    print(f"✅ Success Rate: {successful}/{total_experiments} ({100*successful//total_experiments}%)")
    print(f"⏱️  Total Time: {sum(r['elapsed'] for r in graded_results):.2f}s")
    print(f"🔢 Total Tokens: {total_tokens:,}")
    print(f"💰 Total Cost: ${total_cost:.4f}")
    
    # Quality report
    print("\n" + "="*70)
    print("🎯 QUALITY ASSESSMENT SUMMARY")
    print("="*70 + "\n")
    
    quality_results = [r for r in graded_results if r.get('quality')]
    if quality_results:
        avg_quality = sum(r['quality']['overall_score'] for r in quality_results) / len(quality_results)
        print(f"📊 Average Quality Score: {avg_quality:.1f}/10\n")
        
        # Quality by model
        print("🤖 QUALITY BY MODEL:")
        for model in MODELS:
            model_results = [r for r in quality_results if r['model'] == model]
            if model_results:
                avg_score = sum(r['quality']['overall_score'] for r in model_results) / len(model_results)
                min_score = min(r['quality']['overall_score'] for r in model_results)
                max_score = max(r['quality']['overall_score'] for r in model_results)
                
                print(f"  {model.split('/')[-1]}:")
                print(f"    Avg: {avg_score:.1f}/10 | Range: {min_score:.1f}-{max_score:.1f}")
        
        # Quality by task
        print("\n📝 QUALITY BY TASK:")
        for i, task_vars in enumerate(TASKS, 1):
            task_results = [r for r in quality_results if r['task'] == task_vars['task']]
            if task_results:
                avg_score = sum(r['quality']['overall_score'] for r in task_results) / len(task_results)
                print(f"  Task {i} - {task_vars['task'][:30]}: {avg_score:.1f}/10")
    
    # Save results
    report_file = f"experiments/3x3_graded_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_experiments': total_experiments,
            'success_rate': f"{successful}/{total_experiments}",
            'judge_model': JUDGE_MODEL,
            'average_quality_score': round(avg_quality, 2) if quality_results else 0,
            'results': graded_results
        }, f, indent=2)
    
    print(f"\n💾 Full report saved: {report_file}")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
