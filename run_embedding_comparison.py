#!/usr/bin/env python3
"""
Embedding Model Comparison for RAG Pipeline
Compares 4 embedding models with consistent GPT-4o chat model
Judge: Mistral Large (9.7/10 winner)
"""

import yaml
import json
import time
import subprocess
import os
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class EmbeddingComparison:
    def __init__(self, config_file='embedding-comparison-config.yaml'):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.results = []
        self.output_dir = Path('experiments/embedding_comparison')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load questions
        self.questions = self.load_questions()
        
        # Judge model
        self.judge_model = self.config['judge']['model']
        
        # Consistent chat model
        self.chat_model = self.config['chat_model']
    
    def load_questions(self):
        """Load test questions"""
        questions_file = Path('rag_questions.txt')
        if not questions_file.exists():
            # Default questions
            return [
                "What is the role of the Evaluator component in the AICL framework?",
                "How does the Planner handle resource dependencies?",
                "Explain how provider communication works via gRPC."
            ]
        
        with open(questions_file, 'r') as f:
            return [q.strip() for q in f.readlines() if q.strip()]
    
    def create_rag_config(self, embedding_info, experiment_id):
        """Create RAG pipeline AICL config for given embedding model"""
        
        config_content = f'''terraform {{
  required_providers {{
    naga = {{
      source = "aicl/naga"
    }}
    pinecone = {{
      source = "aicl/pinecone"
    }}
  }}
}}

# 1. Generate embedding for the question using {embedding_info['name']}
resource "naga_embedding" "question_vector" {{
  model = "{embedding_info['id']}"
  text = "{self.current_question}"
  aiclResourceName = "question_vector"
}}

# 2. Query Pinecone for similar code chunks
resource "query" "results" {{
  index_name = "tofu-aicl"
  namespace = "{self.config['test_config']['pinecone_namespace']}"
  top_k = {self.config['test_config']['top_k']}
  vector = "${{resource.naga_embedding.question_vector.attributes.embeddings[0].values}}"
  aiclResourceName = "results"
}}

# 3. Generate answer using GPT-4o (consistent chat model)
resource "naga_chat" "answer" {{
  model = "{self.chat_model['id']}"
  messages = [
    {{
      role = "system"
      content = "You are a helpful assistant that answers questions about the AICL framework codebase. Use the provided code context to give accurate, detailed answers."
    }},
    {{
      role = "user"
      content = <<-EOT
Question: {self.current_question}

Context from codebase:
${{resource.query.results.attributes.matches}}

Please provide a detailed answer based on the context above.
EOT
    }}
  ]
  max_tokens = 500
  temperature = 0.7
  aiclResourceName = "answer"
}}
'''
        
        config_file = self.output_dir / f'{experiment_id}.aicl'
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        return config_file
    
    def run_rag_pipeline(self, embedding_info, question, experiment_id):
        """Run RAG pipeline with specific embedding model"""
        
        self.current_question = question.replace('"', '\\"')
        
        # Create AICL config
        config_file = self.create_rag_config(embedding_info, experiment_id)
        
        print(f"🔄 [{experiment_id}] Running with {embedding_info['name']}...")
        
        start_time = time.time()
        
        try:
            # Run AICL pipeline
            result = subprocess.run(
                ['python', 'run.py', str(config_file)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            elapsed_time = time.time() - start_time
            
            if result.returncode != 0:
                print(f"❌ [{experiment_id}] Failed: {result.stderr}")
                return {
                    'experiment_id': experiment_id,
                    'embedding_model': embedding_info['name'],
                    'embedding_id': embedding_info['id'],
                    'chat_model': self.chat_model['name'],
                    'question': question,
                    'success': False,
                    'error': result.stderr,
                    'elapsed_time': elapsed_time
                }
            
            # Read state file for response
            state_file = Path(f'terraform.tfstate.d/{experiment_id}.tfstate')
            if not state_file.exists():
                raise Exception("State file not found")
            
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            # Extract answer
            answer = state['resources'].get('naga_chat-answer', {}).get('attributes', {}).get('response', '')
            
            # Get token usage
            usage = state['resources'].get('naga_chat-answer', {}).get('attributes', {}).get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)
            
            print(f"✅ [{experiment_id}] Complete in {elapsed_time:.1f}s | Tokens: {total_tokens}")
            
            return {
                'experiment_id': experiment_id,
                'embedding_model': embedding_info['name'],
                'embedding_id': embedding_info['id'],
                'embedding_dimensions': embedding_info.get('dimensions', 'unknown'),
                'chat_model': self.chat_model['name'],
                'chat_model_id': self.chat_model['id'],
                'question': question,
                'answer': answer,
                'success': True,
                'elapsed_time': elapsed_time,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"❌ [{experiment_id}] Exception: {str(e)}")
            return {
                'experiment_id': experiment_id,
                'embedding_model': embedding_info['name'],
                'embedding_id': embedding_info['id'],
                'chat_model': self.chat_model['name'],
                'question': question,
                'success': False,
                'error': str(e),
                'elapsed_time': elapsed_time
            }
    
    def grade_response(self, result):
        """Grade a single response using LLM judge (Mistral Large)"""
        if not result.get('success'):
            return result
        
        grading_prompt = f"""You are an expert evaluator assessing AI-generated answers about a codebase.

Question: {result['question']}

AI Answer: {result['answer']}

Please evaluate the answer on these criteria:
1. Accuracy: Is the answer factually correct based on the question?
2. Completeness: Does it fully address the question?
3. Clarity: Is it well-explained and easy to understand?
4. Relevance: Does it stay focused on the question?

Provide a score from 1-10 and brief justification.

Format your response as:
Score: [number]
Justification: [your reasoning]"""

        try:
            # Use OpenRouter for judge (Mistral Large)
            import requests
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.judge_model,
                    "messages": [{"role": "user", "content": grading_prompt}]
                }
            )
            response.raise_for_status()
            
            judge_response = response.json()['choices'][0]['message']['content']
            
            # Parse score
            score_line = [line for line in judge_response.split('\n') if 'Score:' in line][0]
            score = float(score_line.split(':')[1].strip())
            
            result['quality_score'] = score
            result['judge_feedback'] = judge_response
            
            print(f"   📊 Quality Score: {score}/10")
            
        except Exception as e:
            print(f"   ⚠️  Grading failed: {e}")
            result['quality_score'] = None
            result['judge_feedback'] = f"Grading error: {e}"
        
        return result
    
    def run_experiments(self):
        """Run all embedding comparison experiments"""
        embeddings = [e for e in self.config['embeddings'] if e.get('enabled', True)]
        questions = self.questions[:self.config['test_config']['num_questions']]
        # Run sequentially to avoid provider conflicts
        max_workers = 1  # self.config['test_config'].get('max_workers', 4)
        
        print(f"\n🚀 Starting Embedding Comparison Experiments")
        print(f"   Embeddings: {len(embeddings)}")
        print(f"   Questions: {len(questions)}")
        print(f"   Chat Model: {self.chat_model['name']} (consistent)")
        print(f"   Judge: {self.judge_model}")
        print(f"   Total experiments: {len(embeddings) * len(questions)}")
        print(f"   Parallel workers: {max_workers}\n")
        
        start_time = time.time()
        
        # Run experiments in parallel
        experiment_tasks = []
        for embedding in embeddings:
            for i, question in enumerate(questions):
                experiment_id = f"{embedding['id'].replace('/', '-').replace('.', '-')}-q{i+1}"
                experiment_tasks.append((embedding, question, experiment_id))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.run_rag_pipeline, emb, q, eid): (emb, q, eid)
                for emb, q, eid in experiment_tasks
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    emb, q, eid = futures[future]
                    print(f"❌ [{eid}] Failed: {str(e)}")
                    self.results.append({
                        'experiment_id': eid,
                        'embedding_model': emb['name'],
                        'question': q,
                        'success': False,
                        'error': str(e)
                    })
        
        elapsed_time = time.time() - start_time
        print(f"\n⏱️  Total execution time: {elapsed_time:.1f}s")
        print(f"📊 Average time per experiment: {elapsed_time/len(experiment_tasks):.1f}s\n")
        
        # Grade all responses
        print("🎯 Grading responses with Mistral Large judge...\n")
        self.results = [self.grade_response(r) for r in self.results]
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_results()
    
    def print_summary(self):
        """Print comparison summary"""
        print("\n" + "="*80)
        print("📊 EMBEDDING COMPARISON RESULTS")
        print("="*80)
        
        successful = [r for r in self.results if r.get('success')]
        
        if not successful:
            print("❌ No successful experiments")
            return
        
        # Group by embedding model
        by_embedding = {}
        for result in successful:
            emb = result['embedding_model']
            if emb not in by_embedding:
                by_embedding[emb] = []
            by_embedding[emb].append(result)
        
        # Calculate stats per embedding
        stats = []
        for emb_name, results in by_embedding.items():
            scores = [r['quality_score'] for r in results if r.get('quality_score')]
            tokens = [r.get('total_tokens', 0) for r in results]
            times = [r.get('elapsed_time', 0) for r in results]
            dimensions = results[0].get('embedding_dimensions', 'unknown')
            
            if scores:
                stats.append({
                    'embedding': emb_name,
                    'dimensions': dimensions,
                    'avg_score': sum(scores) / len(scores),
                    'min_score': min(scores),
                    'max_score': max(scores),
                    'avg_tokens': sum(tokens) / len(tokens) if tokens else 0,
                    'avg_time': sum(times) / len(times) if times else 0
                })
        
        # Sort by score
        stats.sort(key=lambda x: x['avg_score'], reverse=True)
        
        print(f"\n🏆 EMBEDDING MODEL RANKINGS (Chat: {self.chat_model['name']}, Judge: {self.judge_model})\n")
        print(f"{'Rank':<6} {'Embedding':<35} {'Dims':<8} {'Score':<8} {'Range':<12} {'Avg Time'}")
        print("-" * 80)
        
        medals = ['🥇', '🥈', '🥉', '4️⃣']
        for i, stat in enumerate(stats):
            medal = medals[i] if i < len(medals) else f"{i+1}"
            print(f"{medal:<6} {stat['embedding']:<35} {stat['dimensions']:<8} "
                  f"{stat['avg_score']:.1f}/10  {stat['min_score']:.1f}-{stat['max_score']:.1f}      "
                  f"{stat['avg_time']:.1f}s")
        
        # Best embedding
        if stats:
            best = stats[0]
            print(f"\n🎯 WINNER: {best['embedding']}")
            print(f"   Average Quality: {best['avg_score']:.1f}/10")
            print(f"   Dimensions: {best['dimensions']}")
            print(f"   Score Range: {best['min_score']:.1f} - {best['max_score']:.1f}")
            print(f"   Avg Response Time: {best['avg_time']:.1f}s")
        
        print("\n" + "="*80)
    
    def save_results(self):
        """Save detailed results"""
        summary_file = self.output_dir / f'embedding_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'chat_model': self.chat_model,
            'judge_model': self.judge_model,
            'total_experiments': len(self.results),
            'successful': sum(1 for r in self.results if r.get('success')),
            'results': self.results
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Results saved: {summary_file}\n")


def main():
    comparison = EmbeddingComparison()
    comparison.run_experiments()


if __name__ == '__main__':
    main()
