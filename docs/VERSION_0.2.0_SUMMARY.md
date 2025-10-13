# tofu-aicl v0.2.0 - Release Summary

## 🎉 What's New

### Multiple Output Destinations with CLI Controls

**v0.2.0** introduces flexible output configuration, allowing experiments to be saved to multiple destinations simultaneously:

- **JSON State Files** - Traditional `.tfstate` files for version control
- **PostgreSQL DocDB** - Structured JSONB storage for querying and analysis  
- **Stdout Console** - Real-time formatted output

All controlled via simple command-line flags.

---

## 🚀 Quick Start (v0.2.0)

### Installation

```bash
# Clone repository
git clone https://github.com/zacharyelston/tofu-aicl.git
cd tofu-aicl

# Install dependencies
pip install -e .
```

### Basic Usage

```bash
# Default behavior (file + stdout)
python run.py experiments/rag-demo/rag-demo-live.aicl

# Save to PostgreSQL with tags
python run.py experiments/rag-demo/rag-demo-live.aicl \
  --output-docdb \
  --experiment-id rag-prod-v1 \
  --tags rag,production,pinecone

# Quiet mode for automation
python run.py config.aicl --quiet --no-stdout --output-file
```

---

## 📋 CLI Flags Reference

### Output Destinations

| Flag | Default | Description |
|------|---------|-------------|
| `--output-file` | ✅ | Save to JSON state files |
| `--output-docdb` | ❌ | Save to PostgreSQL database |
| `--output-stdout` | ✅ | Print to console |
| `--no-stdout` | - | Disable console output |

### Experiment Configuration

| Flag | Description | Example |
|------|-------------|---------|
| `--experiment-id ID` | Custom identifier | `--experiment-id rag-v2` |
| `--tags TAGS` | Comma-separated tags | `--tags rag,demo,gpt4` |
| `--quiet` / `-q` | Minimal output | `--quiet` |

### Experimental

| Flag | Status | Description |
|------|--------|-------------|
| `--parallel` | 🚧 Planned | Parallel execution |

---

## 🧪 PostgreSQL DocDB Feature

### What is DocDB?

A PostgreSQL-backed document store for experiments, enabling:
- **Structured Storage** - JSONB columns for outputs, config, metadata
- **Full-Text Search** - Query experiments by tags, ID, timestamp
- **Historical Tracking** - Compare runs across time
- **Analytics** - Aggregate metrics across experiments

### Setup

**Replit (Automatic)**:
```bash
# DATABASE_URL is already configured
python run.py config.aicl --output-docdb
```

**Local Setup**:
```bash
createdb aicl_experiments
export DATABASE_URL='postgresql://localhost/aicl_experiments'
python run.py config.aicl --output-docdb
```

### Schema (Auto-Created)

```sql
CREATE TABLE experiment_outputs (
    id SERIAL PRIMARY KEY,
    experiment_id VARCHAR(255) NOT NULL,
    run_timestamp TIMESTAMP NOT NULL,
    config_file TEXT,
    config_content JSONB,
    outputs JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_experiment_id ON experiment_outputs(experiment_id);
CREATE INDEX idx_run_timestamp ON experiment_outputs(run_timestamp);
CREATE INDEX idx_metadata_gin ON experiment_outputs USING GIN(metadata);
```

### Query Examples

```python
from experiments.storage.experiment_docdb import ExperimentDocDB

docdb = ExperimentDocDB()

# Get latest run
result = docdb.get_by_id("rag-v1")

# Get all runs with tag
results = docdb.query_by_tags(["production"])

# Compare experiments
comparison = docdb.compare_experiments(["exp1", "exp2", "exp3"])
```

---

## 🧪 Test Coverage

### New CLI Tests (`tests/test_cli.py`)

**20 comprehensive tests** covering:

1. **Output Configuration** (11 tests)
   - Default settings
   - Individual flag behavior
   - Combined multi-flag scenarios
   - Custom IDs and tags

2. **Output Methods** (6 tests)
   - Stdout printing with dict/list
   - Empty/no state handling
   - DocDB save success path
   - Error handling and graceful degradation

3. **CLI Integration** (3 tests)
   - Quiet mode suppression
   - Argparse flag mapping
   - Override behavior (`--no-stdout`)

**Results**: ✅ **20/20 passing** (100% success rate)

### Run Tests

```bash
# All CLI tests
pytest tests/test_cli.py -v

# Specific test class
pytest tests/test_cli.py::TestCLIOutputConfiguration -v

# With coverage
pytest tests/test_cli.py --cov=src.aicl.core.engine
```

---

## 📦 Updated Dependencies

### Core (Required)

```toml
[dependencies]
python-hcl2>=4.0.0
grpcio>=1.39.0
grpcio-tools>=1.39.0
protobuf>=3.19.0
python-dotenv>=1.1.1
requests>=2.32.5
psycopg2-binary>=2.9.0  # NEW: PostgreSQL support
opentelemetry-api>=1.37.0
opentelemetry-sdk>=1.37.0
opentelemetry-exporter-otlp>=1.37.0
pytest>=8.4.2
pytest-cov>=7.0.0
pytest-asyncio>=1.2.0
```

### Python Version

- **Minimum**: Python 3.11
- **Tested**: Python 3.11.13
- **Recommended**: Python 3.11.x

---

