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