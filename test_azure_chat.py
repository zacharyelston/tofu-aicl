#!/usr/bin/env python3
"""
Test Azure OpenAI chat completion

Tests Azure chat completion via REST API.
"""

import os
import requests
import sys


def test_azure_chat():
    """Test Azure OpenAI chat completion via REST API"""
    
    print("=" * 70)
    print("Azure OpenAI Chat Completion Test")
    print("=" * 70)
    
    # Check environment variables
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2023-05-15')
    
    # Ask for chat deployment name
    chat_deployment = os.getenv('AZURE_CHAT_DEPLOYMENT') or input("\n📝 Enter your Azure chat model deployment name (e.g., gpt-4, gpt-4o, gpt-35-turbo): ").strip()
    
    if not chat_deployment:
        print("❌ No chat deployment name provided")
        return False
    
    if not api_key or not endpoint:
        print("\n❌ Missing Azure credentials!")
        return False
    
    print(f"\n✅ Azure credentials configured")
    print(f"   Endpoint: {endpoint}")
    print(f"   API Version: {api_version}")
    print(f"   Chat Deployment: {chat_deployment}")
    
    # Build URL
    url = f"{endpoint}/openai/deployments/{chat_deployment}/chat/completions?api-version={api_version}"
    
    # Test chat completion
    print(f"\n💬 Testing chat completion...")
    
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'messages': [
            {'role': 'user', 'content': 'Say "Hello from Azure OpenAI!" and nothing else.'}
        ],
        'max_tokens': 20
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            message = data['choices'][0]['message']
            usage = data.get('usage', {})
            
            print(f"✅ Chat completion successful!")
            print(f"\n   Response: {message['content']}")
            print(f"   Model: {data.get('model', 'N/A')}")
            print(f"   Tokens - Prompt: {usage.get('prompt_tokens', 'N/A')}, Completion: {usage.get('completion_tokens', 'N/A')}, Total: {usage.get('total_tokens', 'N/A')}")
            print(f"   Finish reason: {data['choices'][0].get('finish_reason', 'N/A')}")
            
            return True
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            error_msg = error_data.get('error', {}).get('message', response.text)
            print(f"❌ API Error {response.status_code}: {error_msg}")
            
            if response.status_code == 404:
                print(f"\n💡 Tip: The deployment '{chat_deployment}' was not found.")
                print(f"   Check your Azure OpenAI Studio for the correct deployment name.")
            
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_azure_chat()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ Azure OpenAI chat completion is working!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("❌ Azure OpenAI chat test failed")
        print("=" * 70)
        sys.exit(1)
