#!/usr/bin/env python3
"""
Test OpenRouter API connectivity and verify real API calls
"""

import os
import requests
import json

def test_openrouter_api():
    """Test if OpenRouter API key works and make a real call."""
    
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        return False
    
    print(f"🔑 API Key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Test API call
    payload = {
        "model": "anthropic/claude-3.5-sonnet",
        "messages": [
            {
                "role": "user",
                "content": "Test message to verify OpenRouter API connectivity. Please respond with 'API_TEST_SUCCESS' if you receive this."
            }
        ],
        "max_tokens": 50
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/zacelston/tofu-aicl",
        "X-Title": "AICL RAG Test"
    }
    
    print("🧪 Testing OpenRouter API call...")
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            message = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            
            print("✅ API call successful!")
            print(f"📝 Response: {message}")
            print(f"💰 Cost: ${usage.get('total_cost', 'unknown')}")
            print(f"🔢 Tokens: {usage.get('total_tokens', 'unknown')}")
            
            return True
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during API call: {e}")
        return False

def check_openrouter_dashboard():
    """Instructions for checking OpenRouter dashboard."""
    print("\n" + "="*50)
    print("🔍 TO VERIFY REAL API ACTIVITY:")
    print("="*50)
    print("1. Go to: https://openrouter.ai/activity")
    print("2. Check for recent API calls")
    print("3. Look for 'AICL RAG Test' or similar requests")
    print("4. Verify timestamp matches this test")
    print("="*50)

if __name__ == "__main__":
    print("🔬 OpenRouter API Connectivity Test")
    print("="*40)
    
    success = test_openrouter_api()
    
    if success:
        print("\n✅ CONFIRMED: Real OpenRouter API call made!")
        print("💡 This proves the infrastructure can make real API calls")
    else:
        print("\n❌ FAILED: No real API call made")
        print("💡 This explains why you don't see activity on OpenRouter")
    
    check_openrouter_dashboard()
