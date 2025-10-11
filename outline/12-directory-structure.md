# Directory Structure Reference

## Complete Project Layout

```
tofu-aicl/
├── README.md
├── LICENSE
├── .gitignore
│
├── docs/                           # Documentation
│   ├── getting-started.md
│   ├── configuration-guide.md
│   ├── provider-development.md
│   └── api-reference.md
│
├── examples/                       # Example AICL configurations
│   ├── hello-world.aicl
│   ├── simple-rag.aicl
│   ├── multi-model-comparison.aicl
│   └── advanced-pipeline.aicl
│
├── src/aicl/                       # Core engine source code
│   ├── __init__.py
│   │
│   ├── core/                       # Core components
│   │   ├── __init__.py
│   │   ├── parser.py              # HCL parser
│   │   ├── evaluator.py           # Expression evaluator
│   │   ├── planner.py             # Dependency planner
│   │   ├── executor.py            # Execution engine
│   │   ├── state_manager.py       # State management
│   │   └── engine.py              # Main orchestrator
│   │
│   ├── cli/                        # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py                # CLI entry point
│   │   ├── commands/
│   │   │   ├── run.py
│   │   │   ├── plan.py
│   │   │   ├── validate.py
│   │   │   └── experiment.py
│   │   └── formatters.py          # Output formatting
│   │
│   └── utils/                      # Shared utilities
│       ├── __init__.py
│       ├── logger.py
│       ├── config.py
│       └── errors.py
│
├── v2/                             # Modular v2 architecture
│   ├── __init__.py
│   │
│   ├── config/                     # Configuration system
│   │   ├── __init__.py
│   │   ├── models.yaml            # Model catalog (SSOT)
│   │   ├── model_catalog.py       # Model catalog class
│   │   ├── provider_loader.py     # Provider config loader
│   │   ├── test_model_catalog.py
│   │   └── test_provider_catalog_integration.py
│   │
│   ├── storage/                    # Storage abstraction
│   │   ├── __init__.py
│   │   ├── base.py                # Abstract interface
│   │   ├── memory.py              # In-memory storage
│   │   ├── sqlite_adapter.py      # SQLite storage
│   │   ├── postgres_adapter.py    # PostgreSQL storage
│   │   └── test_storage.py
│   │
│   ├── api/                        # Shared business logic
│   │   ├── __init__.py
│   │   ├── experiments.py         # Experiment runner
│   │   ├── grading.py             # LLM-as-Judge
│   │   └── analytics.py           # Result analysis
│   │
│   ├── runtime/                    # Provider runtime
│   │   ├── __init__.py
│   │   ├── provider_server.py     # Shared gRPC server
│   │   └── test_provider_server.py
│   │
│   └── schemas/                    # Validation schemas
│       ├── __init__.py
│       ├── validators.py          # Schema validators
│       └── test_validators.py
│
├── providers/                      # Provider implementations
│   ├── openai/
│   │   ├── config.yaml            # Provider metadata
│   │   ├── server.py              # gRPC service
│   │   ├── __init__.py
│   │   └── README.md
│   │
│   ├── naga/
│   │   ├── config.yaml
│   │   ├── server.py
│   │   └── README.md
│   │
│   ├── openrouter/
│   │   ├── config.yaml
│   │   ├── server.py
│   │   └── README.md
│   │
│   ├── pinecone/
│   │   ├── config.yaml
│   │   ├── server.py
│   │   └── README.md
│   │
│   ├── ragie/
│   │   ├── config.yaml
│   │   ├── server.py
│   │   └── README.md
│   │
│   ├── azure_openai/
│   │   ├── config.yaml
│   │   ├── server.py
│   │   └── README.md
│   │
│   ├── file_loader/
│   │   ├── config.yaml
│   │   ├── server.py
│   │   └── README.md
│   │
│   ├── text_splitter/
│   │   ├── config.yaml
│   │   ├── server.py
│   │   └── README.md
│   │
│   └── command_assertion/
│       ├── config.yaml
│       ├── server.py
│       └── README.md
│
├── proto/                          # Protocol Buffer definitions
│   ├── provider.proto             # Provider gRPC service
│   └── Makefile                   # Compile protos
│
├── experiments/                    # Generated experiment configs
│   ├── suites/
│   │   ├── smoke_test/
│   │   ├── comprehensive_test/
│   │   ├── cost_optimization/
│   │   └── quality_optimization/
│   └── results/                   # Experiment results
│
├── tests/                          # Test suite
│   ├── unit/
│   │   ├── test_parser.py
│   │   ├── test_evaluator.py
│   │   ├── test_planner.py
│   │   └── test_executor.py
│   │
│   ├── integration/
│   │   ├── test_end_to_end.py
│   │   ├── test_providers.py
│   │   └── test_experiments.py
│   │
│   ├── fixtures/                  # Test data
│   │   ├── configs/
│   │   ├── states/
│   │   └── responses/
│   │
│   └── conftest.py                # Pytest configuration
│
├── scripts/                        # Utility scripts
│   ├── setup_dev.sh              # Development setup
│   ├── generate_proto.sh         # Compile protocol buffers
│   ├── run_tests.sh              # Run test suite
│   └── release.sh                # Create release
│
├── web/                            # Web application (future)
│   ├── frontend/
│   │   ├── src/
│   │   ├── public/
│   │   └── package.json
│   │
│   └── backend/
│       ├── api/
│       ├── models/
│       └── requirements.txt
│
├── .github/                        # GitHub configuration
│   ├── workflows/
│   │   ├── tests.yml             # CI tests
│   │   ├── release.yml           # Release workflow
│   │   └── docs.yml              # Documentation build
│   │
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
│
├── outline/                        # Project specifications
│   ├── 01-vision-and-goals.md
│   ├── 02-architecture-overview.md
│   ├── 03-core-components.md
│   ├── 04-provider-system.md
│   ├── 05-configuration-format.md
│   ├── 06-api-specifications.md
│   ├── 07-data-models.md
│   ├── 08-storage-layer.md
│   ├── 09-experiment-system.md
│   ├── 10-deployment-model.md
│   ├── 11-implementation-guide.md
│   └── 12-directory-structure.md
│
├── generate_experiments.py         # Experiment generator
├── test-variables.yaml            # Test variable definitions
├── run.py                         # Main CLI entry point
│
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Development dependencies
├── setup.py                       # Package setup
├── pyproject.toml                 # Python project config
│
├── Dockerfile                     # Container image
├── docker-compose.yml             # Local development stack
│
└── .env.example                   # Environment variable template
```

