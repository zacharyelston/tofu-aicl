# GitHub Secrets Sync Scripts

Two complementary scripts for syncing `.env` file variables to GitHub repository secrets for secure CI/CD workflows.

## 🚀 Quick Start

```bash
# Basic sync (auto-detects repository)
./scripts/sync-env-to-github-secrets.sh

# Preview changes without applying
./scripts/sync-env-to-github-secrets.sh --dry-run

# Sync to specific repository
./scripts/sync-env-to-github-secrets.sh --repo myorg/myrepo
```

## 📋 Prerequisites

1. **GitHub CLI**: Install from [cli.github.com](https://cli.github.com/)
2. **Authentication**: Run `gh auth login`
3. **Repository Access**: Admin permissions on target repository
4. **Environment File**: Readable `.env` file

## 🛠️ Scripts Overview

### Bash Script (`sync-env-to-github-secrets.sh`)
**Best for**: Simple, reliable syncing with minimal dependencies

**Features**:
- ✅ Zero dependencies (only requires `gh` CLI)
- ✅ Auto-detects repository from git remote
- ✅ Interactive confirmation prompts
- ✅ Dry-run mode for safety
- ✅ Colored output and logging
- ✅ Handles existing secret overwrites

### Python Script (`sync-env-to-github-secrets.py`)
**Best for**: Advanced filtering, validation, and batch operations

**Features**:
- ✅ Advanced regex filtering (include/exclude patterns)
- ✅ Variable validation and security checks
- ✅ Prefix support for secret names
- ✅ Robust .env parsing with `python-dotenv`
- ✅ Validation-only mode
- ✅ Detailed error reporting

## 📖 Usage Examples

### Bash Script Examples

```bash
# Basic usage
./scripts/sync-env-to-github-secrets.sh

# Custom .env file
./scripts/sync-env-to-github-secrets.sh --file .env.production

# Specific repository
./scripts/sync-env-to-github-secrets.sh --repo ancerallc/tofu-aicl

# Force overwrite without prompts
./scripts/sync-env-to-github-secrets.sh --force

# Preview mode
./scripts/sync-env-to-github-secrets.sh --dry-run
```

### Python Script Examples

```bash
# Install Python dependencies first
pip install python-dotenv requests

# Basic usage
./scripts/sync-env-to-github-secrets.py

# Filter API keys only
./scripts/sync-env-to-github-secrets.py --include ".*API_KEY.*"

# Exclude local development variables
./scripts/sync-env-to-github-secrets.py --exclude "LOCAL_.*|DEV_.*"

# Add environment prefix
./scripts/sync-env-to-github-secrets.py --prefix "PROD_"

# Validate variables without syncing
./scripts/sync-env-to-github-secrets.py --validate

# Complex filtering
./scripts/sync-env-to-github-secrets.py \
  --include "API_KEY|SECRET|TOKEN" \
  --exclude "LOCAL_|TEST_" \
  --prefix "CI_"
```

## 🔧 Command Line Options

### Bash Script Options
```
-f, --file FILE     Path to .env file (default: .env)
-r, --repo REPO     GitHub repository (owner/repo format)
-d, --dry-run       Show what would be done without making changes
--force             Overwrite existing secrets without confirmation
-h, --help          Show help message
```

### Python Script Options
```
-f, --file FILE     Path to .env file (default: .env)
-r, --repo REPO     GitHub repository (owner/repo format)
-d, --dry-run       Show what would be done without making changes
--force             Overwrite existing secrets without confirmation
--include PATTERN   Include only variables matching regex pattern
--exclude PATTERN   Exclude variables matching regex pattern
--prefix PREFIX     Add prefix to all secret names
--validate          Only validate variables, don't sync
--verbose           Enable verbose output
```

## 📁 Example .env File

```bash
# API Keys
OPENAI_API_KEY=sk-1234567890abcdef
PINECONE_API_KEY=12345678-1234-1234-1234-123456789012
AZURE_OPENAI_API_KEY=abcdef1234567890

# Service Configuration
AZURE_OPENAI_ENDPOINT=https://myservice.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-01
PINECONE_HOST_URL=https://index-name-project.svc.environment.pinecone.io

# Application Settings
APP_ENV=production
LOG_LEVEL=info
DEBUG=false
```

## 🔒 Security Best Practices

### ✅ Do's
- **Use different .env files** for different environments (`.env.dev`, `.env.prod`)
- **Review variables** before syncing with `--dry-run`
- **Use filtering** to exclude local-only secrets
- **Validate first** with `--validate` option (Python script)
- **Rotate secrets** regularly in both .env and GitHub

### ❌ Don'ts
- **Don't commit** .env files to git (ensure `.gitignore` includes `.env`)
- **Don't sync local-only** variables (database URLs, file paths)
- **Don't use weak** or test credentials in production
- **Don't sync without** understanding what each variable does

## 🎯 Common Use Cases

### 1. Initial Repository Setup
```bash
# Set up secrets for new repository
./scripts/sync-env-to-github-secrets.sh --repo myorg/new-project --dry-run
./scripts/sync-env-to-github-secrets.sh --repo myorg/new-project
```

### 2. Production Environment Sync
```bash
# Sync production secrets with validation
./scripts/sync-env-to-github-secrets.py \
  --file .env.production \
  --include ".*API_KEY.*|.*SECRET.*" \
  --exclude "LOCAL_.*|DEV_.*" \
  --validate

# Apply after validation passes
./scripts/sync-env-to-github-secrets.py \
  --file .env.production \
  --include ".*API_KEY.*|.*SECRET.*" \
  --exclude "LOCAL_.*|DEV_.*" \
  --prefix "PROD_"
```

### 3. Multi-Environment Setup
```bash
# Development environment
./scripts/sync-env-to-github-secrets.py \
  --file .env.dev \
  --prefix "DEV_" \
  --repo myorg/project

# Staging environment
./scripts/sync-env-to-github-secrets.py \
  --file .env.staging \
  --prefix "STAGING_" \
  --repo myorg/project

# Production environment
./scripts/sync-env-to-github-secrets.py \
  --file .env.prod \
  --prefix "PROD_" \
  --repo myorg/project
```

## 🔍 Troubleshooting

### GitHub CLI Issues
```bash
# Check GitHub CLI installation
gh --version

# Check authentication
gh auth status

# Re-authenticate if needed
gh auth login
```

### Repository Access Issues
```bash
# Verify repository exists and you have access
gh repo view myorg/myrepo

# Check if you have admin access (required for secrets)
gh api repos/myorg/myrepo/collaborators/$(gh api user --jq .login) \
  --jq .permissions.admin
```

### .env File Issues
```bash
# Check file exists and is readable
ls -la .env

# Validate .env format (Python script)
./scripts/sync-env-to-github-secrets.py --validate --verbose
```

## 🔗 Integration with GitHub Actions

After syncing secrets, use them in your workflows:

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy with secrets
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
          AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
        run: |
          echo "Deploying with secure API keys..."
          # Your deployment commands here
```

## 📚 Related Documentation

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [Environment Variables Best Practices](https://12factor.net/config)
- [tofu-aicl Provider Configuration](../docs/providers/)

## 🆘 Support

If you encounter issues:

1. **Check Prerequisites**: Ensure GitHub CLI is installed and authenticated
2. **Validate .env**: Use `--validate` option to check for issues
3. **Use Dry Run**: Always test with `--dry-run` first
4. **Check Permissions**: Ensure you have admin access to the repository
5. **Review Logs**: Use `--verbose` option for detailed output

For tofu-aicl specific issues, see the main project documentation.
