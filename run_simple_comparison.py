#!/usr/bin/env python3
import json
import subprocess
import sys

result = subprocess.run(["python", "run.py", "experiments/provider-comparison-simple.aicl"], 
                       capture_output=True, text=True)

if result.returncode != 0:
    print(f"❌ Failed: {result.stderr}")
    sys.exit(1)

with open("terraform.tfstate.d/default-exp.tfstate") as f:
    state = json.load(f)

resources = state["resources"]

print("\n" + "="*80)
print("🏆 MODEL COMPARISON: GPT-4o vs GPT-4o-mini vs GPT-4o-creative")
print("="*80)

for name, label in [("gpt4o", "GPT-4o (temp=0.7)"), 
                     ("gpt4o_mini", "GPT-4o-mini (temp=0.7)"),
                     ("gpt4o_creative", "GPT-4o (temp=1.2, creative)")]:
    res = resources.get(f"openai_chat-{name}", {}).get("attributes", {})
    print(f"\n📝 {label}:")
    print("-" * 80)
    print(res.get("content", "N/A"))
    usage = res.get("usage", {})
    tokens = usage.get("total_tokens", 0)
    # GPT-4o: $2.50/$10 per 1M tokens, GPT-4o-mini: $0.15/$0.60 per 1M
    cost = tokens * (0.0000025 if "mini" not in name else 0.00000015)
    print(f"\nTokens: {tokens} | Est. Cost: ${cost:.6f}")

judge = resources.get("openai_chat-judge", {}).get("attributes", {}).get("content", "")
print("\n" + "="*80)
print("⚖️  EXPERT JUDGMENT")
print("="*80)

try:
    judgment = json.loads(judge.replace("```json", "").replace("```", "").strip())
    print(f"\n🏆 Winner: {judgment.get('winner', 'N/A')}")
    print(f"Reasoning: {judgment.get('reasoning', 'N/A')}")
    print(f"\n💰 Best Value: {judgment.get('best_for_cost', 'N/A')}")
    
    print("\n📊 Rankings:")
    for r in judgment.get("rankings", []):
        print(f"  {r['response']}. {r['model']}: {r['score']}/100")
except:
    print(judge)

print("\n" + "="*80)
