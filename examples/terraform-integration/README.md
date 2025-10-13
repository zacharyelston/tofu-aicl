# TerraMISO + Terraform Integration Example

## Overview

This example shows how **TerraMISO** seamlessly augments traditional Terraform workflows with AI-driven decision making.

**Scenario**: Deploy Azure PostgreSQL with optimal configuration determined by multi-provider LLM analysis.

## The TerraMISO Advantage

### Traditional Terraform Problem:
```hcl
# Static configuration - guesswork and manual tuning
resource "azurerm_postgresql_server" "main" {
  sku_name = "GP_Gen5_4"  # Is this optimal? 🤷
  storage_mb = 102400     # Too much? Too little? 🤷
  backup_retention_days = 7  # Enough? 🤷
  geo_redundant_backup_enabled = true  # Necessary? 🤷
}
```

### With TerraMISO:
```bash
# AI analyzes your workload and recommends optimal config
./deploy.sh

# 3 LLM providers analyze requirements
# LLM-as-Judge selects best recommendation
# Terraform deploys with AI-optimized settings ✨
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Traditional Terraform Infrastructure Layer         │
│  (azure-postgres-optimized.tf)                     │
│                                                     │
│  • Azure Resource Group                            │
│  • PostgreSQL Server (with variables)              │
│  • Database                                        │
│  • Firewall Rules                                  │
└─────────────────────────────────────────────────────┘
                         ▲
                         │ Variables
                         │
┌─────────────────────────────────────────────────────┐
│  TerraMISO AI Decision Layer                       │
│  (postgres-config-optimizer.aicl)                  │
│                                                     │
│  • GPT-4 analysis      ┐                           │
│  • Claude 3.5 analysis ├─► LLM-as-Judge ──► Config │
│  • Gemini analysis     ┘                           │
└─────────────────────────────────────────────────────┘
                         ▲
                         │ Requirements
                         │
┌─────────────────────────────────────────────────────┐
│  Input Specification                               │
│                                                     │
│  • Workload profile                                │
│  • Budget constraints                              │
│  • Availability requirements                       │
└─────────────────────────────────────────────────────┘
```

## How It Works

### 1. Define Your Requirements
```hcl
# In postgres-config-optimizer.aicl
variable "app_profile" {
  default = "E-commerce app, 10K DAU, transaction-heavy"
}

variable "budget_constraint" {
  default = "$500/month maximum"
}

variable "availability_requirement" {
  default = "99.9% uptime SLA, disaster recovery"
}
```

### 2. TerraMISO Analyzes with Multiple LLMs
- **GPT-4**: Analyzes cost vs performance tradeoffs
- **Claude 3.5**: Evaluates security and compliance
- **Gemini**: Assesses availability and redundancy

Each provider returns a JSON recommendation:
```json
{
  "sku_name": "GP_Gen5_4",
  "storage_mb": 102400,
  "backup_retention_days": 30,
  "geo_redundant_backup": true,
  "reasoning": "General Purpose tier provides best balance...",
  "estimated_monthly_cost": "$450"
}
```

### 3. LLM-as-Judge Selects Best Config
A meta-LLM evaluates all three recommendations and selects optimal configuration:
```json
{
  "selected_provider": "claude",
  "decision_reasoning": "Claude's recommendation best balances cost ($450/mo) with compliance requirements (30-day retention) while meeting 99.9% SLA through geo-redundancy.",
  "terraform_vars": {
    "db_sku_name": "GP_Gen5_4",
    "db_storage_mb": 102400,
    "backup_retention_days": 30,
    "geo_redundant_backup": true
  }
}
```

### 4. Terraform Deploys with AI-Optimized Config
```bash
# Auto-generated terraform.tfvars
db_sku_name = "GP_Gen5_4"
db_storage_mb = 102400
backup_retention_days = 30
geo_redundant_backup = true

# Terraform applies with optimal settings
terraform apply -var-file=terraform.tfvars
```

## Usage

### Prerequisites
```bash
# TerraMISO setup
pip install -e .

# Terraform
terraform --version  # >= 1.0

# Azure CLI
az login

# Required API keys
export OPENAI_API_KEY="sk-..."
export OPENROUTER_API_KEY="sk-..."
export AZURE_POSTGRES_PASSWORD="..."
```

### Quick Start
```bash
# Run integrated deployment
./examples/terraform-integration/deploy.sh
```

### Step-by-Step

**1. Run AI analysis:**
```bash
python run.py examples/terraform-integration/postgres-config-optimizer.aicl \
  --output-file \
  --experiment-id azure-optimizer
```

**2. Review AI recommendations:**
```bash
cat terraform.tfstate.d/azure-optimizer.tfstate | \
  jq '.resources[] | select(.name == "final_config") | .attributes.content'
```

**3. Generate terraform.tfvars:**
```bash
# Extract AI-recommended variables
FINAL_CONFIG=$(cat terraform.tfstate.d/azure-optimizer.tfstate | \
  jq -r '.resources[] | select(.name == "final_config") | .attributes.content')

echo "$FINAL_CONFIG" | jq -r '.terraform_vars' > terraform.tfvars
```

