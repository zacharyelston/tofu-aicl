# AICL Self-Assessment Architecture

## Meta-Framework: The Tool That Improves Itself

**Core Principle:** Use AICL to fix, improve, and assess AICL using RAG + LLM judging.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   AICL Self-Assessment Loop                  │
└─────────────────────────────────────────────────────────────┘

1. DETECT ISSUE
   ├─ Failed test
   ├─ Code smell
   ├─ Performance issue
   └─ Missing docs

2. RAG CONTEXT RETRIEVAL
   ├─ Query: "How should this work?"
   ├─ Sources:
   │  ├─ v2.1 specs (Progressive)
   │  ├─ v2.2 specs (Contract-Based)
   │  ├─ v2.3 specs (Scenario-Based)
   │  ├─ Core implementation
   │  ├─ Test patterns
   │  └─ CLI patterns
   └─ Output: Relevant patterns & examples

3. LLM FIX GENERATION
   ├─ Input: Issue + RAG context
   ├─ Analysis: Root cause
   ├─ Generation: Proposed fix
   └─ Output: Code changes

4. VERIFICATION
   ├─ Apply fix (temporary)
   ├─ Run tests
   ├─ Measure results
   └─ Output: Pass/fail + metrics

5. JUDGE QUALITY
   ├─ Criteria (100 points):
   │  ├─ Correctness (40 pts)
   │  ├─ Code Quality (30 pts)
   │  ├─ Best Practices (20 pts)
   │  └─ Maintainability (10 pts)
   ├─ Decision: ACCEPT (80+) / REJECT (<80)
   └─ Output: Score + reasoning + suggestions

6. APPLY OR LEARN
   ├─ If ACCEPT: Apply changes
   │  ├─ Create PR
   │  ├─ Add to knowledge base
   │  └─ Track in Redmica
   └─ If REJECT: Learn & retry
      ├─ Update RAG query
      ├─ Refine prompt
      └─ Try different approach
```

---

## Knowledge Base (RAG)

### Sources Indexed

**v2 Specifications:**
- `docs/v2.1/` - Progressive Complexity patterns
- `docs/v2.2/` - Contract-Based patterns
- `docs/v2.3/` - Scenario-Based patterns
- `docs/spec/` - Core specification

**Implementation:**
- `src/aicl/` - Core engine, parsers, evaluators
- `cli/` - CLI commands and runners
- `providers/` - Provider implementations

**Patterns:**
- `tests/` - Test patterns and fixtures
- `examples/` - Usage examples
- Previous fixes - Learned improvements

### Query Examples

```
"How should pytest tests handle temporary files?"
→ Returns: Context managers, NamedTemporaryFile patterns

"What's the pattern for state management?"
→ Returns: StateManager class, persistence patterns

"How do other providers implement resource cleanup?"
→ Returns: Provider lifecycle patterns
```

---

## Judging System

### Evaluation Criteria (100 points)

**1. Correctness (40 points)**
- Fixes the original issue? (15 pts)
- Tests pass after fix? (15 pts)
- No new errors introduced? (10 pts)

**2. Code Quality (30 points)**
- Follows framework patterns? (12 pts)
- Clean and readable? (10 pts)
- Proper resource management? (8 pts)

**3. Best Practices (20 points)**
- Uses design patterns from RAG? (8 pts)
- Pythonic code? (7 pts)
- Follows PEP 8? (5 pts)

**4. Maintainability (10 points)**
- Clear intent and comments? (5 pts)
- Easy to understand? (3 pts)
- Well-documented? (2 pts)

### Decision Logic

```python
if score >= 80 and tests_pass and decision == "ACCEPT":
    apply_fix()
    add_to_knowledge_base()
    create_pr()
else:
    learn_from_failure()
    retry_with_improvements()
```

---

## Example: Fix Failing Test

### Input
```
Issue: test_parse_config fails with FileNotFoundError
File: tests/integration/test_engine.py
Error: [Errno 2] No such file or directory: '/tmp/tmpco5hkhbr.aicl'
```

### RAG Query
```
"pytest temporary file cleanup patterns NamedTemporaryFile delete"
```

### RAG Results
```python
# Pattern 1: Use delete=False
with NamedTemporaryFile(mode='w', suffix='.aicl', delete=False) as f:
    f.write(content)
    temp_path = f.name

try:
    # Use temp_path
finally:
    os.unlink(temp_path)

# Pattern 2: Use context manager properly
with NamedTemporaryFile(mode='w', suffix='.aicl') as f:
    f.write(content)
    f.flush()
    # Use f.name while context is active
```

### Generated Fix
```python
def test_parse_config(self):
    """Test config parsing with proper temp file handling"""
    with tempfile.NamedTemporaryFile(
        mode='w', 
        suffix='.aicl', 
        delete=False
    ) as f:
        f.write(sample_config)
        temp_path = f.name
    
    try:
        # Parse config while file exists
        config = engine.parse_config(temp_path)
        assert config is not None
    finally:
        # Clean up in finally block
        if os.path.exists(temp_path):
            os.unlink(temp_path)
