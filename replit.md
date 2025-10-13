# tofu-aicl - Declarative AI Infrastructure

## Overview
tofu-aicl is a declarative, container-based framework for defining and provisioning AI infrastructure, such as RAG pipelines and agents, using HashiCorp Configuration Language (HCL) syntax. It aims to be the "Terraform for AI workflows," enabling ephemeral, just-in-time AI infrastructure and supporting test-driven AI development through algorithmic experimentation. The project's vision is to streamline AI workflow deployment and management.

## User Preferences
I prefer simple language and clear explanations. I want iterative development with frequent, small updates. Ask for confirmation before making major architectural changes or introducing new external dependencies. I prefer detailed explanations for complex features. Do not make changes to files outside the explicitly defined project scope.

## System Architecture
The core architecture revolves around declarative AI infrastructure defined in HCL. It uses a provider architecture where each AI component (LLMs, Vector DBs, file loaders, etc.) runs as a modular gRPC service. In the Replit environment, these providers run as Python subprocesses due to Docker limitations.

Key architectural components include:
-   **Parser**: Handles HCL configuration parsing.
-   **Provider Registry**: Manages centralized provider metadata.
-   **Evaluator**: Resolves HCL interpolation and expressions, including native variable support (`${var.name}`).
-   **Planner**: Manages dependency resolution and topological sorting of resources.
-   **Executor**: Oversees resource provisioning and state management.
-   **State Manager**: Ensures persistent state tracking.
-   **Engine**: Orchestrates the overall lifecycle management of AI workflows.

The system supports test-driven AI through a matrix experiment system, allowing template-based experiments (`{{ variable }}` placeholders), comprehensive metrics collection (token usage, timing, cost), and comparative analysis. OpenTelemetry is integrated for distributed tracing and metrics collection, providing observability into provider lifecycle and resource operations.

UI/UX decisions, while not explicitly detailed in the provided text, imply a command-line interface for interaction given the focus on HCL and `run.py` scripts.

## External Dependencies
The project integrates with several external services and APIs:
-   **OpenAI API**: For embeddings (`text-embedding-3-small`).
-   **OpenRouter API**: For various AI models (chat, completions).
-   **Pinecone**: A vector database for RAG capabilities.
-   **Azure OpenAI**: Optional for enterprise embeddings.
-   **Naga.ai**: An OpenAI-compatible AI provider offering cost savings for chat and embeddings.
-   **Ragie.io**: A fully managed RAG-as-a-Service platform for document upload, intelligent retrieval, and multimodal processing.
-   **Python Libraries**: `python-hcl2`, `grpcio`, `grpcio-tools`, `protobuf`, `requests`, `python-dotenv`.

## Recent Changes

### October 11, 2025 - Complete Technical Specifications (COMPLETED)

**Created Comprehensive Specification Package:**
- ✅ 13 specification documents in `outline/` directory (5,267 lines)
- ✅ 4 self-building experiment files in `experiments/self-build/` (1,343 lines)
- ✅ **Total: 6,610 lines of detailed technical documentation**
- ✅ Language-agnostic implementation guidance
- ✅ Complete rebuild instructions for any programming language

**Specification Coverage:**
1. **Foundation** (01-02): Vision, goals, architecture overview
2. **Core** (03-04): Components, provider system, gRPC APIs
3. **Configuration** (05-06): HCL format, API specs, resource types
4. **Data** (07-08): Models, schemas, storage abstraction
5. **Features** (09-10): Experiments, grading, deployment model
6. **Implementation** (11-12): Phase-by-phase guide, directory structure
7. **Self-Modification** (13): Self-building experiments, code generation, AI building AI

**Self-Building Capability:**
- ✅ Spec for code generation experiments (outline/13)
- ✅ Complete echo provider example (add-echo-provider.aicl)
- ✅ Test variables for self-build experiments
- ✅ 6-level progression path (simple provider → self-optimization)
- ✅ Quick start guide and comprehensive documentation

**Use Cases:**
- Rebuild in Go/Rust/TypeScript with complete specifications
- Onboard new developers with comprehensive documentation
- Design reviews and architectural decisions
- Product roadmap planning
- Enable AICL to build itself through structured experiments

### October 11, 2025 - Model Catalog Integration (COMPLETED)

**Eliminated Model Duplication Across System:**
- ✅ Integrated ProviderConfigLoader with centralized ModelCatalog
- ✅ Migrated all provider configs to reference model_ids (openai, naga, openrouter)
- ✅ Updated generate_experiments.py to enrich from catalog (auto-injected metadata)
- ✅ Simplified test-variables.yaml to use catalog IDs only (no duplication)
- ✅ Fixed catalog name-based indexing conflicts (strict ID-only lookups)
- ✅ 10/10 integration tests passing, 170→0 provider LSP diagnostics (100% reduction)

