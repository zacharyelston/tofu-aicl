#!/usr/bin/env python3
"""Test RAG with a real codebase question"""
import os
import sys
import requests
import time
import json
from datetime import datetime
import hashlib
import yaml

def get_embedding(text, api_key):
    """Get OpenAI embedding"""
    response = requests.post(
        "https://api.openai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "text-embedding-3-small", "input": text, "dimensions": 1024}
    )
    response.raise_for_status()
    return response.json()['data'][0]['embedding']

def query_pinecone(vector, pinecone_key, pinecone_url, top_k=3):
    """Query Pinecone for similar vectors"""
    response = requests.post(
        f"{pinecone_url}/query",
        headers={"Api-Key": pinecone_key, "Content-Type": "application/json"},
        json={
            "vector": vector,
            "topK": top_k,
            "namespace": "tofu-aicl-codebase",
            "includeMetadata": True
        }
    )
    response.raise_for_status()
    return response.json()

def ask_llm(context, question, model, openrouter_key, system_prompt=None, user_prompt_template=None, temperature=0.3, max_tokens=500):
    """Ask LLM with RAG context"""
    # Use defaults if not provided
    if system_prompt is None:
        system_prompt = "You are a helpful assistant that answers questions about the tofu-aicl codebase based on provided context."
    if user_prompt_template is None:
        user_prompt_template = "Context:\n{context}\n\nQuestion: {question}\n\nProvide a clear, technical answer based on the context above."
    
    user_content = user_prompt_template.format(context=context, question=question)
    
    start = time.time()
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/zacharyelston/tofu-aicl",
            "X-Title": "tofu-aicl"
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "usage": {"include": True}
        }
    )
    elapsed = time.time() - start
    response.raise_for_status()
    result = response.json()
    
    usage = result.get('usage', {})
    return {
        'answer': result['choices'][0]['message']['content'],
        'model': model,
        'usage': usage,
        'response_time_ms': int(elapsed * 1000)
    }

def evaluate_answers(question, answers, openrouter_key, eval_prompt_template='', judge_model='anthropic/claude-3.5-sonnet', judge_temp=0.1, judge_max_tokens=1000):
    """Use LLM to evaluate and compare answers"""
    print("\n🔍 Step 4: Evaluating answers with LLM judge...\n")
    
    # Format answers for comparison
    answers_text = "\n\n".join([
        f"**Answer {i+1} ({ans['model']})**:\n{ans['answer']}"
        for i, ans in enumerate(answers)
    ])
    
    # Use custom template or default
    if eval_prompt_template:
        eval_prompt = eval_prompt_template.format(question=question, answers=answers_text)
    else:
        eval_prompt = f"""You are an expert evaluator assessing RAG system outputs. Compare these answers to the question and rate each on:

1. **Accuracy** (0-10): Correctness based on technical details
2. **Completeness** (0-10): How thoroughly it answers the question
3. **Clarity** (0-10): How well-explained and understandable
4. **Code Specificity** (0-10): References to actual code/files

Question: {question}

{answers_text}

Provide your evaluation in JSON format:
{{
  "evaluations": [
    {{"model": "model_name", "accuracy": X, "completeness": X, "clarity": X, "code_specificity": X, "total": X, "reasoning": "brief explanation"}},
    ...
  ],
  "winner": "model_name",
  "summary": "brief comparison summary"
}}"""
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/zacharyelston/tofu-aicl",
            "X-Title": "tofu-aicl"
        },
        json={
            "model": judge_model,
            "messages": [
                {"role": "user", "content": eval_prompt}
            ],
            "temperature": judge_temp,
            "max_tokens": judge_max_tokens,
            "response_format": {"type": "json_object"}
        }
    )
    response.raise_for_status()
    result = response.json()
    
    try:
        evaluation = json.loads(result['choices'][0]['message']['content'])
        return evaluation
    except json.JSONDecodeError:
        return {"error": "Failed to parse evaluation", "raw": result['choices'][0]['message']['content']}

def load_questions(file_path):
    """Load questions from a file (one per line, ignore empty lines and comments)"""
    questions = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                questions.append(line)
    return questions

