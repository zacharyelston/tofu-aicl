#!/usr/bin/env python3
"""Run 3x3 RAG matrix: 3 models x 3 token sizes"""
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

TOKEN_SIZES = {
    "small": 300,
    "medium": 500,
    "large": 800
}

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

def ask_llm(context, question, model, openrouter_key, max_tokens=500):
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
    """Run one complete experiment with all model/token combinations"""
    
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
    
    # Run matrix
    matrix_results = []
    
    for model_name, model_id in MODELS.items():
        for size_name, max_tokens in TOKEN_SIZES.items():
            config = f"{model_name}_{size_name}"
            print(f"🤖 Testing {config} (max_tokens={max_tokens})...", end=" ", flush=True)
            
            try:
                result = ask_llm(context, question, model_id, openrouter_key, max_tokens)
                
                matrix_results.append({
                    "model": model_name,
                    "model_id": model_id,
                    "token_size": size_name,
                    "max_tokens": max_tokens,
                    "config": config,
                    "answer": result["answer"],
                    "answer_length": len(result["answer"]),
                    "usage": result["usage"],
                    "response_time_ms": result["response_time_ms"]
                })
                
                print(f"✅ {result['response_time_ms']}ms, {len(result['answer'])} chars")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                matrix_results.append({
                    "model": model_name,
                    "model_id": model_id,
                    "token_size": size_name,
                    "max_tokens": max_tokens,
                    "config": config,
                    "error": str(e)
                })
    
    return {
        "question": question,
        "context_chunks": len(results.get('matches', [])),
        "results": matrix_results
    }

def print_summary_table(experiment):
    """Print a formatted summary table"""
    print(f"\n{'='*80}")
    print("MATRIX RESULTS SUMMARY")
    print(f"{'='*80}\n")
    
    # Header
    print(f"{'Model':<12} {'Size':<8} {'Time (ms)':<12} {'Tokens':<12} {'Chars':<8}")
    print("-" * 60)
    
    # Results by model and size
    for model_name in MODELS.keys():
        for size_name in TOKEN_SIZES.keys():
            result = next(
                (r for r in experiment['results'] 
                 if r['model'] == model_name and r['token_size'] == size_name),
                None
            )
            
            if result and 'error' not in result:
                usage = result.get('usage', {})
                total_tokens = usage.get('total_tokens', 'N/A')
                
                print(f"{model_name:<12} {size_name:<8} {result['response_time_ms']:<12} "
                      f"{total_tokens!s:<12} {result['answer_length']:<8}")
            else:
                error = result.get('error', 'Unknown') if result else 'Missing'
                print(f"{model_name:<12} {size_name:<8} ERROR: {error}")

def main():
    # Get API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    pinecone_url = os.getenv("PINECONE_HOST_URL") or os.getenv("PINECONE_INDEX_HOST")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if not all([openai_key, pinecone_key, pinecone_url, openrouter_key]):
        print("❌ Missing API keys. Need: OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_HOST_URL, OPENROUTER_API_KEY")
        return
    
    # Default question
    question = "How does the HCL evaluator resolve interpolations?"
    
    if len(sys.argv) > 1:
        question = sys.argv[1]
    
    print("="*80)
    print("RAG 3x3 MATRIX TEST")
    print("="*80)
    print(f"Models: {', '.join(MODELS.keys())}")
    print(f"Token sizes: {', '.join(f'{k}({v})' for k, v in TOKEN_SIZES.items())}")
    print(f"Total tests: {len(MODELS) * len(TOKEN_SIZES)}")
    
    # Run experiment
    run_id = hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    
    experiment = run_experiment(question, openai_key, pinecone_key, pinecone_url, openrouter_key)
    experiment["run_id"] = run_id
    experiment["timestamp"] = datetime.now().isoformat()
    
    # Print summary
    print_summary_table(experiment)
    
    # Save results
    output_file = f"experiments/rag_matrix_3x3_{run_id}.json"
    with open(output_file, 'w') as f:
        json.dump(experiment, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
    
    # Find best performing configuration
    valid_results = [r for r in experiment['results'] if 'error' not in r]
    if valid_results:
        fastest = min(valid_results, key=lambda x: x['response_time_ms'])
        most_detailed = max(valid_results, key=lambda x: x['answer_length'])
        
        print(f"\n🏆 Fastest: {fastest['config']} ({fastest['response_time_ms']}ms)")
        print(f"📝 Most detailed: {most_detailed['config']} ({most_detailed['answer_length']} chars)")

if __name__ == "__main__":
    main()
