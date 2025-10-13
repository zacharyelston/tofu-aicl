# TerraMISO - Multi-In Single-Out AI Framework

## Overview
**TerraMISO** extends Terraform and OpenTofu with AI-powered optimization using the **MISO pattern** (Multi-In Single-Out). Multiple LLM providers analyze problems, compete with solutions, and the best answer is selected through LLM-as-Judge evaluation.

**MISO = Multi-In Single-Out**: A reusable competitive optimization pattern where multiple AI providers compete and the optimal solution wins. This framework enables:
- Terraform configuration optimization (Azure, AWS, GCP)
- RAG pipeline evaluation with provider competition
- Self-healing infrastructure
- Cost optimization through multi-provider analysis

The project extends (not competes with) Terraform/OpenTofu, providing a declarative AI infrastructure layer using HCL/AICL syntax. It's designed as a self-constructing tool system that other systems can adopt by including our templates and methods.

## User Preferences
I prefer simple language and clear explanations. I want iterative development with frequent, small updates. Ask for confirmation before making major architectural changes or introducing new external dependencies. I prefer detailed explanations for complex features. Do not make changes to files outside the explicitly defined project scope.

## Recent Updates (October 13, 2025)
**✅ Multiple Output Destinations with CLI Switches**
- Added flexible output configuration via command-line flags
- Supports JSON state files, PostgreSQL DocDB, and stdout independently
- CLI flags: `--output-file`, `--output-docdb`, `--output-stdout`, `--quiet`, `--tags`, `--experiment-id`
- Comprehensive test suite: 20 CLI tests covering all output modes and configurations
- See `docs/CLI_USAGE.md` for complete usage guide

**✅ RAG Pipeline Dimension Mismatch Fixed**
- Resolved Pinecone 1024-dim vs OpenAI 1536-dim embedding issue
- Added `dimensions` parameter support to all embedding resources
- Fixed HCL float-to-int type conversion for OpenAI API compatibility

**✅ Transparent Error Handling**
- Enhanced error logging with full API response details
- System now "fails loudly" instead of masking errors with fallbacks
- Improved debugging with detailed Pinecone and OpenAI error messages

**✅ Test Coverage**
- Added `tests/test_cli.py` with 20 comprehensive tests (all passing)
- Tests cover output flags, DocDB integration, quiet mode, and argparse

## System Architecture
The core architecture revolves around declarative AI infrastructure defined in HCL. It uses a provider architecture where each AI component (LLMs, Vector DBs, file loaders, etc.) runs as a modular gRPC service, implemented as Python subprocesses.

Key architectural components include:
-   **Parser**: Handles HCL configuration parsing.
-   **Provider Registry**: Manages centralized provider metadata.
-   **Evaluator**: Resolves HCL interpolation and expressions.
-   **Planner**: Manages dependency resolution and topological sorting of resources.
-   **Executor**: Oversees resource provisioning and state management.
-   **State Manager**: Ensures persistent state tracking (in-memory, SQLite, PostgreSQL).
-   **Engine**: Orchestrates the overall lifecycle management of AI workflows.

The system supports test-driven AI through a matrix experiment system, allowing template-based experiments, comprehensive metrics collection (token usage, timing, cost), and comparative analysis using LLM-as-Judge evaluations. OpenTelemetry is integrated for distributed tracing and metrics. A centralized `ModelCatalog` manages all model metadata, pricing, and capabilities. Configuration is managed using a "Configuration-as-Data" pattern with schema validation. The architecture includes modular code, storage abstraction with an abstract interface, and a clear split between CLI (free tier with in-memory/SQLite storage) and a future web-based platform (paid tier with PostgreSQL). Experiment results are stored in a PostgreSQL JSONB document database for organized management, querying, and comparison.

## External Dependencies
The project integrates with several external services and APIs:
-   **OpenAI API**: For embeddings and chat.
-   **OpenRouter API**: For various AI models.
-   **Pinecone**: A vector database.
-   **Azure OpenAI**: For enterprise embeddings and chat (API version 2023-05-15).
-   **Naga.ai**: An OpenAI-compatible AI provider.
-   **Ragie.io**: A fully managed RAG-as-a-Service platform.
-   **Python Libraries**: `python-hcl2`, `grpcio`, `grpcio-tools`, `protobuf`, `requests`, `python-dotenv`.