def load_config(config_file='rag-config.yaml'):
    """Load RAG configuration from YAML file"""
    if not os.path.exists(config_file):
        print(f"⚠️  Config file not found: {config_file}, using defaults")
        return None
    
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def generate_markdown_report(run_id, timestamp, questions_file, all_results):
    """Generate a markdown report of the RAG test results"""
    report = []
    
    # Header
    report.append(f"# RAG Test Report")
    report.append(f"\n**Run ID:** `{run_id}`  ")
    report.append(f"**Timestamp:** {timestamp}  ")
    report.append(f"**Questions File:** `{questions_file}`  ")
    report.append(f"**Total Questions:** {len(all_results)}\n")
    report.append("---\n")
    
    # Summary table
    report.append("## Summary\n")
    report.append("| Question | Winner | Claude Score | GPT-4 Score |")
    report.append("|----------|--------|--------------|-------------|")
    
    for i, result in enumerate(all_results, 1):
        question_short = result['question'][:60] + "..." if len(result['question']) > 60 else result['question']
        eval_data = result.get('evaluation', {})
        
        if 'evaluations' in eval_data:
            claude_score = next((e['total'] for e in eval_data['evaluations'] if 'claude' in e['model'].lower()), 'N/A')
            gpt4_score = next((e['total'] for e in eval_data['evaluations'] if 'gpt-4' in e['model'].lower()), 'N/A')
            winner = eval_data.get('winner', 'N/A')
        else:
            claude_score = gpt4_score = winner = 'N/A'
        
        report.append(f"| Q{i}: {question_short} | {winner} | {claude_score}/40 | {gpt4_score}/40 |")
    
    report.append("\n---\n")
    
    # Detailed results for each question
    for i, result in enumerate(all_results, 1):
        report.append(f"## Question {i}\n")
        report.append(f"**Question:** {result['question']}\n")
        report.append(f"**Context:** {result['code_chunks_used']} code chunks, {result['doc_chunks_used']} doc chunks\n")
        
        # Model answers
        report.append("### Answers\n")
        for model_result in result['results']:
            model_name = model_result['model'].split('/')[-1]
            report.append(f"#### {model_name}\n")
            report.append(f"- **Response Time:** {model_result['response_time_ms']}ms")
            report.append(f"- **Tokens:** {model_result['usage'].get('total_tokens', 'N/A')}\n")
            report.append(f"{model_result['answer']}\n")
        
        # Evaluation
        eval_data = result.get('evaluation', {})
        if 'evaluations' in eval_data:
            report.append("### LLM Judge Evaluation\n")
            
            # Scores table
            report.append("| Model | Accuracy | Completeness | Clarity | Code Specificity | Total |")
            report.append("|-------|----------|--------------|---------|------------------|-------|")
            
            for eval_item in eval_data['evaluations']:
                model_name = eval_item['model'].split('/')[-1] if '/' in eval_item['model'] else eval_item['model']
                report.append(
                    f"| {model_name} | {eval_item['accuracy']}/10 | {eval_item['completeness']}/10 | "
                    f"{eval_item['clarity']}/10 | {eval_item['code_specificity']}/10 | **{eval_item['total']}/40** |"
                )
            
            report.append(f"\n**Winner:** 🏆 {eval_data['winner']}\n")
            report.append(f"**Summary:** {eval_data['summary']}\n")
            
            # Detailed reasoning
            report.append("#### Detailed Reasoning\n")
            for eval_item in eval_data['evaluations']:
                model_name = eval_item['model'].split('/')[-1] if '/' in eval_item['model'] else eval_item['model']
                report.append(f"- **{model_name}:** {eval_item['reasoning']}\n")
        
        report.append("---\n")
    
    return "\n".join(report)