## 🔧 What Changed

### 1. CLI Entry Point (`run.py`)

**Before (v0.1.0)**:
```python
config_path = sys.argv[1] if len(sys.argv) > 1 else 'example.aicl'
engine = AICLEngine(config_path=config_path)
engine.run()
```

**After (v0.2.0)**:
```python
parser = argparse.ArgumentParser()
parser.add_argument('config_path', nargs='?', default='example.aicl')
parser.add_argument('--output-file', action='store_true')
parser.add_argument('--output-docdb', action='store_true')
# ... more flags
args = parser.parse_args()

engine = AICLEngine(
    config_path=args.config_path,
    output_file=args.output_file,
    output_docdb=args.output_docdb,
    # ... more options
)
```

### 2. Engine Constructor (`src/aicl/core/engine.py`)

**New Parameters**:
```python
def __init__(
    self, 
    config_path: str,
    output_file: bool = True,      # NEW
    output_docdb: bool = False,    # NEW
    output_stdout: bool = True,    # NEW
    quiet: bool = False,           # NEW
    parallel: bool = False,        # NEW (planned)
    experiment_id: Optional[str] = None,  # NEW
    tags: Optional[list] = None    # NEW
):
```

### 3. Output Methods

**New Helper Methods**:
- `_save_to_docdb(experiment_id)` - Save to PostgreSQL
- `_print_outputs()` - Formatted stdout printing

**Integration in `apply()`**:
```python
# After resource execution
if self.output_file:
    self.state_manager.save()

if self.output_docdb and self.docdb:
    self._save_to_docdb(experiment_id)

if self.output_stdout and not self.quiet:
    self._print_outputs()
```

---

## 📚 Documentation Updates

### New Files

1. **`docs/CLI_USAGE.md`** - Complete CLI reference
   - All flags documented
   - Usage examples
   - Output destination comparison
   - Parallel execution roadmap

2. **`docs/SETUP.md`** - Installation and setup guide
   - Prerequisites
   - Step-by-step installation
   - API key configuration
   - PostgreSQL setup
   - Troubleshooting

3. **`CHANGELOG.md`** - Version history
   - Release notes
   - Breaking changes
   - Migration guide
   - Roadmap

4. **`VERSION`** - Version file (0.2.0)

### Updated Files

1. **`README.md`**
   - Quick start with CLI examples
   - Flag reference table
   - Link to CLI docs

2. **`tests/README.md`**
   - CLI test coverage section
   - Updated test count

3. **`replit.md`**
   - Recent updates section
   - CLI feature summary
   - Test coverage notes

---

## 🐛 Bug Fixes

### 1. Pinecone Dimension Mismatch

**Problem**: Pinecone expected 1024 dims, OpenAI default was 1536

**Solution**:
```hcl
resource "openai_embedding" "example" {
  dimensions = 1024  # NEW: Explicit dimension control
  # ...
}
```

### 2. HCL Float-to-Int Conversion

**Problem**: HCL parsed `dimensions = 1024` as float (1024.0), OpenAI API rejected

**Solution**:
```python
# providers/openai/server.py
dimensions = config.get('dimensions')
if dimensions:
    data['dimensions'] = int(dimensions)  # Force int conversion
```

### 3. Silent Error Failures

**Problem**: Errors masked with fallbacks, hard to debug

**Solution**: "Fail loudly" approach
```python
# Before: Silent fallback
except Exception as e:
    return default_value

# After: Explicit error
except Exception as e:
    print(f"ERROR: {e}")
    print(f"Full response: {response.text}")
    raise
```

---

## 🔮 Roadmap

### Immediate (v0.2.x)

- [ ] **Parallel Execution** - Implement `--parallel` flag
  - Group resources by dependency level
  - Thread-safe state management
  - Error isolation per resource

- [ ] **Query Tool** - CLI for DocDB queries
  ```bash
  python experiments/query_results.py --experiment-id rag-v1
  python experiments/query_results.py --list
  python experiments/query_results.py --compare exp1,exp2,exp3
  ```

### Short Term (v0.3.0)

- [ ] **Web UI** - Visual experiment builder
- [ ] **More Providers** - Anthropic, Cohere, HuggingFace
- [ ] **Advanced RAG** - Hybrid search, reranking

### Long Term (v1.0.0)

- [ ] **Self-Improvement** - RAG on own codebase
- [ ] **GraphQL API** - Query interface
- [ ] **Multi-tenant** - Experiment isolation

---

## 📊 Migration Guide

### From v0.1.0 to v0.2.0

**No migration needed!** All existing code works:

```bash
# Old way (still works)
python run.py experiments/rag-demo/rag-demo-live.aicl

# New way (optional enhancements)
python run.py experiments/rag-demo/rag-demo-live.aicl \
  --output-docdb \
  --experiment-id rag-v2 \
  --tags rag,demo
```

**Existing `.aicl` files**: No changes required

**Existing workflows**: Continue to work

**State files**: Fully compatible

---

## 🙏 Credits

**Development**: Zachary Elston  
**Framework**: tofu-aicl (Terraform for AI)  
**License**: GPL-3.0

---

## 🔗 Resources

- **Documentation**: `docs/` directory
- **Examples**: `experiments/` directory
- **Tests**: `tests/` directory
- **Repository**: https://github.com/zacharyelston/tofu-aicl
