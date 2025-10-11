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
