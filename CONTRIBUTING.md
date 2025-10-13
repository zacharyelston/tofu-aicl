# Contributing to TerraMISO

Thank you for your interest in contributing to TerraMISO! This guide will help you get started.

**TerraMISO** = Multi-In Single-Out AI framework extending Terraform/OpenTofu

## 🚀 Quick Start for Contributors

### 1. Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/zacharyelston/terramiso.git
cd terramiso

# Install dependencies
pip install -e .

# Install development dependencies
pip install pytest pytest-cov pytest-asyncio

# Run tests to verify setup
pytest
```

### 2. Set Up API Keys

Create a `.env` file in the project root:

```bash
# Core providers
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_HOST_URL=https://...

# Optional providers
AZURE_OPENAI_API_KEY=...
NAGA_API_KEY=...
RAGIE_API_KEY=...

# PostgreSQL (for --output-docdb feature)
DATABASE_URL=postgresql://localhost/aicl_experiments
```

## 📋 Development Workflow

### Making Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our style guide (see below)
   - Add tests for new functionality
   - Update documentation

3. **Run tests**
   ```bash
   # All tests
   pytest
   
   # With coverage
   pytest --cov=src/aicl --cov-report=html
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

## 🧪 Testing Guidelines

### Test Requirements

- All new features must have tests
- Maintain >80% code coverage
- Tests should be independent (no shared state)
- Use fixtures for common setup (`tests/conftest.py`)
- Mock external API calls

### Writing Tests

**Unit Test Example:**
```python
import pytest
from src.aicl.core.parser import HCLParser

class TestHCLParser:
    def test_parse_basic_config(self):
        parser = HCLParser('test.aicl')
        result = parser.parse()
        assert 'resource' in result
```

## 📝 Documentation Standards

### Code Documentation

- Add docstrings to all public functions/classes
- Include type hints
- Provide examples where helpful

### Markdown Documentation

- Keep line length <100 characters
- Include code examples
- Link to related documentation
- Update `docs/README.md` index when adding new docs

## 🎨 Code Style

- Follow PEP 8
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use meaningful variable names

## 🔄 Git Workflow

### Commit Messages

Follow conventional commits:

```
feat: add PostgreSQL DocDB support
fix: resolve dimension mismatch in embeddings
docs: update CLI usage guide
test: add tests for output configuration
```

### Branch Naming

```
feature/cli-output-destinations
fix/pinecone-dimensions
docs/setup-guide
```

## 📄 License

By contributing, you agree that your contributions will be licensed under GPL-3.0.

## 💬 Questions?

Open a GitHub issue or discussion.

## 🙏 Thank You

Every contribution makes TerraMISO better!
