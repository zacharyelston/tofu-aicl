"""
Evaluation and scoring for RAG experiments.

Handles result analysis, scoring, and performance metrics.
"""

from datetime import datetime
from typing import Dict, List, Any

from aicl.state.manager import StateManager


class ExperimentEvaluator:
    """Evaluates and scores RAG experiment results."""
    
    def __init__(self, git_sha: str):
        self.git_sha = git_sha
        
        # Scoring weights for overall evaluation
        self.weights = {
            "relevance": 0.6,    # 60% weight on relevance scores
            "latency": 0.3,      # 30% weight on response time
            "cost": 0.1          # 10% weight on cost efficiency
        }
    
    def evaluate_results(self, manager: StateManager, provider: str,
                        query_results: List[Dict[str, Any]], context_size: str) -> Dict[str, Any]:
        """Evaluate and score the experiment results."""
        manager.start_action()
        
        # Calculate basic metrics
        metrics = self._calculate_metrics(query_results)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(metrics)
        
        evaluation = {
            "provider": provider,
            "context_size": context_size,
            "query_count": len(query_results),
            "metrics": metrics,
            "overall_score": round(overall_score, 3),
            "git_sha": self.git_sha,
            "timestamp": datetime.utcnow().isoformat(),
            "scoring_weights": self.weights
        }
        
        manager.record_execution(
            pipeline="rag_comparison",
            step="evaluate_results",
            input_data={
                "query_count": len(query_results),
                "provider": provider,
                "context_size": context_size
            },
            result=evaluation,
            provider=provider
        )
        
        return evaluation
    
    def _calculate_metrics(self, query_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate performance metrics from query results."""
        if not query_results:
            return {
                "avg_relevance_score": 0.0,
                "avg_latency_ms": 0.0,
                "total_cost": 0.0,
                "min_relevance": 0.0,
                "max_relevance": 0.0,
                "min_latency": 0.0,
                "max_latency": 0.0
            }
        
        relevance_scores = [r["relevance_score"] for r in query_results]
        latencies = [r["latency_ms"] for r in query_results]
        costs = [r["cost_usd"] for r in query_results]
        
        return {
            "avg_relevance_score": round(sum(relevance_scores) / len(relevance_scores), 3),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 1),
            "total_cost": round(sum(costs), 4),
            "min_relevance": round(min(relevance_scores), 3),
            "max_relevance": round(max(relevance_scores), 3),
            "min_latency": round(min(latencies), 1),
            "max_latency": round(max(latencies), 1),
            "cost_per_query": round(sum(costs) / len(costs), 4)
        }
    
    def _calculate_overall_score(self, metrics: Dict[str, float]) -> float:
        """Calculate weighted overall score."""
        # Normalize relevance score (already 0-1)
        relevance_score = metrics["avg_relevance_score"]
        
        # Normalize latency score (lower is better, cap at 2000ms)
        max_latency = 2000.0
        latency_score = max(0, (max_latency - metrics["avg_latency_ms"]) / max_latency)
        
        # Normalize cost score (lower is better, cap at $0.10)
        max_cost = 0.10
        cost_score = max(0, (max_cost - metrics["total_cost"]) / max_cost)
        
        # Calculate weighted score
        overall_score = (
            relevance_score * self.weights["relevance"] +
            latency_score * self.weights["latency"] +
            cost_score * self.weights["cost"]
        )
        
        return overall_score
    
    def generate_recommendations(self, evaluation: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on evaluation results."""
        recommendations = []
        metrics = evaluation["metrics"]
        
        # Relevance recommendations
        if metrics["avg_relevance_score"] < 0.7:
            recommendations.append("Consider improving embedding quality or query processing")
        elif metrics["avg_relevance_score"] > 0.9:
            recommendations.append("Excellent relevance scores - this configuration works well")
        
        # Latency recommendations
        if metrics["avg_latency_ms"] > 1000:
            recommendations.append("High latency detected - consider optimizing query processing")
        elif metrics["avg_latency_ms"] < 200:
            recommendations.append("Excellent response times - good for real-time applications")
        
        # Cost recommendations
        if metrics["total_cost"] > 0.05:
            recommendations.append("High cost per experiment - consider cost optimization")
        elif metrics["total_cost"] < 0.01:
            recommendations.append("Very cost-effective configuration")
        
        # Overall score recommendations
        if evaluation["overall_score"] > 0.8:
            recommendations.append("High-performing configuration - recommended for production")
        elif evaluation["overall_score"] < 0.5:
            recommendations.append("Low overall score - significant improvements needed")
        
        return recommendations
    
    def compare_evaluations(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple evaluations and rank them."""
        if not evaluations:
            return {}
        
        # Sort by overall score (descending)
        sorted_evals = sorted(evaluations, key=lambda x: x["overall_score"], reverse=True)
        
        # Find best performers in each category
        best_relevance = max(evaluations, key=lambda x: x["metrics"]["avg_relevance_score"])
        best_latency = min(evaluations, key=lambda x: x["metrics"]["avg_latency_ms"])
        best_cost = min(evaluations, key=lambda x: x["metrics"]["total_cost"])
        
        comparison = {
            "total_evaluations": len(evaluations),
            "ranking": [
                {
                    "rank": i + 1,
                    "provider": eval_data["provider"],
                    "context_size": eval_data["context_size"],
                    "overall_score": eval_data["overall_score"]
                }
                for i, eval_data in enumerate(sorted_evals)
            ],
            "best_performers": {
                "relevance": {
                    "provider": best_relevance["provider"],
                    "context_size": best_relevance["context_size"],
                    "score": best_relevance["metrics"]["avg_relevance_score"]
                },
                "latency": {
                    "provider": best_latency["provider"],
                    "context_size": best_latency["context_size"],
                    "latency_ms": best_latency["metrics"]["avg_latency_ms"]
                },
                "cost": {
                    "provider": best_cost["provider"],
                    "context_size": best_cost["context_size"],
                    "cost": best_cost["metrics"]["total_cost"]
                }
            },
            "winner": {
                "provider": sorted_evals[0]["provider"],
                "context_size": sorted_evals[0]["context_size"],
                "overall_score": sorted_evals[0]["overall_score"]
            }
        }
        
        return comparison
