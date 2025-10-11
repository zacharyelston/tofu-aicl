#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Test Naga embedding API directly
api_key = os.getenv('NAGA_API_KEY')

print("🧪 Testing Naga.ai Embedding API directly...\n")

# Test 1: Text Embedding 3 Small
print("1️⃣  Testing text-embedding-3-small...")
response = requests.post(
    "https://api.naga.ac/v1/embeddings",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "text-embedding-3-small",
        "input": "What is the role of the Evaluator?"
    }
)

if response.status_code == 200:
    result = response.json()
    embedding = result['data'][0]['embedding']
    print(f"   ✅ Success! Vector dim: {len(embedding)}")
else:
    print(f"   ❌ Failed: {response.status_code} - {response.text}")

# Test 2: Text Embedding 3 Large
print("\n2️⃣  Testing text-embedding-3-large...")
response = requests.post(
    "https://api.naga.ac/v1/embeddings",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "text-embedding-3-large",
        "input": "What is the role of the Evaluator?"
    }
)

if response.status_code == 200:
    result = response.json()
    embedding = result['data'][0]['embedding']
    print(f"   ✅ Success! Vector dim: {len(embedding)}")
else:
    print(f"   ❌ Failed: {response.status_code} - {response.text}")

# Test 3: Ada 002
print("\n3️⃣  Testing text-embedding-ada-002...")
response = requests.post(
    "https://api.naga.ac/v1/embeddings",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "text-embedding-ada-002",
        "input": "What is the role of the Evaluator?"
    }
)

if response.status_code == 200:
    result = response.json()
    embedding = result['data'][0]['embedding']
    print(f"   ✅ Success! Vector dim: {len(embedding)}")
else:
    print(f"   ❌ Failed: {response.status_code} - {response.text}")

# Test 4: Gemini Embedding
print("\n4️⃣  Testing gemini-embedding-001...")
response = requests.post(
    "https://api.naga.ac/v1/embeddings",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "gemini-embedding-001",
        "input": "What is the role of the Evaluator?"
    }
)

if response.status_code == 200:
    result = response.json()
    embedding = result['data'][0]['embedding']
    print(f"   ✅ Success! Vector dim: {len(embedding)}")
else:
    print(f"   ❌ Failed: {response.status_code} - {response.text}")

print("\n✅ Naga API embedding test complete")
