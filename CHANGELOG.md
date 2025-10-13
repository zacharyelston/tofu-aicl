# Changelog - TerraMISO

All notable changes to TerraMISO (formerly tofu-aicl) will be documented in this file.

**Rebranding Note** (October 13, 2025): Project renamed from tofu-aicl to **TerraMISO**
- **TerraMISO** = Terraform/OpenTofu extension with **MISO** pattern (Multi-In Single-Out)
- **MISO** = Multiple AI providers compete → Best solution selected → Single optimal output
- Extends (not competes with) Terraform/OpenTofu
- Self-constructing tool system that other systems can adopt

## [0.2.0] - 2025-10-13

### Added - CLI Output System
- **Multiple Output Destinations**: Independent control of JSON files, PostgreSQL DocDB, and stdout
- **CLI Flags**: `--output-file`, `--output-docdb`, `--output-stdout`, `--no-stdout`, `--quiet`
- **Experiment Tagging**: `--experiment-id` and `--tags` for categorization
- **PostgreSQL DocDB**: JSONB-based experiment storage with full-text search
- **Comprehensive Tests**: 20 CLI tests covering all output modes (100% pass rate)
- **Documentation**: Complete CLI usage guide in `docs/CLI_USAGE.md`

### Enhanced
- **Error Handling**: System now "fails loudly" with detailed API error messages
- **RAG Pipeline**: Fixed Pinecone dimension mismatch (1024 vs 1536)
- **Type Safety**: Fixed HCL float-to-int conversion for OpenAI API

### Fixed
- Pinecone embedding dimensions (1024) vs OpenAI default (1536)
- HCL parser float-to-int type coercion for API compatibility
- Transparent error propagation (no more silent failures)

### Documentation
- Added `docs/SETUP.md` - Complete installation and setup guide
- Added `docs/CLI_USAGE.md` - CLI flag reference and examples
- Updated `README.md` - Quick start with CLI examples
- Updated `tests/README.md` - CLI test coverage documentation

### Dependencies
- Added `psycopg2-binary>=2.9.0` for PostgreSQL DocDB support
- All core dependencies remain compatible with Python 3.11+

### Testing
- **New**: `tests/test_cli.py` - 20 comprehensive CLI tests
- **Coverage**: CLI argument parsing, output methods, DocDB integration
- **Total Test Suite**: 40+ tests across unit, integration, and feature layers

## [0.1.0] - 2025-10-09

### Added - Initial Release
- **Core Engine**: HCL-based declarative AI infrastructure
- **Provider Architecture**: gRPC-based modular providers
- **State Management**: JSON and SQLite persistence
- **RAG Pipeline**: Full RAG implementation with vector database
- **Matrix Experiments**: Template-based multi-configuration testing
- **OpenTelemetry**: Distributed tracing and metrics
- **Multi-Provider Support**: OpenAI, OpenRouter, Pinecone, Azure, Naga, Ragie

### Providers
- OpenAI (embeddings, chat)
- OpenRouter (multi-LLM access)
- Pinecone (vector database)
- Azure OpenAI (enterprise)
- Naga.ai (cost-effective alternative)
- Ragie.io (managed RAG)
- File Loader (document ingestion)
- Text Splitter (chunking)

### Features
- HCL configuration parsing
- Dependency resolution and topological sorting
- Resource state tracking
- Variable interpolation
- LLM-as-Judge evaluation
- Docker and subprocess provider modes
- Experiment comparison and analysis

### Documentation
- Quick Start guide
- Architecture overview
- Experiment builder guide
- Integration guides for all providers

---

## Version Compatibility

### Python Requirements
- **Minimum**: Python 3.11
- **Recommended**: Python 3.11.13
- **Tested**: Python 3.11.x

### Core Dependencies
| Package | Minimum Version | Purpose |
|---------|----------------|---------|
| python-hcl2 | 4.0.0 | HCL parsing |
| grpcio | 1.39.0 | Provider communication |
| protobuf | 3.19.0 | Message serialization |
| psycopg2-binary | 2.9.0 | PostgreSQL support |
| opentelemetry-api | 1.37.0 | Observability |
| pytest | 8.4.2 | Testing framework |

### Optional Dependencies
| Package | Purpose | Required For |
|---------|---------|--------------|
| docker | Container mode | Docker-based providers |
| psycopg2-binary | PostgreSQL | `--output-docdb` flag |

### Breaking Changes
None in this release. All previous configurations remain compatible.

### Migration Guide

#### From 0.1.0 to 0.2.0
No migration needed! The new CLI flags are optional:

```bash
# Old way (still works)
python run.py config.aicl

# New way (with options)
python run.py config.aicl --output-docdb --tags demo,v1
```

All existing `.aicl` configurations work without modification.

---

## Roadmap

### Planned Features
- **Parallel Execution** (`--parallel` flag) - Execute independent resources concurrently
- **Web UI** - Visual experiment builder and result viewer
- **More Providers** - Anthropic, Cohere, HuggingFace
- **Advanced RAG** - Hybrid search, reranking, query expansion
- **Self-Improvement** - Framework uses RAG on its own code for maintenance

### Under Consideration
- GraphQL API for experiment querying
- Real-time experiment streaming
- Multi-tenant experiment isolation
- Experiment versioning and rollback
