#!/usr/bin/env python3
"""
RAG Provider Comparison Experiment Runner

Modular version using focused components for better maintainability.
Uses State as DNA lineage tracking to create reproducible, comparable
experiments across multiple LLM providers with full audit trails.
"""

import argparse
import sys
from pathlib import Path

# Import the modular experiment runner
from experiment_runner import ExperimentRunner


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run RAG provider comparison experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Phase 1 with default providers
  python3 run-experiment.py --phase 1
  
  # Run Phase 2 with specific providers and context sizes
  python3 run-experiment.py --phase 2 --providers openai,azure --context-sizes small,medium
  
  # Run Phase 3 with all supported options
  python3 run-experiment.py --phase 3 --providers openai,azure,openrouter --context-sizes tiny,small,medium,large
        """
    )
    
    parser.add_argument("--phase", type=int, choices=[1, 2, 3],
                       help="Experiment phase to run")
    parser.add_argument("--providers", type=str, 
                       default="openai,azure,openrouter",
                       help="Comma-separated list of providers")
    parser.add_argument("--context-sizes", type=str,
                       default="small,medium,large", 
                       help="Comma-separated list of context sizes")
    parser.add_argument("--experiment-dir", type=str,
                       default="experiments/rag-comparison",
                       help="Experiment directory path")
    parser.add_argument("--list-providers", action="store_true",
                       help="List supported providers and exit")
    parser.add_argument("--list-context-sizes", action="store_true",
                       help="List supported context sizes and exit")
    
    args = parser.parse_args()
    
    # Create experiment runner for info commands
    experiment_dir = Path(args.experiment_dir)
    runner = ExperimentRunner(experiment_dir)
    
    # Handle info commands
    if args.list_providers:
        print("Supported providers:")
        for provider in runner.get_supported_providers():
            info = runner.get_provider_info(provider)
            print(f"  {provider}: {info['models']['embedding']} (embedding), {info['models']['chat']} (chat)")
        return
    
    if args.list_context_sizes:
        print("Supported context sizes:")
        for size in runner.get_supported_context_sizes():
            from modules import ProviderConfig
            desc = ProviderConfig.get_context_description(size)
            print(f"  {size}: {desc}")
        return
    
    # Check if phase is required
    if not args.phase and not args.list_providers and not args.list_context_sizes:
        parser.error("--phase is required unless using --list-providers or --list-context-sizes")
    
    # Parse lists
    providers = [p.strip() for p in args.providers.split(",")]
    context_sizes = [c.strip() for c in args.context_sizes.split(",")]
    
    # Validate inputs
    try:
        # Run experiment phase
        results = runner.run_phase(args.phase, providers, context_sizes)
        
        # Print summary
        successful = [r for r in results if r["status"] == "success"]
        failed = [r for r in results if r["status"] == "failed"]
        
        print("=" * 50)
        print(f"✅ Successful experiments: {len(successful)}")
        print(f"❌ Failed experiments: {len(failed)}")
        
        if successful:
            avg_score = sum(r["results"]["overall_score"] for r in successful) / len(successful)
            total_cost = sum(r["results"]["metrics"]["total_cost"] for r in successful)
            print(f"📊 Average score: {avg_score:.3f}")
            print(f"💰 Total cost: ${total_cost:.4f}")
            
        if failed:
            print("\nFailed experiments:")
            for result in failed:
                print(f"  {result['experiment_id']}: {result.get('error', 'Unknown error')}")
                
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Use --list-providers or --list-context-sizes to see supported options")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
