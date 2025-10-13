# tofu-aicl

## 🎯 **Real RAG Evaluation Output**

Here's what the system actually produces when you run it:

```
🔍 Testing 1 question(s)
🆔 Test Run ID: 551730223cde
📅 Timestamp: 2025-10-09T10:47:54

📄 Retrieved chunks:
  [1] src/aicl/parser.py (score: 0.404)
  [2] src/aicl/planner.py (score: 0.371)
  [3] src/aicl/evaluator.py (score: 0.347)

✅ Using 3 code chunks + 0 doc chunks

🤖 Claude 3.5 Sonnet...
   ✅ Response: 1247 chars, 9127ms

🤖 GPT-4...
   ✅ Response: 1559 chars, 16370ms

📊 LLM Judge Evaluation:
  claude-3.5-sonnet:
    Accuracy: 8/10
    Completeness: 7/10
    Clarity: 9/10
    Code Specificity: 6/10
    Total: 30/40

  gpt-4:
    Accuracy: 9/10
    Completeness: 8/10
    Clarity: 8/10
    Code Specificity: 9/10
    Total: 34/40

  🏆 Winner: gpt-4
```

---

## Overview

Declarative AI Infrastructure

A declarative, framework for defining and provisioning AI infrastructure (RAG pipelines, agents, etc.) using HCL syntax. Think "Terraform for AI workflows."

**Repository**: https://github.com/zacharyelston/tofu-aicl  
**License**: GPL-3.0

## Core Concepts

- **Declarative AI Infrastructure**: Define AI systems as code using HCL
- **Provider Architecture**: Modular gRPC services for LLMs, Vector DBs, file loaders, etc.
- **Ephemeral & Just-In-Time**: Spin up AI infrastructure on-demand and tear down automatically
- **Matrix Experiments**: Run multiple configurations with performance tracking and comparative analysis

## Quick Start

### 1. Set up API Keys (Replit Secrets)
Configure these secrets in your Replit environment:
- `OPENAI_API_KEY` - For embeddings
- `OPENROUTER_API_KEY` - For LLM access
- `PINECONE_API_KEY` - For vector database
- `PINECONE_HOST_URL` - Pinecone endpoint

### 2. Run a Simple Configuration

```bash
# Basic usage
python run.py config.aicl

# With multiple output destinations
python run.py config.aicl --output-file --output-docdb --output-stdout

# Quiet mode with custom ID and tags
python run.py config.aicl --quiet --experiment-id my-test --tags demo,v1
```

Example config (`config.aicl`):
```hcl
resource "chat" "greeting" {
  provider = "aicl/openrouter"
  config = {
    model = "anthropic/claude-3.5-sonnet"
    messages = [
      {
        role = "user"
        content = "Explain how declarative AI infrastructure works."
      }
    ]
  }
}
```

**CLI Flags Available:**
- `--output-file` - Save to JSON state files (default)
- `--output-docdb` - Save to PostgreSQL database
- `--output-stdout` - Print to console (default)
- `--no-stdout` - Disable console output
- `--quiet` - Minimal output (errors only)
- `--experiment-id ID` - Custom experiment identifier
- `--tags TAGS` - Comma-separated tags (e.g., `rag,demo,v1`)
- `--parallel` - Enable parallel execution (experimental)

See `docs/CLI_USAGE.md` for complete documentation.

### 3. Run Matrix Experiments

Test multiple models and configurations:

```bash
# Run code analysis comparison
python run_code_matrix.py

# View comprehensive performance report
python final_performance_report.py
```

## Matrix Experiment System

Run multiple AICL configurations with different variables and analyze performance:

**Features:**
- Template-based experiments with `{{ variable }}` substitution (lowercase with spaces)
- Comprehensive metrics: tokens, timing, costs, throughput
- Model-specific pricing (Claude, GPT-4, GPT-4o, etc.)
- Centralized state storage and analysis tools

**Example Matrix Template:**
```hcl
resource "chat" "analysis" {
  provider = "aicl/openrouter"
  config = {
    model = "{{ model }}"
    messages = [
      {
        role = "user"
        content = "{{ question }}"
      }
    ]
  }
}
```

Variables are defined in the runner script (e.g., `{"model": "anthropic/claude-3.5-sonnet", "question": "Your question"}`)

