"""
Modular RAG Provider Comparison Experiment Runner

Refactored to use smaller, focused modules for better maintainability.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from aicl.state.manager import StateManager
from aicl.state.models import Diagnostic

from modules import (
    GitContext,
    TestDataPreparer,
    ProviderConfig,
    RAGOperations,
    ExperimentEvaluator
)


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
        
        # Initialize components
        self.git_context = GitContext()
        self.repo_root = Path(__file__).parent.parent.parent.parent
        self.test_data_preparer = TestDataPreparer(self.data_dir, self.repo_root)
        self.rag_operations = RAGOperations(self.git_context.sha)
        self.evaluator = ExperimentEvaluator(self.git_context.sha)
        self.config = ProviderConfig()
        
        print(f"🔧 Initialized ExperimentRunner")
        print(f"   Git Context: {self.git_context}")
        print(f"   Experiment Dir: {self.experiment_dir}")
    
    def run_single_experiment(self, provider: str, context_size: str, 
                            test_data: Dict[str, Any], phase: int) -> Dict[str, Any]:
        """Run a single RAG experiment for a specific provider and context size."""
        
        # Validate inputs
        if not self.config.validate_provider(provider):
            raise ValueError(f"Unsupported provider: {provider}")
        if not self.config.validate_context_size(context_size):
            raise ValueError(f"Unsupported context size: {context_size}")
        
        experiment_id = self.git_context.create_experiment_id(provider, context_size, phase)
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
            # Phase 1: Generate embeddings
            print("   📊 Phase 1: Generating embeddings...")
            embedding_result = self.rag_operations.generate_embeddings(
                manager, provider, test_data, context_size
            )
            
            # Phase 2: Create vector index
            print("   🗂️  Phase 2: Creating vector index...")
            index_result = self.rag_operations.create_vector_index(
                manager, provider, embedding_result, context_size
            )
            
            # Phase 3: Run test queries
            print("   ❓ Phase 3: Running test queries...")
            query_results = self.rag_operations.run_test_queries(
                manager, provider, index_result, context_size
            )
            
            # Phase 4: Evaluate results
            print("   📈 Phase 4: Evaluating results...")
            evaluation = self.evaluator.evaluate_results(
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
                    "git_sha": self.git_context.sha,
                    "test_files": test_data["total_files"]
                },
                result={
                    "status": "success",
                    "embedding_count": embedding_result.get("count", 0),
                    "query_count": len(query_results),
                    "evaluation_score": evaluation.get("overall_score", 0.0)
                },
                duration_ms=experiment_duration,
                cost_usd=evaluation.get("metrics", {}).get("total_cost", 0.0)
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
    
    def run_phase(self, phase: int, providers: List[str], context_sizes: List[str]) -> List[Dict[str, Any]]:
        """Run a complete experiment phase."""
        print(f"🚀 Starting Phase {phase} RAG Comparison")
        print(f"   Providers: {', '.join(providers)}")
        print(f"   Context Sizes: {', '.join(context_sizes)}")
        print(f"   Git Context: {self.git_context}")
        print()
        
        # Validate all inputs
        for provider in providers:
            if not self.config.validate_provider(provider):
                raise ValueError(f"Unsupported provider: {provider}")
        
        for context_size in context_sizes:
            if not self.config.validate_context_size(context_size):
                raise ValueError(f"Unsupported context size: {context_size}")
        
        # Prepare test data once
        test_data = self.test_data_preparer.prepare_test_data()
        
        results = []
        total_experiments = len(providers) * len(context_sizes)
        experiment_count = 0
        
        for provider in providers:
            for context_size in context_sizes:
                experiment_count += 1
                print(f"[{experiment_count}/{total_experiments}] {provider} × {context_size}")
                
                result = self.run_single_experiment(provider, context_size, test_data, phase)
                results.append(result)
                
                print(f"   Status: {result['status']}")
                if result['status'] == 'success':
                    print(f"   Score: {result['results']['overall_score']:.3f}")
                    print(f"   Cost: ${result['results']['metrics']['total_cost']:.4f}")
                print()
        
        # Save phase summary
        phase_summary = {
            "phase": phase,
            **self.git_context.to_dict(),
            "timestamp": datetime.utcnow().isoformat(),
            "providers": providers,
            "context_sizes": context_sizes,
            "total_experiments": total_experiments,
            "results": results
        }
        
        summary_file = self.results_dir / f"phase{phase}_summary_{self.git_context.sha}.json"
        with open(summary_file, 'w') as f:
            json.dump(phase_summary, f, indent=2)
        
        print(f"📊 Phase {phase} Complete!")
        print(f"   Summary saved: {summary_file}")
        
        return results
    
    def get_supported_providers(self) -> List[str]:
        """Get list of supported providers."""
        return self.config.get_supported_providers()
    
    def get_supported_context_sizes(self) -> List[str]:
        """Get list of supported context sizes."""
        return self.config.get_supported_context_sizes()
    
    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """Get provider information."""
        return self.config.get_provider_info(provider)
