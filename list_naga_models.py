#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('NAGA_API_KEY')
if not api_key:
    print("Error: NAGA_API_KEY environment variable not set")
    exit(1)

print("🔍 Fetching available models from Naga.ai...\n")

try:
    response = requests.get(
        "https://api.naga.ac/v1/models",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )
    response.raise_for_status()
    data = response.json()
    
    models = data.get('data', [])
    
    print(f"✅ Found {len(models)} models available on Naga.ai:\n")
    print("="*80)
    
    # Group models by provider
    by_provider = {}
    for model in models:
        model_id = model.get('id', '')
        owned_by = model.get('owned_by', 'unknown')
        
        if owned_by not in by_provider:
            by_provider[owned_by] = []
        by_provider[owned_by].append(model_id)
    
    # Display grouped models
    for provider in sorted(by_provider.keys()):
        print(f"\n📦 {provider.upper()}")
        print("-" * 80)
        for model_id in sorted(by_provider[provider]):
            print(f"   • {model_id}")
    
    print("\n" + "="*80)
    print(f"\n💡 Total: {len(models)} models across {len(by_provider)} providers")
    print("\n📖 Usage in AICL:")
    print('   resource "naga_chat" "example" {')
    print('     model = "openai/gpt-4o-mini"  # Use any model ID from above')
    print('     ...')
    print('   }')
    
except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP Error: {e}")
    print(f"Response: {e.response.text if e.response else 'No response'}")
except Exception as e:
    print(f"❌ Error: {e}")
