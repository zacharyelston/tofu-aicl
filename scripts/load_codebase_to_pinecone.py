#!/usr/bin/env python3
"""Load codebase files into Pinecone for RAG"""
import os
import requests
from pathlib import Path

def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks

def get_embedding(text, api_key):
    """Get OpenAI embedding for text"""
    response = requests.post(
        "https://api.openai.com/v1/embeddings",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "text-embedding-3-small",
            "input": text,
            "dimensions": 1024  # Match Pinecone index dimension
        }
    )
    response.raise_for_status()
    return response.json()['data'][0]['embedding']

def upsert_to_pinecone(vectors, pinecone_key, pinecone_url, namespace="tofu-aicl-codebase"):
    """Upload vectors to Pinecone"""
    response = requests.post(
        f"{pinecone_url}/vectors/upsert",
        headers={
            "Api-Key": pinecone_key,
            "Content-Type": "application/json"
        },
        json={
            "vectors": vectors,
            "namespace": namespace
        }
    )
    response.raise_for_status()
    return response.json()

def main():
    # Get API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    pinecone_url = os.getenv("PINECONE_HOST_URL")
    
    if not all([openai_key, pinecone_key, pinecone_url]):
        print("ERROR: Missing API keys. Set OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_HOST_URL")
        return
    
    # Files to index
    files_to_index = [
        "src/aicl/parser.py",
        "src/aicl/evaluator.py",
        "src/aicl/executor.py",
        "src/aicl/planner.py",
        "replit.md",
        "README.md"
    ]
    
    vectors = []
    vector_id = 0
    
    for file_path in files_to_index:
        print(f"Processing {file_path}...")
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Chunk the file
            chunks = chunk_text(content, chunk_size=1000, overlap=200)
            
            # Get embeddings and prepare vectors
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 50:  # Skip tiny chunks
                    continue
                    
                embedding = get_embedding(chunk, openai_key)
                vectors.append({
                    "id": f"doc_{vector_id}",
                    "values": embedding,
                    "metadata": {
                        "file": file_path,
                        "chunk": i,
                        "text": chunk[:500]  # Store first 500 chars as preview
                    }
                })
                vector_id += 1
                print(f"  Chunk {i}: {len(chunk)} chars -> vector {vector_id-1}")
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Upload to Pinecone
    print(f"\nUploading {len(vectors)} vectors to Pinecone...")
    result = upsert_to_pinecone(vectors, pinecone_key, pinecone_url)
    print(f"Success! Upserted {result.get('upsertedCount', len(vectors))} vectors")
    print(f"Namespace: tofu-aicl-codebase")

if __name__ == "__main__":
    main()
