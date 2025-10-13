# Self-Building Experiments

## Vision

Enable AICL to improve and extend itself through experiments that generate and modify source code. The system can add providers, fix bugs, optimize performance, and build new features from specifications.

## Philosophy

**"The tool builds the tool"**

1. AICL knows how it should work (specifications + RAG)
2. AICL can read its own codebase (vector search)
3. AICL can generate code (LLM)
4. AICL can test code (test runner)
5. AICL can judge quality (LLM-as-Judge)
6. AICL can apply changes (file writer)

Therefore, **AICL can build itself**.

---

## Progression Path

### Level 1: Simple Provider (✅ Current)
**Capability**: Add a basic provider from specification

**Example**: Echo provider
- Generate provider code
- Generate config.yaml
- Generate tests
- Verify quality

**Run**:
```bash
python run.py experiments/self-build/add-echo-provider.aicl
```

---

### Level 2: Resource Extension (🔄 Next)
**Capability**: Add resource types to existing providers

**Example**: Batch completion for OpenAI
- Add batch_completion resource
- Implement async parallel requests
- Update provider config
- Generate tests

---

### Level 3: Utility Functions (📋 Planned)
**Capability**: Add helper functions and utilities

**Example**: Retry decorator
- Generate utility function
- Add to utils module
- Write comprehensive tests
- Integrate with existing code

---

### Level 4: Bug Fixes (📋 Planned)
**Capability**: Automatically fix failing tests

**Example**: Fix test_parse_config
- Detect failing test
- RAG: Find temp file patterns
- Generate fix
- Verify tests pass
- Judge quality

---

### Level 5: Features from NL (🎯 Goal)
**Capability**: Build complete features from natural language

**Example**: "Add streaming LLM responses"
- Parse natural language spec
- Break into subtasks
- Generate all necessary code
- Integration tests
- Quality verification

---

### Level 6: Self-Optimization (🚀 Future)
**Capability**: Optimize its own performance

**Example**: Speed up planner
- Profile codebase
- Identify bottlenecks
- Generate optimizations
- Benchmark improvements

---

## Quick Start

### 1. Add Echo Provider (Simplest Example)

```bash
# Run the self-build experiment
python run.py experiments/self-build/add-echo-provider.aicl

# Review the output
# - Check quality_evaluation score
# - Review generated code
# - If score >= 80, manually apply files

# Apply the changes
mkdir -p providers/echo
# Copy generated code to files (shown in output)

# Test the new provider
pytest providers/echo/test_echo.py -v

# The provider auto-discovers on next run
python run.py test-echo.aicl
```

---

### 2. Run Test Suite

```bash
# Generate experiments from test variables
python generate_experiments.py suite simple_provider

# Run all experiments
python run_experiments.py experiments/suites/simple_provider/*.aicl

# Compare results
python compare_results.py --suite simple_provider
```

---

## Experiment Structure

### Input: Specification

```yaml
feature_type: provider
name: echo
description: Simple echo provider with configurable prefix
requirements:
  - Resource type: echo_text
  - Input: text (string), prefix (string)
  - Output: echoed_text (string), length metrics
```

### Process: Self-Build Pipeline

```
1. RAG Query      → Find implementation patterns
2. Code Generation → LLM generates code
3. Test Generation → LLM generates tests
4. Test Execution  → Run pytest
5. Quality Judging → LLM evaluates quality
6. Decision        → Accept/Revise/Reject
```

### Output: Generated Code + Evaluation

```json
{
  "generated_files": {
    "server.py": "<provider code>",
    "config.yaml": "<provider config>",
    "test_echo.py": "<test code>"
  },
  "quality": {
    "overall_score": 88,
    "decision": "ACCEPT",
    "reasoning": "Well-structured provider following AICL patterns..."
  },
  "recommendation": "ACCEPT: Apply to codebase"
}
```

---

## Quality Evaluation

### Grading Criteria (100 points)

1. **Correctness (40 pts)**
   - Implements specification
   - Tests pass
   - No logical errors
   - Edge cases handled

2. **Code Quality (30 pts)**
   - Follows project patterns
   - Clean and readable
   - Proper error handling
   - Resource management

3. **Best Practices (20 pts)**
   - Language idioms
   - Design patterns
   - Security considerations
   - Performance awareness

4. **Maintainability (10 pts)**
   - Documentation
   - Clear intent
   - Self-documenting
   - Easy to understand

### Decision Thresholds

- **≥ 90**: ACCEPT (Excellent)
- **80-89**: ACCEPT (Good)
- **70-79**: REVISE (Needs improvement)
- **< 70**: REJECT (Inadequate)

---

## Safety Mechanisms

### 1. Sandboxed Testing
- Isolated test environment
- Resource limits
- No network access
- Rollback on failure

