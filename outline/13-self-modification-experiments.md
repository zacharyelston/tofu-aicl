# Self-Modification Experiments Specification

## Vision: The Self-Building AI System

Enable AICL to improve and extend itself through experiments that generate and modify source code, creating a feedback loop where the system builds itself.

---

## Overview

Self-modification experiments allow AICL to:
1. **Generate new providers** from specifications
2. **Add resource types** to existing providers
3. **Extend core functionality** with new features
4. **Fix bugs** through automated code generation
5. **Optimize performance** by rewriting bottlenecks

---

## Architecture

### Self-Modification Pipeline

```
Feature Spec → RAG Context → Code Generation → Testing → Quality Grading → Apply/Reject
```

### Components

1. **Specification Parser**: Extract requirements from natural language or structured specs
2. **RAG Context Retrieval**: Find similar implementations, patterns, best practices
3. **Code Generator**: LLM generates code following project patterns
4. **Test Runner**: Execute tests to verify functionality
5. **Code Judge**: Evaluate code quality, correctness, maintainability
6. **Application System**: Apply changes if quality threshold met

---

## Resource Type: `code_generator`

### Purpose
Generate source code files from specifications and context.

### Attributes

**Input**:
- `specification`: Natural language or structured feature description
- `context_query`: RAG query to find relevant patterns
- `output_path`: Where to write the generated code
- `language`: Programming language (python, go, rust, etc)
- `template_type`: Type of code to generate (provider, resource, utility, test)

**Output**:
- `generated_code`: The complete source code
- `file_path`: Where code was written
- `dependencies`: Required imports/packages
- `tests_generated`: Associated test code

### Example Usage

```hcl
resource "code_generator" "echo_provider" {
  provider = provider.openai
  model = "gpt-4o"
  
  specification = <<-EOT
    Create a simple Echo provider that:
    - Accepts text input
    - Returns the same text with a prefix
    - Supports a configurable prefix parameter
    - Follows the AICL provider pattern
  EOT
  
  context_query = "AICL provider implementation patterns"
  output_path = "providers/echo/server.py"
  language = "python"
  template_type = "provider"
}

resource "code_generator" "echo_config" {
  provider = provider.openai
  model = "gpt-4o"
  
  specification = <<-EOT
    Create provider config.yaml for echo provider:
    - name: echo
    - display_name: Echo Provider
    - default_port: 50060
    - resource types: [echo_text]
  EOT
  
  output_path = "providers/echo/config.yaml"
  language = "yaml"
  template_type = "provider_config"
}
```

---

## Resource Type: `test_runner`

### Purpose
Execute tests and collect results for generated code.

### Attributes

**Input**:
- `test_command`: Command to run tests (e.g., `pytest path/to/test.py`)
- `timeout`: Max execution time
- `environment`: Environment variables

**Output**:
- `exit_code`: Test exit code (0 = pass)
- `stdout`: Test output
- `stderr`: Error output
- `passed`: Boolean success indicator
- `coverage`: Code coverage percentage (if available)

### Example Usage

```hcl
resource "test_runner" "verify_echo" {
  provider = provider.command_assertion
  
  test_command = "pytest providers/echo/test_echo.py -v"
  timeout = 30
  
  # Test must pass
  depends_on = [resource.code_generator.echo_provider]
}
```

---

## Resource Type: `code_judge`

### Purpose
Evaluate generated code quality using LLM-as-Judge.

### Attributes

**Input**:
- `code`: Source code to evaluate
- `criteria`: List of evaluation criteria
- `context`: Original specification and requirements
- `test_results`: Test execution results

**Output**:
- `overall_score`: 0-100 quality score
- `dimension_scores`: Breakdown by criteria
- `decision`: ACCEPT | REJECT | REVISE
- `reasoning`: Detailed explanation
- `improvements`: Suggested improvements

### Evaluation Criteria

1. **Correctness (40 points)**
   - Implements specification correctly
   - Tests pass
   - No logical errors

2. **Code Quality (30 points)**
   - Follows project patterns
   - Clean and readable
   - Proper error handling

3. **Best Practices (20 points)**
   - Language idioms
   - Design patterns
   - Security considerations

