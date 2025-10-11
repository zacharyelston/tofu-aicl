#!/usr/bin/env python3
"""Run 3x1 RAG matrix: 3 models x 1 token size (1500)"""
import os
import sys
import requests
import time
import json
from datetime import datetime
import hashlib

# Matrix configuration
MODELS = {
    "claude": "anthropic/claude-3.5-sonnet",
    "mistral": "mistralai/mistral-large",
    "openai": "openai/gpt-4"
}

MAX_TOKENS = 1500

def get_embedding(text, api_key):
    """Get OpenAI embedding"""
    response = requests.post(
        "https://api.openai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "text-embedding-3-small", "input": text, "dimensions": 1024}
    )
    response.raise_for_status()
    return response.json()['data'][0]['embedding']

def query_pinecone(vector, pinecone_key, pinecone_url, top_k=5):
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

def ask_llm(context, question, model, openrouter_key, max_tokens=1500):
    """Ask LLM with RAG context"""
    system_prompt = "You are a helpful assistant that answers questions about the tofu-aicl codebase based on provided context."
    user_content = f"Context:\n{context}\n\nQuestion: {question}\n\nProvide a clear, technical answer based on the context above."
    
    start = time.time()
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
    )
    response.raise_for_status()
    elapsed = int((time.time() - start) * 1000)
    
    data = response.json()
    return {
        "answer": data['choices'][0]['message']['content'],
        "usage": data.get('usage', {}),
        "response_time_ms": elapsed
    }

def run_experiment(question, openai_key, pinecone_key, pinecone_url, openrouter_key):
    """Run one complete experiment with all models"""
    
    print(f"\n{'='*80}")
    print(f"QUESTION: {question}")
    print(f"{'='*80}\n")
    
    # Get embedding and retrieve context
    print("🔍 Creating embedding and retrieving context...")
    query_vector = get_embedding(question, openai_key)
    results = query_pinecone(query_vector, pinecone_key, pinecone_url, top_k=5)
    
    # Build context
    context_parts = []
    for match in results.get('matches', []):
        metadata = match.get('metadata', {})
        file = metadata.get('file', 'unknown')
        text = metadata.get('text', '')
        context_parts.append(f"[{file}]\n{text}")
    
    context = "\n\n".join(context_parts)
    print(f"✅ Retrieved {len(results.get('matches', []))} chunks\n")
    
    # Run all models with 1500 tokens
    matrix_results = []
    
    for model_name, model_id in MODELS.items():
        print(f"🤖 Testing {model_name} (max_tokens={MAX_TOKENS})...", end=" ", flush=True)
        
        try:
            result = ask_llm(context, question, model_id, openrouter_key, MAX_TOKENS)
            
            matrix_results.append({
                "model": model_name,
                "model_id": model_id,
                "max_tokens": MAX_TOKENS,
                "answer": result["answer"],
                "answer_length": len(result["answer"]),
                "usage": result["usage"],
                "response_time_ms": result["response_time_ms"]
            })
            
            tokens = result["usage"].get("total_tokens", "N/A")
            print(f"✅ {result['response_time_ms']}ms, {tokens} tokens, {len(result['answer'])} chars")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            matrix_results.append({
                "model": model_name,
                "model_id": model_id,
                "max_tokens": MAX_TOKENS,
                "error": str(e)
            })
    
    return {
        "question": question,
        "context_chunks": len(results.get('matches', [])),
        "max_tokens": MAX_TOKENS,
        "results": matrix_results
    }

def print_summary_table(experiment):
    """Print a formatted summary table"""
    print(f"\n{'='*80}")
    print("MATRIX RESULTS SUMMARY")
    print(f"{'='*80}\n")
    
    print(f"Max Tokens: {experiment['max_tokens']}")
    print(f"Context Chunks: {experiment['context_chunks']}\n")
    
    # Header
    print(f"{'Model':<12} {'Time (ms)':<12} {'Total Tokens':<15} {'Chars':<10} {'Cost':<10}")
    print("-" * 70)
    
    # Results
    for result in experiment['results']:
        if 'error' not in result:
            usage = result.get('usage', {})
            total_tokens = usage.get('total_tokens', 'N/A')
            
            # Try to get cost if available
            cost = usage.get('cost', 'N/A')
            if isinstance(cost, float):
                cost = f"${cost:.4f}"
            
            print(f"{result['model']:<12} {result['response_time_ms']:<12} "
                  f"{total_tokens!s:<15} {result['answer_length']:<10} {cost:<10}")
        else:
            print(f"{result['model']:<12} ERROR: {result['error']}")

def main():
    # Get API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    pinecone_url = os.getenv("PINECONE_HOST_URL") or os.getenv("PINECONE_INDEX_HOST")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if not all([openai_key, pinecone_key, pinecone_url, openrouter_key]):
        print("❌ Missing API keys. Need: OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_HOST_URL, OPENROUTER_API_KEY")
        return
    
    # Get question from questions.txt or command line
    question = None
    
    # Try to read from questions.txt
    if os.path.exists("questions.txt"):
        with open("questions.txt", 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    question = line
                    break
    
    # Override with command line if provided
    if len(sys.argv) > 1:
        question = sys.argv[1]
    
    if not question:
        question = "What improvements can be made to the tofu-aicl framework?"
    
    print("="*80)
    print("RAG 3x1 MATRIX TEST (1500 tokens)")
    print("="*80)
    print(f"Models: {', '.join(MODELS.keys())}")
    print(f"Max tokens: {MAX_TOKENS}")
    print(f"Total tests: {len(MODELS)}")
    
    # Run experiment
    run_id = hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    
    experiment = run_experiment(question, openai_key, pinecone_key, pinecone_url, openrouter_key)
    experiment["run_id"] = run_id
    experiment["timestamp"] = datetime.now().isoformat()
    
    # Print summary
    print_summary_table(experiment)
    
    # Save results
    output_file = f"experiments/rag_matrix_3x1_{run_id}.json"
    with open(output_file, 'w') as f:
        json.dump(experiment, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
    
    # Find best performing
    valid_results = [r for r in experiment['results'] if 'error' not in r]
    if valid_results:
        fastest = min(valid_results, key=lambda x: x['response_time_ms'])
        most_detailed = max(valid_results, key=lambda x: x['answer_length'])
        
        print(f"\n🏆 Fastest: {fastest['model']} ({fastest['response_time_ms']}ms)")
        print(f"📝 Most detailed: {most_detailed['model']} ({most_detailed['answer_length']} chars)")

if __name__ == "__main__":
    main()
