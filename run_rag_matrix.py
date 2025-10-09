#!/usr/bin/env python3
"""
RAG Matrix Experiment Runner - Test code analysis with different models
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class RAGMatrixRunner:
    def __init__(self, output_dir="experiments/rag-matrix-results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        
    def create_config(self, template, variables, name):
        """Create an AICL config from template with variable substitution"""
        config_content = template
        for key, value in variables.items():
            config_content = config_content.replace(f"{{{{ {key} }}}}", str(value))
        
        config_path = self.output_dir / f"{name}.aicl"
        config_path.write_text(config_content)
        return config_path
    
    def run_experiment(self, config_path, experiment_id):
        """Run a single RAG experiment"""
        print(f"\n{'='*70}")
        print(f"🧪 Running RAG experiment: {experiment_id}")
        print(f"{'='*70}")
        
        result = subprocess.run(
            ['python', 'run.py', str(config_path)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Capture state file
        state_file = Path('terraform.tfstate.d/default-exp.tfstate')
        if state_file.exists():
            dest_state = self.output_dir / f"{experiment_id}.tfstate"
            shutil.copy(state_file, dest_state)
            print(f"✅ State file saved: {dest_state}")
        
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
        """Run matrix of RAG experiments"""
        print(f"\n🚀 Starting RAG Matrix Experiments")
        print(f"Output directory: {self.output_dir}")
        print(f"Total experiments: {len(variable_matrix)}")
        
        for exp in variable_matrix:
            exp_id = exp['id']
            variables = exp['variables']
            
            config_path = self.create_config(template, variables, exp_id)
            
            try:
                result = self.run_experiment(config_path, exp_id)
                self.results.append(result)
                
                status = "✅ SUCCESS" if result['returncode'] == 0 else "❌ FAILED"
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
        """Save experiment summary"""
        summary_file = self.output_dir / 'rag_matrix_summary.json'
        
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
    # RAG pipeline template
    template = """terraform {
  required_providers {
    loader = {
      source  = "aicl/file_loader"
      version = "~> 1.0"
    }
    splitter = {
      source  = "aicl/text_splitter"
      version = "~> 1.0"
    }
    openai = {
      source  = "aicl/openai"
      version = "~> 1.0"
    }
    pinecone = {
      source  = "aicl/pinecone"
      version = "~> 1.0"
    }
    openrouter = {
      source  = "aicl/openrouter"
      version = "~> 1.0"
    }
  }
}

# Load source code
resource "loader_files" "src" {
  path = "{{ source_path }}"
  pattern = "*.py"
  recursive = true
}

# Split into chunks
resource "splitter_text" "chunks" {
  documents = "$${resource.loader_files.src.attributes.documents}"
  chunk_size = 1000
  chunk_overlap = 200
}

# Generate embeddings
resource "embedding" "vectors" {
  texts = "$${resource.splitter_text.chunks.attributes.chunks}"
  model = "text-embedding-3-small"
}

# Store in vector database
resource "pinecone_upsert" "index" {
  vectors = "$${resource.embedding.vectors.attributes.embeddings}"
  namespace = "code-analysis"
}

# Query for relevant code
resource "pinecone_query" "search" {
  vector = "$${resource.embedding.vectors.attributes.embeddings[0].values}"
  top_k = 3
  namespace = "code-analysis"
}

# Ask question about the code
resource "chat" "analysis" {
  model = "{{ model }}"
  messages = [
    {
      role = "system"
      content = "You are a code review expert. Analyze the provided code and suggest specific improvements."
    },
    {
      role = "user"
      content = "{{ question }}"
    }
  ]
  max_tokens = {{ max_tokens }}
}
"""
    
    # Define experiment matrix with code questions
    variable_matrix = [
        {
            'id': 'claude_executor',
            'variables': {
                'source_path': 'src/aicl',
                'model': 'anthropic/claude-3.5-sonnet',
                'question': 'Suggest improvements to the executor.py file',
                'max_tokens': '500'
            }
        },
        {
            'id': 'gpt4_executor',
            'variables': {
                'source_path': 'src/aicl',
                'model': 'openai/gpt-4',
                'question': 'Suggest improvements to the executor.py file',
                'max_tokens': '500'
            }
        },
        {
            'id': 'claude_evaluator',
            'variables': {
                'source_path': 'src/aicl',
                'model': 'anthropic/claude-3.5-sonnet',
                'question': 'Suggest improvements to the evaluator.py file',
                'max_tokens': '500'
            }
        },
        {
            'id': 'gpt4_evaluator',
            'variables': {
                'source_path': 'src/aicl',
                'model': 'openai/gpt-4',
                'question': 'Suggest improvements to the evaluator.py file',
                'max_tokens': '500'
            }
        }
    ]
    
    runner = RAGMatrixRunner()
    runner.run_matrix(template, variable_matrix)
    
    print(f"\n✨ RAG Matrix complete! Check {runner.output_dir} for results")


if __name__ == '__main__':
    main()
