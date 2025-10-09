#!/usr/bin/env python3
"""Test RAG with a real codebase question"""
import os
import requests
import time
import json

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

def ask_llm(context, question, model, openrouter_key):
    """Ask LLM with RAG context"""
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
                {"role": "system", "content": "You are a helpful assistant that answers questions about the tofu-aicl codebase based on provided context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}\n\nProvide a clear, technical answer based on the context above."}
            ],
            "temperature": 0.3,
            "max_tokens": 500,
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

def main():
    # API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    pinecone_url = os.getenv("PINECONE_HOST_URL")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    question = "How does the HCL evaluator resolve interpolations in the tofu-aicl framework?"
    
    print(f"🔍 Question: {question}\n")
    
    # Step 1: Get question embedding
    print("Step 1: Creating question embedding...")
    query_vector = get_embedding(question, openai_key)
    print(f"✅ Embedding created ({len(query_vector)} dimensions)\n")
    
    # Step 2: Query Pinecone
    print("Step 2: Searching Pinecone for relevant code...")
    results = query_pinecone(query_vector, pinecone_key, pinecone_url, top_k=3)
    matches = results.get('matches', [])
    print(f"✅ Found {len(matches)} relevant chunks\n")
    
    # Build context
    context_parts = []
    for i, match in enumerate(matches):
        meta = match.get('metadata', {})
        context_parts.append(f"[{i+1}] From {meta.get('file', 'unknown')}:\n{meta.get('text', '')}")
    
    context = "\n\n".join(context_parts)
    
    # Step 3: Ask both models
    print("Step 3: Querying models with RAG context...\n")
    
    models = [
        ("anthropic/claude-3.5-sonnet", "Claude 3.5 Sonnet"),
        ("openai/gpt-4", "GPT-4")
    ]
    
    results_data = []
    for model, name in models:
        print(f"🤖 {name}...")
        result = ask_llm(context, question, model, openrouter_key)
        results_data.append((name, result))
        print(f"   ✅ Response: {len(result['answer'])} chars, {result['response_time_ms']}ms\n")
    
    # Display results
    print("="*80)
    print("📊 RAG TEST RESULTS")
    print("="*80)
    
    for name, result in results_data:
        print(f"\n{name}:")
        print(f"  Time: {result['response_time_ms']}ms")
        print(f"  Tokens: {result['usage'].get('total_tokens', 'N/A')}")
        print(f"  Answer: {result['answer'][:200]}...")
    
    # Save results
    output_file = "experiments/rag_test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'question': question,
            'context_chunks': len(matches),
            'results': [{'model': name, **result} for name, result in results_data]
        }, f, indent=2)
    print(f"\n💾 Results saved to {output_file}")

if __name__ == "__main__":
    main()
