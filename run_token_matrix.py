#!/usr/bin/env python3
"""
3x3 Token Size x Code Model Matrix Experiment
Tests small/medium/large token limits across specialized coding models
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class TokenMatrixRunner:
    def __init__(self, output_dir="experiments/token-matrix-results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        
    def create_config(self, template, variables, name):
        """Create config from template"""
        config_content = template
        for key, value in variables.items():
            config_content = config_content.replace(f"{{{{ {key} }}}}", str(value))
        
        config_path = self.output_dir / f"{name}.aicl"
        config_path.write_text(config_content)
        return config_path
    
    def run_experiment(self, config_path, experiment_id):
        """Run experiment"""
        print(f"\n{'='*70}")
        print(f"🧪 Running: {experiment_id}")
        print(f"{'='*70}")
        
        # Clean state first
        state_file = Path('terraform.tfstate.d/default-exp.tfstate')
        if state_file.exists():
            state_file.unlink()
        
        result = subprocess.run(
            ['python', 'run.py', str(config_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Capture state
        if state_file.exists():
            dest_state = self.output_dir / f"{experiment_id}.tfstate"
            shutil.copy(state_file, dest_state)
            print(f"✅ State saved: {dest_state}")
        
        return {
            'experiment_id': experiment_id,
            'config_path': str(config_path),
            'state_file': str(dest_state) if state_file.exists() else None,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'timestamp': datetime.now().isoformat()
        }
    
    def run_matrix(self, template, variable_matrix):
        """Run matrix"""
        print(f"\n🚀 3x3 Token Size x Code Model Matrix")
        print(f"Output: {self.output_dir}")
        print(f"Experiments: {len(variable_matrix)}")
        
        for exp in variable_matrix:
            exp_id = exp['id']
            variables = exp['variables']
            
            config_path = self.create_config(template, variables, exp_id)
            
            try:
                result = self.run_experiment(config_path, exp_id)
                self.results.append(result)
                
                status = "✅" if result['returncode'] == 0 else "❌"
                print(f"Status: {status}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                self.results.append({
                    'experiment_id': exp_id,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        self.save_summary()
        self.analyze_results()
    
    def save_summary(self):
        """Save summary"""
        summary_file = self.output_dir / 'token_matrix_summary.json'
        
        summary = {
            'total_experiments': len(self.results),
            'successful': sum(1 for r in self.results if r.get('returncode') == 0),
            'failed': sum(1 for r in self.results if r.get('returncode', 1) != 0),
            'timestamp': datetime.now().isoformat(),
            'experiments': self.results
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Summary: {summary_file}")
        print(f"Total: {summary['total_experiments']} | Success: {summary['successful']} | Failed: {summary['failed']}")
    
    def analyze_results(self):
        """Analyze and display results"""
        print(f"\n{'='*70}")
        print("📈 TOKEN SIZE vs MODEL PERFORMANCE")
        print(f"{'='*70}\n")
        
        # Extract metrics from state files
        metrics = []
        for result in self.results:
            if result.get('state_file'):
                try:
                    with open(result['state_file'], 'r') as f:
                        state = json.load(f)
                    
                    for resource in state.get('resources', []):
                        if resource.get('type') == 'chat':
                            attrs = resource['instances'][0]['attributes']
                            usage = attrs.get('usage', {})
                            
                            # Parse experiment ID
                            parts = result['experiment_id'].split('_')
                            model_name = parts[0]
                            token_size = parts[1]
                            
                            metrics.append({
                                'model': model_name,
                                'token_size': token_size,
                                'response_tokens': usage.get('completion_tokens', 0),
                                'total_tokens': usage.get('total_tokens', 0),
                                'cost': usage.get('cost', 0),
                                'response_length': len(attrs.get('response', ''))
                            })
                except Exception as e:
                    print(f"Warning: Could not analyze {result['experiment_id']}: {e}")
        
        # Display results in table format
        if metrics:
            print(f"{'Model':<20} {'Token Limit':<15} {'Used Tokens':<15} {'Cost':<12} {'Response Length'}")
            print("-" * 80)
            
            for m in sorted(metrics, key=lambda x: (x['model'], x['token_size'])):
                print(f"{m['model']:<20} {m['token_size']:<15} {m['response_tokens']:<15} ${m['cost']:<11.6f} {m['response_length']}")
            
            # Summary stats
            print(f"\n{'='*70}")
            print("📊 KEY INSIGHTS")
            print(f"{'='*70}\n")
            
            for model in set(m['model'] for m in metrics):
                model_metrics = [m for m in metrics if m['model'] == model]
                avg_cost = sum(m['cost'] for m in model_metrics) / len(model_metrics)
                avg_tokens = sum(m['response_tokens'] for m in model_metrics) / len(model_metrics)
                print(f"{model}:")
                print(f"  Average Cost: ${avg_cost:.6f}")
                print(f"  Average Tokens: {avg_tokens:.0f}")
                print()


def main():
    # Code review prompt
    code_sample = Path('src/aicl/executor.py').read_text()[:800]
    
    prompt = f"""Review this Python code and provide specific improvements for:
1. Performance optimization
2. Error handling
3. Code maintainability

Code:
{code_sample}

Provide detailed, actionable suggestions."""
    
    template = """terraform {
  required_providers {
    openrouter = {
      source  = "aicl/openrouter"
      version = "~> 1.0"
    }
  }
}

resource "chat" "code_review" {
  model = "{{ model }}"
  messages = [
    {
      role = "system"
      content = "You are an expert code reviewer specializing in Python. Provide detailed, technical feedback."
    },
    {
      role = "user"
      content = "{{ prompt }}"
    }
  ]
  max_tokens = {{ max_tokens }}
  temperature = 0.3
}
"""
    
    # 3x3 Matrix: 3 token sizes x 3 code models
    models = [
        ('claude', 'anthropic/claude-3.5-sonnet'),
        ('gpt4o', 'openai/gpt-4o'),
        ('deepseek', 'deepseek/deepseek-coder')
    ]
    
    token_sizes = [
        ('small', 500),
        ('medium', 1500),
        ('large', 3000)
    ]
    
    variable_matrix = []
    for model_name, model_id in models:
        for size_name, max_tokens in token_sizes:
            variable_matrix.append({
                'id': f'{model_name}_{size_name}',
                'variables': {
                    'model': model_id,
                    'prompt': prompt,
                    'max_tokens': str(max_tokens)
                }
            })
    
    print("\n🎯 3x3 Token Size x Code Model Matrix")
    print("\nModels:")
    for name, model_id in models:
        print(f"  • {name}: {model_id}")
    print("\nToken Sizes:")
    for name, size in token_sizes:
        print(f"  • {name}: {size} tokens")
    print(f"\nTotal Experiments: {len(variable_matrix)}")
    
    runner = TokenMatrixRunner()
    runner.run_matrix(template, variable_matrix)
    
    print(f"\n✨ Complete! Results in {runner.output_dir}")


if __name__ == '__main__':
    main()
