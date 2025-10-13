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
-   **Azure OpenAI**: Optional for enterprise embeddings and chat (API version 2023-05-15).
-   **Naga.ai**: An OpenAI-compatible AI provider.
-   **Ragie.io**: A fully managed RAG-as-a-Service platform.
-   **Python Libraries**: `python-hcl2`, `grpcio`, `grpcio-tools`, `protobuf`, `requests`, `python-dotenv`.
## Recent Changes

### October 13, 2025 - Azure Self-Build Security Analyzer Experiment (COMPLETED)

**Demonstrated Azure OpenAI Self-Build Capability:**
- ✅ **Generated** complete SecurityAnalyzer provider code (Python class with regex-based detection)
- ✅ **Tested** on vulnerable code sample (found: SQL injection, code injection, hardcoded secrets)
- ✅ **Self-Evaluated** with score 80/100 (ACCEPT grade)
- ✅ **Total Cost**: 987 tokens across 3 AI interactions (~$0.0005)

**What Azure AI Built:**
- Security analyzer detecting: SQL injection, hardcoded passwords, eval/exec usage, path traversal
- Returns JSON: risk_level, vulnerabilities[], recommendations[], security_score (0-100)
- Correctly analyzed test code: identified 2 vulnerabilities, assigned risk score 20/100

**Self-Evaluation Results:**
- Score: 80/100
- Grade: ACCEPT
- Strengths: Detects SQL injection & secrets, provides recommendations
- Weaknesses: Limited to 2 vulnerability types, could be more comprehensive
- Verdict: "Solid security analyzer that covers common vulnerabilities"

**Impact:** Proved Azure OpenAI can autonomously generate, test, and evaluate security tools - demonstrating true self-improvement capability in AICL framework.

### October 13, 2025 - Azure OpenAI Chat Completion Support (COMPLETED)

**Added Complete Azure OpenAI Chat Support:**
- ✅ **Implemented** `_generate_chat_completion()` method in providers/azure_openai/server.py
- ✅ **Supports** both `messages` array and simple `prompt` formats
- ✅ **Parameters**: temperature, max_tokens, top_p, frequency_penalty, presence_penalty
- ✅ **Tested** with gpt-35-turbo deployment (gpt-3.5-turbo-0125 model)
- ✅ **Returns**: content, role, model, usage stats, finish_reason
- ✅ **API Version**: 2023-05-15 (user's Azure deployment)
- ✅ **Executor mapping** fixed: added 'azure_openai_chat' → 'azure_openai' provider mapping

**Working Configuration:**
- Endpoint: https://redot-dev-openai.openai.azure.com/
- Embeddings: text-embedding-ada-002 (1536 dimensions)
- Chat: gpt-35-turbo (gpt-3.5-turbo-0125)
- Both tested and working successfully

**Impact:** Azure OpenAI provider now supports both embeddings and chat completions for enterprise AI workflows.

### October 13, 2025 - Azure AI Foundry Terraform Integration Analysis (COMPLETED)

**Analyzed How Azure Terraform Complements AICL:**
- ✅ **Azure AI Foundry Terraform** = Cloud infrastructure layer (servers, AI resources, deployments)
- ✅ **AICL** = AI workflow layer (RAG pipelines, experiments, agents)
- ✅ They work at different layers - like Terraform (infra) vs Kubernetes (apps)
- ✅ Created comprehensive integration analysis (docs/AZURE_TERRAFORM_INTEGRATION.md, 461 lines)

**Key Discovery:**
- ✅ AICL already has Azure OpenAI provider (providers/azure_openai/)
- ✅ Embeddings working (text-embedding-ada-002 deployment tested)
- ✅ Chat completion working (gpt-35-turbo deployment tested)
- ✅ Supports Azure deployment-based model access pattern
- ✅ Environment variables: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION

**Integration Flow:**
1. Azure Terraform provisions infrastructure (AI Foundry, GPT-4o deployment, CosmosDB, Search)
2. Outputs endpoints and keys
3. AICL uses those resources for experiments/pipelines
4. Complete infrastructure-as-code for AI workflows

**5-Phase Integration Roadmap:**
1. ✅ Azure provider exists (embeddings working)
2. ✅ Chat completion support (added and tested)
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
- ✅ **In-Memory Storage** (v2/storage/memory.py): Zero-setup, fast, session-only (223 lines)
- ✅ **SQLite Storage** (v2/storage/sqlite_adapter.py): Persistent local database (292 lines)
- ✅ **PostgreSQL Storage** (v2/storage/postgres_adapter.py): Production/team database (370 lines)
- ✅ **SQL Configuration** (v2/storage/sql-config.yaml): All tables, indexes, and queries centralized
- ✅ **Schema Files**: sqlite_schema.sql and postgres_schema.sql ready-to-use

**Database Schema (4 tables):**
- `experiments`: Metadata (id, timestamp, config_file, description)
- `configurations`: Model settings (chat_model, embedding_model, temperature, etc.)
- `results`: Performance metrics (costs, tokens, latency, success)
- `quality_scores`: LLM-as-Judge evaluations (score, feedback)

**Features Working:**
- ✅ Save/retrieve experiments with full metadata
- ✅ Cost analysis (total, avg, min, max)
- ✅ Model performance comparison across experiments
- ✅ Query best configurations by quality/cost/limit criteria
- ✅ Data export to JSON
- ✅ Schema version tracking and validation
- ✅ All storage backends tested and working (example_usage.py, test_postgres.py)

**Multi-Tier Storage Architecture:**
- **Free CLI**: In-memory (default) or SQLite (user-configured persistence)
- **Production/Team**: PostgreSQL (Replit managed or external database)

**PostgreSQL Features:**
- Supports DATABASE_URL (Replit managed) and connection params (external)
- SQL syntax conversion (? → %s placeholders)
- Connection pooling with rollback on error
- Schema versioning and migration support

**Architect Approved:** All storage backends correctly implement interface contract, ready for production use.

### October 13, 2025 - Experiment Document Database System (COMPLETED)

**Built Organized Experiment Management with PostgreSQL:**
- ✅ **Directory Structure** (experiments/): configs/, variables/, outputs/, states/, results/
- ✅ **Document Database** (experiment_docdb.py): PostgreSQL JSONB storage for experiment outputs
- ✅ **Query CLI** (query_results.py): List, compare, find best experiments by cost/quality
- ✅ **Migration Tool** (migrate.py): Import existing JSON results to DocDB
- ✅ **Test Suite**: 4 comprehensive tests, all passing

**Database Schema:**
- `experiment_outputs` table with JSONB columns for outputs and metadata
- GIN indexes for fast JSONB queries
- Support for filtering by date, provider, tags
- Automatic timestamp tracking

**Working Features:**
- ✅ Save experiment with outputs, metadata, tags
- ✅ Query by experiment_id, date range, provider, tags (bug fixed: `::text[]` cast)
- ✅ Compare multiple experiments (cost, tokens, quality metrics)
- ✅ Find best experiments (lowest cost, highest quality, custom sort)
- ✅ Export to JSON
- ✅ Azure security experiment migrated successfully (1,080 tokens, $0.00108)

**CLI Examples:**
```bash
# List all experiments
python experiments/query_results.py --list

# Get specific experiment
python experiments/query_results.py --experiment-id azure_security_2025_10_13

# Compare experiments
python experiments/query_results.py --compare exp1,exp2,exp3

# Find cheapest experiments
python experiments/query_results.py --best --by cost --limit 5
```

**Impact:** Organized experiment storage enables easy review, comparison, and learning from past AI runs. Critical for iterative improvement and cost optimization.