def main():
    # Load configuration
    config = load_config('rag-config.yaml')
    
    # Check for questions file argument
    questions_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    # API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    pinecone_url = os.getenv("PINECONE_HOST_URL")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    # Get settings from config or use defaults
    if config:
        retrieval_settings = config.get('retrieval', {})
        top_k = retrieval_settings.get('top_k', 10)
        max_code_chunks = retrieval_settings.get('code_chunks_to_use', 3)
        max_doc_chunks = retrieval_settings.get('doc_chunks_to_use', 2)
        models_config = config.get('models_to_test', [])
        judge_config = config.get('judge', {})
        eval_prompt_template = config.get('evaluation_prompt', '')
        system_prompt = config.get('system_prompt', 'You are a helpful assistant that answers questions about the tofu-aicl codebase based on provided context.')
        user_prompt_template = config.get('user_prompt_template', 'Context:\n{context}\n\nQuestion: {question}\n\nProvide a clear, technical answer based on the context above.')
        model_settings = config.get('model_settings', {})
    else:
        top_k = 10
        max_code_chunks = 3
        max_doc_chunks = 2
        models_config = []
        judge_config = {}
        eval_prompt_template = ''
        system_prompt = 'You are a helpful assistant that answers questions about the tofu-aicl codebase based on provided context.'
        user_prompt_template = 'Context:\n{context}\n\nQuestion: {question}\n\nProvide a clear, technical answer based on the context above.'
        model_settings = {'temperature': 0.3, 'max_tokens': 500}
    
    # Load questions
    if questions_file:
        print(f"📋 Loading questions from: {questions_file}\n")
        questions = load_questions(questions_file)
    else:
        # Default question
        questions = ["How does the HCL evaluator resolve interpolations in the tofu-aicl framework?"]
    
    print(f"🔍 Testing {len(questions)} question(s)\n")
    print("="*80)
    
    # Generate unique test run ID
    timestamp = datetime.now()
    run_id = hashlib.md5(f"{timestamp.isoformat()}_{len(questions)}".encode()).hexdigest()[:12]
    
    print(f"🆔 Test Run ID: {run_id}")
    print(f"📅 Timestamp: {timestamp.isoformat()}")
    print("="*80)
    
    all_results = []
    
    for q_idx, question in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"QUESTION {q_idx}/{len(questions)}")
        print(f"{'='*80}")
        print(f"❓ {question}\n")
        
        # Step 1: Get question embedding
        print("Step 1: Creating question embedding...")
        query_vector = get_embedding(question, openai_key)
        print(f"✅ Embedding created ({len(query_vector)} dimensions)\n")
    
        # Step 2: Query Pinecone
        print("Step 2: Searching Pinecone for relevant code...")
        results = query_pinecone(query_vector, pinecone_key, pinecone_url, top_k=top_k)
        matches = results.get('matches', [])
        print(f"✅ Found {len(matches)} relevant chunks\n")
        
        # Build context - prioritize .py files
        context_parts = []
        print("📄 Retrieved chunks:")
    
        # Separate code files from docs
        code_chunks = []
        doc_chunks = []
        
        for i, match in enumerate(matches):
            meta = match.get('metadata', {})
            score = match.get('score', 0)
            file_path = meta.get('file', 'unknown')
            text = meta.get('text', '')
            print(f"  [{i+1}] {file_path} (score: {score:.3f})")
            print(f"      Preview: {text[:150]}...")
            
            if file_path.endswith('.py'):
                code_chunks.append((file_path, text, score))
            else:
                doc_chunks.append((file_path, text, score))
        
        # Prioritize code files, then add docs
        for file_path, text, score in code_chunks[:max_code_chunks]:  # Top N code files
            context_parts.append(f"From {file_path} (score: {score:.3f}):\n{text}")
        for file_path, text, score in doc_chunks[:max_doc_chunks]:  # Top N doc files
            context_parts.append(f"From {file_path} (score: {score:.3f}):\n{text}")
        
        print(f"\n✅ Using {len(code_chunks[:max_code_chunks])} code chunks + {len(doc_chunks[:max_doc_chunks])} doc chunks\n")
        
        context = "\n\n".join(context_parts)
        
        # Step 3: Ask both models
        print("Step 3: Querying models with RAG context...\n")
        
        # Use models from config or defaults
        if models_config:
            models = [(m['model_id'], m['display_name']) for m in models_config]
        else:
            models = [
                ("anthropic/claude-3.5-sonnet", "Claude 3.5 Sonnet"),
                ("openai/gpt-4", "GPT-4")
            ]
        
        results_data = []
        for model, name in models:
            print(f"🤖 {name}...")
            result = ask_llm(
                context, question, model, openrouter_key,
                system_prompt=system_prompt,
                user_prompt_template=user_prompt_template,
                temperature=model_settings.get('temperature', 0.3),
                max_tokens=model_settings.get('max_tokens', 500)
            )
            results_data.append((name, result))
            print(f"   ✅ Response: {len(result['answer'])} chars, {result['response_time_ms']}ms\n")
        
        # Evaluate answers
        evaluation = evaluate_answers(
            question, 
            [result for _, result in results_data], 
            openrouter_key,
            eval_prompt_template=eval_prompt_template,
            judge_model=judge_config.get('model', 'anthropic/claude-3.5-sonnet'),
            judge_temp=judge_config.get('temperature', 0.1),
            judge_max_tokens=judge_config.get('max_tokens', 1000)
        )
        
        # Display evaluation
        if 'evaluations' in evaluation:
            print("📊 LLM Judge Evaluation:")
            for eval_item in evaluation['evaluations']:
                print(f"\n  {eval_item['model']}:")
                print(f"    Accuracy: {eval_item['accuracy']}/10")
                print(f"    Completeness: {eval_item['completeness']}/10")
                print(f"    Clarity: {eval_item['clarity']}/10")
                print(f"    Code Specificity: {eval_item['code_specificity']}/10")
                print(f"    Total: {eval_item['total']}/40")
                print(f"    Reasoning: {eval_item['reasoning']}")
            print(f"\n  🏆 Winner: {evaluation['winner']}")
            print(f"  Summary: {evaluation['summary']}\n")
        
        # Store results for this question
        all_results.append({
            'question': question,
            'context_chunks': len(matches),
            'code_chunks_used': len(code_chunks[:3]),
            'doc_chunks_used': len(doc_chunks[:2]),
            'results': [{'model': name, **result} for name, result in results_data],
            'evaluation': evaluation
        })
        
        # Display results for this question
        print("="*80)
        print(f"📊 RESULTS FOR QUESTION {q_idx}")
        print("="*80)
        
        for name, result in results_data:
            print(f"\n{name}:")
            print(f"  Time: {result['response_time_ms']}ms")
            print(f"  Tokens: {result['usage'].get('total_tokens', 'N/A')}")
            print(f"  Answer: {result['answer'][:200]}...")
    
    # Save all results with metadata
    output_file = f"experiments/rag_test_{run_id}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'run_id': run_id,
            'timestamp': timestamp.isoformat(),
            'questions_file': questions_file if questions_file else 'default',
            'total_questions': len(questions),
            'models_tested': ['anthropic/claude-3.5-sonnet', 'openai/gpt-4'],
            'questions': all_results
        }, f, indent=2)
    
    # Also save as latest for easy access
    latest_file = "experiments/rag_test_results.json"
    with open(latest_file, 'w') as f:
        json.dump({
            'run_id': run_id,
            'timestamp': timestamp.isoformat(),
            'questions_file': questions_file if questions_file else 'default',
            'total_questions': len(questions),
            'models_tested': ['anthropic/claude-3.5-sonnet', 'openai/gpt-4'],
            'questions': all_results
        }, f, indent=2)
    
    # Generate markdown report
    markdown_report = generate_markdown_report(
        run_id, 
        timestamp.isoformat(), 
        questions_file if questions_file else 'default',
        all_results
    )
    
    markdown_file = f"experiments/rag_test_{run_id}.md"
    with open(markdown_file, 'w') as f:
        f.write(markdown_report)
    
    # Also save as latest markdown
    latest_markdown = "experiments/rag_test_results.md"
    with open(latest_markdown, 'w') as f:
        f.write(markdown_report)
    
    print(f"\n{'='*80}")
    print(f"💾 Results saved:")
    print(f"   JSON:")
    print(f"     - {output_file} (unique)")
    print(f"     - {latest_file} (latest)")
    print(f"   Markdown:")
    print(f"     - {markdown_file} (unique)")
    print(f"     - {latest_markdown} (latest)")
    print(f"✅ Tested {len(questions)} question(s) successfully")
    print(f"🆔 Run ID: {run_id}")

if __name__ == "__main__":
    main()
