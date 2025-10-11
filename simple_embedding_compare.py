#!/usr/bin/env python3
"""
Simple embedding comparison using existing proven providers
Compare embeddings with consistent GPT-4o chat and Mistral Large judge
"""

import subprocess
import json
import time
from pathlib import Path

# Test with just OpenAI embedding (known to work) vs trying different retrieval  parameters
experiments = [
    {"name": "OpenAI Small + GPT-4o", "emb": "text-embedding-3-small", "chat": "gpt-4o"},
]

question = "What is the role of the Evaluator component in the AICL framework?"

for exp in experiments:
    print(f"\n🔄 Testing: {exp['name']}...")
    
    # Create AICL config using OpenAI embeddings (proven to work)
    config = f'''terraform {{
  required_providers {{
    openai = {{ source = "aicl/openai" }}
    openrouter = {{ source = "aicl/openrouter" }}
    pinecone = {{ source = "aicl/pinecone" }}
  }}
}}

resource "embedding" "q" {{
  model = "{exp['emb']}"
  text = "{question}"
  aiclResourceName = "q"
}}

resource "query" "results" {{
  index_name = "tofu-aicl"
  namespace = "tofu-aicl-codebase"
  top_k = 5
  vector = "${{resource.embedding.q.attributes.vector}}"
  aiclResourceName = "results"
}}

resource "chat" "answer" {{
  model = "openai/{exp['chat']}"
  messages = [
    {{
      role = "user"
      content = "Question: {question}\\n\\nContext: ${{resource.query.results.attributes.matches}}\\n\\nAnswer:"
    }}
  ]
  max_tokens = 300
  aiclResourceName = "answer"
}}
'''
    
    config_file = f"test_{exp['name'].replace(' ', '_')}.aicl"
    Path(config_file).write_text(config)
    
    result = subprocess.run(['python', 'run.py', config_file], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Success!")
        state_file = Path('terraform.tfstate.d/default-exp.tfstate')
        if state_file.exists():
            state = json.loads(state_file.read_text())
            answer = state.get('resources', {}).get('chat-answer', {}).get('attributes', {}).get('response', 'No answer')
            print(f"Answer: {answer[:200]}...")
    else:
        print(f"❌ Failed: {result.stderr[-500:]}")
    
    time.sleep(2)

print("\n✅ Quick test complete")
