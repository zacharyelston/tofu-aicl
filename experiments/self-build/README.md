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

## 🎯 Modular Architecture (v2)

**All experiments refactored to use external prompt files!**

### Structure
```
experiments/self-build/
├── prompts/                    # ✅ 15 modular prompt files
│   ├── echo-*.txt             # Echo provider prompts
│   ├── anthropic-*.txt        # Anthropic provider prompts
│   ├── replit-*.txt           # Replit provider prompts
│   └── quality-judge*.txt     # Quality evaluation prompts
│
├── add-echo-provider-v2.aicl        # ✅ Refactored (uses prompts/)
├── add-anthropic-provider-v2.aicl   # ✅ Refactored (uses prompts/)
├── add-replit-provider-v2.aicl      # ✅ Refactored (uses prompts/)
│
├── add-echo-provider.aicl           # ⚠️  Deprecated (inline)
├── add-anthropic-provider.aicl      # ⚠️  Deprecated (inline)
└── add-replit-provider.aicl         # ⚠️  Deprecated (inline)
```

### Benefits

**Before (Inline)**:
- 100+ lines of prompt text embedded in AICL files
- Hard to edit, poor version control diffs
- Duplicated prompts across experiments

**After (Modular)**:
- ✅ Clean separation: code vs prompts
- ✅ Edit prompts in plain text (no AICL syntax)
- ✅ Reusable prompts across experiments
- ✅ Version control friendly
- ✅ Template placeholders (`{variable}`)

---

## Available Challenges

### ⚠️ Echo Provider (Level 1 - Deprecated)
**File**: `add-echo-provider.aicl`, `add-echo-provider-v2.aicl`  
**Complexity**: Low (150 lines)  
**Status**: Reference implementation

### 🔥 Anthropic Provider (Level 5 - Production)
**File**: `add-anthropic-provider-v2.aicl`  
**Complexity**: High (~800 lines)  
**Features**: 3 models, streaming, circuit breaker, cost tracking  
**Prompts**: `prompts/anthropic-*.txt` (4 files)

### 🚀 Replit Provider (Level 6 - Ultimate)
**File**: `add-replit-provider-v2.aicl`  
**Complexity**: Very High (~1000+ lines)  
**Features**: 3 resource types, GraphQL, deployments, databases, agents  
**Prompts**: `prompts/replit-*.txt` (7 files)

---

## Quick Start

### 1. Edit a Prompt

```bash
# Edit prompts directly - no AICL syntax needed!
nano experiments/self-build/prompts/echo-provider-spec.txt
```

### 2. Run an Experiment

```bash
# Use v2 (modular) experiments
python run.py experiments/self-build/add-echo-provider-v2.aicl
python run.py experiments/self-build/add-anthropic-provider-v2.aicl
python run.py experiments/self-build/add-replit-provider-v2.aicl
```

### 3. Review Results

Check the output for:
- Generated code quality score (0-100)
- File contents (provider, config, tests)
- Recommendations for next steps

---

## Prompt Template System

### Placeholders

Prompts support dynamic placeholders:

```text
REFERENCE PATTERNS:
{rag_context}

PROVIDER CODE:
{provider_code}
```

### Loading Prompts

```hcl
# Load all prompts from directory
resource "loader_files" "prompts" {
  path = "./experiments/self-build/prompts"
  glob = "*.txt"
}

# Use prompt with placeholder substitution
resource "chat" "generate" {
  messages = [{
    content = replace(
      "${lookup(resource.loader_files.prompts.attributes.files, "spec.txt", "")}",
      "{rag_context}",
      "${resource.query.patterns.attributes.results}"
    )
  }]
}
```

---

## Prompt Files Reference

### Echo Provider
- `echo-provider-spec.txt` - Main implementation prompt
- `echo-config-spec.txt` - Config generation
- `echo-tests-spec.txt` - Test generation
- `quality-judge.txt` - Quality evaluation

### Anthropic Provider
- `anthropic-provider-spec.txt` - Main implementation (streaming)
- `anthropic-config-spec.txt` - Config with 3 models
- `anthropic-streaming-spec.txt` - Async streaming handler
- `anthropic-tests-spec.txt` - 5 test files

### Replit Provider
- `replit-spec.txt` - 3 resource types specification
- `replit-provider-spec.txt` - Main provider implementation
- `replit-config-spec.txt` - Provider config
- `replit-api-client-spec.txt` - GraphQL API client
- `replit-tests-spec.txt` - 6 test files
- `replit-example-spec.txt` - Usage example
- `quality-judge-complex.txt` - Complex quality evaluation

---

## Progression Path

### Level 1: Simple Provider (✅ Implemented)
**Capability**: Add basic provider from specification

**Status**: v2 refactored with modular prompts

---

### Level 2: Resource Extension (📋 Planned)
**Capability**: Add resource types to existing providers

**Example**: Batch completion for OpenAI

---

### Level 3: Utility Functions (📋 Planned)
**Capability**: Add helper functions and utilities

**Example**: Retry decorator with exponential backoff

---

### Level 4: Bug Fixes (📋 Planned)
**Capability**: Automatically fix failing tests

**Example**: Detect and fix test failures

---

### Level 5: Features from NL (🎯 Goal)
**Capability**: Build complete features from natural language

**Example**: "Add streaming LLM responses"

---

### Level 6: Self-Optimization (🚀 Future)
**Capability**: Optimize its own performance

**Example**: Profile and fix bottlenecks

---

## Current Status

### ✅ Completed
- Modular prompt system (15 files)
- 3 refactored experiments (echo, anthropic, replit)
- External file loading via `loader_files`
- Template placeholder system
- Quality judging framework

### 🔧 Known Issues
- Provider routing needs fixes for generic "chat" resources
- RAG index exists but may need population
- Experiments need integration testing with actual execution

### 📋 Next Steps
1. Fix provider routing in engine
2. Test end-to-end code generation
3. Validate generated code quality
4. Implement apply mechanism

---

## Architecture

### Self-Building Pipeline
```
Specification → RAG Context → Code Generation → Testing → Quality Judge → Apply/Reject
```

### Quality Grading (100 points)
- **Correctness (40)**: Implements spec, tests pass
- **Code Quality (30)**: Clean, follows patterns
- **Best Practices (20)**: Idioms, security
- **Maintainability (10)**: Documentation, clarity

---

## Contributing

### Adding New Prompts
1. Create `.txt` file in `prompts/`
2. Use `{placeholder}` for dynamic content
3. Reference in experiment with `lookup(...)`

### Adding New Experiments
1. Create `-v2.aicl` file
2. Load prompts with `loader_files`
3. Use `replace()` for placeholder substitution
4. Test with small example first

---

*These files represent the foundation for AICL's self-building capability - enabling AI systems that improve themselves.*