---

## File Purpose Guide

### Root Level

| File | Purpose |
|------|---------|
| `README.md` | Project overview, quick start, installation |
| `LICENSE` | Software license (MIT, Apache, etc) |
| `.gitignore` | Files to exclude from version control |
| `requirements.txt` | Python runtime dependencies |
| `setup.py` | Package installation configuration |
| `pyproject.toml` | Modern Python project metadata |
| `Dockerfile` | Container image definition |
| `run.py` | Main CLI entry point |

---

### src/aicl/ - Core Engine

| Directory | Contains |
|-----------|----------|
| `core/` | Engine components (parser, planner, executor) |
| `cli/` | Command-line interface implementation |
| `utils/` | Shared utilities (logging, config, errors) |

---

### v2/ - Modular Architecture

| Directory | Contains |
|-----------|----------|
| `config/` | Model catalog, provider loader, configs |
| `storage/` | Storage backends (memory, SQLite, PostgreSQL) |
| `api/` | Shared business logic (experiments, grading) |
| `runtime/` | Provider runtime components |
| `schemas/` | Validation schemas |

---

### providers/ - Provider Implementations

Each provider directory contains:
- `config.yaml`: Provider metadata and configuration
- `server.py` (or equivalent): gRPC service implementation
- `README.md`: Provider-specific documentation

---

### experiments/ - Experiment System

| Directory | Contains |
|-----------|----------|
| `suites/` | Pre-configured test suites |
| `results/` | Experiment execution results |

---

### tests/ - Test Suite

| Directory | Contains |
|-----------|----------|
| `unit/` | Unit tests for individual components |
| `integration/` | End-to-end integration tests |
| `fixtures/` | Test data (configs, states, mock responses) |

---

### outline/ - Specifications

Complete technical specification documents for rebuilding the project in any language.

---

## Configuration Files

### .env.example

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Naga.ai
NAGA_API_KEY=...

# OpenRouter
OPENROUTER_API_KEY=...

# Pinecone
PINECONE_API_KEY=...
PINECONE_HOST_URL=https://...

# Ragie.io
RAGIE_API_KEY=...

# Database (optional)
DATABASE_URL=sqlite:///experiments.db
# DATABASE_URL=postgresql://user:pass@host/db

# Observability (optional)
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_EXPORTER_OTLP_HEADERS=...
```

---

### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "tofu-aicl"
version = "1.0.0"
description = "Declarative AI infrastructure framework"
authors = [{name = "Your Name", email = "email@example.com"}]
license = {text = "MIT"}
requires-python = ">=3.11"

dependencies = [
    "python-hcl2>=4.0.0",
    "grpcio>=1.60.0",
    "grpcio-tools>=1.60.0",
    "protobuf>=4.25.0",
    "pyyaml>=6.0",
    "requests>=2.31.0",
    "opentelemetry-api>=1.20.0",
    "opentelemetry-sdk>=1.20.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "mypy>=1.5.0",
]

[project.scripts]
aicl = "src.aicl.cli.main:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

---

## Build Artifacts

### Generated Files (Gitignored)

```
__pycache__/               # Python bytecode
*.pyc
*.pyo
*.pyd

.pytest_cache/             # Pytest cache
.mypy_cache/               # Type checker cache
.coverage                  # Coverage report
htmlcov/                   # Coverage HTML report

dist/                      # Built packages
build/                     # Build artifacts
*.egg-info/                # Package metadata

*.tfstate                  # State files (user data)
*.tfstate.backup
*.tfstate.lock

experiments.db             # SQLite database (user data)
*.log                      # Log files
```