4. **Maintainability (10 points)**
   - Documentation/comments
   - Clear intent
   - Easy to understand

### Example Usage

```hcl
resource "code_judge" "evaluate_echo" {
  provider = provider.openai
  model = "gpt-4o"
  
  code = resource.code_generator.echo_provider.generated_code
  
  criteria = [
    "correctness",
    "code_quality", 
    "best_practices",
    "maintainability"
  ]
  
  context = <<-EOT
    Original Specification:
    ${resource.code_generator.echo_provider.specification}
    
    Test Results:
    ${resource.test_runner.verify_echo.passed ? "PASSED" : "FAILED"}
  EOT
  
  test_results = resource.test_runner.verify_echo
}
```

---

## Complete Self-Modification Workflow

### Example: Add Echo Provider

```hcl
# experiments/self-build/add-echo-provider.aicl

variable "quality_threshold" {
  default = 80
}

provider "openai" {
  api_key = env("OPENAI_API_KEY")
}

# Step 1: Query RAG for provider patterns
data "rag_query" "provider_patterns" {
  provider = provider.pinecone
  query = "How to implement a gRPC provider in AICL? Show examples."
  top_k = 5
}

# Step 2: Generate provider implementation
resource "code_generator" "echo_provider" {
  provider = provider.openai
  model = "gpt-4o"
  
  specification = <<-EOT
    Create an Echo provider that implements the AICL provider interface:
    
    Resource Type: echo_text
    - Input: text (string), prefix (string, default: "Echo: ")
    - Output: echoed_text (prefixed input text)
    
    Follow these patterns from the codebase:
    ${data.rag_query.provider_patterns.results}
  EOT
  
  output_path = "providers/echo/server.py"
  language = "python"
  template_type = "provider"
}

# Step 3: Generate provider config
resource "code_generator" "echo_config" {
  provider = provider.openai
  model = "gpt-4o-mini"
  
  specification = <<-EOT
    Create config.yaml for echo provider:
    - name: echo
    - display_name: Echo Provider  
    - port: 50060
    - resource_types: [echo_text]
    - operations: [create, read]
  EOT
  
  output_path = "providers/echo/config.yaml"
  language = "yaml"
}

# Step 4: Generate tests
resource "code_generator" "echo_tests" {
  provider = provider.openai
  model = "gpt-4o"
  
  specification = <<-EOT
    Create pytest tests for echo provider:
    - Test basic echo functionality
    - Test custom prefix
    - Test empty input
    - Test error handling
    
    Use patterns from: ${data.rag_query.provider_patterns.results}
  EOT
  
  output_path = "providers/echo/test_echo.py"
  language = "python"
  template_type = "test"
}

# Step 5: Run tests
resource "test_runner" "verify_echo" {
  provider = provider.command_assertion
  
  test_command = "pytest providers/echo/test_echo.py -v --tb=short"
  timeout = 30
  
  depends_on = [
    resource.code_generator.echo_provider,
    resource.code_generator.echo_tests
  ]
}

# Step 6: Judge code quality
resource "code_judge" "evaluate_implementation" {
  provider = provider.openai
  model = "gpt-4o"
  
  code = jsonencode({
    provider = resource.code_generator.echo_provider.generated_code,
    config = resource.code_generator.echo_config.generated_code,
    tests = resource.code_generator.echo_tests.generated_code
  })
  
  criteria = ["correctness", "code_quality", "best_practices", "maintainability"]
  
  context = <<-EOT
    Specification: Simple echo provider with configurable prefix
    Tests: ${resource.test_runner.verify_echo.passed ? "PASSED ✅" : "FAILED ❌"}
    Coverage: ${resource.test_runner.verify_echo.coverage}%
  EOT
  
  test_results = resource.test_runner.verify_echo
}

# Outputs
output "generated_files" {
  value = [
    resource.code_generator.echo_provider.file_path,
    resource.code_generator.echo_config.file_path,
    resource.code_generator.echo_tests.file_path
  ]
}

output "test_results" {
  value = {
    passed = resource.test_runner.verify_echo.passed
    exit_code = resource.test_runner.verify_echo.exit_code
  }
}

output "quality_evaluation" {
  value = {
    score = resource.code_judge.evaluate_implementation.overall_score
    decision = resource.code_judge.evaluate_implementation.decision
    reasoning = resource.code_judge.evaluate_implementation.reasoning
    meets_threshold = resource.code_judge.evaluate_implementation.overall_score >= var.quality_threshold
  }
}

output "recommendation" {
  value = (
    resource.test_runner.verify_echo.passed && 
    resource.code_judge.evaluate_implementation.overall_score >= var.quality_threshold
  ) ? "ACCEPT: Apply changes to codebase" : "REJECT: Revise implementation"
}
```

