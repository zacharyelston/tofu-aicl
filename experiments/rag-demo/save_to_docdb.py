#!/usr/bin/env python3
"""Save RAG demo results to experiment DocDB"""

import json
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.storage import ExperimentDocDB

def main():
    # Load results
    with open('experiments/rag-demo/outputs/rag-demo-results.json', 'r') as f:
        results = json.load(f)
    
    # Connect to DocDB
    db = ExperimentDocDB()
    
    # Prepare outputs
    outputs = {
        "experiment_type": "rag_demo_live",
        "stages_completed": 11,
        "pipeline": {
            "load_documents": results["resources"].get("knowledge_base", ""),
            "chunk_text": results["resources"].get("doc_chunks", ""),
            "generate_embeddings": results["resources"].get("doc_vectors", ""),
            "index_vectors": results["resources"].get("vector_index", ""),
            "validate_retrieval": results["resources"].get("validation_results", ""),
            "main_question": "What are the main architectural components of the AICL engine?",
            "retrieve_context": results["resources"].get("rag_context", ""),
            "answers": {
                "gpt4o_mini": results["resources"].get("answer_gpt4o_mini", ""),
                "claude_3_5_sonnet": results["resources"].get("answer_claude", ""),
                "gemini_pro_1_5": results["resources"].get("answer_gemini", "")
            },
            "judge_evaluation": results["resources"].get("judge_evaluation", "")
        },
        "resources_created": results["resources_created"],
        "opentelemetry_traces": results["opentelemetry_traces"]
    }
    
    # Prepare metadata
    metadata = {
        "provider": "multi",
        "providers_used": ["file_loader", "text_splitter", "openai", "pinecone", "openrouter"],
        "tags": ["rag", "demo", "multi-llm", "judge", "live"],
        "models": {
            "embedding": "text-embedding-3-small",
            "vector_db": "pinecone",
            "answers": ["openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet", "google/gemini-pro-1.5"],
            "judge": "openai/gpt-4o"
        },
        "namespace": "rag-demo-live",
        "experiment_date": datetime.now().isoformat()
    }
    
    # Save to DocDB
    experiment_id = f"rag_demo_live_{datetime.now().strftime('%Y_%m_%d')}"
    doc_id = db.save_experiment(
        experiment_id=experiment_id,
        outputs=outputs,
        metadata=metadata
    )
    
    print(f"✅ Saved to DocDB:")
    print(f"   Document ID: {doc_id}")
    print(f"   Experiment ID: {experiment_id}")
    print(f"   Resources Created: {results['resources_created']}")
    print(f"   Pipeline Stages: 11")
    print(f"\n📊 Query with:")
    print(f"   python experiments/query_results.py --experiment-id {experiment_id}")
    print(f"   python experiments/query_results.py --list --tags rag,demo")

if __name__ == "__main__":
    main()
