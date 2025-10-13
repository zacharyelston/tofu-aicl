# AICL Setup Guide

## Prerequisites

- **Python**: 3.11 or higher
- **PostgreSQL**: Optional, only needed for `--output-docdb` feature
- **API Keys**: See API Keys section below

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/zacharyelston/tofu-aicl.git
cd tofu-aicl
```

### 2. Install Dependencies

**Option A: Using pip (Recommended)**
```bash
pip install -r requirements.txt
# or using pyproject.toml
pip install -e .
```

**Option B: Replit Environment**
Dependencies are automatically managed. Just ensure these secrets are configured:
- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_HOST_URL`
- `DATABASE_URL` (if using `--output-docdb`)

### 3. Core Dependencies

```bash
# Required
python-hcl2>=4.0.0         # HCL configuration parsing
grpcio>=1.39.0             # Provider communication
grpcio-tools>=1.39.0       # Proto compilation
protobuf>=3.19.0           # Message serialization
python-dotenv>=1.1.1       # Environment variables
requests>=2.32.5           # HTTP client

# Optional (for advanced features)
psycopg2-binary>=2.9.0     # PostgreSQL DocDB (--output-docdb)
docker>=5.0.0              # Docker provider mode

# Observability
opentelemetry-api>=1.37.0
opentelemetry-sdk>=1.37.0
opentelemetry-exporter-otlp>=1.37.0

# Testing
pytest>=8.4.2
pytest-cov>=7.0.0
pytest-asyncio>=1.2.0
```

## API Keys

### Required for RAG Demo

Set these as environment variables or Replit Secrets:

```bash
export OPENAI_API_KEY='sk-...'          # OpenAI embeddings & chat
export OPENROUTER_API_KEY='sk-...'     # Multi-LLM access
export PINECONE_API_KEY='...'           # Vector database
export PINECONE_HOST_URL='https://...'  # Pinecone endpoint
```

### Optional for DocDB Output

```bash
export DATABASE_URL='postgresql://user:pass@host:5432/dbname'
```

### Provider-Specific Keys

```bash
export AZURE_OPENAI_API_KEY='...'      # Azure OpenAI (optional)
export AZURE_OPENAI_ENDPOINT='...'     # Azure endpoint (optional)
export NAGA_API_KEY='...'              # Naga.ai (optional)
export RAGIE_API_KEY='...'             # Ragie.io RAG (optional)
```

## Minimal Setup (Learning/Testing)

For minimal learning environment:

```bash
cd versions/minimal
pip install python-hcl2 grpcio grpcio-tools protobuf requests python-dotenv
export NAGA_API_KEY='your-key'  # Get from https://naga.ac
python run.py self-build
```

## PostgreSQL DocDB Setup (Optional)

Only needed if using `--output-docdb` flag:

### Local PostgreSQL

```bash
# Install PostgreSQL
brew install postgresql  # macOS
sudo apt install postgresql  # Ubuntu

# Create database
createdb aicl_experiments

# Set connection
export DATABASE_URL='postgresql://localhost/aicl_experiments'
```

### Replit PostgreSQL

PostgreSQL is available by default in Replit:
```bash
# DATABASE_URL is automatically set
python run.py config.aicl --output-docdb
```

### Schema Auto-Creation

The schema is created automatically on first use:
- `experiment_outputs` table with JSONB columns
- Indexes on `experiment_id`, `run_timestamp`, and `metadata`

## CLI Usage

### Basic Commands

```bash
# Run with default outputs (file + stdout)
python run.py experiments/rag-demo/rag-demo-live.aicl

# Save to PostgreSQL with tags
python run.py experiments/rag-demo/rag-demo-live.aicl \
  --output-docdb \
  --experiment-id rag-v1 \
  --tags rag,pinecone,gpt4

# Quiet mode (errors only)
python run.py config.aicl --quiet
```

### Output Destinations

| Flag | Default | Description |
|------|---------|-------------|
| `--output-file` | ✅ | JSON state files in `terraform.tfstate.d/` |
| `--output-docdb` | ❌ | PostgreSQL JSONB storage |
| `--output-stdout` | ✅ | Console output |
| `--no-stdout` | - | Disable console output |

### Experiment Configuration

| Flag | Description |
|------|-------------|
| `--experiment-id ID` | Custom experiment identifier |
| `--tags TAG,TAG,...` | Comma-separated tags for categorization |
| `--quiet` / `-q` | Minimal output (errors only) |

### Experimental Features

| Flag | Status | Description |
|------|--------|-------------|
| `--parallel` | 🚧 Planned | Parallel resource execution |

### Help

```bash
python run.py --help
```

## Verification

### Test Installation

```bash
# Run unit tests
pytest tests/unit/

# Run CLI tests
pytest tests/test_cli.py -v

# Run with coverage
pytest --cov=src/aicl --cov-report=html
```

### Test RAG Pipeline

```bash
# Ensure all API keys are set
python run.py experiments/rag-demo/rag-demo-live.aicl

# Expected: 12 resources provisioned
# - File loading
# - Embeddings
# - Vector storage
# - RAG queries
# - Multi-LLM responses
# - Judge evaluation
```

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'proto'`

**Solution**:
```bash
# Ensure proto files are compiled
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  proto/provider.proto
```

### Provider Startup Failures

**Problem**: Provider won't start or connection refused

**Solution**:
1. Check provider config: `cat v2/config/providers/*.yaml`
2. Verify ports aren't in use: `lsof -i:50051`
3. Check logs for errors
4. Ensure API keys are set

### DocDB Connection Errors

**Problem**: `DATABASE_URL environment variable not set`

**Solution**:
```bash
# Verify DATABASE_URL is set
echo $DATABASE_URL

# In Replit, DATABASE_URL is automatic
# For local: export DATABASE_URL='postgresql://...'
```

### State File Not Saved

**Problem**: No `.tfstate` files created

**Solution**:
1. Check directory exists: `mkdir -p terraform.tfstate.d`
2. Verify `--output-file` flag is set (default: true)
3. Check write permissions

## Next Steps

- 📖 **CLI Guide**: See `docs/CLI_USAGE.md` for complete CLI documentation
- 🎯 **Quick Start**: See `README.md` for examples
- 🧪 **Experiments**: See `experiments/` for pre-built configurations
- 🏗️ **Architecture**: See `replit.md` for system architecture

## Support

- **Documentation**: `docs/` directory
- **Tests**: `tests/` directory with examples
- **Issues**: GitHub Issues
- **Examples**: `experiments/` directory