---

## Progression Path to Self-Building

### Level 1: Simple Provider Addition (Current)
- Generate provider code from spec
- Generate config files
- Generate tests
- Verify and grade

**Example**: Echo provider (above)

---

### Level 2: Resource Type Extension

```hcl
# experiments/self-build/add-batch-support.aicl

resource "code_generator" "batch_completion" {
  specification = <<-EOT
    Add batch completion support to OpenAI provider:
    
    New Resource Type: llm_batch_completion
    - Input: prompts (list of strings), model, temperature
    - Output: completions (list of responses)
    - Optimization: Use asyncio for parallel requests
  EOT
  
  context_query = "async batch processing patterns in providers"
  output_path = "providers/openai/batch_handler.py"
}
```

---

### Level 3: Core Feature Addition

```hcl
# experiments/self-build/add-caching-layer.aicl

resource "code_generator" "response_cache" {
  specification = <<-EOT
    Add response caching to core engine:
    
    Feature: Cache LLM responses by (model, prompt, params)
    - Storage: Redis or in-memory
    - TTL: Configurable (default 1 hour)
    - Cache key: Hash of inputs
    - Integration: Transparent to providers
  EOT
  
  context_query = "caching patterns in Python, Redis integration"
  output_path = "src/aicl/core/cache.py"
}
```

---

### Level 4: Bug Fix Automation

```hcl
# experiments/self-build/fix-failing-test.aicl

data "test_failure" "detect_issue" {
  provider = provider.command_assertion
  command = "pytest tests/ --tb=short"
}

resource "code_generator" "bug_fix" {
  specification = <<-EOT
    Fix failing test: ${data.test_failure.detect_issue.failed_test}
    
    Error: ${data.test_failure.detect_issue.error_message}
    
    Test code: ${data.test_failure.detect_issue.test_code}
  EOT
  
  context_query = "How to fix: ${data.test_failure.detect_issue.error_type}"
}
```

---

### Level 5: Feature from Natural Language

```hcl
# experiments/self-build/add-streaming-support.aicl

resource "feature_builder" "streaming" {
  specification = <<-EOT
    User Request: "Add streaming support for LLM responses so I can see 
    tokens as they arrive instead of waiting for the full response."
    
    Implementation Requirements:
    - Modify OpenAI provider to use streaming API
    - Add stream=true parameter to llm_completion resource
    - Update response handling to yield tokens
    - Maintain backward compatibility
  EOT
  
  # This will:
  # 1. Break down into subtasks
  # 2. Generate code for each
  # 3. Generate integration tests
  # 4. Run full test suite
  # 5. Grade quality
  # 6. Propose changes
}
```

---

### Level 6: Self-Optimization

```hcl
# experiments/self-build/optimize-performance.aicl

data "profiling_results" "bottlenecks" {
  provider = provider.command_assertion
  command = "python -m cProfile -o profile.stats run.py test.aicl"
}

resource "code_generator" "optimization" {
  specification = <<-EOT
    Optimize bottleneck: ${data.profiling_results.bottlenecks.slowest_function}
    
    Current: ${data.profiling_results.bottlenecks.current_time}ms
    Target: <100ms
    
    Suggestions from profiling:
    ${data.profiling_results.bottlenecks.optimization_hints}
  EOT
  
  context_query = "Python performance optimization patterns"
}
```

---

## Test Variables for Self-Building

### test-self-build.yaml

