#!/usr/bin/env python3
"""
Matrix Experiment Runner for AICL
Runs experiments with different variable combinations and stores state files centrally
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import tempfile

class MatrixRunner:
    def __init__(self, output_dir="experiments/matrix-results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        
    def create_config(self, template, variables, name):
        """Create an AICL config from template with variable substitution"""
        config_content = template
        for key, value in variables.items():
            config_content = config_content.replace(f"{{{{ {key} }}}}", str(value))
        
        # Write to temp file
        config_path = self.output_dir / f"{name}.aicl"
        config_path.write_text(config_content)
        return config_path
    
    def run_experiment(self, config_path, experiment_id):
        """Run a single AICL experiment and capture state"""
        print(f"\n{'='*70}")
        print(f"🧪 Running experiment: {experiment_id}")
        print(f"{'='*70}")
        
        # Run AICL
        result = subprocess.run(
            ['python', 'run.py', str(config_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Capture state file if it exists
        state_file = Path('terraform.tfstate.d/default-exp.tfstate')
        if state_file.exists():
            # Copy state to results directory with experiment ID
            dest_state = self.output_dir / f"{experiment_id}.tfstate"
            shutil.copy(state_file, dest_state)
            print(f"✅ State file saved: {dest_state}")
        
        # Parse output for metrics
        metrics = self.parse_output(result.stdout, result.stderr)
        
        return {
            'experiment_id': experiment_id,
            'config_path': str(config_path),
            'state_file': str(dest_state) if state_file.exists() else None,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
    
    def parse_output(self, stdout, stderr):
        """Extract metrics from AICL output"""
        metrics = {
            'resources_created': 0,
            'success': False
        }
        
        # Look for "Apply complete: X resources created"
        if 'Apply complete' in stdout:
            metrics['success'] = True
            # Extract resource count
            for line in stdout.split('\n'):
                if 'resources created' in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit():
                            metrics['resources_created'] = int(part)
                            break
        
        return metrics
    
    def run_matrix(self, template, variable_matrix):
        """Run matrix of experiments with different variable combinations"""
        print(f"\n🚀 Starting Matrix Experiments")
        print(f"Output directory: {self.output_dir}")
        print(f"Total experiments: {len(variable_matrix)}")
        
        for exp in variable_matrix:
            exp_id = exp['id']
            variables = exp['variables']
            
            # Create config from template
            config_path = self.create_config(template, variables, exp_id)
            
            # Run experiment
            try:
                result = self.run_experiment(config_path, exp_id)
                self.results.append(result)
                
                # Print summary
                status = "✅ SUCCESS" if result['returncode'] == 0 else "❌ FAILED"
                print(f"Status: {status}")
                print(f"Resources: {result['metrics']['resources_created']}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                self.results.append({
                    'experiment_id': exp_id,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # Save summary
        self.save_summary()
    
    def save_summary(self):
        """Save experiment summary to JSON"""
        summary_file = self.output_dir / 'matrix_summary.json'
        
        summary = {
            'total_experiments': len(self.results),
            'successful': sum(1 for r in self.results if r.get('returncode') == 0),
            'failed': sum(1 for r in self.results if r.get('returncode', 1) != 0),
            'timestamp': datetime.now().isoformat(),
            'experiments': self.results
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Summary saved to: {summary_file}")
        print(f"Total: {summary['total_experiments']} | Success: {summary['successful']} | Failed: {summary['failed']}")


def main():
    # Example: Simple chat experiment matrix
    template = """terraform {
  required_providers {
    openrouter = {
      source  = "aicl/openrouter"
      version = "~> 1.0"
    }
  }
}

resource "chat" "test_response" {
  model = "{{ model }}"
  messages = [
    {
      role = "user"
      content = "{{ prompt }}"
    }
  ]
  max_tokens = {{ max_tokens }}
}
"""
    
    # Define experiment matrix
    variable_matrix = [
        {
            'id': 'claude_short',
            'variables': {
                'model': 'anthropic/claude-3.5-sonnet',
                'prompt': 'Say hello in 5 words',
                'max_tokens': '50'
            }
        },
        {
            'id': 'claude_medium',
            'variables': {
                'model': 'anthropic/claude-3.5-sonnet',
                'prompt': 'Explain REST APIs in one sentence',
                'max_tokens': '100'
            }
        },
        {
            'id': 'gpt4_short',
            'variables': {
                'model': 'openai/gpt-4',
                'prompt': 'Say hello in 5 words',
                'max_tokens': '50'
            }
        },
        {
            'id': 'gpt4_medium',
            'variables': {
                'model': 'openai/gpt-4',
                'prompt': 'Explain REST APIs in one sentence',
                'max_tokens': '100'
            }
        }
    ]
    
    # Run matrix
    runner = MatrixRunner()
    runner.run_matrix(template, variable_matrix)
    
    print(f"\n✨ Matrix complete! Check {runner.output_dir} for results")
    print(f"\nState files available for comparison:")
    for state_file in runner.output_dir.glob("*.tfstate"):
        print(f"  - {state_file.name}")


if __name__ == '__main__':
    main()
