# AICL Self-Assessment System

## Concept

Use AICL to improve AICL through RAG-powered self-assessment and LLM judging.

```
Issue → RAG Context → LLM Fix → Run Tests → Judge Quality → Apply/Reject
```

## Architecture

### 1. RAG Knowledge Base
- **Sources**: v2 specs, core code, tests, CLI
- **Purpose**: Provide context about how AICL should work
- **Query**: Find patterns, best practices, similar solutions

### 2. Fix Generation
- **Input**: Failing test + RAG context
- **Process**: LLM analyzes and generates fix
- **Output**: Proposed code changes

### 3. Verification
- **Test**: Run pytest to verify fix works
- **Measure**: Check exit code and output

### 4. Quality Judging
- **Criteria**: Correctness, code quality, best practices, maintainability
- **Scoring**: 100-point scale with breakdown
- **Decision**: ACCEPT (80+) or REJECT (<80)

## Experiments

### Phase 1: Index Codebase
**File**: `index-codebase.aicl`

Creates RAG index of:
- v2.1, v2.2, v2.3 specifications
- Core AICL implementation
- Test patterns
- CLI patterns

**Run**:
```bash
./aicl_modular run experiments/self-assessment/index-codebase.aicl
```

### Phase 2: Fix Failing Test
**File**: `fix-test.aicl`

Automatically fixes `test_parse_config` using:
1. RAG query for temp file patterns
2. LLM analysis of issue
3. LLM generates fix
4. Run tests to verify
5. Judge quality (4 criteria, 100 points)
6. Accept if score >= 80

**Run**:
```bash
./aicl_modular run experiments/self-assessment/fix-test.aicl
```

## Evaluation Criteria

### Correctness (40 points)
- Fixes the original issue?
- Tests pass?
- No new errors?

### Code Quality (30 points)
- Follows framework patterns?
- Clean and readable?
- Proper resource management?

### Best Practices (20 points)
- Uses context managers?
- Follows RAG patterns?
- Pythonic code?

### Maintainability (10 points)
- Clear intent?
- Easy to understand?
- Well-commented?

## Quality Gates

1. **Tests Must Pass**: `exit_code == 0`
2. **Minimum Score**: `score >= 80`
3. **Judge Decision**: `decision == 'ACCEPT'`

## Example Output

```json
{
  "total_score": 85,
  "breakdown": {
    "correctness": 38,
    "code_quality": 27,
    "best_practices": 15,
    "maintainability": 5
  },
  "decision": "ACCEPT",
  "reasoning": "Fix properly handles temp file cleanup using delete=False pattern...",
  "improvements": [
    "Could add explicit cleanup in finally block",
    "Consider adding docstring explaining temp file handling"
  ]
}
```

## Future Experiments

### Self-Assessment Loop
- Continuous monitoring of test failures
- Automatic fix proposals
- Judge approval required
- Human review for final merge

### Code Quality Improvement
- Query RAG for better patterns
- LLM suggests refactorings
- Judge evaluates improvements
- Apply if score improves

### Documentation Generation
- RAG context from specs
- LLM generates missing docs
- Judge evaluates completeness
- Auto-update documentation

### Performance Optimization
- Detect slow tests/code
- RAG finds optimization patterns
- LLM proposes improvements
- Judge measures impact

## Meta-Learning

The system learns from:
- Accepted fixes (positive examples)
- Rejected fixes (negative examples)
- Judge feedback (improvement suggestions)
- Test results (verification data)

## Philosophy

**"Use the tool to improve the tool"**

1. AICL knows how it should work (v2 specs)
2. AICL can read its own code (RAG)
3. AICL can generate fixes (LLM)
4. AICL can judge quality (LLM grader)
5. AICL can apply changes (command provider)

Therefore, AICL can improve itself!

## Next Steps

1. ✅ Create RAG index of codebase
2. ✅ Design self-fix experiment
3. ⏭️ Run index-codebase.aicl
4. ⏭️ Run fix-test.aicl
5. ⏭️ Evaluate results
6. ⏭️ Iterate and improve
7. ⏭️ Integrate with Redmica
8. ⏭️ Automate self-assessment loop