```

### Judge Evaluation
```json
{
  "total_score": 88,
  "breakdown": {
    "correctness": 38,
    "code_quality": 28,
    "best_practices": 17,
    "maintainability": 5
  },
  "decision": "ACCEPT",
  "reasoning": "Fix properly handles temp file lifecycle using delete=False pattern from RAG results. Tests pass. Follows pytest best practices.",
  "improvements": [
    "Could add docstring explaining temp file pattern",
    "Consider extracting temp file logic to fixture"
  ]
}
```

---

## Integration with Redmica

### Issue Tracking

**Tracker:** Self-Assessment  
**Custom Fields:**
- Target Type: test / code / docs
- Issue Type: bug / quality / performance
- Fix Score: 0-100
- Judge Decision: ACCEPT / REJECT
- RAG Sources: list of used sources

**Workflow:**
```
New → RAG Query → Fix Generated → Testing → Judged → Applied/Rejected
```

### Automation

**Trigger:** Failed test detected  
**Process:**
1. Create Redmica issue
2. Run self-assessment experiment
3. Update issue with results
4. If accepted: Create PR
5. Human reviews PR
6. Merge or refine

---

## Use Cases

### 1. Fix Failing Tests
```bash
./experiments/self-assessment/run-self-fix.sh
```

### 2. Improve Code Quality
```yaml
# quality-improvement.aicl
steps:
  - query: "Find code smells in module X"
  - analyze: "What patterns should be used?"
  - fix: "Refactor following patterns"
  - judge: "Does quality improve?"
```

### 3. Generate Documentation
```yaml
# doc-generation.aicl
steps:
  - query: "Find undocumented functions"
  - context: "Similar documented functions"
  - generate: "Write docstrings"
  - judge: "Is documentation complete?"
```

### 4. Performance Optimization
```yaml
# performance-optimization.aicl
steps:
  - detect: "Slow tests/functions"
  - query: "Find optimization patterns"
  - optimize: "Apply improvements"
  - judge: "Measure performance gain"
```

---

## Meta-Learning

### Knowledge Accumulation

**Accepted Fixes:**
- Add to RAG knowledge base
- Tag with: issue type, score, patterns used
- Query: "Show successful fixes for similar issues"

**Rejected Fixes:**
- Store as negative examples
- Include judge feedback
- Learn: "Avoid these patterns"

**Improvement Tracking:**
```python
{
  "fix_id": "test_parse_config_001",
  "issue": "FileNotFoundError",
  "attempts": 2,
  "final_score": 88,
  "patterns_used": ["delete=False", "finally block"],
  "learned": "Always use finally for cleanup"
}
```

---

## Quality Gates

### Pre-Apply Checks

1. **Score >= 80** (Minimum quality)
2. **Tests Pass** (Verification)
3. **Judge Accepts** (Decision)
4. **No Regressions** (Safety)

### Post-Apply Validation

1. All tests still pass
2. No new warnings/errors
3. Code coverage maintained
4. Performance not degraded

---

## Future Enhancements

### 1. Continuous Self-Assessment
- Monitor all test runs
- Auto-detect issues
- Queue self-fix experiments
- Report results to Redmica

### 2. Multi-Model Judging
- Use multiple LLMs as judges
- Aggregate scores
- Require consensus for ACCEPT
- Learn from disagreements

### 3. Self-Improving RAG
- Analyze which queries work best
- Refine embedding strategy
- Update index with new patterns
- Remove obsolete patterns

### 4. Human-in-the-Loop
- Request human review for edge cases
- Learn from human overrides
- Improve judge calibration
- Build trust through transparency

---

## Philosophy

**The Recursive Improvement Loop:**

```
AICL knows:
  ├─ How it should work (specs)
  ├─ How it currently works (code)
  ├─ What patterns exist (RAG)
  └─ What quality means (judge)

Therefore AICL can:
  ├─ Detect its own issues
  ├─ Find relevant solutions
  ├─ Generate improvements
  ├─ Evaluate quality
  └─ Apply fixes

Result:
  Self-improving system that gets better over time
```

**Key Insight:** The tool that knows itself can improve itself.

---

## Getting Started

### 1. Index Codebase
```bash
./aicl_modular run experiments/self-assessment/index-codebase.aicl
```

### 2. Run Self-Fix
```bash
./experiments/self-assessment/run-self-fix.sh
```

### 3. Review Results
- Check judge evaluation
- Review proposed fix
- Verify tests pass
- Apply if acceptable

### 4. Iterate
- Learn from results
- Refine prompts
- Improve RAG queries
- Enhance judging criteria

---

## Success Metrics

- **Fix Acceptance Rate:** % of fixes with score >= 80
- **Test Pass Rate:** % of fixes that pass all tests
- **Human Override Rate:** % of judge decisions overridden
- **Time to Fix:** Minutes from detection to applied fix
- **Quality Improvement:** Average score trend over time

---

## Conclusion

AICL Self-Assessment demonstrates the power of meta-frameworks:
- Use AI to improve AI systems
- RAG provides context and patterns
- LLM judges evaluate quality
- System learns from outcomes

**Result:** A framework that continuously improves itself while maintaining quality and safety.
