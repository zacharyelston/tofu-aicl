#!/usr/bin/env python3
"""Load codebase into Pinecone for RAG"""
import os
import sys
import requests
import json
from pathlib import Path
import yaml

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

def discover_files_from_directory(directory):
    """Recursively find all files in directory"""
    files = []
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"❌ Directory not found: {directory}")
        return files
    
    # Find all files recursively
    for file_path in dir_path.rglob('*'):
        if file_path.is_file():
            # Skip common non-code files
            if file_path.suffix in ['.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib']:
                continue
            if file_path.name in ['.DS_Store', 'Thumbs.db']:
                continue
            if '__pycache__' in str(file_path):
                continue
            
            files.append(str(file_path))
    
    return sorted(files)

def load_files_from_list(list_file):
    """Load file paths from a text file (one per line)"""
    files = []
    with open(list_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                files.append(line)
    return files

def main():
    # Load config
    config = None
    if os.path.exists('rag-config.yaml'):
        print("📋 Loading configuration from rag-config.yaml")
        with open('rag-config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    
    # Get API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    pinecone_url = os.getenv("PINECONE_HOST_URL")
    
    if not all([openai_key, pinecone_key, pinecone_url]):
        print("ERROR: Missing API keys. Set OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_HOST_URL")
        return
    
    # Get chunking settings from config
    if config and 'chunking' in config:
        chunk_size = config['chunking'].get('chunk_size', 1000)
        overlap = config['chunking'].get('overlap', 200)
        min_chunk_size = config['chunking'].get('min_chunk_size', 50)
    else:
        chunk_size = 1000
        overlap = 200
        min_chunk_size = 50
    
    # Determine source of files to index
    # Priority: 1. rag-config.yaml, 2. RAG-files.txt, 3. rag-config/ directory, 4. Default list
    files_to_index = []
    source_method = "default"
    
    if config and config.get('files_to_index'):
        print("📋 Loading files from rag-config.yaml")
        files_to_index = config['files_to_index']
        source_method = "rag-config.yaml"
    elif os.path.exists("RAG-files.txt"):
        print("📋 Loading files from RAG-files.txt")
        files_to_index = load_files_from_list("RAG-files.txt")
        source_method = "RAG-files.txt"
    elif os.path.exists("rag-config"):
        print("📁 Scanning rag-config/ directory")
        files_to_index = discover_files_from_directory("rag-config")
        source_method = "rag-config/"
    else:
        print("📝 Using default file list")
        files_to_index = [
            "src/aicl/planner.py",
            "src/aicl/core/engine.py",
            "src/aicl/state/manager.py",
            "src/aicl/parser.py",
            "src/aicl/evaluator.py",
            "src/aicl/executor.py",
            "src/aicl/provider_registry.py"
        ]
        source_method = "default"
    
    print(f"📊 Found {len(files_to_index)} file(s) to index (source: {source_method})")
    print(f"⚙️  Chunking: {chunk_size} chars, {overlap} overlap, min {min_chunk_size}\n")
    
    vectors = []
    vector_id = 0
    
    for file_path in files_to_index:
        print(f"Processing {file_path}...")
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Chunk the file
            chunks = chunk_text(content, chunk_size=chunk_size, overlap=overlap)
            
            # Get embeddings and prepare vectors
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < min_chunk_size:  # Skip tiny chunks
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
