import subprocess
import json
import re
from pathlib import Path

def run_aicl_config(config_file):
    """Run an AICL config and capture output"""
    result = subprocess.run(
        ['python', 'run.py', config_file],
        capture_output=True,
        text=True,
        timeout=120
    )
    return result.returncode, result.stdout, result.stderr

def extract_resources_created(output):
    """Extract number of resources created from output"""
    match = re.search(r'Apply complete: (\d+) resources created', output)
    return int(match.group(1)) if match else 0

def extract_grade_scores(output):
    """Extract all grade scores from output"""
    scores = []
    for match in re.finditer(r'Score: ([\d.]+)/([\d.]+) \(([\d.]+)%\)', output):
        scores.append({
            'earned': float(match.group(1)),
            'total': float(match.group(2)),
            'percentage': float(match.group(3))
        })
    return scores

def test_experiment_demo():
    """Test experiment_demo.aicl - Model comparison"""
    print("\n🧪 Testing: experiment_demo.aicl (Model Comparison)")
    
    returncode, stdout, stderr = run_aicl_config('experiment_demo.aicl')
    
    assert returncode == 0, f"Config failed to run: {stderr}"
    
    resources = extract_resources_created(stdout)
    assert resources == 4, f"Expected 4 resources, got {resources}"
    
    scores = extract_grade_scores(stdout)
    assert len(scores) == 2, f"Expected 2 grades, got {len(scores)}"
    
    print(f"   ✅ Created {resources} resources")
    print(f"   ✅ Generated {len(scores)} grade scores")
    for i, score in enumerate(scores, 1):
        status = "✅ PASSED" if score['percentage'] == 100 else "⚠️ PARTIAL"
        print(f"   ✅ Model {i}: {score['percentage']}% {status}")

def test_context_packaging():
    """Test experiment_context_packaging.aicl - Context experiments"""
    print("\n🧪 Testing: experiment_context_packaging.aicl (Context Packaging)")
    
    returncode, stdout, stderr = run_aicl_config('experiment_context_packaging.aicl')
    
    assert returncode == 0, f"Config failed to run: {stderr}"
    
    resources = extract_resources_created(stdout)
    assert resources >= 4, f"Expected at least 4 resources, got {resources}"
    
    scores = extract_grade_scores(stdout)
    assert len(scores) >= 2, f"Expected at least 2 grades, got {len(scores)}"
    
    print(f"   ✅ Created {resources} resources")
    print(f"   ✅ Generated {len(scores)} grade scores")
    print(f"   ✅ Context comparison validated")

def test_rag_query():
    """Test replit_rag_query.aicl - RAG pipeline"""
    print("\n🧪 Testing: replit_rag_query.aicl (RAG Query)")
    
    returncode, stdout, stderr = run_aicl_config('replit_rag_query.aicl')
    
    assert returncode == 0, f"Config failed to run: {stderr}"
    
    resources = extract_resources_created(stdout)
    assert resources >= 2, f"Expected at least 2 resources, got {resources}"
    
    assert 'query-answer' in stdout or 'Query:' in stdout, "No query results found"
    
    print(f"   ✅ Created {resources} resources")
    print(f"   ✅ RAG pipeline executed successfully")

def test_simple_demo():
    """Test demo_simple.aicl - Basic chat"""
    print("\n🧪 Testing: demo_simple.aicl (Simple Chat)")
    
    returncode, stdout, stderr = run_aicl_config('demo_simple.aicl')
    
    assert returncode == 0, f"Config failed to run: {stderr}"
    
    resources = extract_resources_created(stdout)
    assert resources >= 1, f"Expected at least 1 resource, got {resources}"
    
    assert 'chat-greeting' in stdout or 'Response:' in stdout, "No chat response found"
    
    print(f"   ✅ Created {resources} resources")
    print(f"   ✅ Chat completion validated")

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 AICL POC Test Suite")
    print("=" * 70)
    
    tests = [
        test_simple_demo,
        test_experiment_demo,
        test_context_packaging,
        test_rag_query
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"   ❌ FAILED: {e}")
        except Exception as e:
            failed += 1
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 70)
    
    exit(0 if failed == 0 else 1)
