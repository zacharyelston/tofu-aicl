# TerraMISO

## Multi-In Single-Out AI Framework for Terraform/OpenTofu

**TerraMISO** extends Terraform and OpenTofu with AI-powered optimization using the **MISO pattern** (Multi-In Single-Out): multiple LLM providers compete, and the best solution wins.

```
Multiple Providers (Multi-In)    →    Optimal Solution (Single-Out)
    GPT-4         ─┐
    Claude        ─┼──→  Competition  →  🏆 Best Answer
    Gemini        ─┘
```

**Repository**: https://github.com/zacharyelston/terramiso  
**License**: GPL-3.0

---

## 🎯 What is MISO?

**MISO = Multi-In Single-Out** - A reusable competitive optimization pattern:

1. **Multi-In**: Multiple AI providers analyze the same problem
2. **Competition**: Each provider proposes a solution
3. **Selection**: LLM-as-Judge picks the optimal solution
4. **Single-Out**: One best answer emerges

This isn't just for AI - **any system can adopt MISO** for competitive optimization by including our templates and methods.

---

## 🚀 Quick Start: Terraform Integration

### Traditional Terraform Problem:
```hcl
resource "azurerm_postgresql_server" "main" {
  sku_name = "GP_Gen5_4"   # Is this optimal? 🤷
  storage_mb = 102400       # Guesswork! 🤷
}
```

### With TerraMISO:
```bash
# 1. AI analyzes your workload (3 providers compete)
python run.py postgres-optimizer.aicl

# 2. Best config automatically selected
# 3. Terraform deploys with optimal settings ✨
terraform apply -var-file=ai-optimized.tfvars
```

See `examples/terraform-integration/README.md` for complete walkthrough.

---

## 💡 Real RAG Evaluation Output

Here's what the system produces with MISO pattern:

```
🔍 Testing 1 question(s)
🆔 Test Run ID: 551730223cde
📅 Timestamp: 2025-10-09T10:47:54

📄 Retrieved chunks:
  [1] src/aicl/parser.py (score: 0.404)
  [2] src/aicl/planner.py (score: 0.371)
  [3] src/aicl/evaluator.py (score: 0.347)

✅ Using 3 code chunks + 0 doc chunks

🤖 Claude 3.5 Sonnet...
   ✅ Response: 1247 chars, 9127ms

🤖 GPT-4...
   ✅ Response: 1559 chars, 16370ms

📊 LLM Judge Evaluation (MISO Selection):
  claude-3.5-sonnet:
    Accuracy: 8/10
    Completeness: 7/10
    Clarity: 9/10
    Code Specificity: 6/10
    Total: 30/40

  gpt-4:
    Accuracy: 9/10
    Completeness: 8/10
    Clarity: 8/10
    Code Specificity: 9/10
    Total: 34/40

  🏆 Winner: gpt-4  (Single-Out)
```

---

## Overview

**TerraMISO** is a declarative AI infrastructure framework that extends Terraform/OpenTofu with intelligent optimization.

### Core Concepts

- **MISO Pattern**: Multi-In Single-Out competitive optimization
- **Terraform Extension**: Works with existing `.tf` files, no migration needed
- **Declarative AI Infrastructure**: Define AI systems as code using HCL/AICL
- **Provider Architecture**: Modular gRPC services for LLMs, Vector DBs, file loaders
- **Ephemeral & Just-In-Time**: Spin up AI infrastructure on-demand
- **Matrix Experiments**: Run multiple configurations with performance tracking

---

## 🏗️ Use Cases

### 1. Terraform Configuration Optimization
```bash
# Analyze workload, 3 LLMs compete, optimal config selected
python run.py azure-postgres-optimizer.aicl
terraform apply -var-file=optimized.tfvars
```

### 2. RAG Pipeline Evaluation
```bash
# Test multiple LLMs, best answer selected via MISO
python run.py rag-pipeline.aicl --output-docdb --tags rag,production
```

### 3. Cost Optimization
```bash
# Compare 3 providers on price/performance
python run.py cost-optimizer.aicl --experiment-id cost-analysis
```

### 4. Self-Healing Infrastructure
```bash
# AI detects issues, proposes fixes, selects best solution
python run.py self-heal.aicl --parallel
```

---

## Quick Start

### 1. Set up API Keys

Configure these environment variables:
```bash
export OPENAI_API_KEY="sk-..."
export OPENROUTER_API_KEY="sk-..."
export PINECONE_API_KEY="..."
export PINECONE_HOST_URL="https://..."
export DATABASE_URL="postgresql://..."  # Optional: for DocDB
```

### 2. Run a Simple MISO Example

