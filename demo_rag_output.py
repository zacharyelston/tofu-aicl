#!/usr/bin/env python3
"""
Demo script to show RAG pipeline outputs
"""
from pathlib import Path
from src.aicl.core.engine import AICLEngine

def main():
    print("=" * 80)
    print("REPLIT API DOCUMENTATION RAG DEMO")
    print("=" * 80)
    print("\nRunning RAG query pipeline...")
    
    config_path = Path("replit_rag_query.aicl")
    engine = AICLEngine(config_path)
    
    try:
        # Apply without auto-destroy
        engine.apply()
        
        # Display outputs
        print("\n" + "=" * 80)
        print("QUERY RESULTS")
        print("=" * 80)
        
        # Get search results
        search_state = engine.state_manager.get_resource_by_name("query", "search_docs")
        if search_state:
            print("\n📚 Retrieved Documentation Chunks:")
            results = search_state.attributes.get('results', [])
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Score: {result.get('score', 0):.3f}")
                print(f"   Source: {result.get('source', 'unknown')}")
                content = result.get('content', '')[:200]
                print(f"   Content: {content}...")
        
        # Get generated code
        chat_state = engine.state_manager.get_resource_by_name("chat", "write_feature")
        if chat_state:
            print("\n" + "=" * 80)
            print("AI-GENERATED FEATURE CODE (with RAG context)")
            print("=" * 80)
            response = chat_state.attributes.get('response', '')
            print(f"\n{response}\n")
        
        print("=" * 80)
        print("Demo Complete!")
        print("=" * 80)
        
    finally:
        # Cleanup
        print("\nCleaning up resources...")
        engine.destroy()
        print("Done!")

if __name__ == "__main__":
    main()