```yaml
experiment:
  name: Self-Building Experiments
  description: Test AICL's ability to modify itself

# Code generation models
code_generation:
  models:
    - name: "gpt-4o"              # Best quality
      quality_score: 9.5
    - name: "gpt-4o-mini"         # Best value
      quality_score: 8.5
    - name: "openrouter-claude-sonnet"  # Alternative
      quality_score: 9.7

# Judge models (for code evaluation)
judge_models:
  models:
    - name: "gpt-4o"
      reliability_score: 9.0
    - name: "openrouter-claude-sonnet"
      reliability_score: 9.7

# Feature types to add
feature_types:
  - provider              # New provider
  - resource_type         # New resource in existing provider
  - utility_function      # Helper function
  - bug_fix              # Fix failing test
  - optimization         # Performance improvement

# Quality thresholds
quality:
  minimum_score: 80
  test_pass_required: true
  
# Code generation parameters
generation:
  temperature:
    values: [0.0, 0.3, 0.7]
  max_tokens:
    values: [2000, 4000, 8000]
```

---

## Grading Rubric for Generated Code

### Judge Prompt Template

```python
CODE_JUDGE_PROMPT = """
You are an expert code reviewer evaluating AI-generated code.

SPECIFICATION:
{specification}

GENERATED CODE:
{code}

TEST RESULTS:
- Tests Passed: {tests_passed}
- Coverage: {coverage}%
- Exit Code: {exit_code}

Evaluate the code on these criteria (100 points total):

1. CORRECTNESS (40 points)
   - Implements specification fully
   - Tests pass
   - No logical errors
   - Edge cases handled

2. CODE QUALITY (30 points)
   - Follows project patterns
   - Clean and readable
   - Proper error handling
   - Resource management

3. BEST PRACTICES (20 points)
   - Language idioms
   - Design patterns
   - Security considerations
   - Performance awareness

4. MAINTAINABILITY (10 points)
   - Documentation/comments
   - Clear intent
   - Easy to understand
   - Self-documenting

DECISION RULES:
- Score >= 90: ACCEPT (Excellent)
- Score 80-89: ACCEPT (Good)
- Score 70-79: REVISE (Needs improvement)
- Score < 70: REJECT (Inadequate)

Provide evaluation in JSON format:
{
  "overall_score": <0-100>,
  "breakdown": {
    "correctness": <0-40>,
    "code_quality": <0-30>,
    "best_practices": <0-20>,
    "maintainability": <0-10>
  },
  "decision": "ACCEPT | REVISE | REJECT",
  "reasoning": "<detailed explanation>",
  "improvements": ["<suggestion 1>", "<suggestion 2>", ...]
}
"""
```

---

## Safety Mechanisms

### 1. Sandboxed Execution
- Run generated code in isolated environment
- Resource limits (CPU, memory, time)
- No network access during tests

### 2. Human Review Gate
- Auto-apply only for score >= 95
- Score 80-94: Require human approval
- Score < 80: Auto-reject

### 3. Rollback Capability
- Git commit before applying changes
- Automatic rollback if tests fail post-apply
- State snapshots for recovery

### 4. Progressive Trust
- Start with simple, low-risk changes
- Build confidence through successful iterations
- Gradually allow more complex modifications

---

## Metrics and Success Criteria

### Per-Experiment Metrics

```python
class SelfBuildMetrics:
    # Generation
    specification_length: int
    context_retrieved: int
    generation_time_ms: int
    code_lines_generated: int
    
    # Testing
    tests_generated: int
    tests_passed: int
    test_coverage: float
    
    # Quality
    overall_score: float
    decision: str
    human_review_required: bool
    
    # Application
    applied: bool
    rollback_needed: bool
```

### Success Criteria

✅ **Functional**: Tests pass (exit_code == 0)  
✅ **Quality**: Score >= 80  
✅ **Safe**: No security issues detected  
✅ **Maintainable**: Clear, documented code  

---

## Example Workflow

### CLI Commands

```bash
# Generate new provider
aicl self-build add-provider --spec "Echo provider with prefix support"

# Fix failing test
aicl self-build fix-test --test "test_parse_config"

# Optimize performance
aicl self-build optimize --target "src/aicl/core/planner.py"

# Add feature from description
aicl self-build add-feature --spec "Add streaming LLM responses"
```
