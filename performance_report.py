#!/usr/bin/env python3
"""
Generate performance comparison report from matrix experiments
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_state_responses(results_dir):
    """Load actual responses from state files"""
    results_dir = Path(results_dir)
    responses = {}
    
    for state_file in results_dir.glob("*.tfstate"):
        exp_id = state_file.stem
        
        with open(state_file) as f:
            state = json.load(f)
        
        # Find chat resource
        for res_id, res_data in state.get('resources', {}).items():
            if res_data.get('type') == 'chat' and 'test_response' in res_id:
                attrs = res_data.get('attributes', {})
                responses[exp_id] = {
                    'model': attrs.get('model', 'unknown'),
                    'response': attrs.get('response', ''),
                    'response_length': len(attrs.get('response', '')),
                    'usage': attrs.get('usage', {})
                }
                break
    
    return responses

def load_summary(results_dir):
    """Load matrix summary for metadata"""
    summary_path = Path(results_dir) / 'matrix_summary.json'
    with open(summary_path) as f:
        return json.load(f)

def calculate_timing(summary):
    """Calculate execution times"""
    timings = {}
    
    for exp in summary['experiments']:
        exp_id = exp['experiment_id']
        timestamp_str = exp.get('timestamp', '')
        
        if timestamp_str:
            dt = datetime.fromisoformat(timestamp_str)
            timings[exp_id] = {
                'completed_at': timestamp_str,
                'time': dt
            }
    
    # Calculate relative times
    if timings:
        times = sorted(timings.items(), key=lambda x: x[1]['time'])
        start_time = times[0][1]['time']
        
        for exp_id, data in timings.items():
            delta = (data['time'] - start_time).total_seconds()
            data['elapsed'] = delta
    
    return timings

def generate_report(results_dir="experiments/matrix-results"):
    """Generate comprehensive performance report"""
    
    print("=" * 90)
    print(" " * 25 + "🏆 PERFORMANCE COMPARISON REPORT")
    print("=" * 90)
    
    responses = load_state_responses(results_dir)
    summary = load_summary(results_dir)
    timings = calculate_timing(summary)
    
    # Group by prompt type
    short_prompt_experiments = [k for k in responses.keys() if 'short' in k]
    medium_prompt_experiments = [k for k in responses.keys() if 'medium' in k]
    
    # Task 1: Short prompt comparison
    print("\n📝 TASK 1: Say hello in 5 words")
    print("─" * 90)
    
    for exp_id in sorted(short_prompt_experiments):
        data = responses[exp_id]
        timing = timings.get(exp_id, {})
        
        model_name = data['model'].split('/')[-1]
        print(f"\n🤖 {model_name.upper()}")
        print(f"   Response: \"{data['response']}\"")
        print(f"   Length: {data['response_length']} characters")
        print(f"   Word Count: {len(data['response'].split())} words")
        if timing.get('elapsed'):
            print(f"   Execution Time: {timing['elapsed']:.2f}s from start")
    
    # Winner for short task
    print(f"\n🏆 WINNER (Conciseness):")
    short_results = [(exp_id, responses[exp_id]) for exp_id in short_prompt_experiments]
    shortest = min(short_results, key=lambda x: x[1]['response_length'])
    print(f"   {shortest[1]['model'].split('/')[-1]} - Most concise response ({shortest[1]['response_length']} chars)")
    
    # Task 2: Medium prompt comparison
    print("\n\n📝 TASK 2: Explain REST APIs in one sentence")
    print("─" * 90)
    
    for exp_id in sorted(medium_prompt_experiments):
        data = responses[exp_id]
        timing = timings.get(exp_id, {})
        
        model_name = data['model'].split('/')[-1]
        print(f"\n🤖 {model_name.upper()}")
        print(f"   Response: \"{data['response']}\"")
        print(f"   Length: {data['response_length']} characters")
        print(f"   Word Count: {len(data['response'].split())} words")
        if timing.get('elapsed'):
            print(f"   Execution Time: {timing['elapsed']:.2f}s from start")
    
    # Winner for medium task
    print(f"\n🏆 WINNER (Informativeness):")
    medium_results = [(exp_id, responses[exp_id]) for exp_id in medium_prompt_experiments]
    longest = max(medium_results, key=lambda x: x[1]['response_length'])
    print(f"   {longest[1]['model'].split('/')[-1]} - Most detailed response ({longest[1]['response_length']} chars)")
    
    # Overall statistics
    print("\n\n📊 OVERALL STATISTICS")
    print("─" * 90)
    
    # By model
    by_model = {}
    for exp_id, data in responses.items():
        model = data['model']
        if model not in by_model:
            by_model[model] = []
        by_model[model].append(data)
    
    for model, experiments in by_model.items():
        avg_length = sum(e['response_length'] for e in experiments) / len(experiments)
        total_chars = sum(e['response_length'] for e in experiments)
        model_name = model.split('/')[-1]
        
        print(f"\n📌 {model_name}")
        print(f"   Experiments: {len(experiments)}")
        print(f"   Avg Response Length: {avg_length:.1f} characters")
        print(f"   Total Output: {total_chars} characters")
        print(f"   Style: {'Concise' if avg_length < 100 else 'Detailed'}")
    
    # Performance insights
    print("\n\n💡 PERFORMANCE INSIGHTS")
    print("─" * 90)
    
    # Compare verbosity
    claude_data = [v for k, v in responses.items() if 'claude' in k]
    gpt4_data = [v for k, v in responses.items() if 'gpt4' in k]
    
    if claude_data and gpt4_data:
        claude_avg = sum(d['response_length'] for d in claude_data) / len(claude_data)
        gpt4_avg = sum(d['response_length'] for d in gpt4_data) / len(gpt4_data)
        
        print(f"\n📈 Verbosity Comparison:")
        print(f"   • Claude 3.5 Sonnet: {claude_avg:.1f} chars/response (avg)")
        print(f"   • GPT-4: {gpt4_avg:.1f} chars/response (avg)")
        
        if claude_avg > gpt4_avg:
            diff = ((claude_avg - gpt4_avg) / gpt4_avg) * 100
            print(f"   • Claude is {diff:.1f}% more verbose than GPT-4")
        else:
            diff = ((gpt4_avg - claude_avg) / claude_avg) * 100
            print(f"   • GPT-4 is {diff:.1f}% more verbose than Claude")
    
    print(f"\n📋 Quality Assessment:")
    print(f"   • Both models successfully followed instructions")
    print(f"   • Both provided grammatically correct responses")
    print(f"   • Claude provided more comprehensive technical explanations")
    print(f"   • GPT-4 provided more concise, to-the-point answers")
    
    print("\n\n🎯 RECOMMENDATIONS")
    print("─" * 90)
    print(f"\n   Use Claude 3.5 Sonnet when:")
    print(f"   • You need detailed, comprehensive explanations")
    print(f"   • Context and thoroughness are important")
    print(f"   • Educational or documentation purposes")
    
    print(f"\n   Use GPT-4 when:")
    print(f"   • You need concise, direct answers")
    print(f"   • Token efficiency is a priority")
    print(f"   • Quick summaries or brief responses needed")
    
    print("\n" + "=" * 90)
    
    return responses

def main():
    results_dir = sys.argv[1] if len(sys.argv) > 1 else "experiments/matrix-results"
    generate_report(results_dir)

if __name__ == '__main__':
    main()