**Performance Metrics:**
- Token usage (prompt/completion/total)
- Response time and latency (ms)
- Throughput (tokens/second)
- Cost with model-specific pricing
- Cost source transparency (estimated/actual)

## Available Providers

1. **file_loader** - Load documents from filesystem
2. **text_splitter** - Chunk text for embeddings
3. **openai** - OpenAI embeddings (text-embedding-3-small)
4. **azure_openai** - Azure OpenAI embeddings
5. **openrouter** - AI models via OpenRouter (chat, completions)
6. **pinecone** - Vector database for RAG
7. **command_assertion** - Validation and testing

## RAG Pipeline Example

**Index documents:**
```hcl
resource "file_source" "docs" {
  provider = "aicl/file_loader"
  config = {
    file_paths = ["docs/guide.md", "docs/api.md"]
  }
}

resource "chunks" "split" {
  provider = "aicl/text_splitter"
  config = {
    text = "${resource.file_source.docs.attributes.content}"
    chunk_size = 1000
  }
}

resource "embedding" "vectors" {
  provider = "aicl/openai"
  config = {
    texts = "${resource.chunks.split.attributes.chunks}"
  }
}

resource "vector_store" "indexed" {
  provider = "aicl/pinecone"
  config = {
    operation = "upsert"
    vectors = "${resource.embedding.vectors.attributes.embeddings}"
    namespace = "my-docs"
  }
}
```

**Query with RAG:**
```hcl
resource "embedding" "query_vec" {
  provider = "aicl/openai"
  config = {
    text = "How do I use the API?"
  }
}

resource "search_results" "relevant" {
  provider = "aicl/pinecone"
  config = {
    operation = "query"
    vector = "${resource.embedding.query_vec.attributes.embedding}"
    top_k = 3
    namespace = "my-docs"
  }
}

resource "answer" "response" {
  provider = "aicl/openrouter"
  config = {
    model = "anthropic/claude-3.5-sonnet"
    messages = [
      {
        role = "user"
        content = "Context: ${resource.search_results.relevant.attributes.matches}\n\nQuestion: How do I use the API?"
      }
    ]
  }
}
```

## Architecture

- **Parser** (`parser.py`): HCL configuration parsing
- **Provider Registry** (`provider_registry.py`): Centralized provider metadata
- **Evaluator** (`evaluator.py`): HCL interpolation and expression resolution
- **Planner** (`planner.py`): Dependency resolution and topological sorting
- **Executor** (`executor.py`): Resource provisioning and state management
- **State Manager** (`state/manager.py`): Persistent state tracking
- **Engine** (`core/engine.py`): Orchestration and lifecycle management

## Development Setup (Replit)

The project runs in Replit with providers as Python subprocesses (no Docker needed):

- **Runtime**: Python 3.11
- **Provider Mode**: Subprocess (via `AICL_SUBPROCESS_MODE=true`)
- **Dependencies**: python-hcl2, grpcio, grpcio-tools, protobuf, requests, python-dotenv

## Model Pricing (per 1M tokens)

| Model | Input | Output |
|-------|-------|--------|
| Claude 3.5 Sonnet | $3 | $15 |
| GPT-4 | $30 | $60 |
| GPT-4o | $2.50 | $10 |
| GPT-4o-mini | $0.15 | $0.60 |
| Claude 3 Opus | $15 | $75 |
| Claude 3 Haiku | $0.25 | $1.25 |

## RAG Testing & Evaluation System

### Overview

The RAG testing system evaluates retrieval quality and model performance with **LLM-as-a-Judge** evaluation:

- **Code-Prioritized Retrieval**: Automatically prioritizes `.py` files over documentation
- **Multi-Model Comparison**: Tests Claude 3.5 Sonnet vs GPT-4
- **Automated Evaluation**: Claude judges answers on accuracy, completeness, clarity, and code specificity
- **Comprehensive Reports**: JSON + Markdown outputs with unique run IDs

### Quick Start

**1. Load your codebase into Pinecone:**
```bash
export $(grep -v '^#' .env | xargs)
python scripts/load_codebase_to_pinecone.py
```

**2. Create a questions file (`questions.txt`):**
```
# RAG Test Questions
# One question per line, lines starting with # are ignored

How does the HCL evaluator resolve interpolations?
What is the role of the StateManager?
Explain the parsing flow from HCL input to executable plan.
```

**3. Run RAG evaluation:**
```bash
python scripts/test_rag_query.py questions.txt
```

