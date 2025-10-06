#!/usr/bin/env python3
"""
Direct RAG Analysis of AICL Codebase using OpenRouter
Demonstrates the concept of using RAG to analyze and improve code
"""

import os
import requests
import json
from pathlib import Path
from typing import List, Dict, Any

def load_codebase_files(base_path: str, pattern: str = "**/*.py") -> List[Dict[str, str]]:
    """Load relevant codebase files."""
    files = []
    base = Path(base_path)
    
    # Load key framework files
    key_files = [
        "experiments/rag-comparison/scripts/aicl_orchestrator.py",
        "experiments/rag-comparison/scripts/modules/providers.py", 
        "experiments/rag-comparison/scripts/modules/rag_operations.py",
        "src/aicl/core/engine.py",
        "src/aicl/state/manager.py"
    ]
    
    for file_path in key_files:
        full_path = base / file_path
        if full_path.exists():
            with open(full_path, 'r') as f:
                content = f.read()
                files.append({
                    "path": file_path,
                    "content": content[:3000]  # Limit content for API
                })
                print(f"📄 Loaded: {file_path} ({len(content)} chars)")
    
    return files

def analyze_with_openrouter(files: List[Dict[str, str]], api_key: str) -> Dict[str, Any]:
    """Use OpenRouter to analyze the codebase."""
    
    # Prepare context from files
    context = "\n\n".join([
        f"=== {file['path']} ===\n{file['content']}" 
        for file in files
    ])
    
    query = """
    Analyze this AICL RAG comparison framework code. I need to:
    
    1. Replace simulation code with real AICL pipeline orchestration
    2. Create proper 2x2 matrix comparisons across OpenAI, Azure, OpenRouter
    3. Track real costs and performance metrics
    4. Use AICL's built-in State as DNA lineage tracking
    
    Key questions:
    - What architectural improvements are needed?
    - How should I structure real API comparisons?
    - What are the critical metrics to track?
    - How can I leverage AICL's container-based provider system?
    
    Provide specific, actionable recommendations.
    """
    
    payload = {
        "model": "anthropic/claude-3.5-sonnet",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert software architect analyzing AI infrastructure code. Provide specific, actionable recommendations for improving RAG comparison frameworks."
            },
            {
                "role": "user", 
                "content": f"Context:\n{context}\n\nQuery:\n{query}"
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.3
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("🤖 Analyzing codebase with Claude 3.5 Sonnet...")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        return {
            "analysis": result["choices"][0]["message"]["content"],
            "cost": result.get("usage", {}).get("total_cost", "unknown"),
            "tokens": result.get("usage", {}).get("total_tokens", "unknown")
        }
    else:
        return {
            "error": f"API call failed: {response.status_code}",
            "details": response.text
        }

def main():
    """Main analysis function."""
    print("🔬 RAG Analysis of AICL Codebase")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        return
    
    # Load codebase files
    print("\n📚 Loading codebase files...")
    files = load_codebase_files("/Users/zacelston/code/tofu-aicl")
    print(f"✅ Loaded {len(files)} files")
    
    # Analyze with OpenRouter
    print("\n🧠 Analyzing with OpenRouter...")
    result = analyze_with_openrouter(files, api_key)
    
    if "error" in result:
        print(f"❌ Analysis failed: {result['error']}")
        print(f"Details: {result['details']}")
        return
    
    # Display results
    print("\n" + "=" * 50)
    print("🎯 ANALYSIS RESULTS")
    print("=" * 50)
    print(f"💰 Cost: ${result['cost']}")
    print(f"🔢 Tokens: {result['tokens']}")
    print("\n📋 Recommendations:")
    print("-" * 30)
    print(result["analysis"])
    
    # Save results
    output_file = "/Users/zacelston/code/tofu-aicl/codebase_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("\n✅ RAG analysis complete!")

if __name__ == "__main__":
    main()
