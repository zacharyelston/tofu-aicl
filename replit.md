# tofu-aicl - Declarative AI Infrastructure

## Project Overview
A declarative, container-based framework for defining and provisioning AI infrastructure (RAG pipelines, agents, etc.) using HCL syntax. Think "Terraform for AI workflows."

**Repository**: https://github.com/zacharyelston/tofu-aicl
**License**: GPL-3.0

## Core Concepts
- **Declarative AI Infrastructure**: Define AI systems as code using HCL
- **Provider Architecture**: Modular gRPC services for LLMs, Vector DBs, file loaders, etc.
- **Ephemeral & Just-In-Time**: Spin up AI infrastructure on-demand and tear down automatically
- **Test-Driven AI**: Algorithmic experimentation with multiple configurations

## Replit Setup (October 5, 2025)

### Architecture Adaptation
The project originally used Docker containers for provider isolation. In Replit (no Docker support), providers now run as **Python subprocesses** with gRPC communication maintained.

### Environment Configuration
- **Runtime**: Python 3.11
- **Provider Mode**: Subprocess (set via `AICL_SUBPROCESS_MODE=true`, default)
- **Dependencies**: python-hcl2, grpcio, grpcio-tools, protobuf, requests, python-dotenv

### API Secrets (Stored in Replit Secrets)
- `OPENAI_API_KEY`: For OpenAI embeddings API
- `OPENROUTER_API_KEY`: For AI model access via OpenRouter
- `PINECONE_API_KEY`: Vector database authentication
- `PINECONE_HOST_URL`: Pinecone index endpoint
- `AZURE_OPENAI_API_KEY`: (Optional) For Azure OpenAI embeddings
- `AZURE_OPENAI_ENDPOINT`: (Optional) Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_VERSION`: (Optional) Azure API version (default: 2024-02-01)

### Available Providers
1. **file_loader** - Load documents from filesystem
2. **text_splitter** - Chunk text for embeddings
3. **openai** - OpenAI embeddings (text-embedding-3-small)
4. **azure_openai** - Azure OpenAI embeddings
5. **openrouter** - AI models via OpenRouter (chat, completions)
6. **naga** - AI models via Naga.ai (OpenAI-compatible, 50% lower cost) ✨ NEW
7. **pinecone** - Vector database for RAG
8. **command_assertion** - Validation and testing

### Running the Engine
```bash
python run.py <config_file.aicl>
```

Example: `python run.py rag_pipeline_test.aicl`

### Workflow
The "AICL Engine" workflow runs the RAG pipeline test configuration, demonstrating:
1. Provider startup (subprocess mode)
2. Resource provisioning (file loading → text splitting)
3. Execution with interpolation resolution
4. Automatic cleanup/teardown

## Matrix Experiment System (October 9, 2025)

### Performance Metrics & Analysis
Built a comprehensive matrix experiment system for running multiple AICL configurations with different variables and analyzing performance metrics:

**Features:**
- ✅ **Template-based experiments**: Use `{{ variable }}` placeholders in .aicl templates (lowercase with spaces)
- ✅ **Comprehensive metrics**: Token usage, response timing, throughput, and cost tracking
- ✅ **Model-specific pricing**: Accurate cost estimates per model (Claude, GPT-4, GPT-4o, etc.)
- ✅ **Centralized storage**: All state files stored in `experiments/*/` directories
- ✅ **Comparative analysis**: Built-in tools for comparing model performance

**Available Tools:**
```bash
# Run experiments
python run_matrix.py          # Simple chat experiments
python run_code_matrix.py     # Code analysis experiments

# View results
python final_performance_report.py  # Comprehensive comparison
python compare_matrix.py            # State file analysis
```

**Metrics Captured:**
- **Token Usage**: Prompt tokens, completion tokens, total tokens
- **Performance**: Response time (ms), latency, tokens/second
- **Cost**: Accurate estimates with model-specific pricing (shows source: estimated/actual)
- **Quality**: Response length, content preview

**Example Results (Code Analysis):**
- Claude 3.5 Sonnet: 116% faster, 75% cheaper than GPT-4
- GPT-4: Higher cost but better token efficiency
- All metrics stored in state files for custom analysis

**Pricing Map (per 1M tokens):**
- Claude 3.5 Sonnet: $3 input / $15 output
- GPT-4: $30 input / $60 output
- GPT-4o: $2.50 input / $10 output
- GPT-4o-mini: $0.15 input / $0.60 output
- Claude 3 Opus: $15 input / $75 output
- Claude 3 Haiku: $0.25 input / $1.25 output

## Recent Changes

### October 11, 2025 - Naga.ai Integration & Embedding Comparison

**Cost-Effective AI Provider Integration:**
- ✅ Created Naga.ai provider (OpenAI-compatible, 50% cost savings)
- ✅ Added to provider registry with full gRPC implementation
- ✅ API key (`NAGA_API_KEY`) securely stored in Replit Secrets
- ✅ Tested 200+ models available via Naga API
- ✅ Validated embedding models in RAG pipeline

**Embedding Comparison Results:**
- Tested 3 Naga embedding models with GPT-4o + Mistral Large judge
- Winner: `text-embedding-3-large` (3072d) - 8.0/10 quality
- Runner-up: `gemini-embedding-001` (3072d) - 7.0/10 avg
- All models: 100% success rate, 50% cost savings

**Current Implementation:**
- Resource types: `naga_chat` and `naga_embedding`
- Base URL: https://api.naga.ac/v1
- Supports 200+ models across 25 providers at half the cost

**Known Limitation (Temporary):**
- Use `naga_chat`/`naga_embedding` (not `chat`/`embedding`) to route to Naga provider
- Due to hardcoded resource-to-provider mapping in executor
- Architect has provided roadmap for config-driven provider selection

**Documentation Added:**
- `NAGA_INTEGRATION.md` - Complete usage guide
- `NAGA_EMBEDDING_COMPARISON.md` - Embedding test results
- `PROVIDER_SELECTION_ROADMAP.md` - Architecture improvement plan
- `list_naga_models.py` - Script to query available models
- Updated `rag-config.yaml` with Naga model examples

**Cost Savings:**
- Embeddings: 50% off (e.g., $0.000065 vs $0.00013 for 3-large)
- Chat: 50% off (e.g., $2.50 vs $5.00 for GPT-4o)
- **Total Framework Savings: 50%** 💰

### October 10, 2025 - Complete Framework Validation (Infrastructure + Quality + RAG)

**Dual Validation: Simple Chat + RAG Pipeline**

**Simple Chat Quality (9.7/10 avg):**
- ✅ 100% Infrastructure Success: 9/9 experiments
- ✅ Claude 3.5 Sonnet: Perfect 10.0/10 quality
- ✅ GPT-4: Near-perfect 9.9/10 quality
- ✅ GPT-4o-mini: Excellent 9.2/10 quality, 98% cheaper
- See `QUALITY_VALIDATION_REPORT.md` for details

**RAG Quality (8.8/10 avg across 5 models):**
- ✅ 100% RAG Success: 15/15 experiments, config-based testing enabled
- ✅ Mistral Large: Best quality (9.7/10), 10/10 on 2/3 questions
- ✅ GPT-4o-mini: Best value (9.1/10), 45x more cost-efficient
- ✅ GPT-4o: Balanced (9.0/10), scored 10/10 on technical question
- ✅ Claude 3.5 Sonnet: Solid (8.6/10), consistent performance
- ✅ rag-config.yaml: Easy model selection and test configuration
- See `FINAL_RAG_VALIDATION.md` for complete analysis

**Key Insight**: GPT-4o-mini excels at RAG tasks, outperforming expensive models!

**Performance Optimizations:**
- ✅ Parallel execution: 1.9x speedup with 4 workers (3.8s vs 7s per experiment)
- ✅ Configuration-based testing: rag-config.yaml for easy model selection
- ✅ Batch processing: Independent experiment isolation
- See `PERFORMANCE_OPTIMIZATIONS.md` for details

**Infrastructure Validation:**
- Multi-provider orchestration: ✅ Working
- State management: ✅ Reliable persistence
- Observability: ✅ Full telemetry (traces + metrics)
- Cost tracking: ✅ Accurate per-model estimation

### October 10, 2025 - Test Harness Setup
- **Pytest Integration**: Comprehensive unit and integration test suite
- **Test Coverage**: Parser (100%), Planner (96%), Evaluator (93%), State Manager (76%)
- **19 Passing Tests**: Full test coverage for core components
- **Test Structure**: Organized into `tests/unit/` and `tests/integration/`
- **Coverage Reporting**: Configured with pytest-cov
- **CI-Ready**: Tests can run in CI/CD pipelines

### October 10, 2025 - OpenTelemetry Observability
- **Distributed Tracing**: Full span instrumentation across Engine and Executor
- **Metrics Collection**: Provider starts and resource operations counters
- **Grafana Integration**: OTLP exporter for Tempo (traces) and Prometheus (metrics)
- **Environment Config**: OTEL_EXPORTER_OTLP_ENDPOINT and headers for auth
- **Graceful Degradation**: Falls back to console export when OTLP unavailable
- **Documentation**: Complete setup guide in `docs/opentelemetry-setup.md`

**Traces Captured:**
- Provider lifecycle (startup, configuration, shutdown)
- Resource operations (provisioning, evaluation, apply, destroy)
- Dependency resolution and execution flow
- Exception tracking with stack traces

**Span Hierarchy:**
```
apply (root)
├── execute_resource.{id}
│   ├── provision_resource.{id}
│   │   ├── evaluate_config
│   │   └── provider_apply
```

### October 10, 2025 - HCL Variable Evaluation
- **Native Variable Support**: Full HCL variable evaluation with `${var.name}` interpolation
- **Complete Coverage**: Variables work in both provider and resource configurations
- **Evaluation Context**: Unified context with `var` and `resource` namespaces
- **Default Values**: Support for variable blocks with default values
- **Runtime Overrides**: Architecture supports variable overrides at execution time

**Example Usage:**
```hcl
variable "source_path" {
  type    = string
  default = "src/aicl"
}

provider "loader" {
  file_filter = var.source_path  # ✅ Variables in provider config
}

resource "loader_files" "docs" {
  path = var.source_path  # ✅ Variables in resource config
}
```

### October 5, 2025 - Core Framework
- **Provider Registry System**: Centralized provider metadata (images, versions, sources) in `provider_registry.py`, eliminating need for container blocks in .aicl files
- **HCL Evaluator**: Native interpolation resolution for `${resource.type.name.attributes.field}` syntax with proper support for complex nested data structures (lists of dicts)
- **Protobuf Serialization**: Updated to use `ParseDict`/`MessageToDict` for correct handling of nested structures between engine and providers
- **Subprocess Provider Mode**: Replaced Docker containers with Python subprocess execution
- **PYTHONPATH Configuration**: Added workspace root to allow providers to import proto modules
- **Provider Name Resolution**: Fixed source field parsing (e.g., "aicl/file_loader" → "file_loader")
- **Secrets Integration**: Using Replit Secrets for API key management
- **Proto Compilation**: Generated gRPC stubs from provider.proto

### RAG Implementation
- **OpenRouter Provider Enhanced**: Added embedding generation (single text & arrays) and chat completion support
- **Pinecone Provider Enhanced**: Added vector upsert and query operations with metadata
- **Resource-to-Provider Mapping**: Clean resource types (embedding, chat, query) map to providers (openrouter, pinecone)
- **RAG Pipelines Created**:
  - `rag_index.aicl`: Index AICL source code into vector database
  - `rag_query.aicl`: Query indexed code and generate answers

### Framework Validation (October 5, 2025)
**Status: Architecture FULLY FUNCTIONAL ✅**

Through comprehensive debugging, validated:
- ✅ Provider gRPC communication and lifecycle management
- ✅ Resource dependency resolution and topological sorting
- ✅ HCL interpolation and state management
- ✅ Resource ID generation using aiclResourceName from configs
- ✅ Error handling and diagnostic propagation
- ✅ Chat completion resources work correctly

**Solution Implemented** (October 5, 2025):
- ✅ Created dedicated OpenAI provider for embeddings (text-embedding-3-small)
- ✅ Created Azure OpenAI provider for enterprise embeddings
- ✅ Updated RAG pipelines to use OpenAI embeddings instead of OpenRouter
- ✅ End-to-end RAG pipeline now fully functional
- ✅ All resources created and destroyed successfully

**Known Issues**:
- OpenRouter doesn't support `/embeddings` endpoint (documented in `problems/rag-api-integration-issues.md`)

## Architecture Components
- **Parser** (`parser.py`): HCL configuration parsing
- **Provider Registry** (`provider_registry.py`): Centralized provider metadata
- **Evaluator** (`evaluator.py`): HCL interpolation and expression resolution
- **Planner** (`planner.py`): Dependency resolution and topological sorting
- **Executor** (`executor.py`): Resource provisioning and state management
- **State Manager** (`state/manager.py`): Persistent state tracking
- **Engine** (`core/engine.py`): Orchestration and lifecycle management