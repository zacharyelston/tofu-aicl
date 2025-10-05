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
6. **pinecone** - Vector database for RAG
7. **command_assertion** - Validation and testing

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

## Recent Changes (October 5, 2025)

### Core Framework
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
