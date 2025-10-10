#!/usr/bin/env python3
"""Analyze response quality metrics from 3x3 matrix"""

import json
from pathlib import Path
import re

def count_code_blocks(text):
    """Count code blocks in response"""
    return len(re.findall(r'```', text)) // 2

def count_suggestions(text):
    """Count numbered suggestions"""
    return len(re.findall(r'^\s*\d+\.', text, re.MULTILINE))

def extract_key_ideas(text):
    """Extract unique technical suggestions"""
    ideas = []
    
    # Look for specific patterns
    patterns = [
        (r'frozendict|immutable', 'Immutability pattern'),
        (r'cache|caching|memoiz', 'Caching optimization'),
        (r'type hint|typing|TypedDict', 'Type safety'),
        (r'dataclass|@dataclass', 'Dataclass usage'),
        (r'async|asyncio|await', 'Async programming'),
        (r'logging|logger', 'Logging improvements'),
        (r'exception|error handling|try.*except', 'Error handling'),
        (r'docstring|documentation', 'Documentation'),
        (r'performance|optimization|efficient', 'Performance'),
        (r'test|testing|unittest', 'Testing'),
        (r'validation|validate', 'Input validation'),
        (r'dependency injection', 'Dependency injection'),
        (r'factory pattern|builder pattern', 'Design patterns'),
        (r'singleton|decorator pattern', 'Design patterns'),
    ]
    
    for pattern, label in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            ideas.append(label)
    
    return list(set(ideas))

def analyze_conciseness(text, tokens):
    """Calculate conciseness metrics"""
    words = len(text.split())
    chars = len(text)
    
    return {
        'chars_per_token': chars / tokens if tokens > 0 else 0,
        'words_per_token': words / tokens if tokens > 0 else 0,
        'avg_word_length': chars / words if words > 0 else 0
    }

def main():
    results_dir = Path("experiments/token-matrix-results")
    
    quality_metrics = []
    
    for state_file in sorted(results_dir.glob("*.tfstate")):
        exp_id = state_file.stem
        parts = exp_id.split('_')
        model_name = parts[0].upper()
        token_size = parts[1]
        
        with open(state_file) as f:
            state = json.load(f)
        
        resources = state.get('resources', {})
        for resource_id, resource_data in resources.items():
            if resource_data.get('type') == 'chat':
                attrs = resource_data.get('attributes', {})
                response = attrs.get('response', '')
                usage = attrs.get('usage', {})
                tokens = usage.get('completion_tokens', 0)
                
                if not response or tokens == 0:
                    continue
                
                code_blocks = count_code_blocks(response)
                suggestions = count_suggestions(response)
                key_ideas = extract_key_ideas(response)
                conciseness = analyze_conciseness(response, tokens)
                
                quality_metrics.append({
                    'model': model_name,
                    'token_size': token_size,
                    'code_blocks': code_blocks,
                    'suggestions': suggestions,
                    'unique_ideas': len(key_ideas),
                    'ideas_list': key_ideas,
                    'chars_per_token': conciseness['chars_per_token'],
                    'response_preview': response[:200] + '...'
                })
    
    # Display quality analysis
    print("\n" + "="*100)
    print("🎨 RESPONSE QUALITY ANALYSIS")
    print("="*100 + "\n")
    
    print(f"{'Model':<10} {'Size':<10} {'Code Blocks':<15} {'Suggestions':<15} {'Unique Ideas':<15} {'Chars/Token':<15}")
    print("-" * 100)
    
    for m in sorted(quality_metrics, key=lambda x: (x['model'], ['small', 'medium', 'large'].index(x['token_size']))):
        print(f"{m['model']:<10} {m['token_size']:<10} {m['code_blocks']:<15} {m['suggestions']:<15} {m['unique_ideas']:<15} {m['chars_per_token']:<15.1f}")
    
    # Unique ideas by model
    print("\n" + "="*100)
    print("💡 UNIQUE IDEAS & TECHNIQUES SUGGESTED")
    print("="*100 + "\n")
    
    model_ideas = {}
    for m in quality_metrics:
        if m['model'] not in model_ideas:
            model_ideas[m['model']] = set()
        model_ideas[m['model']].update(m['ideas_list'])
    
    for model in sorted(model_ideas.keys()):
        ideas = sorted(model_ideas[model])
        print(f"{model}:")
        for idea in ideas:
            print(f"  ✓ {idea}")
        print()
    
    # Conciseness analysis
    print("="*100)
    print("📏 CONCISENESS METRICS")
    print("="*100 + "\n")
    
    for model in sorted(set(m['model'] for m in quality_metrics)):
        model_metrics = [m for m in quality_metrics if m['model'] == model]
        avg_chars_per_token = sum(m['chars_per_token'] for m in model_metrics) / len(model_metrics)
        avg_code_blocks = sum(m['code_blocks'] for m in model_metrics) / len(model_metrics)
        avg_ideas = sum(m['unique_ideas'] for m in model_metrics) / len(model_metrics)
        
        print(f"{model}:")
        print(f"  Avg chars/token:     {avg_chars_per_token:.1f}")
        print(f"  Avg code blocks:     {avg_code_blocks:.1f}")
        print(f"  Avg unique ideas:    {avg_ideas:.1f}")
        print()
    
    # Code-heaviness analysis
    print("="*100)
    print("💻 CODE-HEAVINESS (Code Blocks per Response)")
    print("="*100 + "\n")
    
    for size in ['small', 'medium', 'large']:
        size_metrics = [m for m in quality_metrics if m['token_size'] == size]
        avg_code = sum(m['code_blocks'] for m in size_metrics) / len(size_metrics)
        print(f"{size.upper()} ({size.replace('small', '500').replace('medium', '1500').replace('large', '3000')} tokens):")
        print(f"  Average code blocks: {avg_code:.1f}")
    
    print("\n" + "="*100)
    print("🔍 SAMPLE RESPONSES (First 200 chars)")
    print("="*100 + "\n")
    
    for m in quality_metrics[:3]:  # Show first 3
        print(f"{m['model']} ({m['token_size']}):")
        print(f"  {m['response_preview']}")
        print()

if __name__ == '__main__':
    main()
