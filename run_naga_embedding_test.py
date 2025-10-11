#!/usr/bin/env python3
"""
Naga Embedding Comparison - Sequential Isolated Experiments
Compare 3 Naga embedding models with GPT-4o chat and Mistral Large judge
"""

import subprocess
import json
import time
import os
import requests
from pathlib import Path
from datetime import datetime

# Test configuration
EMBEDDINGS = [
    {"name": "text-embedding-3-small", "dims": 1536},
    {"name": "text-embedding-3-large", "dims": 3072},
    {"name": "gemini-embedding-001", "dims": 3072},
]

QUESTIONS = [
    "What is the role of the Evaluator component in the AICL framework?",
    "How does the Planner handle resource dependencies?",
]

CHAT_MODEL = "gpt-4o-2024-08-06"
JUDGE_MODEL = "mistralai/mistral-large"

results = []

print("\n🚀 Naga Embedding Comparison")
print(f"   Embeddings: {len(EMBEDDINGS)}")
print(f"   Questions: {len(QUESTIONS)}")
print(f"   Chat Model: {CHAT_MODEL} (via Naga)")
print(f"   Judge: {JUDGE_MODEL} (via OpenRouter)")
print(f"   Total experiments: {len(EMBEDDINGS) * len(QUESTIONS)}\n")

start_time = time.time()

for emb_idx, embedding in enumerate(EMBEDDINGS):
    for q_idx, question in enumerate(QUESTIONS):
        exp_id = f"{embedding['name']}-q{q_idx+1}"
        
        print(f"🔄 [{exp_id}] {embedding['name']} ({embedding['dims']}d)...")
        
        # Create AICL config
        escaped_question = question.replace('"', '\\"')
        config_content = f'''terraform {{
  required_providers {{
    naga = {{ source = "aicl/naga" }}
    pinecone = {{ source = "aicl/pinecone" }}
  }}
}}

resource "naga_embedding" "question_vector" {{
  model = "{embedding['name']}"
  text = "{escaped_question}"
  aiclResourceName = "question_vector"
}}

resource "query" "results" {{
  index_name = "tofu-aicl"
  namespace = "tofu-aicl-codebase"
  top_k = 5
  vector = "${{resource.naga_embedding.question_vector.attributes.embeddings[0].values}}"
  aiclResourceName = "results"
}}

resource "naga_chat" "answer" {{
  model = "{CHAT_MODEL}"
  messages = [
    {{
      role = "system"
      content = "You are a helpful assistant that answers questions about the AICL framework. Use the provided context."
    }},
    {{
      role = "user"
      content = "Question: {escaped_question}\\n\\nContext: ${{resource.query.results.attributes.matches}}\\n\\nProvide a detailed answer."
    }}
  ]
  max_tokens = 500
  temperature = 0.7
  aiclResourceName = "answer"
}}
'''
        
        config_file = Path(f'experiments/naga_emb/{exp_id}.aicl')
        config_file.parent.mkdir(parents=True, exist_ok=True)
        config_file.write_text(config_content)
        
        # Run experiment
        exp_start = time.time()
        result = subprocess.run(
            ['python', 'run.py', str(config_file)],
            capture_output=True,
            text=True,
            timeout=120
        )
        exp_time = time.time() - exp_start
        
        if result.returncode != 0:
            print(f"   ❌ Failed: {result.stderr[-200:]}")
            results.append({
                'exp_id': exp_id,
                'embedding': embedding['name'],
                'dimensions': embedding['dims'],
                'question': question,
                'success': False,
                'error': result.stderr,
                'time': exp_time
            })
            time.sleep(3)  # Wait before next experiment
            continue
        
        # Read state
        state_file = Path('terraform.tfstate.d/default-exp.tfstate')
        if not state_file.exists():
            print(f"   ❌ No state file")
            results.append({
                'exp_id': exp_id,
                'embedding': embedding['name'],
                'dimensions': embedding['dims'],
                'question': question,
                'success': False,
                'error': 'No state file',
                'time': exp_time
            })
            time.sleep(3)
            continue
        
        state = json.loads(state_file.read_text())
        answer = state['resources'].get('naga_chat-answer', {}).get('attributes', {}).get('response', '')
        usage = state['resources'].get('naga_chat-answer', {}).get('attributes', {}).get('usage', {})
        
        print(f"   ✅ Complete in {exp_time:.1f}s | Tokens: {usage.get('total_tokens', 0)}")
        
        # Grade with Mistral Large
        grading_prompt = f"""Evaluate this AI answer about a codebase:

Question: {question}
Answer: {answer}

Score 1-10 based on accuracy, completeness, clarity, and relevance.

Format:
Score: [number]
Justification: [brief reasoning]"""
        
        try:
            judge_response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": JUDGE_MODEL,
                    "messages": [{"role": "user", "content": grading_prompt}]
                },
                timeout=60
            )
            judge_response.raise_for_status()
            
            judge_text = judge_response.json()['choices'][0]['message']['content']
            score_line = [line for line in judge_text.split('\n') if 'Score:' in line][0]
            score = float(score_line.split(':')[1].strip().split()[0])
            
            print(f"   📊 Quality Score: {score}/10")
            
            results.append({
                'exp_id': exp_id,
                'embedding': embedding['name'],
                'dimensions': embedding['dims'],
                'question': question,
                'answer': answer,
                'quality_score': score,
                'judge_feedback': judge_text,
                'success': True,
                'time': exp_time,
                'tokens': usage.get('total_tokens', 0),
                'prompt_tokens': usage.get('prompt_tokens', 0),
                'completion_tokens': usage.get('completion_tokens', 0),
            })
            
        except Exception as e:
            print(f"   ⚠️  Grading failed: {e}")
            results.append({
                'exp_id': exp_id,
                'embedding': embedding['name'],
                'dimensions': embedding['dims'],
                'question': question,
                'answer': answer,
                'success': True,
                'time': exp_time,
                'tokens': usage.get('total_tokens', 0),
                'quality_score': None,
                'judge_feedback': f"Error: {e}"
            })
        
        # Wait between experiments to ensure clean provider shutdown
        time.sleep(3)

