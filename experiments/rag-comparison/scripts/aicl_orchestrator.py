#!/usr/bin/env python3
"""
AICL Pipeline Orchestrator for RAG Comparisons

Orchestrates real AICL pipeline executions across multiple providers
and context sizes, collecting actual performance and cost data.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from aicl.state.manager import StateManager
from modules.git_utils import GitContext


class AICLOrchestrator:
    """Orchestrates AICL pipeline executions for RAG comparisons."""
    
    def __init__(self, experiment_dir: Path):
        self.experiment_dir = experiment_dir
        self.templates_dir = experiment_dir / "templates"
        self.states_dir = experiment_dir / "states"
        self.results_dir = experiment_dir / "results"
        self.git_context = GitContext()
        
        # Ensure directories exist
        self.states_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        
        # Context size configurations
        self.context_sizes = {
            "tiny": {"chunk_limit": 5, "description": "5 chunks for quick testing"},
            "small": {"chunk_limit": 20, "description": "20 chunks for basic comparison"},
            "medium": {"chunk_limit": 50, "description": "50 chunks for standard testing"},
            "large": {"chunk_limit": 100, "description": "100 chunks for comprehensive testing"}
        }
        
        # Provider configurations
        self.providers = {
            "openai": {
                "template": "openai_rag.aicl",
                "description": "OpenAI text-embedding-3-small"
            },
            "azure": {
                "template": "azure_rag.aicl", 
                "description": "Azure OpenAI text-embedding-ada-002"
            },
            "openrouter": {
                "template": "openrouter_rag.aicl",
                "description": "OpenRouter text-embedding-3-small"
            }
        }
    
    def run_experiment(self, provider: str, context_size: str, phase: int = 1) -> Dict[str, Any]:
        """Run a single AICL experiment."""
        print(f"🧪 Running {provider} × {context_size} experiment (Phase {phase})")
        
        # Get git context
        git_sha = self.git_context.sha
        
        # Create experiment ID
        experiment_id = f"phase{phase}_{provider}_{context_size}_{git_sha}"
        
        # Get template path
        template_path = self.templates_dir / self.providers[provider]["template"]
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        # Create temporary experiment file with variables
        with tempfile.NamedTemporaryFile(mode='w', suffix='.aicl', delete=False) as temp_file:
            # Read template
            with open(template_path) as f:
                template_content = f.read()
            
            # Write template with experiment-specific variables
            temp_file.write(template_content)
            temp_file_path = temp_file.name
        
        try:
            # Set environment variables for the experiment
            env = os.environ.copy()
            env.update({
                'AICL_EXPERIMENT_ID': experiment_id,
                'AICL_CONTEXT_SIZE': context_size,
                'AICL_PROVIDER': provider,
                'AICL_PHASE': str(phase)
            })
            
            # Run AICL pipeline
            print(f"   📊 Executing AICL pipeline...")
            start_time = datetime.now()
            
            result = subprocess.run([
                sys.executable, 
                str(Path(__file__).parent.parent.parent.parent / "run.py"),
                temp_file_path
            ], 
            capture_output=True, 
            text=True, 
            env=env,
            cwd=str(Path(__file__).parent.parent.parent.parent)
            )
            
            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            if result.returncode != 0:
                print(f"   ❌ AICL execution failed:")
                print(f"   STDOUT: {result.stdout}")
                print(f"   STDERR: {result.stderr}")
                return {
                    "experiment_id": experiment_id,
                    "status": "failed",
                    "error": result.stderr,
                    "duration_ms": duration_ms
                }
            
            print(f"   ✅ AICL execution completed ({duration_ms}ms)")
            
            # Parse AICL output for results
            experiment_data = self._parse_aicl_output(result.stdout, result.stderr)
            experiment_data.update({
                "experiment_id": experiment_id,
                "provider": provider,
                "context_size": context_size,
                "phase": phase,
                "git_sha": git_sha,
                "status": "success",
                "duration_ms": duration_ms,
                "executed_at": start_time.isoformat()
            })
            
            # Save experiment results
            result_file = self.results_dir / f"{experiment_id}.json"
            with open(result_file, 'w') as f:
                json.dump(experiment_data, f, indent=2)
            
            print(f"   💾 Results saved: {result_file}")
            return experiment_data
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    def _parse_aicl_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse AICL execution output to extract metrics."""
        data = {
            "stdout": stdout,
            "stderr": stderr,
            "embedding_count": 0,
            "total_cost": 0.0,
            "model_used": "unknown"
        }
        
        # Look for output values in stdout
        lines = stdout.split('\n')
        for line in lines:
            if 'embedding_count' in line and '=' in line:
                try:
                    data["embedding_count"] = int(line.split('=')[1].strip())
                except:
                    pass
            elif 'total_cost' in line and '=' in line:
                try:
                    data["total_cost"] = float(line.split('=')[1].strip())
                except:
                    pass
            elif 'model_used' in line and '=' in line:
                try:
                    data["model_used"] = line.split('=')[1].strip().strip('"')
                except:
                    pass
        
        return data
    
    def run_matrix_experiment(self, providers: List[str], context_sizes: List[str], phase: int = 2) -> List[Dict[str, Any]]:
        """Run matrix experiment across multiple providers and context sizes."""
        print(f"🔬 Starting Phase {phase} Matrix Experiment")
        print(f"   Providers: {', '.join(providers)}")
        print(f"   Context Sizes: {', '.join(context_sizes)}")
        print(f"   Total Experiments: {len(providers) * len(context_sizes)}")
        print()
        
        results = []
        total_experiments = len(providers) * len(context_sizes)
        current_experiment = 0
        
        for provider in providers:
            for context_size in context_sizes:
                current_experiment += 1
                print(f"[{current_experiment}/{total_experiments}] {provider} × {context_size}")
                
                try:
                    result = self.run_experiment(provider, context_size, phase)
                    results.append(result)
                    
                    if result["status"] == "success":
                        print(f"   Status: success")
                        print(f"   Cost: ${result.get('total_cost', 0):.4f}")
                        print(f"   Embeddings: {result.get('embedding_count', 0)}")
                    else:
                        print(f"   Status: failed - {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"   ❌ Experiment failed: {e}")
                    results.append({
                        "experiment_id": f"phase{phase}_{provider}_{context_size}_failed",
                        "provider": provider,
                        "context_size": context_size,
                        "phase": phase,
                        "status": "error",
                        "error": str(e)
                    })
                
                print()
        
        # Save matrix results summary
        summary = {
            "phase": phase,
            "providers": providers,
            "context_sizes": context_sizes,
            "total_experiments": total_experiments,
            "successful_experiments": len([r for r in results if r.get("status") == "success"]),
            "failed_experiments": len([r for r in results if r.get("status") != "success"]),
            "total_cost": sum(r.get("total_cost", 0) for r in results),
            "results": results,
            "executed_at": datetime.now().isoformat()
        }
        
        summary_file = self.results_dir / f"phase{phase}_matrix_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("=" * 50)
        print(f"📊 Phase {phase} Matrix Experiment Complete!")
        print(f"   ✅ Successful: {summary['successful_experiments']}")
        print(f"   ❌ Failed: {summary['failed_experiments']}")
        print(f"   💰 Total Cost: ${summary['total_cost']:.4f}")
        print(f"   📄 Summary: {summary_file}")
        
        return results
    
    def list_providers(self) -> None:
        """List available providers."""
        print("Available Providers:")
        for provider, config in self.providers.items():
            print(f"  {provider}: {config['description']}")
    
    def list_context_sizes(self) -> None:
        """List available context sizes."""
        print("Available Context Sizes:")
        for size, config in self.context_sizes.items():
            print(f"  {size}: {config['description']}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AICL RAG Comparison Orchestrator")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], default=2,
                       help="Experiment phase")
    parser.add_argument("--providers", type=str, 
                       help="Comma-separated list of providers (openai,azure,openrouter)")
    parser.add_argument("--context-sizes", type=str,
                       help="Comma-separated list of context sizes (tiny,small,medium,large)")
    parser.add_argument("--list-providers", action="store_true",
                       help="List available providers")
    parser.add_argument("--list-context-sizes", action="store_true", 
                       help="List available context sizes")
    
    args = parser.parse_args()
    
    # Create orchestrator
    experiment_dir = Path(__file__).parent.parent
    orchestrator = AICLOrchestrator(experiment_dir)
    
    # Handle list commands
    if args.list_providers:
        orchestrator.list_providers()
        return
    
    if args.list_context_sizes:
        orchestrator.list_context_sizes()
        return
    
    # Parse providers and context sizes
    providers = args.providers.split(',') if args.providers else ['openai', 'azure']
    context_sizes = args.context_sizes.split(',') if args.context_sizes else ['small', 'medium']
    
    # Validate inputs
    invalid_providers = [p for p in providers if p not in orchestrator.providers]
    if invalid_providers:
        print(f"❌ Invalid providers: {invalid_providers}")
        print("Use --list-providers to see available options")
        return
    
    invalid_sizes = [s for s in context_sizes if s not in orchestrator.context_sizes]
    if invalid_sizes:
        print(f"❌ Invalid context sizes: {invalid_sizes}")
        print("Use --list-context-sizes to see available options")
        return
    
    # Run matrix experiment
    orchestrator.run_matrix_experiment(providers, context_sizes, args.phase)


if __name__ == "__main__":
    main()
