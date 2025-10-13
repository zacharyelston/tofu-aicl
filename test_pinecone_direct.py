#!/usr/bin/env python3
"""
Direct test of Pinecone upload to verify connection and format
"""

import os
import requests
import json

# Get credentials from environment
api_key = os.getenv("PINECONE_API_KEY")
host_url = os.getenv("PINECONE_HOST_URL")

print(f"Testing Pinecone connection...")
print(f"Host: {host_url}")
print(f"API Key: {'*' * 20}{api_key[-10:] if api_key else 'NOT SET'}")
print()

# Create a test vector
test_vector = {
    "id": "test-direct-upload-001",
    "values": [0.1] * 1024,  # 1024 dimensions (matching your index)
    "metadata": {
        "content": "This is a direct test upload to verify Pinecone connectivity",
        "source": "test_pinecone_direct.py",
        "test": True
    }
}

# Prepare upsert payload
payload = {
    "vectors": [test_vector],
    "namespace": "rag-demo-live"
}

print("Uploading test vector to Pinecone...")
print(f"Vector ID: {test_vector['id']}")
print(f"Namespace: rag-demo-live")
print(f"Dimensions: {len(test_vector['values'])}")
print()

try:
    response = requests.post(
        f"{host_url}/vectors/upsert",
        headers={
            "Api-Key": api_key,
            "Content-Type": "application/json"
        },
        json=payload
    )
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCESS! Upserted {result.get('upsertedCount', 0)} vector(s)")
        print(f"Total vectors in index should now be: 42 (41 + 1)")
    else:
        print(f"\n❌ FAILED with status {response.status_code}")
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
