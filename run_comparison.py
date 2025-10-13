#!/usr/bin/env python3
"""
Multi-Provider Comparison Experiment Runner
Displays side-by-side comparison and judging results
"""

import json
import subprocess
import sys

def run_comparison(aicl_file="experiments/provider-comparison.aicl"):
    """Run multi-provider comparison and display results."""
    
    print(f"\n{'='*80}")
    print("🏆 MULTI-PROVIDER COMPARISON EXPERIMENT")
    print(f"{'='*80}\n")
    
    # Run the experiment
    print("Running experiment across OpenAI, Naga, and Claude...\n")
    result = subprocess.run(
        ["python", "run.py", aicl_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Experiment failed:\n{result.stderr}")
        return False
    
    # Read state file
    try:
        with open("terraform.tfstate.d/default-exp.tfstate", "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        print("❌ No state file found")
        return False
    
    resources = state.get("resources", {})
    
    # Extract responses
    openai_res = resources.get("openai_chat-test_openai", {}).get("attributes", {})
    naga_res = resources.get("naga_chat-test_naga", {}).get("attributes", {})
    claude_res = resources.get("openrouter_chat-test_claude", {}).get("attributes", {})
    judge_res = resources.get("openai_chat-judge_comparison", {}).get("attributes", {})
    
    openai_content = openai_res.get("content", "N/A")
    naga_content = naga_res.get("content", "N/A")
    claude_content = claude_res.get("content", "N/A")
    judge_content = judge_res.get("content", "N/A")
    
    # Display responses
    print("="*80)
    print("📊 PROVIDER RESPONSES")
    print("="*80)
    
    print("\n🔵 RESPONSE A: OpenAI GPT-4o-mini (Direct)")
    print("-" * 80)
    print(openai_content)
    if "usage" in openai_res:
        usage = openai_res["usage"]
        print(f"\nTokens: {usage.get('total_tokens', 'N/A')} | Cost: ~${usage.get('total_tokens', 0) * 0.00000015:.6f}")
    
    print("\n🟢 RESPONSE B: Naga GPT-4o-mini (Cost-Optimized)")
    print("-" * 80)
    print(naga_content)
    if "usage" in naga_res:
        usage = naga_res["usage"]
        print(f"\nTokens: {usage.get('total_tokens', 'N/A')} | Cost: ~${usage.get('total_tokens', 0) * 0.00000010:.6f}")
    
    print("\n🟣 RESPONSE C: Claude 3 Haiku (Different Architecture)")
    print("-" * 80)
    print(claude_content)
    if "usage" in claude_res:
        usage = claude_res.get("usage", {})
        tokens = usage.get("total_tokens", 0)
        print(f"\nTokens: {tokens} | Cost: ~${tokens * 0.00000025:.6f}")
    
    # Display judgment
    print("\n" + "="*80)
    print("⚖️  EXPERT JUDGMENT")
    print("="*80)
    
    # Try to parse JSON judgment
    try:
        # Remove markdown code fences if present
        judge_clean = judge_content.replace("```json", "").replace("```", "").strip()
        judgment = json.loads(judge_clean)
        
        print(f"\n🏆 WINNER: {judgment.get('winner', 'N/A')}")
        print(f"\nReasoning: {judgment.get('reasoning', 'N/A')}")
        
        print("\n📈 RANKINGS:")
        for rank in judgment.get('rankings', []):
            print(f"  {rank.get('rank', '?')}. {rank.get('provider', 'N/A')}: {rank.get('score', 'N/A')}/100")
        
        print("\n💰 COST ANALYSIS:")
        cost_analysis = judgment.get('cost_analysis', {})
        for key, value in cost_analysis.items():
            print(f"  {key}: {value}")
        
        print("\n📝 DETAILED ANALYSIS:")
        analysis = judgment.get('analysis', {})
        for resp_key, resp_data in analysis.items():
            print(f"\n  {resp_key.upper()}:")
            print(f"    Score: {resp_data.get('score', 'N/A')}/100")
            print(f"    Strengths: {', '.join(resp_data.get('strengths', []))}")
            print(f"    Weaknesses: {', '.join(resp_data.get('weaknesses', []))}")
            
    except json.JSONDecodeError:
        print("\n(Raw judgment - couldn't parse JSON)")
        print(judge_content)
    
    print("\n" + "="*80)
    print("✅ COMPARISON COMPLETE")
    print("="*80)
    
    return True

if __name__ == "__main__":
    aicl_file = sys.argv[1] if len(sys.argv) > 1 else "experiments/provider-comparison.aicl"
    run_comparison(aicl_file)
