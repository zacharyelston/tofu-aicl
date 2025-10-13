#!/usr/bin/env python3
"""
Simple self-building experiment runner that displays generated code.
"""

import json
import subprocess
import sys

def run_experiment(aicl_file):
    """Run AICL experiment and extract generated code from state."""
    
    print(f"\n{'='*70}")
    print(f"Running Self-Building Experiment: {aicl_file}")
    print(f"{'='*70}\n")
    
    # Run the experiment
    result = subprocess.run(
        ["python", "run.py", aicl_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Experiment failed with error:\n{result.stderr}")
        return False
    
    # Read state file
    try:
        with open("terraform.tfstate.d/default-exp.tfstate", "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        print("❌ No state file found")
        return False
    
    # Extract generated code from resources
    resources = state.get("resources", {})
    
    # Find the generated provider code
    provider_code = None
    config_code = None
    test_code = None
    quality_eval = None
    
    for key, resource in resources.items():
        if "generate_provider" in key:
            attrs = resource.get("attributes", {})
            provider_code = attrs.get("content") or attrs.get("response")
        elif "generate_config" in key:
            attrs = resource.get("attributes", {})
            config_code = attrs.get("content") or attrs.get("response")
        elif "generate_tests" in key:
            attrs = resource.get("attributes", {})
            test_code = attrs.get("content") or attrs.get("response")
        elif "judge_quality" in key:
            attrs = resource.get("attributes", {})
            quality_eval = attrs.get("content") or attrs.get("response")
    
    # Display results
    print("\n" + "="*70)
    print("GENERATED PROVIDER CODE (providers/echo/server.py)")
    print("="*70)
    print(provider_code or "❌ Not found")
    
    print("\n" + "="*70)
    print("GENERATED CONFIG (providers/echo/config.yaml)")
    print("="*70)
    print(config_code or "❌ Not found")
    
    print("\n" + "="*70)
    print("GENERATED TESTS (providers/echo/test_echo.py)")
    print("="*70)
    print(test_code or "❌ Not found")
    
    print("\n" + "="*70)
    print("QUALITY EVALUATION")
    print("="*70)
    print(quality_eval or "❌ Not found")
    
    print("\n" + "="*70)
    print("EXPERIMENT COMPLETE")
    print("="*70)
    
    return True

if __name__ == "__main__":
    aicl_file = sys.argv[1] if len(sys.argv) > 1 else "experiments/self-build/add-echo-provider-v2.aicl"
    run_experiment(aicl_file)
