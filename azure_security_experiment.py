#!/usr/bin/env python3
"""Azure Self-Build Security Analyzer Experiment"""
import os
import requests
import json
from datetime import datetime

API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2023-05-15')
DEPLOYMENT = 'gpt-35-turbo'

def azure_chat(prompt, temperature=0.3, max_tokens=1500):
    url = f"{ENDPOINT}/openai/deployments/{DEPLOYMENT}/chat/completions?api-version={API_VERSION}"
    response = requests.post(
        url,
        headers={'api-key': API_KEY, 'Content-Type': 'application/json'},
        json={'messages': [{'role': 'user', 'content': prompt}], 'temperature': temperature, 'max_tokens': max_tokens},
        timeout=60
    )
    data = response.json()
    return data['choices'][0]['message']['content'], data['usage']

# Run experiment
results = {
    'experiment': 'Azure Self-Build Security Analyzer',
    'timestamp': datetime.now().isoformat(),
    'deployment': DEPLOYMENT,
    'steps': []
}

# Step 1: Generate code
print("Step 1: Generating SecurityAnalyzer code...")
gen_prompt = """You are a Python expert. Create a security code analyzer that:
1. Accepts code snippets
2. Analyzes for: SQL injection, hardcoded secrets, eval/exec, path traversal
3. Returns JSON with: risk_level, vulnerabilities[], recommendations[], security_score

Write complete Python code. Output ONLY the code, no explanations."""

generated_code, usage1 = azure_chat(gen_prompt, 0.3, 1500)
results['steps'].append({
    'step': 1,
    'description': 'Generate SecurityAnalyzer code',
    'output': generated_code,
    'tokens': usage1
})

# Step 2: Test it
print("Step 2: Testing security analysis...")
test_prompt = """Analyze this vulnerable code:

```python
import os
password = "admin123"
def login(username, pwd):
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + pwd + "'"
    exec("import " + username)
    return eval(query)
```

Provide JSON: {"risk_level": "...", "vulnerabilities": ["..."], "recommendations": ["..."], "security_score": 0-100}"""

analysis, usage2 = azure_chat(test_prompt, 0.1, 800)
results['steps'].append({
    'step': 2,
    'description': 'Test on vulnerable code',
    'output': analysis,
    'tokens': usage2
})

# Step 3: Grade it
print("Step 3: Self-evaluation...")
grade_prompt = f"""Grade this AI-generated security analyzer:

{generated_code[:800]}

Evaluate: completeness, accuracy, code quality, practicality

Return JSON: {{"score": 0-100, "grade": "ACCEPT/REJECT", "strengths": ["..."], "weaknesses": ["..."], "verdict": "..."}}"""

grade, usage3 = azure_chat(grade_prompt, 0.2, 600)
results['steps'].append({
    'step': 3,
    'description': 'Self-evaluation',
    'output': grade,
    'tokens': usage3
})

results['total_tokens'] = usage1['total_tokens'] + usage2['total_tokens'] + usage3['total_tokens']

# Save to file
with open('azure_experiment_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Results saved to: azure_experiment_results.json")
print(f"💰 Total tokens: {results['total_tokens']}")
