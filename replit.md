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
- `OPENROUTER_API_KEY`: For AI model access via OpenRouter
- `PINECONE_API_KEY`: Vector database authentication
- `PINECONE_HOST_URL`: Pinecone index endpoint

### Available Providers
1. **file_loader** - Load documents from filesystem
2. **text_splitter** - Chunk text for embeddings
3. **openrouter** - Access AI models (Claude, GPT-4, etc.)
4. **pinecone** - Vector database for RAG
5. **command_assertion** - Validation and testing

### Running the Engine
```bash
python run.py <config_file.aicl>
```

Example: `python run.py test_simple.aicl`

### Workflow
The "AICL Engine" workflow runs the test configuration, demonstrating:
1. Provider startup (subprocess mode)
2. Resource provisioning
3. Execution
4. Automatic cleanup/teardown

## Recent Changes
- **Subprocess Provider Mode**: Replaced Docker containers with Python subprocess execution
- **PYTHONPATH Configuration**: Added workspace root to allow providers to import proto modules
- **Provider Name Resolution**: Fixed source field parsing (e.g., "aicl/file_loader" → "file_loader")
- **Secrets Integration**: Using Replit Secrets for API key management
- **Proto Compilation**: Generated gRPC stubs from provider.proto
