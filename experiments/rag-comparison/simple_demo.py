#!/usr/bin/env python3
"""
Simple RAG Comparison Framework Demo

Demonstrates the State as DNA lineage tracking for RAG experiments
without external dependencies.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from aicl.state.manager import StateManager
from aicl.state.models import State, LineageEntry, Diagnostic


def demo_state_as_dna_for_rag():
    """Demonstrate State as DNA for RAG experiments."""
    
    print("🧬 State as DNA for RAG Experiments Demo")
    print("=" * 50)
    print()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"📁 Using temporary directory: {tmpdir}")
        
        # Create state manager with lineage tracking
        manager = StateManager(state_dir=tmpdir, enable_lineage=True)
        
        # Simulate RAG experiment with git context
        experiment_id = "phase1_openai_medium_a1b2c3d4"
        state = manager.load(experiment_id)
        
        print(f"✅ Created experiment state: {type(state).__name__}")
        print(f"   Experiment ID: {state.experiment_id}")
        print(f"   Initial lineage entries: {len(state.lineage)}")
        print()
        
        # Simulate RAG experiment phases with lineage tracking
        print("🔬 Simulating RAG Experiment Phases...")
        print()
        
        # Phase 1: Prepare test data
        print("📊 Phase 1: Preparing test data...")
        manager.start_action()
        
        # Simulate data preparation
        import time
        time.sleep(0.1)
        
        manager.record_execution(
            pipeline="rag_comparison",
            step="prepare_test_data",
            input_data={
                "source_files": ["src/aicl/state/models.py", "docs/design/state-as-dna/"],
                "git_sha": "a1b2c3d4",
                "git_branch": "feature/972-phase1-lineage-tracking"
            },
            result={
                "files_processed": 25,
                "total_tokens": 15000,
                "snapshot_created": True
            },
            cost_usd=0.001
        )
        
        print(f"   ✅ Recorded data preparation (lineage entries: {len(state.lineage)})")
        
        # Phase 2: Generate embeddings
        print("🔗 Phase 2: Generating embeddings...")
        manager.start_action()
        time.sleep(0.05)
        
        manager.record_provision(
            resource_type="embeddings",
            resource_name="openai_embeddings",
            provider="openai",
            input_data={
                "model": "text-embedding-ada-002",
                "files": 25,
                "context_size": "medium"
            },
            result={
                "embedding_count": 25,
                "dimensions": 1536,
                "total_tokens": 15000
            },
            cost_usd=0.015,
            pipeline="rag_comparison",
            step="generate_embeddings"
        )
        
        print(f"   ✅ Recorded embedding generation (lineage entries: {len(state.lineage)})")
        
        # Phase 3: Create vector index
        print("🗂️  Phase 3: Creating vector index...")
        manager.start_action()
        time.sleep(0.02)
        
        manager.record_provision(
            resource_type="vector_index",
            resource_name="openai_index",
            provider="openai",
            input_data={
                "embeddings": 25,
                "index_type": "flat"
            },
            result={
                "index_id": "openai_index_a1b2c3d4",
                "status": "ready"
            },
            pipeline="rag_comparison",
            step="create_index"
        )
        
        print(f"   ✅ Recorded index creation (lineage entries: {len(state.lineage)})")
        
        # Phase 4: Run test queries
        print("❓ Phase 4: Running test queries...")
        
        test_queries = [
            "How does tofu-aicl handle state management?",
            "What is the State as DNA model?",
            "How does lineage tracking work?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            manager.start_action()
            time.sleep(0.01)
            
            manager.record_execution(
                pipeline="rag_comparison",
                step=f"query_{i}",
                input_data={
                    "query": query,
                    "index_id": "openai_index_a1b2c3d4",
                    "context_size": "medium"
                },
                result={
                    "response_length": len(query) * 8,
                    "relevance_score": 0.85 + (i * 0.02),
                    "latency_ms": 180 + (i * 20)
                },
                cost_usd=0.002,
                provider="openai"
            )
        
        print(f"   ✅ Recorded {len(test_queries)} queries (lineage entries: {len(state.lineage)})")
        
        # Phase 5: Evaluate results
        print("📈 Phase 5: Evaluating results...")
        manager.start_action()
        time.sleep(0.01)
        
        manager.record_execution(
            pipeline="rag_comparison",
            step="evaluate_results",
            input_data={
                "query_count": len(test_queries),
                "provider": "openai"
            },
            result={
                "avg_relevance_score": 0.89,
                "avg_latency_ms": 200,
                "total_cost": 0.023,
                "overall_score": 0.875
            },
            provider="openai"
        )
        
        print(f"   ✅ Recorded evaluation (lineage entries: {len(state.lineage)})")
        print()
        
        # Add some diagnostics
        manager.add_diagnostic(Diagnostic(
            severity="info",
            message="RAG experiment completed successfully",
            source="demo"
        ))
        
        manager.add_diagnostic(Diagnostic(
            severity="info", 
            message="All queries returned relevant results",
            source="evaluation"
        ))
        
        # Save state
        state_file = manager.save()
        print(f"💾 State saved to: {state_file}")
        print()
        
        # Generate summary
        summary = manager.get_lineage_summary()
        
        print("📊 Experiment Summary:")
        print(f"   Lineage Enabled: {summary['lineage_enabled']}")
        print(f"   Total Actions: {summary['total_actions']}")
        print(f"   Actions by Type: {summary['actions_by_type']}")
        print(f"   Total Duration: {summary['total_duration_ms']}ms")
        print(f"   Total Cost: ${summary['total_cost_usd']:.4f}")
        print(f"   Diagnostics: {summary['diagnostics_count']}")
        print()
        
        # Show lineage details
        print("🧬 Complete DNA Lineage:")
        for i, entry in enumerate(state.lineage, 1):
            print(f"   {i}. {entry.action.upper()}: {entry.step or 'N/A'}")
            print(f"      Provider: {entry.provider or 'N/A'}")
            print(f"      Duration: {entry.duration_ms}ms")
            if entry.cost_usd:
                print(f"      Cost: ${entry.cost_usd:.4f}")
            print(f"      Timestamp: {entry.timestamp}")
            print()
        
        print("🎉 Demo Complete!")
        print()
        print("✅ What was demonstrated:")
        print("   • State as DNA lineage tracking for RAG experiments")
        print("   • Complete audit trail of all experiment phases")
        print("   • Cost and performance tracking per operation")
        print("   • Git context integration (simulated)")
        print("   • Diagnostic message tracking")
        print("   • Comprehensive experiment summaries")
        print("   • Ready for multi-provider comparison framework")
        print()
        print("🚀 Next Steps:")
        print("   • Install PyYAML: pip install pyyaml")
        print("   • Run full demo: python3 demo.py")
        print("   • Execute real experiments: python3 scripts/run-experiment.py --phase 1")
        print("   • Analyze results: python3 scripts/compare-results.py --phase 1")


if __name__ == "__main__":
    demo_state_as_dna_for_rag()
