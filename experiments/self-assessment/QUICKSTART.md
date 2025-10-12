# Self-Assessment Quick Start

Focus: Use AICL tooling to test and fix its own functions.

## Simple Loop

```
Issue → RAG Context → LLM Fix → Run Test → Judge Quality
```

No Redmica. No external tracking. Just pure self-improvement.

---

## Step 1: Run the Self-Fix

```bash
cd /Users/zacelston/code/tofu-aicl

# Make sure dependencies are installed
pip install typer python-redmine

# Run the self-fix experiment
./aicl_modular run experiments/self-assessment/fix-test.aicl
```

---

## What It Does

### Current Target: `test_parse_config`

**Issue:**
```
FileNotFoundError: /tmp/tmpco5hkhbr.aicl
Test tries to delete temp file twice
```

**Process:**
1. **RAG Query**: "How should pytest handle temp files?"
2. **Context**: Finds patterns in existing tests
3. **LLM Analyze**: Understands the root cause
4. **LLM Fix**: Generates proper temp file handling
5. **Run Test**: Verifies fix works
6. **Judge**: Scores fix quality (0-100)

**Output:**
- Proposed fix (code)
- Test results (pass/fail)
- Judge evaluation (score + reasoning)
- Decision (ACCEPT/REJECT)

---

## Expected Output

```json
{
  "analysis": "Test fails because NamedTemporaryFile auto-deletes...",
  "proposed_fix": "def test_parse_config(self): ...",
  "test_result": {
    "exit_code": 0,
    "passed": true
  },
  "judgment": {
    "total_score": 88,
    "breakdown": {
      "correctness": 38,
      "code_quality": 28,
      "best_practices": 17,
      "maintainability": 5
    },
    "decision": "ACCEPT",
    "reasoning": "Fix properly uses delete=False pattern..."
  }
}
```

---

## If Judge Accepts (Score >= 80)

**Manual Review:**
1. Read the proposed fix
2. Verify it makes sense
3. Check test results
4. Apply to `tests/integration/test_engine.py`
5. Run full test suite

**Apply:**
```bash
# Copy the generated fix into the test file
nano tests/integration/test_engine.py

# Verify
pytest tests/integration/test_engine.py::TestAICLEngine::test_parse_config -v
```

---

## If Judge Rejects (Score < 80)

**Review:**
- Check judge reasoning
- Look at improvement suggestions
- Understand what went wrong

**Iterate:**
- Refine RAG query
- Adjust LLM prompt
- Try different approach
- Run again

---

## Simple Test Run

Want to see it work without full RAG setup?

Create `experiments/self-assessment/simple-test.aicl`:

```yaml
config:
  name: "Simple Self-Test"

steps:
  # Just test the judging system
  - name: "Mock Fix"
    provider: "naga"
    model: "claude-3-5-sonnet"
    prompt: |
      Generate a simple fix for this issue:
      
      Problem: Function returns None instead of empty list
      
      Current code:
      ```python
      def get_items():
          pass
      ```
      
      Fix: Return empty list
    outputs:
      fix: "{{.response}}"

  - name: "Judge Quality"
    provider: "naga"
    model: "gpt-4"
    prompt: |
      Judge this fix:
      
      Issue: Function returns None
      Fix: {{.fix}}
      
      Score (0-100):
      - Correctness (40): Does it fix the issue?
      - Quality (30): Is code clean?
      - Practices (20): Follows Python patterns?
      - Maintainability (10): Clear and simple?
      
      Return JSON with score and decision.
    outputs:
      judgment: "{{.response}}"

assertions:
  - condition: "{{.judgment.score}} >= 60"
    message: "Minimum quality threshold"
```

Run:
```bash
./aicl_modular run experiments/self-assessment/simple-test.aicl
```

---

## Debugging

### Check CLI Works
```bash
./aicl_modular --help
./aicl_modular validate experiments/self-assessment/fix-test.aicl
```

### Check in Container
```bash
docker-compose run --rm tofu-aicl-test /bin/bash
# Inside container:
./aicl_modular run experiments/self-assessment/fix-test.aicl
```

### Verbose Output
```bash
./aicl_modular run experiments/self-assessment/fix-test.aicl -v
```

---

## Next Tests to Fix

After `test_parse_config` works, expand to:

### 1. Code Quality Issues
```yaml
target: "src/aicl/parser.py"
issue: "Function too complex (cyclomatic complexity > 10)"
query: "Code simplification patterns"
```

### 2. Performance Issues
```yaml
target: "slow test in test_state_manager.py"
issue: "Test takes 2+ seconds"
query: "Test optimization patterns"
```

### 3. Missing Tests
```yaml
target: "cli/runners/docker.py"
issue: "No unit tests for DockerRunner"
query: "Test patterns for Docker code"
```

---

## Architecture

**Simple and focused:**

```
1. Detect → What's broken?
2. RAG    → How should it work?
3. Fix    → Generate solution
4. Test   → Does it work?
5. Judge  → Is it good?
```

**No external dependencies. No tracking systems. Just AICL fixing AICL.**

---

## Success Criteria

✅ **Fix works**: Tests pass  
✅ **Quality good**: Score >= 80  
✅ **Patterns followed**: Uses RAG context  
✅ **Maintainable**: Clear and simple  

---

## Philosophy

Keep it simple:
- One issue at a time
- Clear evaluation criteria
- Manual review before applying
- Learn from each iteration

The tool improves itself through tight feedback loops, not complex orchestration.
