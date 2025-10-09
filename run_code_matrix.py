#!/usr/bin/env python3
"""
Code Analysis Matrix - Test models on code improvement questions
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class CodeMatrixRunner:
    def __init__(self, output_dir="experiments/code-matrix-results"):
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
        print(f"\n🚀 Code Analysis Matrix")
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
    
    def save_summary(self):
        """Save summary"""
        summary_file = self.output_dir / 'code_matrix_summary.json'
        
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


def main():
    # Read actual source code
    executor_code = Path('src/aicl/executor.py').read_text()[:1000]
    evaluator_code = Path('src/aicl/evaluator.py').read_text()[:1000]
    
    template = """terraform {
  required_providers {
    openrouter = {
      source  = "aicl/openrouter"
      version = "~> 1.0"
    }
  }
}

resource "chat" "analysis" {
  model = "{{ model }}"
  messages = [
    {
      role = "system"
      content = "You are a code review expert. Suggest specific, actionable improvements."
    },
    {
      role = "user"
      content = "{{ question }}"
    }
  ]
  max_tokens = {{ max_tokens }}
}
"""
    
    variable_matrix = [
        {
            'id': 'claude_executor',
            'variables': {
                'model': 'anthropic/claude-3.5-sonnet',
                'question': f'Review this executor.py code and suggest 3 improvements:\\n\\n{executor_code}',
                'max_tokens': '400'
            }
        },
        {
            'id': 'gpt4_executor',
            'variables': {
                'model': 'openai/gpt-4',
                'question': f'Review this executor.py code and suggest 3 improvements:\\n\\n{executor_code}',
                'max_tokens': '400'
            }
        },
        {
            'id': 'claude_evaluator',
            'variables': {
                'model': 'anthropic/claude-3.5-sonnet',
                'question': f'Review this evaluator.py code and suggest 3 improvements:\\n\\n{evaluator_code}',
                'max_tokens': '400'
            }
        },
        {
            'id': 'gpt4_evaluator',
            'variables': {
                'model': 'openai/gpt-4',
                'question': f'Review this evaluator.py code and suggest 3 improvements:\\n\\n{evaluator_code}',
                'max_tokens': '400'
            }
        }
    ]
    
    runner = CodeMatrixRunner()
    runner.run_matrix(template, variable_matrix)
    
    print(f"\n✨ Complete! Results in {runner.output_dir}")


if __name__ == '__main__':
    main()
