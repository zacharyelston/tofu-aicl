#!/usr/bin/env python3
import subprocess
import json
import sys

def run_aicl_config(config_file):
    result = subprocess.run(
        ['python', 'run.py', config_file],
        capture_output=True,
        text=True
    )
    return result.stdout, result.stderr

def main():
    config = sys.argv[1] if len(sys.argv) > 1 else 'rag_query.aicl'
    
    print(f"Running RAG pipeline: {config}\n")
    print("=" * 80)
    
    stdout, stderr = run_aicl_config(config)
    
    print(stdout)
    if stderr:
        print("\nErrors:", stderr)
    
    print("\n" + "=" * 80)
    print("\nRAG Pipeline Complete!")
    print("\nNote: To see resource outputs, check the state or add output blocks to your .aicl config")

if __name__ == '__main__':
    main()