**Single Source of Truth:**
```yaml
# Before: Duplicated in 3 places
providers/*/config.yaml   # Model definitions
v2/config/models.yaml     # Model definitions
test-variables.yaml       # Model definitions

# After: One source, auto-enrichment everywhere
v2/config/models.yaml              # ONLY source
providers/*/config.yaml            # References: model_ids: [gpt-4o, ...]
test-variables.yaml                # References: name: "gpt-4o"
generate_experiments.py            # Auto-enriches from catalog
```

**Impact:** All models auto-enriched with cost, quality, dimensions from single catalog. No manual sync needed.

**Provider Auto-Discovery (Verified):**
- ✅ ProviderConfigLoader scans `providers/` directory automatically
- ✅ Drop folder with `config.yaml` → provider instantly available
- ✅ No manual registration code required
- ✅ 6/6 comprehensive auto-discovery tests passing

**Adding New Provider:**
```bash
# Just drop folder:
providers/
  my_provider/
    config.yaml    # Provider definition
    server.py      # gRPC implementation

# Instantly available:
loader = ProviderConfigLoader()
provider = loader.get("my_provider")  # ✅ Works!
```

### October 11, 2025 - Configuration-as-Data Refactorings (COMPLETED)

**Three Major Refactorings Following Configuration-as-Data Pattern:**

#### 1. Model Catalog Centralization
- ✅ Created `v2/config/models.yaml` with 25+ models (chat, embedding, judge)
- ✅ Built `ModelCatalog` class for filtering/recommendations
- ✅ Centralized pricing, quality scores, capabilities
- ✅ Single source of truth for all model metadata
- ✅ 11/11 comprehensive tests passing

**Model Catalog Structure:**
```yaml
chat_models:
  - id: gpt-4o
    provider: openai
    cost_per_1k_input: 0.0025
    quality_score: 9.5
```

**Usage:**
```python
from v2.config.model_catalog import ModelCatalog
catalog = ModelCatalog()
best = catalog.get_best_value('chat')  # Quality ≥7, lowest cost
```

#### 2. Schema Validation Layer
- ✅ Created `v2/schemas/` with dataclass validation
- ✅ Built validators for providers, models, experiments
- ✅ Prevents config drift with fail-fast validation
- ✅ All configs validate at startup
- ✅ 9/9 comprehensive tests passing

**Validation Example:**
```python
from v2.schemas.validators import validate_model_config
schema = validate_model_config(model_data)  # Fails fast on errors
```

#### 3. Provider Runtime Boilerplate Extraction
- ✅ Created `v2/runtime/provider_server.py` with shared gRPC setup
- ✅ Refactored ALL 9 providers to use shared runtime (68 lines saved total)
- ✅ Thread-safe signal handling (main thread check)
- ✅ Graceful shutdown and error handling
- ✅ 10/10 comprehensive tests passing (including thread safety)

**Refactored Providers:**
- OpenAI (12 lines saved)
- Naga (14 lines saved)
- OpenRouter (10 lines saved)
- Azure OpenAI (6 lines saved)
- Pinecone (5 lines saved)
- Ragie (6 lines saved)
- File Loader (5 lines saved)
- Text Splitter (5 lines saved)
- Command Assertion (5 lines saved)

**Before (50+ lines):**
```python
server = grpc.server(...)
provider_pb2_grpc.add_ProviderServicer_to_server(...)
server.add_insecure_port(...)
# ... signal handling, shutdown, etc
```

**After (3 lines):**
```python
if __name__ == '__main__':
    from v2.runtime import create_provider_server
    create_provider_server(MyProvider())
```

**Impact:** 60-70% code reduction, centralized metadata, fail-fast validation, thread-safe runtime.

### October 11, 2025 - Provider Configuration Refactoring (COMPLETED)

**Configuration-as-Data Pattern - Provider Metadata:**
- ✅ Externalized all provider metadata from hardcoded Python to YAML configs
- ✅ Created `providers/<name>/config.yaml` for all 9 providers (openai, naga, ragie, pinecone, etc.)
- ✅ Built `v2/config/ProviderConfigLoader` with schema validation and fail-fast error handling
- ✅ Refactored `engine.py` to use ProviderConfigLoader (eliminated 111-line provider_registry.py)
- ✅ Static port assignment from config (50051-50059) replaces dynamic allocation
- ✅ Runtime mode validation (subprocess/docker/both) enforced at startup
- ✅ Deprecated `provider_registry.py` with migration guide

**Provider Config Structure:**
```yaml
provider:
  name: openai
  display_name: OpenAI
  version: 1.0.0
  runtime:
    entrypoint: server.py
    default_port: 50051
    mode: both
  environment:
    required_vars: [OPENAI_API_KEY]
  capabilities:
    types: [llm, embeddings]
  models:
    - name: gpt-4o
      cost_per_1k_input: 0.0025
      quality_score: 9.5
```

