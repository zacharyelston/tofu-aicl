#!/usr/bin/env python3
"""
RAG Comparison Framework Demo

Demonstrates the complete RAG comparison workflow using State as DNA lineage tracking.
Shows how experiments are run, tracked, and analyzed with git context.
"""

import os
import sys
from pathlib import Path

# Add both the scripts directory and the project root to the path
scripts_dir = Path(__file__).parent / "scripts"
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(project_root))

# Import the experiment modules
try:
    import run_experiment
    import compare_results
    ExperimentRunner = run_experiment.ExperimentRunner
    ExperimentAnalyzer = compare_results.ExperimentAnalyzer
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"Scripts directory: {scripts_dir}")
    print(f"Project root: {project_root}")
    print("Available files in scripts directory:")
    if scripts_dir.exists():
        for file in scripts_dir.iterdir():
            print(f"  - {file.name}")
    sys.exit(1)


def demo_rag_comparison():
    """Run a complete RAG comparison demo."""
    
    print("🚀 RAG Provider Comparison Framework Demo")
    print("=" * 50)
    print()
    
    # Setup experiment directory
    experiment_dir = Path(__file__).parent
    print(f"📁 Experiment Directory: {experiment_dir}")
    print()
    
    # Initialize runner and analyzer
    runner = ExperimentRunner(experiment_dir)
    analyzer = ExperimentAnalyzer(experiment_dir)
    
    print(f"🔬 Git Context:")
    print(f"   SHA: {runner.git_sha}")
    print(f"   Branch: {runner.git_branch}")
    print()
    
    # Run Phase 1: Basic 3-provider comparison
    print("🧪 Running Phase 1: Basic Provider Comparison")
    print("-" * 40)
    
    phase1_providers = ["openai", "azure"]  # Reduced for demo
    phase1_context = ["medium"]
    
    try:
        phase1_results = runner.run_phase(1, phase1_providers, phase1_context)
        
        print(f"✅ Phase 1 Complete!")
        print(f"   Experiments run: {len(phase1_results)}")
        print(f"   Successful: {len([r for r in phase1_results if r['status'] == 'success'])}")
        print()
        
        # Analyze Phase 1 results
        print("📊 Analyzing Phase 1 Results")
        print("-" * 30)
        
        analysis = analyzer.run_analysis(phase=1, git_sha=runner.git_sha)
        
        if analysis:
            print("✅ Analysis complete!")
            
            # Show key findings
            provider_comparison = analysis.get('provider_comparison', {})
            if provider_comparison:
                print("\n🏆 Provider Performance:")
                for provider, stats in provider_comparison.items():
                    print(f"   {provider.title()}:")
                    print(f"     Overall Score: {stats['avg_overall_score']:.3f}")
                    print(f"     Avg Cost: ${stats['avg_cost_per_experiment']:.4f}")
                    print(f"     Avg Latency: {stats['avg_latency_ms']:.1f}ms")
            
            # Show recommendations
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                print(f"\n💡 Key Recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"   {i}. {rec}")
        
        print()
        
        # Run Phase 2: Context size comparison (smaller demo)
        print("🧪 Running Phase 2 Demo: Context Size Impact")
        print("-" * 45)
        
        phase2_providers = ["openai"]  # Single provider for demo
        phase2_contexts = ["small", "medium"]  # Reduced for demo
        
        phase2_results = runner.run_phase(2, phase2_providers, phase2_contexts)
        
        print(f"✅ Phase 2 Demo Complete!")
        print(f"   Experiments run: {len(phase2_results)}")
        print()
        
        # Final analysis across all phases
        print("📈 Final Cross-Phase Analysis")
        print("-" * 30)
        
        final_analysis = analyzer.run_analysis(git_sha=runner.git_sha)
        
        if final_analysis:
            lineage_stats = final_analysis.get('lineage_analysis', {})
            print(f"📊 Complete Experiment Summary:")
            print(f"   Total Experiments: {lineage_stats.get('total_experiments', 0)}")
            print(f"   Total Actions Tracked: {lineage_stats.get('total_actions_across_all', 0)}")
            print(f"   Total Cost: ${lineage_stats.get('total_cost_across_all', 0):.4f}")
            print(f"   Total Duration: {lineage_stats.get('total_duration_across_all', 0)}ms")
            
            # Show git SHA distribution
            git_distribution = lineage_stats.get('git_sha_distribution', {})
            print(f"\n🔗 Git Context Tracking:")
            for sha, count in git_distribution.items():
                print(f"   {sha}: {count} experiments")
        
        print()
        print("🎉 Demo Complete!")
        print()
        print("📋 What was demonstrated:")
        print("   ✅ State as DNA lineage tracking for each experiment")
        print("   ✅ Git SHA integration for reproducible research")
        print("   ✅ Multi-provider RAG performance comparison")
        print("   ✅ Context size impact analysis")
        print("   ✅ Comprehensive cost and performance tracking")
        print("   ✅ Automated report generation (JSON + HTML)")
        print("   ✅ Cross-experiment analysis and recommendations")
        print()
        print("📁 Check the following directories:")
        print(f"   States: {experiment_dir / 'states'}")
        print(f"   Results: {experiment_dir / 'results'}")
        print(f"   Data: {experiment_dir / 'data'}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_rag_comparison()
