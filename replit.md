# tofu-aicl - Declarative AI Infrastructure

## Overview
tofu-aicl is a declarative, container-based framework for defining and provisioning AI infrastructure, such as RAG pipelines and agents, using HashiCorp Configuration Language (HCL) syntax. It aims to be the "Terraform for AI workflows," enabling ephemeral, just-in-time AI infrastructure and supporting test-driven AI development through algorithmic experimentation. The project's vision is to streamline AI workflow deployment and management, allowing for self-modification and objective comparison of AI provider quality and cost.

## User Preferences
I prefer simple language and clear explanations. I want iterative development with frequent, small updates. Ask for confirmation before making major architectural changes or introducing new external dependencies. I prefer detailed explanations for complex features. Do not make changes to files outside the explicitly defined project scope.

## System Architecture
The core architecture revolves around declarative AI infrastructure defined in HCL. It uses a provider architecture where each AI component (LLMs, Vector DBs, file loaders, etc.) runs as a modular gRPC service, implemented as Python subprocesses in the Replit environment.

Key architectural components include:
-   **Parser**: Handles HCL configuration parsing.
-   **Provider Registry**: Manages centralized provider metadata through YAML configurations.
-   **Evaluator**: Resolves HCL interpolation and expressions.
-   **Planner**: Manages dependency resolution and topological sorting of resources.
-   **Executor**: Oversees resource provisioning and state management.
-   **State Manager**: Ensures persistent state tracking (supports in-memory, SQLite, and future PostgreSQL).
-   **Engine**: Orchestrates the overall lifecycle management of AI workflows.

The system supports test-driven AI through a matrix experiment system, allowing template-based experiments, comprehensive metrics collection (token usage, timing, cost), and comparative analysis using LLM-as-Judge evaluations. OpenTelemetry is integrated for distributed tracing and metrics. A centralized `ModelCatalog` manages all model metadata, pricing, and capabilities. Configuration is managed using a "Configuration-as-Data" pattern with schema validation. The architecture includes a `v2/` directory for modular code, storage abstraction, and a clear split between CLI (free tier with in-memory/SQLite storage) and a future web-based platform (paid tier with PostgreSQL).

## External Dependencies
The project integrates with several external services and APIs:
-   **OpenAI API**: For embeddings and chat.
-   **OpenRouter API**: For various AI models.
-   **Pinecone**: A vector database.
-   **Azure OpenAI**: Optional for enterprise embeddings.
-   **Naga.ai**: An OpenAI-compatible AI provider.
-   **Ragie.io**: A fully managed RAG-as-a-Service platform.
-   **Python Libraries**: `python-hcl2`, `grpcio`, `grpcio-tools`, `protobuf`, `requests`, `python-dotenv`.
## Recent Changes

### October 13, 2025 - Azure AI Foundry Terraform Integration Analysis (COMPLETED)

**Analyzed How Azure Terraform Complements AICL:**
- ✅ **Azure AI Foundry Terraform** = Cloud infrastructure layer (servers, AI resources, deployments)
- ✅ **AICL** = AI workflow layer (RAG pipelines, experiments, agents)
- ✅ They work at different layers - like Terraform (infra) vs Kubernetes (apps)
- ✅ Created comprehensive integration analysis (docs/AZURE_TERRAFORM_INTEGRATION.md, 461 lines)

**Key Discovery:**
- ✅ AICL already has Azure OpenAI provider (providers/azure_openai/)
- ✅ Embeddings working, chat completion needs implementation
- ✅ Supports Azure deployment-based model access pattern
- ✅ Environment variables: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT

**Integration Flow:**
1. Azure Terraform provisions infrastructure (AI Foundry, GPT-4o deployment, CosmosDB, Search)
2. Outputs endpoints and keys
3. AICL uses those resources for experiments/pipelines
4. Complete infrastructure-as-code for AI workflows

**5-Phase Integration Roadmap:**
1. ✅ Azure provider exists (embeddings working)
2. ⏳ Add chat completion support
3. ⏳ Terraform output integration (vars-file detection)
4. ⏳ Unified state management
5. ⏳ Enterprise features (managed identity, private networking)

**Impact:** Clear path for enterprise adoption using Azure-provisioned infrastructure with AICL workflows.

### October 13, 2025 - Minimal Spartan Version (COMPLETED)

**Created versions/minimal/ - Learning-Focused Distribution:**
- ✅ **~820 lines total** (92% reduction from 10,000+ line full version)
- ✅ Removed complex Executor → direct provider calls
- ✅ Replaced StateManager → SimpleState (12 lines)
- ✅ Single provider (Naga) instead of 9
- ✅ No OpenTelemetry, no database - just core essentials
- ✅ Created comprehensive README.md, ARCHITECTURE.md, EXAMPLES.md

**Two Working Experiments:**
1. **self-build.aicl** - AI generates its own provider code (Quality: 85/100)
2. **matrix-test.aicl** - Compare model variations (Winner: Response B, 88/100)

**Impact:** Anyone can now understand AICL's core concepts in ~30 minutes. Perfect for learning, prototyping, or building custom versions.

### October 13, 2025 - V2 Storage Layer Complete (COMPLETED)

**Built Complete Storage Abstraction for SQL Experiments:**
- ✅ **Abstract Interface** (v2/storage/base.py): ExperimentStorage with save/retrieve/analyze methods
- ✅ **In-Memory Storage** (v2/storage/memory.py): Zero-setup, fast, session-only (free CLI default)
- ✅ **SQLite Storage** (v2/storage/sqlite_adapter.py): Persistent local database with schema versioning
- ✅ **SQL Configuration** (v2/storage/sql-config.yaml): All tables, indexes, and queries centralized
- ✅ **SQL Schema File** (v2/schemas/sqlite_schema.sql): Ready-to-use database initialization

**Database Schema (4 tables):**
- `experiments`: Metadata (id, timestamp, config_file, description)
- `configurations`: Model settings (chat_model, embedding_model, temperature, etc.)
- `results`: Performance metrics (costs, tokens, latency, success)
- `quality_scores`: LLM-as-Judge evaluations (score, feedback)

**Features Working:**
- ✅ Save/retrieve experiments with full metadata
- ✅ Cost analysis (total, avg, min, max)
- ✅ Model performance comparison across experiments
- ✅ Query best configurations by quality/cost criteria
- ✅ Data export to JSON
- ✅ Schema version tracking and validation
- ✅ Example usage demonstrated (v2/storage/example_usage.py)

**Dual-Tier Architecture:**
- **Free CLI**: In-memory (default) or SQLite (user-configured)
- **Paid Web** (future): PostgreSQL with multi-user support

**Architect Approved:** Storage layer meets functional objectives, ready for SQL-based experiments.