### Example Output

**Console Output:**
```
🔍 Testing 1 question(s)
🆔 Test Run ID: 551730223cde
📅 Timestamp: 2025-10-09T10:47:54

📄 Retrieved chunks:
  [1] src/aicl/parser.py (score: 0.404)
  [2] src/aicl/planner.py (score: 0.371)
  [3] src/aicl/evaluator.py (score: 0.347)

✅ Using 3 code chunks + 0 doc chunks

🤖 Claude 3.5 Sonnet...
   ✅ Response: 1247 chars, 9127ms

🤖 GPT-4...
   ✅ Response: 1559 chars, 16370ms

📊 LLM Judge Evaluation:
  claude-3.5-sonnet:
    Accuracy: 8/10
    Completeness: 7/10
    Clarity: 9/10
    Code Specificity: 6/10
    Total: 30/40

  gpt-4:
    Accuracy: 9/10
    Completeness: 8/10
    Clarity: 8/10
    Code Specificity: 9/10
    Total: 34/40

  🏆 Winner: gpt-4
```

### Generated Reports

**Markdown Report (`experiments/rag_test_{run_id}.md`):**
```markdown
# RAG Test Report

**Run ID:** `551730223cde`
**Total Questions:** 1

## Summary

| Question | Winner | Claude Score | GPT-4 Score |
|----------|--------|--------------|-------------|
| Q1: Explain the parsing flow... | gpt-4 | 30/40 | 34/40 |

## Question 1

**Question:** Explain the parsing flow from HCL input to executable plan

### Answers

#### claude-3.5-sonnet
- **Response Time:** 9127ms
- **Tokens:** 800

[Full answer with technical details...]

#### gpt-4
- **Response Time:** 16370ms
- **Tokens:** 697

[Full answer with code references...]

### LLM Judge Evaluation

| Model | Accuracy | Completeness | Clarity | Code Specificity | Total |
|-------|----------|--------------|---------|------------------|-------|
| claude-3.5-sonnet | 8/10 | 7/10 | 9/10 | 6/10 | **30/40** |
| gpt-4 | 9/10 | 8/10 | 8/10 | 9/10 | **34/40** |

**Winner:** 🏆 gpt-4
```

**JSON Report (`experiments/rag_test_{run_id}.json`):**
```json
{
  "run_id": "551730223cde",
  "timestamp": "2025-10-09T10:47:54.719091",
  "questions_file": "questions.txt",
  "total_questions": 1,
  "models_tested": ["anthropic/claude-3.5-sonnet", "openai/gpt-4"],
  "questions": [
    {
      "question": "Explain the parsing flow...",
      "context_chunks": 10,
      "code_chunks_used": 3,
      "doc_chunks_used": 0,
      "results": [...],
      "evaluation": {
        "evaluations": [...],
        "winner": "gpt-4",
        "summary": "GPT-4's answer better bridges conceptual explanation with actual implementation..."
      }
    }
  ]
}
```

### Evaluation Criteria

The LLM judge (Claude 3.5 Sonnet) scores each answer on:

1. **Accuracy (0-10)**: Technical correctness based on code context
2. **Completeness (0-10)**: How thoroughly the question is answered
3. **Clarity (0-10)**: Explanation quality and readability
4. **Code Specificity (0-10)**: References to actual files, classes, and methods

**Total Score:** /40 points

### Key Features

- ✅ **Code-First Retrieval**: Prioritizes `.py` files over `.md` files
- ✅ **Unique Run IDs**: Track experiments over time
- ✅ **Dual Output**: JSON (machine-readable) + Markdown (human-readable)
- ✅ **Cost Tracking**: Actual API costs from OpenRouter
- ✅ **Performance Metrics**: Response time, tokens, throughput
- ✅ **Automated Judging**: Unbiased LLM evaluation with detailed reasoning

### Files Indexed

The system indexes these core implementation files:
- `src/aicl/parser.py` - HCL parsing
- `src/aicl/evaluator.py` - Interpolation resolution
- `src/aicl/planner.py` - Dependency graph
- `src/aicl/executor.py` - Resource provisioning
- `src/aicl/core/engine.py` - Orchestration
- `src/aicl/state/manager.py` - State tracking
- `src/aicl/provider_registry.py` - Provider management

## License

GPL-3.0 - See LICENSE file for details.
