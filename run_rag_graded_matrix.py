#!/usr/bin/env python3
"""
RAG Matrix with LLM-as-Judge Quality Validation
Tests RAG pipeline against real codebase with quality grading
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from llm_grader import LLMGrader

class RAGGradedMatrixRunner:
    def __init__(self, output_dir="experiments/rag-graded-results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        self.judge_model = "openai/gpt-4"
        
    def load_questions(self, questions_file="questions.txt"):
        """Load test questions from file"""
        questions = []
        with open(questions_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    questions.append(line)
        return questions
    
    def create_rag_config(self, question, model, experiment_id):
        """Create RAG query AICL config for a specific question"""
        config = f"""terraform {{
  required_providers {{
    openai = {{
      source = "aicl/openai"
    }}
    openrouter = {{
      source = "aicl/openrouter"
    }}
    pinecone = {{
      source = "aicl/pinecone"
    }}
  }}
}}

# Generate embedding for the question
resource "embedding" "question_vector" {{
  text = "{question}"
  model = "text-embedding-3-small"
  aiclResourceName = "question_vector"
}}

# Query Pinecone for relevant code chunks
resource "query" "relevant_chunks" {{
  vector = "${{resource.embedding.question_vector.attributes.embedding}}"
  top_k = 5
  namespace = "tofu-aicl-codebase"
  aiclResourceName = "relevant_chunks"
}}