```bash
# Basic usage
python run.py config.aicl

# With multiple output destinations
python run.py config.aicl --output-file --output-docdb --output-stdout

# Quiet mode with custom ID and tags
python run.py config.aicl --quiet --experiment-id my-test --tags demo,v1
```

Example config (`config.aicl`):
```hcl
# MISO Pattern: Test 3 providers, pick best answer
resource "openai_chat" "answer_gpt" {
  model = "gpt-4"
  messages = [
    {
      role = "user"
      content = "Explain Terraform best practices"
    }
  ]
  aiclResourceName = "gpt_answer"
}

resource "openrouter_chat" "answer_claude" {
  model = "anthropic/claude-3.5-sonnet"
  messages = [
    {
      role = "user"
      content = "Explain Terraform best practices"
    }
  ]
  aiclResourceName = "claude_answer"
}

# LLM-as-Judge: Select best answer
resource "openai_chat" "judge" {
  model = "gpt-4"
  messages = [
    {
      role = "user"
      content = "Compare these answers and select the best: ${resource.openai_chat.answer_gpt.content} vs ${resource.openrouter_chat.answer_claude.content}"
    }
  ]
  aiclResourceName = "final_answer"
}
```

### 3. CLI Flags

- `--output-file` - Save to JSON state files (default)
- `--output-docdb` - Save to PostgreSQL database
- `--output-stdout` - Print to console (default)
- `--no-stdout` - Disable console output
- `--quiet` - Minimal output (errors only)
- `--experiment-id ID` - Custom experiment identifier
- `--tags TAGS` - Comma-separated tags (e.g., `rag,demo,v1`)
- `--parallel` - Enable parallel execution (experimental)

See `docs/CLI_USAGE.md` for complete documentation.

---

## 🔧 Terraform Integration

### Seamless Extension

TerraMISO works **with** your existing Terraform code:

```hcl
# main.tf (existing Terraform - no changes!)
variable "db_sku_name" { }

resource "azurerm_postgresql_server" "main" {
  sku_name = var.db_sku_name  # TerraMISO optimizes this
  ...
}
```

```bash
# TerraMISO analyzes and optimizes
python run.py optimizer.aicl --output-file

# Extract AI recommendations
jq '.terraform_vars' state.json > terraform.tfvars

# Deploy with Terraform
terraform apply -var-file=terraform.tfvars
```

### Example: Azure Postgres Optimization

```bash
cd examples/terraform-integration
./deploy.sh

# Output:
# ✓ GPT-4: $475/mo, GP_Gen5_4
# ✓ Claude: $450/mo, GP_Gen5_4 + geo-redundant
# ✓ Gemini: $420/mo, GP_Gen5_2
# 🏆 Winner: Claude (best balance of cost + compliance)
# → Terraform deploys optimal config
```

See `examples/terraform-integration/README.md` for details.

---

## Architecture

### MISO Engine Flow

```
Input Specification
    ↓
┌─────────────────────────────────────┐
│  Multi-In: Provider Competition     │
│                                     │
│  GPT-4     → Analysis 1             │
│  Claude    → Analysis 2             │
│  Gemini    → Analysis 3             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  LLM-as-Judge Selection             │
│  Evaluates all → Picks best         │
└─────────────────────────────────────┘
    ↓
Single-Out: Optimal Solution
    ↓
Terraform Variables / Outputs
```

### Core Components

- **Parser**: HCL/AICL configuration parsing
- **Evaluator**: Variable resolution and interpolation
- **Planner**: Dependency graph and topological sorting
- **Executor**: Resource provisioning with MISO pattern
- **State Manager**: Persistent state (in-memory/SQLite/PostgreSQL)
- **Provider Registry**: Modular gRPC services

---

## 📊 Experiment System

Create and run declarative AI experiments:

```bash
# Run complete RAG demo with MISO
python run.py experiments/rag-demo/rag-demo-live.aicl

# With PostgreSQL output and tags
python run.py experiments/rag-demo/rag-demo-live.aicl \
  --output-docdb \
  --experiment-id rag-demo-$(date +%Y%m%d) \
  --tags rag,demo,pinecone
```

### Matrix Experiments

Test multiple configurations systematically:

```hcl
# Template with variables
resource "openai_chat" "analysis" {
  model = "{{ model }}"
  temperature = {{ temperature }}
  messages = [...]
}
```

Run matrix:
```bash
# Tests: gpt-4 @ 0.3, 0.5, 0.7 + gpt-4o @ 0.3, 0.5, 0.7
python run.py matrix-config.aicl --tags matrix,comparison
```

---

## 🎯 Why TerraMISO?

### For Terraform Users
✅ **Optimize configurations** - AI determines best settings  
✅ **Reduce costs** - Avoid over/under-provisioning  
✅ **Improve reliability** - Multi-provider validation  
✅ **No migration** - Works with existing `.tf` files  

