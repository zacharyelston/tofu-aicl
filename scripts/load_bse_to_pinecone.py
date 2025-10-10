#!/usr/bin/env python3
"""Load BSE PDF library into Pinecone for RAG"""
import os
import sys
import requests
import json
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
            "dimensions": 1024
        }
    )
    response.raise_for_status()
    return response.json()['data'][0]['embedding']

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using PyMuPDF (fitz)"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except ImportError:
        print("ERROR: PyMuPDF not installed. Install with: pip install PyMuPDF")
        sys.exit(1)
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def upsert_to_pinecone(vectors, pinecone_key, pinecone_url, namespace="bse-library"):
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
    pinecone_url = "  "
    
    if not all([openai_key, pinecone_key]):
        print("ERROR: Missing API keys. Set OPENAI_API_KEY and PINECONE_API_KEY")
        return
    
    # BSE directory
    bse_dir = Path.home() / "code" / "BSE"
    
    if not bse_dir.exists():
        print(f"ERROR: BSE directory not found at {bse_dir}")
        return
    
    # Find all PDF files
    pdf_files = list(bse_dir.rglob("*.pdf"))
    print(f"📚 Found {len(pdf_files)} PDF files in {bse_dir}")
    print(f"🎯 Target: {pinecone_url}")
    print(f"📦 Namespace: bse-library\n")
    
    # Chunking settings
    chunk_size = 1000
    overlap = 200
    min_chunk_size = 100
    
    vectors = []
    vector_id = 0
    
    for pdf_path in pdf_files:
        relative_path = pdf_path.relative_to(bse_dir)
        category = relative_path.parts[0] if len(relative_path.parts) > 1 else "general"
        
        print(f"Processing [{category}] {pdf_path.name}...")
        
        try:
            # Extract text from PDF
            text = extract_text_from_pdf(str(pdf_path))
            
            if not text or len(text.strip()) < min_chunk_size:
                print(f"  ⚠️  Skipped: No extractable text")
                continue
            
            # Chunk the text
            chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
            print(f"  📄 Extracted {len(text)} chars -> {len(chunks)} chunks")
            
            # Get embeddings and prepare vectors
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < min_chunk_size:
                    continue
                
                try:
                    embedding = get_embedding(chunk, openai_key)
                    vectors.append({
                        "id": f"bse_{vector_id}",
                        "values": embedding,
                        "metadata": {
                            "file": str(relative_path),
                            "filename": pdf_path.name,
                            "category": category,
                            "chunk": i,
                            "text": chunk[:500]  # Store first 500 chars
                        }
                    })
                    vector_id += 1
                    
                    if vector_id % 10 == 0:
                        print(f"  ✅ {vector_id} vectors created...")
                        
                except Exception as e:
                    print(f"  ⚠️  Error embedding chunk {i}: {e}")
                    continue
        
        except Exception as e:
            print(f"  ❌ Error processing {pdf_path.name}: {e}")
            continue
    
    if not vectors:
        print("\n❌ No vectors created. Exiting.")
        return
    
    # Upload to Pinecone in batches
    batch_size = 100
    total_uploaded = 0
    
    print(f"\n📤 Uploading {len(vectors)} vectors to Pinecone in batches of {batch_size}...")
    
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        try:
            result = upsert_to_pinecone(batch, pinecone_key, pinecone_url)
            uploaded = result.get('upsertedCount', len(batch))
            total_uploaded += uploaded
            print(f"  ✅ Batch {i//batch_size + 1}: {uploaded} vectors uploaded")
        except Exception as e:
            print(f"  ❌ Batch {i//batch_size + 1} failed: {e}")
    
    print(f"\n✨ Complete! Uploaded {total_uploaded}/{len(vectors)} vectors")
    print(f"📊 Namespace: bse-library")
    print(f"🔍 Ready for RAG queries!")

if __name__ == "__main__":
    main()