# Generate answer using retrieved context
resource "chat" "answer" {{
  model = "{model}"
  messages = [
    {{
      role = "system"
      content = "You are an expert on the AICL framework. Answer questions accurately based on the provided code context. Be specific and reference actual implementation details."
    }},
    {{
      role = "user"
      content = "Context from codebase:\\n${{resource.query.relevant_chunks.attributes.results}}\\n\\nQuestion: {question}"
    }}
  ]
  max_tokens = 500
  aiclResourceName = "answer"
}}
"""
        config_path = self.output_dir / f"{experiment_id}.aicl"
        config_path.write_text(config)
        return config_path
    
    def run_rag_experiment(self, question, model, experiment_id):
        """Run a single RAG experiment"""
        print(f"\n🔧 [{experiment_id}] {model.split('/')[-1]}: {question[:60]}...")
        
        # Create config
        config_path = self.create_rag_config(question, model, experiment_id)
        
        # Run experiment
        result = subprocess.run(
            ['python', 'run.py', str(config_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Extract response from state file
        response_text = ""
        state_file = Path('terraform.tfstate.d/default-exp.tfstate')
        
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
                chat_resource = state.get('resources', {}).get('chat-answer', {})
                response_text = chat_resource.get('attributes', {}).get('response', '')
                usage = chat_resource.get('attributes', {}).get('usage', {})
                perf = chat_resource.get('attributes', {}).get('performance', {})
                cost = chat_resource.get('attributes', {}).get('cost', {})
        
        success = result.returncode == 0 and len(response_text) > 0
        status = "✅" if success else "❌"
        print(f"{status} {len(response_text)} chars | Cost: ${cost.get('total_usd', 0):.4f}")
        
        return {
            'experiment_id': experiment_id,
            'model': model,
            'question': question,
            'success': success,
            'response': response_text,
            'response_preview': response_text[:150] + '...' if len(response_text) > 150 else response_text,
            'usage': usage if state_file.exists() else {},
            'performance': perf if state_file.exists() else {},
            'cost': cost if state_file.exists() else {},
            'returncode': result.returncode,
            'timestamp': datetime.now().isoformat()
        }
    
    def grade_responses(self, results):
        """Grade RAG responses using LLM-as-Judge"""
        print("\n" + "="*70)
        print("🎯 GRADING RAG RESPONSES WITH LLM-AS-JUDGE")
        print("="*70)
        print(f"Judge Model: {self.judge_model}\n")
        
        grader = LLMGrader(judge_model=self.judge_model)
        graded_results = []
        
        for i, result in enumerate(results, 1):
            if not result.get('success'):
                graded_results.append(result)
                continue
            
            question = result['question']
            response = result['response']
            
            print(f"[{i}/{len(results)}] Grading: {result['model'].split('/')[-1]}...", end=' ')
            
            try:
                # Grade with context that this is a code-related question
                context = "This is a technical question about the AICL framework codebase. The answer should be accurate, specific, and reference actual implementation details."
                grades = grader.grade_response(
                    question, 
                    response, 
                    criteria=['accuracy', 'relevance', 'completeness'],
                    context=context
                )
                
                result['quality'] = {
                    'scores': grades.get('scores', {}),
                    'overall_score': grades.get('overall_score', 0),
                    'reasoning': grades.get('reasoning', ''),
                    'judge_model': self.judge_model
                }
                
                score = result['quality']['overall_score']
                print(f"✅ {score}/10")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                result['quality'] = {'error': str(e), 'overall_score': 0}
            
            graded_results.append(result)
        
        return graded_results
    
    def run_matrix(self, questions, models):
        """Run matrix of RAG experiments with grading"""
        print("\n" + "="*70)
        print("🧪 RAG MATRIX WITH QUALITY GRADING")
        print("="*70)
        print(f"📊 Testing {len(models)} models × {len(questions)} questions = {len(models) * len(questions)} experiments")
        print(f"👨‍⚖️ Judge Model: {self.judge_model}\n")
        
        experiment_num = 1
        for model in models:
            for question in questions:
                experiment_id = f"rag_{experiment_num:02d}_{model.split('/')[-1].replace('-', '_')}"
                
                result = self.run_rag_experiment(question, model, experiment_id)
                self.results.append(result)
                
                experiment_num += 1
        
        # Grade all responses
        self.results = self.grade_responses(self.results)
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_summary()
    
    def print_summary(self):
        """Print summary report"""
        print("\n" + "="*70)
        print("📈 RAG QUALITY VALIDATION SUMMARY")
        print("="*70 + "\n")
        
        successful = [r for r in self.results if r.get('success')]
        total = len(self.results)
        
        print(f"✅ Success Rate: {len(successful)}/{total} ({100*len(successful)//total if total > 0 else 0}%)")
        
        if successful:
            avg_quality = sum(r.get('quality', {}).get('overall_score', 0) for r in successful) / len(successful)
            total_cost = sum(r.get('cost', {}).get('total_usd', 0) for r in successful)
            total_tokens = sum(r.get('usage', {}).get('total_tokens', 0) for r in successful)
            
            print(f"📊 Average Quality Score: {avg_quality:.1f}/10")
            print(f"🔢 Total Tokens: {total_tokens:,}")
            print(f"💰 Total Cost: ${total_cost:.4f}\n")
            
            # By model
            print("🤖 QUALITY BY MODEL:")
            models = set(r['model'] for r in successful)
            for model in sorted(models):
                model_results = [r for r in successful if r['model'] == model]
                avg_score = sum(r.get('quality', {}).get('overall_score', 0) for r in model_results) / len(model_results)
                min_score = min(r.get('quality', {}).get('overall_score', 0) for r in model_results)
                max_score = max(r.get('quality', {}).get('overall_score', 0) for r in model_results)
                
                print(f"  {model.split('/')[-1]}:")
                print(f"    Avg: {avg_score:.1f}/10 | Range: {min_score:.1f}-{max_score:.1f}")
    
    def save_summary(self):
        """Save detailed results to JSON"""
        summary_file = self.output_dir / f'rag_graded_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_experiments': len(self.results),
            'successful': sum(1 for r in self.results if r.get('success')),
            'judge_model': self.judge_model,
            'results': self.results
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Full report saved: {summary_file}")
        print("="*70 + "\n")


def main():
    runner = RAGGradedMatrixRunner()
    
    # Load questions from file
    print("📝 Loading test questions from questions.txt...")
    questions = runner.load_questions()
    print(f"   Loaded {len(questions)} questions\n")
    
    # Select a subset for testing (first 3 questions)
    test_questions = questions[:3]
    
    # Models to test
    models = [
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4",
        "openai/gpt-4o-mini"
    ]
    
    # Run the matrix
    runner.run_matrix(test_questions, models)
    
    print(f"✨ RAG quality validation complete! Check {runner.output_dir} for results")


if __name__ == '__main__':
    main()