### For AI Engineers
✅ **MISO pattern** - Reusable competitive optimization  
✅ **Provider flexibility** - Easy to add new LLMs  
✅ **Built-in evaluation** - LLM-as-Judge selection  
✅ **Experiment tracking** - PostgreSQL DocDB storage  

### For DevOps Teams
✅ **Self-healing** - AI detects and fixes issues  
✅ **Declarative** - Infrastructure as Code principles  
✅ **Observable** - OpenTelemetry integration  
✅ **Adoptable** - Include our templates in your systems  

---

## 📁 Project Structure

```
terramiso/
├── src/aicl/              # Core engine
│   ├── core/
│   │   ├── engine.py      # MISO orchestration
│   │   ├── parser.py      # HCL parsing
│   │   ├── evaluator.py   # Variable resolution
│   │   ├── planner.py     # Dependency graph
│   │   └── executor.py    # Resource execution
│   ├── state/             # State management
│   └── observability/     # OpenTelemetry
│
├── providers/             # gRPC providers
│   ├── openai/           # OpenAI provider
│   ├── openrouter/       # OpenRouter provider
│   ├── pinecone/         # Pinecone vector DB
│   └── ...
│
├── experiments/           # Example experiments
│   ├── terraform-integration/  # Terraform examples
│   ├── rag-demo/              # RAG pipeline
│   └── self-build/            # Self-modification
│
├── docs/                  # Documentation
├── outline/               # Technical specs
└── tests/                 # Test suite
```

---

## 📖 Documentation

- **[Setup Guide](docs/SETUP.md)** - Installation and configuration
- **[CLI Usage](docs/CLI_USAGE.md)** - Command-line reference
- **[Terraform Integration](examples/terraform-integration/README.md)** - Terraform examples
- **[Experiment Builder](docs/EXPERIMENT_BUILDER_GUIDE.md)** - Create experiments
- **[Architecture](docs/architecture/01_overview.md)** - System design
- **[Contributing](CONTRIBUTING.md)** - Development guide
- **[Outline Specs](outline/README.md)** - Complete technical specifications

---

## 🔬 Advanced Features

### Multi-Provider Testing
```aicl
# Test 3 providers simultaneously
resource "openai_chat" "test_gpt" { ... }
resource "openrouter_chat" "test_claude" { ... }
resource "openrouter_chat" "test_gemini" { ... }

# Judge selects winner
resource "openai_chat" "judge" { ... }
```

### Self-Healing Infrastructure
```aicl
# Monitor → Detect issue → AI proposes fix → Apply
resource "monitor" "health_check" { ... }
resource "openai_chat" "diagnosis" { ... }
resource "terraform_apply" "auto_fix" { ... }
```

### Cost Optimization
```aicl
# Compare configurations on cost/performance
resource "openai_chat" "cost_analysis" { ... }
# Outputs optimal price/performance ratio
```

---

## 🚢 Deployment

### CLI (Free Tier)
- In-memory or SQLite storage
- Local execution
- All core features

### Web Platform (Future - Paid Tier)
- PostgreSQL storage
- Multi-user support
- Team collaboration
- Advanced analytics

---

## 🤝 Adopting MISO in Your System

The **MISO pattern** is designed to be reusable:

1. **Include our templates** - Use our `.aicl` configurations
2. **Use our methods** - Competitive selection logic
3. **Offload optimization** - Let TerraMISO handle Multi-In Single-Out

Example integration:
```python
from terramiso import MISO

# Your system calls TerraMISO
optimizer = MISO(providers=['gpt-4', 'claude', 'gemini'])
best_solution = optimizer.compete(your_problem)
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src/aicl --cov-report=html

# CLI tests
pytest tests/test_cli.py -v
```

---

## 📜 License

GPL-3.0 - See [LICENSE](LICENSE)

---

## 🌟 Key Innovations

1. **MISO Pattern**: Multi-In Single-Out competitive optimization
2. **Terraform Extension**: Augments existing Terraform workflows
3. **Self-Constructing**: Can modify its own code
4. **Adoptable**: Other systems can use our MISO templates
5. **LLM-as-Judge**: Automated quality evaluation

---

## 🔗 Links

- **Repository**: https://github.com/zacharyelston/terramiso
- **Issues**: https://github.com/zacharyelston/terramiso/issues
- **Discussions**: https://github.com/zacharyelston/terramiso/discussions
- **Documentation**: [docs/README.md](docs/README.md)

---

**TerraMISO**: Extending Terraform/OpenTofu with AI-powered MISO optimization 🧠✨

**Remember**: We don't compete with Terraform - we extend it!