**4. Deploy with Terraform:**
```bash
cd examples/terraform-integration
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## Key Benefits

### 🧠 AI-Driven Optimization
- Analyzes workload requirements intelligently
- Considers cost, performance, compliance, availability
- Multi-provider consensus reduces single-model bias

### 🔄 Seamless Integration
- Works with existing Terraform code
- No special syntax required in `.tf` files
- TerraMISO handles AI logic in separate `.aicl` files

### 💰 Cost Optimization
- Avoids over-provisioning (wastes money)
- Avoids under-provisioning (risks performance)
- AI finds sweet spot for your specific workload

### 📊 Transparent Decisions
- See reasoning from each LLM
- Understand why final config was chosen
- Full audit trail in state files

### 🛡️ Self-Healing Potential
- Monitor actual performance
- Re-run analysis if workload changes
- Automatically adjust configuration

## Example Output

```
🚀 TerraMISO + Terraform Deployment Pipeline
==============================================

Step 1: Running TerraMISO AI analysis...
Testing 3 LLM providers to determine optimal Postgres configuration...

✓ GPT-4 recommendation: $475/mo, GP_Gen5_4, 100GB
✓ Claude recommendation: $450/mo, GP_Gen5_4, 100GB, geo-redundant
✓ Gemini recommendation: $420/mo, GP_Gen5_2, 75GB

✅ AI analysis complete!

Step 2: LLM-as-Judge selecting optimal configuration...

Selected: Claude's recommendation
Reasoning: Best balances cost with compliance and availability requirements.

Step 3: Generating terraform.tfvars...

db_sku_name = "GP_Gen5_4"
db_storage_mb = 102400
backup_retention_days = 30
geo_redundant_backup = true

Step 4: Running Terraform plan...

Terraform will perform the following actions:

  # azurerm_postgresql_server.main will be created
  + resource "azurerm_postgresql_server" "main" {
      + sku_name                       = "GP_Gen5_4"      # AI-optimized ✨
      + storage_mb                     = 102400           # AI-optimized ✨
      + backup_retention_days          = 30               # AI-optimized ✨
      + geo_redundant_backup_enabled   = true             # AI-optimized ✨
      ...
    }

Plan: 3 to add, 0 to change, 0 to destroy.

✅ Deployment complete!

🎉 TerraMISO enhanced your Terraform deployment with AI-driven optimization!
```

## Real-World Use Cases

### 1. Database Right-Sizing
- Analyze actual workload patterns
- LLM recommends optimal instance size
- Terraform deploys cost-effective configuration

### 2. Security Compliance
- LLM analyzes compliance requirements (HIPAA, SOC2, etc.)
- Recommends security configurations
- Terraform applies compliant infrastructure

### 3. Multi-Region Strategy
- LLM evaluates latency, cost, and availability
- Recommends optimal region distribution
- Terraform deploys multi-region setup

### 4. Disaster Recovery Planning
- AI analyzes RTO/RPO requirements
- Recommends backup and replication strategy
- Terraform implements DR infrastructure

## TerraMISO vs Traditional Terraform

| Aspect | Traditional Terraform | With TerraMISO |
|--------|----------------------|----------------|
| **Configuration** | Manual/static | AI-optimized |
| **Decision Making** | Human guess | Multi-LLM analysis |
| **Optimization** | Trial and error | Data-driven |
| **Adaptation** | Manual updates | Self-adjusting |
| **Cost Efficiency** | Unknown | Analyzed & optimized |
| **Compliance** | Manual checklist | AI-verified |

## Integration with .tf Files

TerraMISO is **100% compatible** with existing Terraform:

```hcl
# Your existing main.tf - no changes needed!
variable "db_sku_name" {
  type = string
  default = "B_Gen5_2"  # Fallback
}

resource "azurerm_postgresql_server" "main" {
  sku_name = var.db_sku_name  # TerraMISO populates this
  ...
}
```

Just add TerraMISO analysis as a **pre-deployment step**:
```bash
# 1. AI analysis (new)
python run.py optimizer.aicl --output-file

# 2. Extract vars (new)
jq '.terraform_vars' state.json > terraform.tfvars

# 3. Deploy (existing workflow)
terraform apply -var-file=terraform.tfvars
```

## Direct HCL Integration (Coming Soon)

Future versions will support direct `.tf` file integration:

```hcl
# main.tf with embedded TerraMISO blocks
terraform {
  required_providers {
    terramiso = {
      source = "terramiso/terramiso"
    }
  }
}

# TerraMISO analysis embedded in HCL
data "terramiso_optimizer" "postgres" {
  workload_profile = "E-commerce, 10K DAU"
  budget = 500
  providers = ["openai", "claude", "gemini"]
}

# Use AI recommendations directly
resource "azurerm_postgresql_server" "main" {
  sku_name = data.terramiso_optimizer.postgres.recommended_sku
  storage_mb = data.terramiso_optimizer.postgres.recommended_storage
  ...
}
```

## License

GPL-3.0 - Same as TerraMISO core

---

**TerraMISO**: Making Terraform smarter with AI 🧠✨
