#!/usr/bin/env python3
"""
Minimal AICL Runner - Simple wrapper for running experiments
"""
import sys
import json
import subprocess
from pathlib import Path

def print_banner(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_result(state_file):
    """Pretty print experiment results"""
    try:
        with open(state_file) as f:
            state = json.load(f)
        
        resources = state.get('resources', {})
        
        print_banner("EXPERIMENT RESULTS")
        
        for rid, rstate in resources.items():
            attrs = rstate.get('attributes', {})
            
            # Skip if no meaningful output
            if not attrs or rid.endswith('-generate_provider'):
                continue
            
            print(f"\n📊 {rid}")
            print("-" * 70)
            
            # Show content
            if 'content' in attrs:
                content = attrs['content']
                if len(content) > 500:
                    print(content[:500] + f"\n... (truncated, {len(content)} chars total)")
                else:
                    print(content)
            
            # Show usage if available
            if 'usage' in attrs:
                usage = attrs['usage']
                total = usage.get('total_tokens', 0)
                print(f"\n💰 Tokens: {total}")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"Error reading results: {e}")

def main():
    if len(sys.argv) < 2:
        print("""
Usage: python run.py <experiment>

Available experiments:
  self-build    - AI generates its own provider code
  matrix-test   - Compare model variations (temperature, tokens)

Examples:
  python run.py self-build
  python run.py matrix-test
""")
        sys.exit(1)
    
    experiment = sys.argv[1]
    
    # Map short names to full paths
    experiments = {
        'self-build': 'experiments/self-build.aicl',
        'matrix-test': 'experiments/matrix-test.aicl',
    }
    
    if experiment not in experiments:
        print(f"❌ Unknown experiment: {experiment}")
        print(f"Available: {', '.join(experiments.keys())}")
        sys.exit(1)
    
    config_path = experiments[experiment]
    
    if not Path(config_path).exists():
        print(f"❌ Experiment file not found: {config_path}")
        sys.exit(1)
    
    print_banner(f"Running {experiment}")
    
    # Run the engine
    result = subprocess.run(
        ['python', 'engine.py', config_path],
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"\n❌ Experiment failed with exit code {result.returncode}")
        sys.exit(1)
    
    # Show results
    state_file = 'terraform.tfstate.d/default-minimal.tfstate'
    if Path(state_file).exists():
        print_result(state_file)
    
    print("✅ Experiment complete!\n")
    print(f"📁 Full state saved to: {state_file}")
    print(f"💡 View JSON: cat {state_file} | jq\n")

if __name__ == '__main__':
    main()
