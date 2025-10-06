"""
RAG operations for experiments.

Handles embeddings generation, vector indexing, and query execution.
"""

import time
from typing import Dict, List, Any

from aicl.state.manager import StateManager
from .providers import ProviderConfig


class RAGOperations:
    """Handles RAG operations with state tracking."""
    
    def __init__(self, git_sha: str):
        self.git_sha = git_sha
        self.config = ProviderConfig()
    
    def generate_embeddings(self, manager: StateManager, provider: str, 
                          test_data: Dict[str, Any], context_size: str) -> Dict[str, Any]:
        """Generate embeddings for test data."""
        manager.start_action()
        
        # Calculate embedding parameters
        embedding_count = min(
            test_data["total_files"], 
            self.config.get_context_limit(context_size)
        )
        cost_per_embedding = self.config.get_provider_cost(provider, "embedding")
        model = self.config.get_embedding_model(provider)
        dimensions = self.config.get_embedding_dimensions(provider)
        
        # Simulate embedding generation time
        time.sleep(0.1)
        
        result = {
            "count": embedding_count,
            "provider": provider,
            "model": model,
            "dimensions": dimensions,
            "cost_usd": embedding_count * cost_per_embedding
        }
        
        manager.record_provision(
            resource_type="embeddings",
            resource_name=f"{provider}_embeddings",
            provider=provider,
            input_data={
                "files": test_data["total_files"],
                "context_size": context_size,
                "model": model
            },
            result=result,
            cost_usd=result["cost_usd"],
            pipeline="rag_comparison",
            step="generate_embeddings"
        )
        
        return result
    
    def create_vector_index(self, manager: StateManager, provider: str,
                          embedding_result: Dict[str, Any], context_size: str) -> Dict[str, Any]:
        """Create vector index from embeddings."""
        manager.start_action()
        
        # Simulate index creation time
        time.sleep(0.05)
        
        result = {
            "index_id": f"{provider}_index_{self.git_sha}",
            "embedding_count": embedding_result["count"],
            "dimensions": embedding_result["dimensions"],
            "provider": provider,
            "context_size": context_size
        }
        
        manager.record_provision(
            resource_type="vector_index",
            resource_name=f"{provider}_index",
            provider=provider,
            input_data={
                "embeddings": embedding_result["count"],
                "dimensions": embedding_result["dimensions"],
                "context_size": context_size
            },
            result=result,
            pipeline="rag_comparison",
            step="create_index"
        )
        
        return result
    
    def run_test_queries(self, manager: StateManager, provider: str,
                        index_result: Dict[str, Any], context_size: str) -> List[Dict[str, Any]]:
        """Run test queries against the RAG system."""
        test_queries = self._get_test_queries()
        query_results = []
        
        for i, query in enumerate(test_queries):
            manager.start_action()
            
            # Simulate query processing time
            time.sleep(0.02)
            
            query_cost = self.config.get_provider_cost(provider, "query")
            
            # Simulate realistic results with some variation
            result = {
                "query": query,
                "response_length": len(query) * 10,  # Simulated response length
                "relevance_score": 0.8 + (i * 0.02),  # Simulated scoring with variation
                "latency_ms": 200 + (i * 50),  # Simulated latency with variation
                "cost_usd": query_cost,
                "provider": provider,
                "context_size": context_size
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
    
    def _get_test_queries(self) -> List[str]:
        """Get standardized test queries for RAG evaluation."""
        return [
            "How does tofu-aicl handle state management?",
            "What providers are supported for AI operations?",
            "How do you configure API keys for different services?",
            "What is the State as DNA model?",
            "How does lineage tracking work?",
            "What are the main components of the AICL framework?",
            "How do you run experiments with different providers?",
            "What cost tracking features are available?"
        ]
