# Docker Usage Guide - tofu-aicl

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Run the default RAG pipeline test
docker-compose up tofu-aicl

# Run the simple test
docker-compose --profile test up tofu-aicl-test

# Start an interactive shell for debugging
docker-compose --profile debug run --rm tofu-aicl-shell
```

### Using Docker Commands

```bash
# Build the image
docker build -t tofu-aicl:latest .

# Run default configuration
docker run --rm --env-file .env tofu-aicl:latest

# Run custom AICL file
docker run --rm --env-file .env tofu-aicl:latest python3 run.py your_config.aicl

# Run with mounted volumes
docker run --rm \
  --env-file .env \
  -v $(pwd)/docs:/app/docs:ro \
  -v $(pwd)/experiments:/app/experiments \
  tofu-aicl:latest

# Interactive shell
docker run --rm -it \
  --env-file .env \
  -v $(pwd):/app \
  --entrypoint /bin/bash \
  tofu-aicl:latest
```

## Container Features

### Volumes

- **`/app/docs`**: Mount your documents for RAG indexing (read-only)
- **`/app/experiments`**: Persist experiment results
- **`/app/terraform.tfstate.d`**: Persist state files across runs
- **`/app/src`**: Mount source code for development

### Environment Variables

All environment variables from `.env` are automatically loaded:
- `OPENAI_API_KEY` - OpenAI API access
- `OPENROUTER_API_KEY` - OpenRouter API access
- `PINECONE_API_KEY` - Pinecone vector database
- `ANTHROPIC_API_KEY` - Anthropic Claude access
- See `.env.template` for complete list

### Provider Mode

The container runs in **subprocess mode** by default:
- All providers run as Python subprocesses
- No Docker-in-Docker required
- Faster startup and execution
- Ideal for containerized environments

## Common Use Cases

### 1. RAG Pipeline Testing

```bash
# Create a test AICL file
cat > my_rag_test.aicl << 'EOF'
terraform {
  required_providers {
    loader = { source = "aicl/file_loader" }
    splitter = { source = "aicl/text_splitter" }
  }
}

resource "loader_files" "docs" {
  path = "./docs"
  glob = "**/*.md"
}

resource "splitter_text" "chunks" {
  documents = "${resource.loader_files.docs.attributes.documents}"
  chunk_size = 500
}
EOF

# Run in container
docker run --rm \
  --env-file .env \
  -v $(pwd)/docs:/app/docs:ro \
  tofu-aicl:latest \
  python3 run.py my_rag_test.aicl
```

### 2. Development and Debugging

```bash
# Start interactive container
docker-compose --profile debug run --rm tofu-aicl-shell

# Inside container:
python3 run.py test_simple.aicl
pytest tests/
python3 -m aicl.parser config.aicl
```

### 3. CI/CD Integration

```yaml
# Example GitHub Actions
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build container
        run: docker build -t tofu-aicl:test .
      - name: Run tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          echo "OPENAI_API_KEY=$OPENAI_API_KEY" > .env
          docker run --rm --env-file .env tofu-aicl:test
```

### 4. Experiment Comparison

```bash
# Run multiple experiments with different configurations
for config in exp_*.aicl; do
  echo "Running $config"
  docker run --rm \
    --env-file .env \
    -v $(pwd)/experiments:/app/experiments \
    tofu-aicl:latest \
    python3 run.py "$config"
done

# Compare results
ls experiments/
```

## Troubleshooting

### Issue: "Provider not found"

**Problem:** AICL file references a provider not included in the container.

**Solution:** Ensure all required providers are in the `providers/` directory and have valid `config.yaml`.

### Issue: "No such file or directory"

**Problem:** AICL file tries to access files not in the container.

**Solution:** Mount the required directories as volumes:
```bash
docker run --rm \
  -v $(pwd)/data:/app/data:ro \
  tofu-aicl:latest \
  python3 run.py config.aicl
```

### Issue: Verbose JSON output

**Problem:** OpenTelemetry outputs detailed JSON metrics.

**Solution:** This is normal behavior. Metrics are exported to stdout. To suppress:
```bash
# Redirect telemetry to /dev/null (keeps application output)
docker run --rm --env-file .env tofu-aicl:latest 2>&1 | grep -v "telemetry.sdk"
```

### Issue: "Permission denied"

**Problem:** Container can't write to mounted volumes.

**Solution:** Ensure volumes have correct permissions:
```bash
chmod 755 experiments/ terraform.tfstate.d/
```

## Performance Optimization

### Build Cache

The Dockerfile uses multi-layer caching:
- Layer 1-3: System dependencies (rarely changes)
- Layer 4-6: Python dependencies (changes with pyproject.toml)
- Layer 7: Application code (changes frequently)

Rebuild only when needed:
```bash
# Quick rebuild (only copies changed files)
docker build -t tofu-aicl:latest .

# Full rebuild (no cache)
docker build --no-cache -t tofu-aicl:latest .
```

### Container Size

Current image: ~500MB (Python 3.9 slim + dependencies)

To reduce size further:
- Use alpine base image (more complex build)
- Remove development dependencies in production
- Use multi-stage build with runtime-only stage

### Execution Speed

Subprocess mode is optimized for containers:
- No Docker socket mounting required
- Faster provider startup (~2s vs ~5s for Docker)
- Lower memory footprint

## Security Considerations

### API Keys

- Never commit `.env` files
- Use secrets management in production
- Rotate keys regularly
- Use read-only mounts for sensitive data

### Container Isolation

The container runs as root by default. For production:

```dockerfile
# Add to Dockerfile
RUN useradd -m -u 1000 aicl
USER aicl
```

### Network Access

Providers make external API calls:
- OpenAI, Anthropic, OpenRouter: API requests
- Pinecone: Vector database operations

Ensure firewall rules allow HTTPS egress.

## Next Steps

- See `DOCKER_FIX_SUMMARY.md` for technical details on fixes applied
- See `README.md` for AICL language documentation
- See `experiments/` for example configurations
- See `providers/` for available provider documentation