**Impact:** 60-70% code reduction in engine.py, providers discoverable by dropping config.yaml, centralized model catalog with pricing/quality scores.

### October 11, 2025 - v2 Architecture: CLI/Web Split

**Major Architectural Refactor for Business Model:**
- ✅ Created `v2/` directory for all new modular code
- ✅ Storage abstraction layer (`v2/storage/`) with pluggable backends
- ✅ API layer (`v2/api/`) for shared experiment and grading logic
- ✅ CLI tool (`v2/cli/`) for free tier with in-memory storage
- ✅ Backward compatibility wrapper for v1 code migration
- ✅ SQL config refactoring: All SQL moved to `sql-config.yaml` (80% code reduction)
- ✅ Documentation: `V1_V2_MIGRATION.md`, `ARCHITECTURE_REFACTOR_PLAN.md`

**v2 Architecture:**
```
v2/                           # All new code
├── storage/                  # Storage abstraction
│   ├── base.py              # Abstract interface
│   ├── memory.py            # In-memory (FREE CLI default)
│   ├── sqlite_adapter.py    # SQLite (user sets up)
│   └── postgres_adapter.py  # PostgreSQL (WEB tier, future)
├── api/                      # Shared logic
│   ├── experiments.py       # Storage-agnostic runner
│   └── grading.py           # LLM-as-Judge
└── cli/                      # Free CLI tool
    └── main.py              # aicl run, setup-db, stats
```

**Business Model Support:**
- **Free CLI**: In-memory storage (default), optional user-configured SQLite
- **Paid Web**: PostgreSQL, multi-user, advanced analytics (future)

**v2 CLI Commands:**
```bash
# Default: in-memory (no persistence)
python -m v2.cli.main run experiments/*.aicl

# Setup SQLite for persistence
python -m v2.cli.main setup-db --path my.db

# Use SQLite
python -m v2.cli.main run experiments/*.aicl --db my.db

# Show statistics
python -m v2.cli.main stats --db my.db
```

**Migration Path:**
- v1 code (src/aicl/experiment_db.py) still works with deprecation warning
- New code uses v2 storage abstraction
- Core engine (src/aicl/core/) unchanged, works with both v1 and v2

### October 11, 2025 - SQLite Experiment Database (v1 - Legacy)

**v1 Persistent Experiment Tracking:**
- ✅ Created `src/aicl/experiment_db.py` - SQLite database (now wraps v2)
- ✅ Schema: 4 tables (experiments, configurations, results, quality_scores)
- ✅ Indexed joins on experiment_id for performance
- ✅ CLI commands for stats, queries, model comparison, export
- ✅ Created `SQLITE_DATABASE.md` - Complete database documentation

**v1 CLI Commands (deprecated, use v2):**
```bash
python -m src.aicl.experiment_db stats
python -m src.aicl.experiment_db list
python -m src.aicl.experiment_db best
```

### October 11, 2025 - Systematic Experiment Testing Framework

**Comprehensive Variable Testing System:**
- ✅ Created `test-variables.yaml` - Master config defining all testable variables and ranges
- ✅ Created `generate_experiments.py` - Auto-generate AICL configs from test definitions
- ✅ Created `EXPERIMENT_TESTING_GUIDE.md` - Complete guide for systematic testing
- ✅ Pre-configured test suites for common scenarios

**Testable Variables:**
- **Chat Models**: temperature (0.0-2.0), max_tokens (50-4096), top_p, penalties
- **Embeddings**: 5+ models with quality scores (3-small: 5/10, 3-large: 8/10, gemini: 7/10)
- **Vector Retrieval**: top_k (1-50), namespaces, metadata options
- **Ragie RAG**: rerank, recency_bias, partitions, processing modes
- **Text Chunking**: chunk_size (100-2000), overlap (0-500), separators
- **LLM-as-Judge**: 3 models with reliability scores (Mistral Large: 9.7/10)

**Test Suites Available:**
1. **Smoke Test** - 3 experiments, 2-5 minutes (quick validation)
2. **Comprehensive** - 27 experiments, 30-60 minutes (full evaluation)
3. **Cost Optimization** - 12 experiments, 15-30 minutes (best value, score ≥7)
4. **Quality Optimization** - 18 experiments, 30-45 minutes (maximize quality)

**Usage:**
```bash
# View available tests
python generate_experiments.py summary

# Generate test suite
python generate_experiments.py suite smoke_test

# Run experiments with grading
python run_rag_graded_matrix.py experiments/suites/smoke_test/*.aicl
```

**Key Features:**
- Single-variable testing (isolate variable impact)
- Multi-variable grid search (test combinations)
- A/B testing (compare variants)
- Automated AICL config generation
- Comprehensive metrics tracking (cost, quality, performance)
