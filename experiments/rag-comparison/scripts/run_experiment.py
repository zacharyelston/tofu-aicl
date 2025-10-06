#!/usr/bin/env python3
"""
RAG Provider Comparison Experiment Runner

Uses State as DNA lineage tracking to create reproducible, comparable
experiments across multiple LLM providers with full audit trails.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from aicl.state.manager import StateManager
from aicl.state.models import Diagnostic


class ExperimentRunner:
    """Runs RAG comparison experiments with complete lineage tracking."""
    
    def __init__(self, experiment_dir: Path):
        self.experiment_dir = experiment_dir
        self.states_dir = experiment_dir / "states"
        self.data_dir = experiment_dir / "data"
        self.results_dir = experiment_dir / "results"
        
        # Ensure directories exist
        for dir_path in [self.states_dir, self.data_dir, self.results_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Get git context
        self.git_sha = self._get_git_sha()
        self.git_branch = self._get_git_branch()
        
    def _get_git_sha(self) -> str:
        """Get current git commit SHA (short form)."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"
    
    def _get_git_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"
    
    def _create_experiment_id(self, provider: str, context_size: str, phase: int) -> str:
        """Create descriptive experiment ID with git context."""
        return f"phase{phase}_{provider}_{context_size}_{self.git_sha}"
    
    def _prepare_test_data(self) -> Dict[str, Any]:
        """Prepare source code test data with git snapshot."""
        print("📁 Preparing test data from tofu-aicl source code...")
        
        # Create source snapshot
        snapshot_dir = self.data_dir / "source-snapshots" / self.git_sha
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy relevant source files
        source_files = []
        repo_root = Path(__file__).parent.parent.parent.parent
        
        # Collect documentation files
        docs_dir = repo_root / "docs"
        if docs_dir.exists():
            for doc_file in docs_dir.rglob("*.md"):
                if doc_file.is_file():
                    source_files.append(str(doc_file.relative_to(repo_root)))
        
        # Collect source code files
        src_dir = repo_root / "src"
        if src_dir.exists():
            for src_file in src_dir.rglob("*.py"):
                if src_file.is_file() and "__pycache__" not in str(src_file):
                    source_files.append(str(src_file.relative_to(repo_root)))
        
        # Collect API documentation
        api_docs_dir = repo_root / "APIDocs"
        if api_docs_dir.exists():
            for api_file in api_docs_dir.rglob("*.md"):
                if api_file.is_file():
                    source_files.append(str(api_file.relative_to(repo_root)))
        
        test_data = {
            "git_sha": self.git_sha,
            "git_branch": self.git_branch,
            "timestamp": datetime.utcnow().isoformat(),
            "source_files": source_files,
            "total_files": len(source_files),
            "snapshot_dir": str(snapshot_dir)
        }
        
        # Save test data manifest
        manifest_file = snapshot_dir / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        print(f"   ✅ Prepared {len(source_files)} source files")
        print(f"   📸 Snapshot saved to: {snapshot_dir}")
        
        return test_data
    
    def _run_rag_experiment(self, 
                           provider: str, 
                           context_size: str, 
                           test_data: Dict[str, Any],
                           experiment_id: str) -> Dict[str, Any]:
        """Run RAG experiment for a specific provider and context size."""
        
        print(f"🧪 Running RAG experiment: {experiment_id}")
        
        # Create state manager for this experiment
        manager = StateManager(
            state_dir=str(self.states_dir),
            enable_lineage=True
        )
        
        # Load experiment state
        state = manager.load(experiment_id)
        
        # Add experiment metadata
        manager.add_diagnostic(Diagnostic(
            severity="info",
            message=f"Starting RAG experiment: {provider} with {context_size} context",
            source="ExperimentRunner"
        ))
        
        # Start experiment timer
        experiment_start = time.time()
        manager.start_action()
        
        try:
            # Phase 1: Prepare embeddings
            print("   📊 Phase 1: Generating embeddings...")
            embedding_result = self._generate_embeddings(
                manager, provider, test_data, context_size
            )
            
            # Phase 2: Create vector index
            print("   🗂️  Phase 2: Creating vector index...")
            index_result = self._create_vector_index(
                manager, provider, embedding_result, context_size
            )
            
            # Phase 3: Run test queries
            print("   ❓ Phase 3: Running test queries...")
            query_results = self._run_test_queries(
                manager, provider, index_result, context_size
            )
            
            # Phase 4: Evaluate results
            print("   📈 Phase 4: Evaluating results...")
            evaluation = self._evaluate_results(
                manager, provider, query_results, context_size
            )
            
            experiment_duration = int((time.time() - experiment_start) * 1000)
            
            # Record overall experiment completion
            manager.record_execution(
                pipeline="rag_comparison",
                step="complete_experiment",
                input_data={
                    "provider": provider,
                    "context_size": context_size,
                    "git_sha": self.git_sha,
                    "test_files": test_data["total_files"]
                },
                result={
                    "status": "success",
                    "embedding_count": embedding_result.get("count", 0),
                    "query_count": len(query_results),
                    "evaluation_score": evaluation.get("overall_score", 0.0)
                },
                duration_ms=experiment_duration,
                cost_usd=evaluation.get("total_cost", 0.0)
            )
            
            # Save state
            state_file = manager.save()
            print(f"   💾 State saved: {state_file}")
            
            return {
                "experiment_id": experiment_id,
                "provider": provider,
                "context_size": context_size,
                "status": "success",
                "duration_ms": experiment_duration,
                "results": evaluation,
                "state_file": str(state_file)
            }
            
        except Exception as e:
            # Record failure
            manager.add_diagnostic(Diagnostic(
                severity="error",
                message=f"Experiment failed: {str(e)}",
                source="ExperimentRunner"
            ))
            
            experiment_duration = int((time.time() - experiment_start) * 1000)
            
            manager.record_execution(
                pipeline="rag_comparison",
                step="experiment_failed",
                input_data={
                    "provider": provider,
                    "context_size": context_size,
                    "error": str(e)
                },
                result={"status": "failed"},
                duration_ms=experiment_duration
            )
            
            manager.save()
            
            return {
                "experiment_id": experiment_id,
                "provider": provider,
                "context_size": context_size,
                "status": "failed",
                "error": str(e),
                "duration_ms": experiment_duration
            }
    
    def _generate_embeddings(self, manager: StateManager, provider: str, 
                           test_data: Dict[str, Any], context_size: str) -> Dict[str, Any]:
        """Generate embeddings for test data."""
        manager.start_action()
        
        # Simulate embedding generation (replace with actual implementation)
        embedding_count = min(test_data["total_files"], self._get_context_limit(context_size))
        cost_per_embedding = self._get_provider_cost(provider, "embedding")
        
        time.sleep(0.1)  # Simulate processing time
        
        result = {
            "count": embedding_count,
            "provider": provider,
            "model": self._get_embedding_model(provider),
            "dimensions": 1536,
            "cost_usd": embedding_count * cost_per_embedding
        }
        
        manager.record_provision(
            resource_type="embeddings",
            resource_name=f"{provider}_embeddings",
            provider=provider,
            input_data={
                "files": test_data["total_files"],
                "context_size": context_size,
                "model": result["model"]
            },
            result=result,
            cost_usd=result["cost_usd"],
            pipeline="rag_comparison",
            step="generate_embeddings"
        )
        
        return result
    
    def _create_vector_index(self, manager: StateManager, provider: str,
                           embedding_result: Dict[str, Any], context_size: str) -> Dict[str, Any]:
        """Create vector index from embeddings."""
        manager.start_action()
        
        time.sleep(0.05)  # Simulate index creation
        
        result = {
            "index_id": f"{provider}_index_{self.git_sha}",
            "embedding_count": embedding_result["count"],
            "dimensions": embedding_result["dimensions"],
            "provider": provider
        }
        
        manager.record_provision(
            resource_type="vector_index",
            resource_name=f"{provider}_index",
            provider=provider,
            input_data={
                "embeddings": embedding_result["count"],
                "dimensions": embedding_result["dimensions"]
            },
            result=result,
            pipeline="rag_comparison",
            step="create_index"
        )
        
        return result
    
    def _run_test_queries(self, manager: StateManager, provider: str,
                         index_result: Dict[str, Any], context_size: str) -> List[Dict[str, Any]]:
        """Run test queries against the RAG system."""
        test_queries = [
            "How does tofu-aicl handle state management?",
            "What providers are supported for AI operations?",
            "How do you configure API keys for different services?",
            "What is the State as DNA model?",
            "How does lineage tracking work?"
        ]
        
        query_results = []
        
        for i, query in enumerate(test_queries):
            manager.start_action()
            
            # Simulate query processing
            time.sleep(0.02)  # Simulate query time
            
            query_cost = self._get_provider_cost(provider, "query")
            
            result = {
                "query": query,
                "response_length": len(query) * 10,  # Simulated response
                "relevance_score": 0.8 + (i * 0.02),  # Simulated scoring
                "latency_ms": 200 + (i * 50),
                "cost_usd": query_cost
            }
            
            manager.record_execution(
                pipeline="rag_comparison",
                step=f"query_{i+1}",
                input_data={
                    "query": query,
                    "index_id": index_result["index_id"],
                    "context_size": context_size
                },
                result=result,
                cost_usd=result["cost_usd"],
                provider=provider
            )
            
            query_results.append(result)
        
        return query_results
    
    def _evaluate_results(self, manager: StateManager, provider: str,
                         query_results: List[Dict[str, Any]], context_size: str) -> Dict[str, Any]:
        """Evaluate and score the experiment results."""
        manager.start_action()
        
        # Calculate metrics
        avg_relevance = sum(r["relevance_score"] for r in query_results) / len(query_results)
        avg_latency = sum(r["latency_ms"] for r in query_results) / len(query_results)
        total_cost = sum(r["cost_usd"] for r in query_results)
        
        # Calculate overall score (weighted combination)
        overall_score = (avg_relevance * 0.6) + ((1000 - avg_latency) / 1000 * 0.3) + ((1 - total_cost) * 0.1)
        
        evaluation = {
            "provider": provider,
            "context_size": context_size,
            "query_count": len(query_results),
            "avg_relevance_score": round(avg_relevance, 3),
            "avg_latency_ms": round(avg_latency, 1),
            "total_cost": round(total_cost, 4),
            "overall_score": round(overall_score, 3),
            "git_sha": self.git_sha,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        manager.record_execution(
            pipeline="rag_comparison",
            step="evaluate_results",
            input_data={
                "query_count": len(query_results),
                "provider": provider
            },
            result=evaluation,
            provider=provider
        )
        
        return evaluation
    
    def _get_context_limit(self, context_size: str) -> int:
        """Get file limit based on context size."""
        limits = {
            "small": 10,
            "medium": 25,
            "large": 50
        }
        return limits.get(context_size, 25)
    
    def _get_provider_cost(self, provider: str, operation: str) -> float:
        """Get cost per operation for provider."""
        costs = {
            "openai": {"embedding": 0.0001, "query": 0.002},
            "azure": {"embedding": 0.0001, "query": 0.002},
            "openrouter": {"embedding": 0.00005, "query": 0.001}
        }
        return costs.get(provider, {}).get(operation, 0.001)
    
    def _get_embedding_model(self, provider: str) -> str:
        """Get embedding model for provider."""
        models = {
            "openai": "text-embedding-ada-002",
            "azure": "text-embedding-ada-002",
            "openrouter": "text-embedding-ada-002"
        }
        return models.get(provider, "unknown")
    
    def run_phase(self, phase: int, providers: List[str], context_sizes: List[str]) -> List[Dict[str, Any]]:
        """Run a complete experiment phase."""
        print(f"🚀 Starting Phase {phase} RAG Comparison")
        print(f"   Providers: {', '.join(providers)}")
        print(f"   Context Sizes: {', '.join(context_sizes)}")
        print(f"   Git SHA: {self.git_sha}")
        print(f"   Git Branch: {self.git_branch}")
        print()
        
        # Prepare test data once
        test_data = self._prepare_test_data()
        
        results = []
        total_experiments = len(providers) * len(context_sizes)
        experiment_count = 0
        
        for provider in providers:
            for context_size in context_sizes:
                experiment_count += 1
                print(f"[{experiment_count}/{total_experiments}] {provider} × {context_size}")
                
                experiment_id = self._create_experiment_id(provider, context_size, phase)
                result = self._run_rag_experiment(provider, context_size, test_data, experiment_id)
                results.append(result)
                
                print(f"   Status: {result['status']}")
                if result['status'] == 'success':
                    print(f"   Score: {result['results']['overall_score']:.3f}")
                    print(f"   Cost: ${result['results']['total_cost']:.4f}")
                print()
        
        # Save phase summary
        phase_summary = {
            "phase": phase,
            "git_sha": self.git_sha,
            "git_branch": self.git_branch,
            "timestamp": datetime.utcnow().isoformat(),
            "providers": providers,
            "context_sizes": context_sizes,
            "total_experiments": total_experiments,
            "results": results
        }
        
        summary_file = self.results_dir / f"phase{phase}_summary_{self.git_sha}.json"
        with open(summary_file, 'w') as f:
            json.dump(phase_summary, f, indent=2)
        
        print(f"📊 Phase {phase} Complete!")
        print(f"   Summary saved: {summary_file}")
        
        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run RAG provider comparison experiments")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], required=True,
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
    
    args = parser.parse_args()
    
    # Parse lists
    providers = [p.strip() for p in args.providers.split(",")]
    context_sizes = [c.strip() for c in args.context_sizes.split(",")]
    
    # Create experiment runner
    experiment_dir = Path(args.experiment_dir)
    runner = ExperimentRunner(experiment_dir)
    
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
        total_cost = sum(r["results"]["total_cost"] for r in successful)
        print(f"📊 Average score: {avg_score:.3f}")
        print(f"💰 Total cost: ${total_cost:.4f}")


if __name__ == "__main__":
    main()