total_time = time.time() - start_time

# Print results
print("\n" + "="*80)
print("📊 NAGA EMBEDDING COMPARISON RESULTS")
print("="*80)

successful = [r for r in results if r.get('success') and r.get('quality_score')]

if successful:
    # Group by embedding
    by_embedding = {}
    for r in successful:
        emb = r['embedding']
        if emb not in by_embedding:
            by_embedding[emb] = []
        by_embedding[emb].append(r)
    
    # Calculate stats
    stats = []
    for emb, res_list in by_embedding.items():
        scores = [r['quality_score'] for r in res_list]
        dims = res_list[0]['dimensions']
        stats.append({
            'embedding': emb,
            'dims': dims,
            'avg_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'count': len(scores)
        })
    
    stats.sort(key=lambda x: x['avg_score'], reverse=True)
    
    print(f"\n🏆 EMBEDDING MODEL RANKINGS (Chat: GPT-4o via Naga, Judge: Mistral Large)\n")
    print(f"{'Rank':<6} {'Embedding':<30} {'Dims':<8} {'Score':<8} {'Range'}")
    print("-" * 70)
    
    medals = ['🥇', '🥈', '🥉']
    for i, stat in enumerate(stats):
        medal = medals[i] if i < len(medals) else f"{i+1}"
        print(f"{medal:<6} {stat['embedding']:<30} {stat['dims']:<8} "
              f"{stat['avg_score']:.1f}/10  {stat['min_score']:.1f}-{stat['max_score']:.1f}")
    
    if stats:
        winner = stats[0]
        print(f"\n🎯 WINNER: {winner['embedding']}")
        print(f"   Dimensions: {winner['dims']}")
        print(f"   Average Quality: {winner['avg_score']:.1f}/10")
        print(f"   Score Range: {winner['min_score']:.1f} - {winner['max_score']:.1f}")

print(f"\n⏱️  Total time: {total_time:.1f}s")
print(f"📊 Successful: {len(successful)}/{len(results)}")

# Save results
output_file = Path(f'experiments/naga_emb/results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
output_file.write_text(json.dumps({
    'timestamp': datetime.now().isoformat(),
    'chat_model': CHAT_MODEL,
    'judge_model': JUDGE_MODEL,
    'total_experiments': len(results),
    'successful': len(successful),
    'results': results
}, indent=2))

print(f"💾 Results saved: {output_file}")
print("="*80 + "\n")
