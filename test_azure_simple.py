#!/usr/bin/env python3
"""
Simple Azure OpenAI embedding test

Tests Azure OpenAI API directly without gRPC providers.
"""

import os
import requests


def test_azure_embeddings():
    """Test Azure OpenAI embeddings via REST API"""
    
    print("=" * 70)
    print("Azure OpenAI Simple Test")
    print("=" * 70)
    
    # Check environment variables
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-01')
    deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'text-embedding-ada-002')
    
    if not api_key or not endpoint:
        print("\n❌ Missing Azure credentials!")
        print(f"   AZURE_OPENAI_API_KEY: {'✓' if api_key else '✗'}")
        print(f"   AZURE_OPENAI_ENDPOINT: {'✓' if endpoint else '✗'}")
        return False
    
    print(f"\n✅ Azure credentials configured")
    print(f"   Endpoint: {endpoint}")
    print(f"   API Version: {api_version}")
    print(f"   Deployment: {deployment}")
    
    # Build URL
    url = f"{endpoint}/openai/deployments/{deployment}/embeddings?api-version={api_version}"
    
    # Test embeddings
    print(f"\n📊 Testing embeddings...")
    
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'input': 'Hello, Azure OpenAI! This is a test embedding.'
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            embedding = data['data'][0]['embedding']
            
            print(f"✅ Embedding generated successfully!")
            print(f"   Dimensions: {len(embedding)}")
            print(f"   First 5 values: {embedding[:5]}")
            print(f"   Model: {data.get('model', 'N/A')}")
            print(f"   Tokens used: {data.get('usage', {}).get('total_tokens', 'N/A')}")
            
            return True
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_azure_embeddings()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ Azure OpenAI is working correctly!")
        print("=" * 70)
        exit(0)
    else:
        print("\n" + "=" * 70)
        print("❌ Azure OpenAI test failed")
        print("=" * 70)
        exit(1)
