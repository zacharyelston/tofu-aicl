# AICL CLI Setup Guide

## Installation

### 1. Make CLI Executable
```bash
cd /Users/zacelston/code/tofu-aicl
chmod +x aicl
```

### 2. Add to PATH (Optional but Recommended)
```bash
# Symlink to /usr/local/bin
sudo ln -s $(pwd)/aicl /usr/local/bin/aicl

# Or add to PATH in your shell config
echo 'export PATH="$PATH:/Users/zacelston/code/tofu-aicl"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Create Configuration File
```bash
# Create AICL config directory
mkdir -p ~/.aicl

# Copy example config
cp config.yaml.example ~/.aicl/config.yaml

# Edit to your preferences
nano ~/.aicl/config.yaml
```

## Quick Start

### Basic Usage
```bash
# Run a configuration locally
aicl run test_simple.aicl

# Run in Docker
aicl run test_simple.aicl --docker

# Validate configuration
aicl validate test_simple.aicl

# List providers
aicl providers list

# Show current config
aicl config show
```

### With Custom Working Directory
```bash
# Run config from specific directory
aicl run experiment.aicl --workdir ./experiments

# With custom experiment ID
aicl run experiment.aicl --experiment-id exp-001
```

### Docker Commands
```bash
# Run in Docker with custom mounts
aicl docker run experiment.aicl --mount ./data:/app/data:ro

# Interactive Docker shell
aicl docker shell

# Run with specific Docker image
aicl run experiment.aicl --docker --config <(echo "runtime:
  docker_image: tofu-aicl:v1.0.0")
```

### State Management
```bash
# List all resources in current experiment
aicl state list

# List resources in specific experiment
aicl state list --experiment-id exp-001

# Show specific resource
aicl state show loader_files-docs

# Show with experiment ID
aicl state show loader_files-docs --experiment-id exp-001
```

## Configuration Examples

### Minimal Config (~/.aicl/config.yaml)
```yaml
runtime:
  mode: local  # Run locally by default

paths:
  state_dir: ./terraform.tfstate.d
  experiments_dir: ./experiments
```

### Docker-Focused Config
```yaml
runtime:
  mode: docker
  docker_image: tofu-aicl:latest
  provider_mode: subprocess

docker:
  remove_after: true
  mounts:
    - ./data:/app/data:ro
    - ./custom:/app/custom:ro

observability:
  enabled: true
  log_level: INFO
```

### Development Config
```yaml
runtime:
  mode: local

development:
  debug: true
  show_provider_logs: true

observability:
  enabled: false  # Reduce noise
```

## Environment Variables

Override config with environment variables:

```bash
# Runtime mode
export AICL_RUNTIME_MODE=docker

# Docker image
export AICL_DOCKER_IMAGE=tofu-aicl:v1.0.0

# API keys (same as before)
export OPENAI_API_KEY=sk-...
export PINECONE_API_KEY=pc-...

# Run with env vars
aicl run experiment.aicl
```

## Configuration Precedence

From **highest** to **lowest** priority:
1. **CLI arguments**: `--docker`, `--workdir`, etc.
2. **Environment variables**: `AICL_*`
3. **Config file**: `~/.aicl/config.yaml`
4. **Defaults**: Built-in fallbacks

Example:
```bash
# Config file says: mode = local
# Env var says: AICL_RUNTIME_MODE=docker
# CLI says: --no-docker

# Result: Runs locally (CLI wins)
```

## Common Workflows

### Experiment Workflow
```bash
# 1. Create experiment config
cat > exp_001.aicl << 'EOF'
terraform {
  required_providers {
    loader = { source = "aicl/file_loader" }
  }
}
resource "loader_files" "docs" {
  path = "./docs"
  glob = "**/*.md"
}
EOF

# 2. Validate
aicl validate exp_001.aicl

# 3. Run
aicl run exp_001.aicl --experiment-id exp-001

# 4. Check results
aicl state list --experiment-id exp-001

# 5. View state file
cat terraform.tfstate.d/exp-001.tfstate | jq
```

### Docker Development Workflow
```bash
# Set Docker mode in config
cat > ~/.aicl/config.yaml << EOF
runtime:
  mode: docker
docker:
  mounts:
    - ./src:/app/src:ro
EOF

# Now all runs use Docker
aicl run test.aicl

# Override for local testing
aicl run test.aicl --no-docker
```

### Multi-Environment Setup
```bash
# Dev config
aicl run exp.aicl --config ./config/dev.yaml

# Prod config
aicl run exp.aicl --config ./config/prod.yaml
```

## Troubleshooting

### "Command not found: aicl"
```bash
# Check if in PATH
which aicl

# Add to PATH or use full path
/Users/zacelston/code/tofu-aicl/aicl --help
```

### "ModuleNotFoundError"
```bash
# Ensure dependencies installed
pip install -e /Users/zacelston/code/tofu-aicl

# Or run in Docker mode
aicl run config.aicl --docker
```

### Docker image not found
```bash
# Build image first
cd /Users/zacelston/code/tofu-aicl
docker build -t tofu-aicl:latest .

# Or pull if available
docker pull tofu-aicl:latest
```

### State file not found
```bash
# Create state directory
mkdir -p terraform.tfstate.d

# Or set in config
echo "paths:
  state_dir: ./state" > ~/.aicl/config.yaml
```

## Advanced Usage

### Custom Provider Discovery
```yaml
# Add custom provider paths
paths:
  providers_dir: ./providers
  custom_providers:
    - ./my-providers
    - /opt/aicl-providers
```

### Resource Limits (Docker)
```yaml
docker:
  resources:
    memory: 4g
    cpus: 2
    gpu: 1  # If GPU support needed
```

### Multiple Configs
```bash
# Work config
aicl run exp.aicl --config ~/.aicl/work.yaml

# Personal config
aicl run exp.aicl --config ~/.aicl/personal.yaml
```

## Next Steps

- See `CLI_VS_TERRAFORM.md` for comparison with Terraform
- See `DOCKER_USAGE_GUIDE.md` for Docker details
- See `README.md` for AICL language documentation
- See `examples/` for more configuration examples
