# Self-Building Quick Start

Get started with AICL's self-modification capability in 5 minutes.

---

## What is Self-Building?

AICL can generate and modify its own source code through structured experiments:
- Add new providers
- Extend existing features
- Fix bugs automatically
- Optimize performance
- Build features from natural language

---

## Run Your First Self-Build Experiment

### 1. Prerequisites

Ensure you have:
```bash
# API keys set
export OPENAI_API_KEY="sk-..."
export PINECONE_API_KEY="..."
export PINECONE_HOST_URL="https://..."

# AICL installed
pip install -r requirements.txt
```

---

### 2. Run the Echo Provider Experiment

This experiment generates a complete provider from scratch:

```bash
# Navigate to project root
cd tofu-aicl

# Run the self-build experiment
python run.py experiments/self-build/add-echo-provider.aicl
```

**What it does:**
1. Queries RAG for provider implementation patterns
2. Generates provider code (`server.py`)
3. Generates provider config (`config.yaml`)
4. Generates comprehensive tests (`test_echo.py`)
5. Evaluates code quality (0-100 score)
6. Provides recommendation (ACCEPT/REJECT)

---

### 3. Review the Output

The experiment outputs:

```json
{
  "generated_files": {
    "server.py": "...provider code...",
    "config.yaml": "...provider config...",
    "test_echo.py": "...test code..."
  },
  "quality_evaluation": {
    "overall_score": 88,
    "breakdown": {
      "correctness": 38,
      "code_quality": 27,
      "best_practices": 16,
      "maintainability": 7
    },
    "decision": "ACCEPT",
    "reasoning": "Well-structured provider..."
  },
  "recommendation": "ACCEPT: Apply changes"
}
```

**Check the quality score:**
- ≥ 90: Excellent quality
- 80-89: Good quality ✅ (Safe to apply)
- 70-79: Needs revision
- < 70: Reject

---

### 4. Apply the Generated Code

If the quality score is ≥ 80:

```bash
# Create provider directory
mkdir -p providers/echo

# Copy the generated code from the output
# (The experiment shows the exact code to copy)

# Example - create each file:
cat > providers/echo/server.py << 'EOF'
# Paste the generated server.py code here
EOF

cat > providers/echo/config.yaml << 'EOF'
# Paste the generated config.yaml code here
EOF

cat > providers/echo/test_echo.py << 'EOF'
# Paste the generated test_echo.py code here
EOF
```

Or use the helper script (if available):
```bash
# Extract and apply generated code
python scripts/apply_self_build.py \
  --output output/add-echo-provider.json \
  --approve
```

---

### 5. Test the New Provider

Run the generated tests:

```bash
# Run tests
pytest providers/echo/test_echo.py -v

# Expected output:
# test_basic_echo PASSED
# test_custom_prefix PASSED
# test_empty_input PASSED
# test_special_characters PASSED
# test_length_tracking PASSED
```

---

### 6. Verify Auto-Discovery

The provider should automatically be discovered:

```bash
# Check provider registry
python -c "from v2.config import ProviderConfigLoader; \
  loader = ProviderConfigLoader(); \
  print(loader.get('echo'))"

# Should output echo provider config
```

---

### 7. Use the New Provider

Create a test configuration:

```hcl
# test-echo.aicl
provider "echo" {}

resource "echo_text" "greeting" {
  provider = provider.echo
  text     = "Hello, World!"
  prefix   = "🔊 "
}

output "result" {
  value = resource.echo_text.greeting.echoed_text
}
```

Run it:
```bash
python run.py test-echo.aicl

# Output:
# result = "🔊 Hello, World!"
```

---

## Next Experiments

### Option 1: Run Test Suite

Compare different models for code generation:

```bash
# Generate experiments from test variables
python generate_experiments.py suite simple_provider

# Run all experiments
ls experiments/suites/simple_provider/*.aicl | \
  xargs -I {} python run.py {}

# Compare results
python compare_self_build_results.py
```

---

### Option 2: Try Different Specifications