### 2. Human Review Gate
- Auto-apply: Score ≥ 95
- Human review: Score 80-94
- Auto-reject: Score < 80

### 3. Git Integration
- Commit before changes
- Automatic rollback
- Branch per experiment
- PR for review

### 4. Progressive Trust
- Start with simple changes
- Build confidence
- Gradually increase complexity
- Track success rate

---

## Test Suites

### Simple Provider (2-5 min)
Add basic echo provider
- 1-2 experiments
- Quick validation
- Entry point for self-building

### Resource Extension (5-10 min)
Add resource to existing provider
- 2-4 experiments
- Medium complexity
- Test integration

### Bug Fix (5-10 min)
Fix failing tests automatically
- 1-3 experiments
- Real-world issues
- Verify solutions

### Quality Comparison (15-30 min)
Compare code generation models
- 6-9 experiments
- Model evaluation
- Best practices

---

## Usage Examples

### CLI Commands (Future)

```bash
# Add new provider
aicl self-build add-provider --spec "Echo provider"

# Add resource type
aicl self-build add-resource \
  --provider openai \
  --spec "Batch completion resource"

# Fix failing test
aicl self-build fix-test \
  --test test_parse_config

# Add feature from description
aicl self-build add-feature \
  --spec "Add streaming LLM responses"

# Optimize performance
aicl self-build optimize \
  --target src/aicl/core/planner.py
```

---

## Metrics & Success

### Per-Experiment Metrics

```python
{
  "generation": {
    "code_lines": 156,
    "generation_time_ms": 3200,
    "tokens_used": 4500,
    "cost_usd": 0.045
  },
  "testing": {
    "tests_generated": 5,
    "tests_passed": 5,
    "coverage_pct": 92
  },
  "quality": {
    "overall_score": 88,
    "decision": "ACCEPT"
  },
  "application": {
    "applied": true,
    "rollback_needed": false
  }
}
```

### Success Criteria

✅ **Functional**: Tests pass  
✅ **Quality**: Score ≥ 80  
✅ **Safe**: No security issues  
✅ **Maintainable**: Clear code  

---

## Example Output

```
=== SELF-BUILD EXPERIMENT: Add Echo Provider ===

📋 Specification:
   Create echo provider with prefix support

🔍 RAG Context Retrieved:
   - Found 5 provider implementation patterns
   - Identified gRPC service structure
   - Located v2.runtime helpers

💻 Code Generated:
   ✅ providers/echo/server.py (156 lines)
   ✅ providers/echo/config.yaml (15 lines)
   ✅ providers/echo/test_echo.py (87 lines)

🧪 Tests Executed:
   ✅ 5/5 tests passed
   ✅ Coverage: 92%

⚖️ Quality Evaluation:
   Score: 88/100
   - Correctness: 38/40
   - Code Quality: 27/30
   - Best Practices: 16/20
   - Maintainability: 7/10
   
   Decision: ACCEPT ✅
   Reasoning: Well-structured provider following AICL 
   patterns. Proper error handling, clear documentation.
   
   Improvements:
   - Consider adding async support
   - Add rate limiting example

💰 Cost:
   Total tokens: 8,500
   Estimated cost: $0.085

✅ RECOMMENDATION: Apply changes to codebase

Next steps:
1. Review generated code above
2. Copy files to providers/echo/
3. Run: pytest providers/echo/test_echo.py
4. Verify auto-discovery works
```

---

## Roadmap

### Phase 1: Foundation (✅ Current)
- [x] Design self-modification architecture
- [x] Create example experiments
- [x] Define quality criteria
- [x] Build test suites

### Phase 2: Basic Self-Building (🔄 In Progress)
- [ ] Implement code_generator resource
- [ ] Implement test_runner resource
- [ ] Implement code_judge resource
- [ ] Run echo provider experiment

### Phase 3: Advanced Features (📋 Next)
- [ ] Resource type extension
- [ ] Utility function generation
- [ ] Bug fix automation
- [ ] Performance optimization

### Phase 4: Natural Language (🎯 Goal)
- [ ] Parse NL specifications
- [ ] Multi-file feature generation
- [ ] Complex feature building
- [ ] Full self-building capability

---

## Contributing

When adding new self-building experiments:

1. **Define Clear Spec**: What should be built?
2. **Create Test Variables**: Parameter space to explore
3. **Set Quality Criteria**: How to evaluate?
4. **Add Safety Checks**: Prevent bad code
5. **Document Process**: Help others learn

---

## Philosophy

The self-building capability is about:
- **Automation**: Reduce manual coding
- **Quality**: Maintain high standards
- **Learning**: Improve from feedback
- **Safety**: Human oversight when needed
- **Empowerment**: Let AI do the tedious work

**The future is AI systems that build themselves.**
