# tofu-aicl - Declarative AI Infrastructure

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
python run.py config.aicl
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

## RAG Testing Scripts

Quick scripts to test RAG functionality:

```bash
# Load codebase into Pinecone
python scripts/load_codebase_to_pinecone.py

# Run RAG query test
python scripts/test_rag_query.py
```

Results are saved to `experiments/rag_test_results.json` with actual OpenRouter costs and performance metrics.

## License

GPL-3.0 - See LICENSE file for details.