Modify the specification in `add-echo-provider.aicl`:

```hcl
resource "llm_completion" "generate_provider" {
  specification = <<-EOT
    Create a Reverse provider that:
    - Accepts text input
    - Returns reversed text
    - Optionally converts to uppercase
    - Resource type: reverse_text
  EOT
}
```

Run again and see different generated code!

---

### Option 3: Advanced - Add Resource Type

Try extending an existing provider:

```hcl
# experiments/self-build/add-batch-to-openai.aicl
resource "code_generator" "batch_completion" {
  specification = <<-EOT
    Add batch_completion resource to OpenAI provider:
    - Input: prompts (list of strings)
    - Output: completions (list of responses)
    - Use asyncio for parallel requests
  EOT
  
  target_provider = "openai"
  output_path = "providers/openai/batch_handler.py"
}
```

---

## Understanding the Results

### Quality Score Breakdown

**Correctness (40 points)**:
- ✅ Implements spec fully
- ✅ Follows provider interface
- ✅ Handles errors properly

**Code Quality (30 points)**:
- ✅ Clean, readable code
- ✅ Proper imports/structure
- ✅ Uses framework patterns

**Best Practices (20 points)**:
- ✅ Python idioms
- ✅ Security considerations
- ✅ Documentation

**Maintainability (10 points)**:
- ✅ Clear intent
- ✅ Good naming
- ✅ Easy to understand

### Decision Guide

| Score Range | Decision | Action |
|-------------|----------|--------|
| 90-100 | ACCEPT (Excellent) | Apply automatically |
| 80-89 | ACCEPT (Good) | Review & apply |
| 70-79 | REVISE | Fix issues & re-run |
| 0-69 | REJECT | New approach needed |

---

## Troubleshooting

### Low Quality Score

**Problem**: Score < 80

**Solutions**:
1. **Improve RAG context**: Add better examples to knowledge base
2. **Adjust model**: Try `gpt-4o` instead of `gpt-4o-mini`
3. **Refine spec**: Be more specific about requirements
4. **Lower temperature**: Use 0.0 for deterministic output

### Tests Fail

**Problem**: Generated tests don't pass

**Solutions**:
1. Check the error message
2. Fix manually or re-run with error context
3. Add test patterns to RAG knowledge base

### Provider Not Discovered

**Problem**: `loader.get('echo')` returns None

**Solutions**:
1. Verify `providers/echo/config.yaml` exists
2. Check YAML syntax is valid
3. Restart Python interpreter
4. Check ProviderConfigLoader scan path

---

## Best Practices

### 1. Start Simple
- Begin with basic providers
- Add complexity gradually
- Learn from each iteration

### 2. Review Before Applying
- Always check quality score
- Read generated code
- Verify test coverage

### 3. Maintain Quality Bar
- Set minimum score threshold
- Reject low-quality code
- Improve prompts over time

### 4. Learn from Results
- Track what works
- Refine specifications
- Build better patterns

---

## What's Next?

### Progression Path

1. ✅ **Simple Provider** (You are here!)
2. 🔄 **Resource Extension** - Add to existing providers
3. 📋 **Utility Functions** - Generate helper code
4. 📋 **Bug Fixes** - Automated test fixing
5. 🎯 **Features from NL** - Natural language to code
6. 🚀 **Self-Optimization** - Performance improvements

See [PROGRESSION.md](PROGRESSION.md) for the complete roadmap.

---

## Summary

You just:
1. ✅ Ran a self-build experiment
2. ✅ Generated a complete provider
3. ✅ Evaluated code quality
4. ✅ Applied the changes
5. ✅ Verified it works

**AICL is now building itself! 🚀**

---

## Additional Resources

- [README.md](README.md) - Complete self-building documentation
- [PROGRESSION.md](PROGRESSION.md) - Roadmap to full self-building
- [outline/13-self-modification-experiments.md](../../outline/13-self-modification-experiments.md) - Technical specification

---

*Remember: The goal isn't just to generate code, but to generate **good** code that follows project patterns and maintains quality standards.*
