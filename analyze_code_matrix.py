#!/usr/bin/env python3
import json
from pathlib import Path

# Analyze successful experiments
for exp_id in ['claude_executor', 'gpt4_executor']:
    state_file = f'experiments/code-matrix-results/{exp_id}.tfstate'
    try:
        with open(state_file) as f:
            state = json.load(f)
        
        for res_id, res_data in state.get('resources', {}).items():
            if res_data.get('type') == 'chat':
                attrs = res_data.get('attributes', {})
                print(f'\n🧪 {exp_id.upper()}')
                print(f'Model: {attrs.get("model")}')
                print(f'\n📊 Metrics:')
                print(f'  Tokens: {attrs.get("usage", {}).get("total_tokens", 0)}')
                print(f'  Time: {attrs.get("performance", {}).get("response_time_ms", 0)}ms')
                print(f'  Cost: ${attrs.get("cost", {}).get("estimated_usd", 0):.6f}')
                print(f'  Speed: {attrs.get("performance", {}).get("tokens_per_second", 0)} tok/sec')
                print(f'\nResponse Preview ({len(attrs.get("response", ""))} chars):')
                print(f'{attrs.get("response", "")[:400]}...')
                break
    except Exception as e:
        print(f'Error loading {exp_id}: {e}')
