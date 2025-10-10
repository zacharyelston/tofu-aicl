# Docker-Based RAG Testing Setup

## Overview

This project includes a complete Docker-based setup for portable RAG testing and evaluation. Users can run the entire RAG evaluation system without installing Python dependencies locally.

## Files

### Core Docker Files
- **Dockerfile.rag** - Lightweight Python 3.11 image with all dependencies
- **docker-compose.rag.yml** - Docker Compose configuration for easy execution
- **setup-rag.sh** - Automated setup script for initial configuration

### Configuration
- **.env** - API keys and environment variables (created by setup script)
- **questions.txt** - Test questions (created by setup script)
- **rag-config.yaml** - RAG system configuration

## Quick Start

### 1. Run Setup Script
```bash
./setup-rag.sh
```

This creates:
- `.env` template with placeholder API keys
- `questions.txt` with sample questions
- `experiments/` directory for results

### 2. Add Your API Keys

Edit `.env` and add your actual API keys:
```bash
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east-1
```

### 3. Run Tests with Docker

```bash
# Build the image
docker compose -f docker-compose.rag.yml build

# Run tests
docker compose -f docker-compose.rag.yml run --rm rag-test

# Results are saved to experiments/ directory
```

## Advanced Usage

### Custom Questions

Edit `questions.txt` to add your own questions:
```
How does the StateManager track dependencies?
Explain the provider protocol implementation.
What is the role of the Planner?
```

### Direct Docker Commands

```bash
# Build image
docker build -f Dockerfile.rag -t tofu-aicl-rag .

# Run with custom questions file
docker run --rm \
  --env-file .env \
  -v $(pwd)/experiments:/app/experiments \
  -v $(pwd)/my-questions.txt:/app/questions.txt \
  tofu-aicl-rag python scripts/test_rag_query.py questions.txt

# Run with custom config
docker run --rm \
  --env-file .env \
  -v $(pwd)/experiments:/app/experiments \
  -v $(pwd)/custom-config.yaml:/app/rag-config.yaml \
  tofu-aicl-rag python scripts/test_rag_query.py questions.txt
```

### View Results

Results are automatically saved to `experiments/`:
```bash
# Latest results
cat experiments/rag_test_results.md

# Specific run
cat experiments/rag_test_<run_id>.md

# JSON format
cat experiments/rag_test_results.json
```

## Docker Image Details

### Base Image
- **Python 3.11-slim** - Minimal Debian-based image

### Dependencies Installed
- pyyaml - YAML configuration parsing
- pinecone-client - Vector database access
- openai - OpenAI API client
- anthropic - Anthropic API client
- All other tofu-aicl dependencies from pyproject.toml

### Environment Variables
- `PYTHONPATH=/app/src` - Python module path
- `PYTHONUNBUFFERED=1` - Real-time output
- API keys from .env file

### Volumes Mounted
- `./experiments:/app/experiments` - Results output
- `./questions.txt:/app/questions.txt` - Questions input
- `./rag-config.yaml:/app/rag-config.yaml` - Configuration
- `./.env:/app/.env` - Environment variables

## Troubleshooting

### Permission Errors
```bash
# Fix experiments directory permissions
chmod -R 755 experiments
```

### Missing API Keys
```bash
# Verify .env file exists and has keys
cat .env
```

### Image Build Failures
```bash
# Clean build without cache
docker compose -f docker-compose.rag.yml build --no-cache
```

### Container Won't Start
```bash
# Check logs
docker compose -f docker-compose.rag.yml logs

# Run with shell for debugging
docker compose -f docker-compose.rag.yml run --rm rag-test /bin/bash
```

## Benefits

### Portability
- Works on any system with Docker installed
- No Python version conflicts
- No local dependency management

### Consistency
- Same environment for all users
- Reproducible results
- Isolated from host system

### Simplicity
- One command to run tests
- Automatic result collection
- No cleanup needed

## Integration with CI/CD

The Docker setup can be used in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run RAG Tests
  run: |
    docker compose -f docker-compose.rag.yml build
    docker compose -f docker-compose.rag.yml run --rm rag-test
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
```

## Local vs Docker Comparison

| Aspect | Local Python | Docker |
|--------|-------------|--------|
| Setup | Install dependencies | Build image once |
| Portability | Python version dependent | Works anywhere |
| Isolation | Uses host Python | Fully isolated |
| Speed | Faster startup | Slower first build |
| Cleanup | Manual venv management | Automatic |

## Next Steps

After running tests:
1. Review results in `experiments/rag_test_results.md`
2. Compare model performance in JSON output
3. Adjust `rag-config.yaml` for different configurations
4. Add more questions to `questions.txt`
5. Re-run tests and compare results over time
