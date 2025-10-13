# Azure AI Foundry Terraform Integration

## Overview

This document explains how **Azure AI Foundry Terraform** and **AICL** relate to each other, and how they could work together to provide end-to-end AI infrastructure provisioning.

## What is Azure AI Foundry Terraform?

Azure AI Foundry Terraform is Microsoft's infrastructure-as-code (IaC) solution for provisioning **cloud AI infrastructure** in Azure. It uses HashiCorp's Terraform with HCL syntax to create:

### Cloud Resources It Provisions:
- ✅ **AI Foundry Resources** (Cognitive Services accounts)
- ✅ **Model Deployments** (GPT-4o, GPT-4, embeddings)
- ✅ **Projects** (workspaces for AI development)
- ✅ **Connections** (Bing grounding, Azure Search, CosmosDB)
- ✅ **Security** (Private networking, managed identities, RBAC)
- ✅ **Storage** (Azure Storage, CosmosDB, Key Vault)

### Example Azure Terraform Code:
```hcl
# Provision an AI Foundry resource in Azure
resource "azapi_resource" "ai_foundry" {
  type      = "Microsoft.CognitiveServices/accounts@2025-06-01"
  name      = "my-ai-foundry"
  location  = "eastus"
  
  body = {
    kind = "AIServices"
    sku = {
      name = "S0"
    }
    properties = {
      allowProjectManagement = true
    }
  }
}

# Deploy GPT-4o model
resource "azapi_resource" "gpt4o_deployment" {
  type      = "Microsoft.CognitiveServices/accounts/deployments@2023-05-01"
  name      = "gpt-4o"
  parent_id = azapi_resource.ai_foundry.id
  
  body = {
    properties = {
      model = {
        format  = "OpenAI"
        name    = "gpt-4o"
        version = "2024-11-20"
      }
    }
  }
}
```

**Output**: Cloud infrastructure (servers, APIs, databases) running in Azure

---

## What is AICL (tofu-aicl)?

AICL is a declarative framework for provisioning **AI workflows and experiments** using those cloud resources. It also uses HCL syntax but focuses on AI application logic:

### AI Workflows It Provisions:
- ✅ **RAG Pipelines** (document loaders, embeddings, vector search)
- ✅ **AI Experiments** (matrix testing, model comparison)
- ✅ **Chat Agents** (conversational AI, context management)
- ✅ **Self-Building Systems** (AI generates its own code)
- ✅ **LLM-as-Judge** (quality evaluation, grading)

### Example AICL Code:
```hcl
# Use Azure-deployed resources to build a RAG workflow
resource "openai_embedding" "embed_docs" {
  model = "text-embedding-3-small"
  input = file("docs/spec.md")
  
  # This would connect to Azure AI Foundry endpoint
  endpoint = var.azure_foundry_endpoint
  api_key  = var.azure_foundry_key
}

resource "pinecone_index" "knowledge" {
  name       = "documentation"
  dimension  = 1536
  embeddings = openai_embedding.embed_docs.output
}

resource "openai_chat" "rag_query" {
  model = "gpt-4o"
  context = pinecone_index.knowledge.query(var.question)
  
  # Uses Azure-deployed GPT-4o
  endpoint = var.azure_foundry_endpoint
  api_key  = var.azure_foundry_key
  
  messages = [
    {
      role    = "user"
      content = var.question
    }
  ]
}
```

**Output**: AI workflows (pipelines, experiments, agents) running on infrastructure

---

## Key Difference

| Aspect | Azure AI Foundry Terraform | AICL (tofu-aicl) |
|--------|---------------------------|------------------|
| **Purpose** | Provision cloud infrastructure | Provision AI workflows |
| **Layer** | Infrastructure (servers, APIs) | Application (pipelines, agents) |
| **Creates** | AI Foundry resources, model deployments | RAG pipelines, experiments |
| **Syntax** | Terraform HCL | AICL HCL (similar but different resources) |
| **Scope** | Azure cloud resources | Cross-provider AI logic |
| **Example** | `azapi_resource "ai_foundry"` | `resource "openai_chat"` |
| **Analogy** | Terraform (servers, networking) | Kubernetes (app deployment) |

### Simple Analogy:
- **Azure Terraform** = Building a restaurant (kitchen, tables, utilities)
- **AICL** = Running the restaurant (recipes, menu, service workflow)

---

## How They Work Together

Azure AI Foundry Terraform and AICL are **complementary** - they work at different layers of the AI stack:

### Integration Flow:

```
┌─────────────────────────────────────────────────────────┐
│  1. Azure AI Foundry Terraform                          │
│     Provisions cloud infrastructure                     │
│                                                          │
│     terraform apply azure-infra.tf                      │
│     ↓                                                   │
│     Creates:                                            │
│     - AI Foundry Resource (endpoint: ai-foundry.azure)  │
│     - GPT-4o Deployment (model: gpt-4o)                 │
│     - Cosmos DB (for agent storage)                     │
│     - Azure Search (for vector search)                  │
└─────────────────────────────────────────────────────────┘
                            ↓
                   Outputs: endpoints, keys
                            ↓
┌─────────────────────────────────────────────────────────┐
│  2. AICL Workflow                                       │
│     Uses those resources for AI workflows               │
│                                                          │
│     python run.py rag-pipeline.aicl                     │
│                                                          │
│     variable "azure_endpoint" {                         │
│       default = "https://ai-foundry12345.azure.com"     │
│     }                                                   │
│                                                          │
│     resource "openai_chat" "answer" {                   │
│       model    = "gpt-4o"                               │
│       endpoint = var.azure_endpoint  # From Terraform   │
│     }                                                   │
└─────────────────────────────────────────────────────────┘
                            ↓
                   Outputs: AI results, experiments
```

### Example End-to-End Setup:

**Step 1: Provision Azure Infrastructure (Azure Terraform)**
```hcl
# azure-infra.tf
resource "azapi_resource" "ai_foundry" {
  type = "Microsoft.CognitiveServices/accounts@2025-06-01"
  name = "my-company-ai"
  
  body = {
    kind = "AIServices"
    properties = {
      allowProjectManagement = true
    }
  }
}

resource "azapi_resource" "gpt4o" {
  type      = "Microsoft.CognitiveServices/accounts/deployments@2023-05-01"
  name      = "gpt-4o"
  parent_id = azapi_resource.ai_foundry.id
  
  body = {
    properties = {
      model = {
        name = "gpt-4o"
      }
    }
  }
}

output "foundry_endpoint" {
  value = azapi_resource.ai_foundry.properties.endpoint
}

output "foundry_key" {
  value     = azapi_resource.ai_foundry.properties.primaryKey
  sensitive = true
}
```

Run: `terraform apply azure-infra.tf`

**Step 2: Use Resources in AICL Workflow**
```hcl
# rag-pipeline.aicl
variable "azure_foundry_endpoint" {
  type = string
  # From Terraform output
}

variable "azure_foundry_key" {
  type = string
  # From Terraform output (secret)
}

# Now build AI workflow using Azure resources
resource "azure_openai_chat" "generate" {
  model       = "gpt-4o"
  endpoint    = var.azure_foundry_endpoint
  api_key     = var.azure_foundry_key
  
  messages = [
    {
      role    = "system"
      content = "You are a helpful assistant."
    },
    {
      role    = "user"
      content = "Explain recursion"
    }
  ]
}

resource "azure_openai_chat" "grade" {
  model    = "gpt-4o"
  endpoint = var.azure_foundry_endpoint
  api_key  = var.azure_foundry_key
  
  messages = [
    {
      role    = "user"
      content = "Grade this response: ${azure_openai_chat.generate.content}"
    }
  ]
}
```

Run: `python run.py rag-pipeline.aicl`

---

## Benefits of Integration

### 1. **Complete Infrastructure-as-Code**
- Azure Terraform → Cloud infrastructure
- AICL → AI workflows on that infrastructure
- Both versioned, reproducible, declarative

### 2. **Enterprise Security**
- Azure Terraform provisions private networking, RBAC, managed identities
- AICL workflows inherit those security controls
- No hardcoded credentials in AICL configs

### 3. **Cost Optimization**
- Azure Terraform provisions right-sized resources
- AICL experiments track token usage and costs
- Combined view of infrastructure + AI costs

### 4. **Separation of Concerns**
- **Platform Team**: Manages Azure Terraform (infrastructure)
- **AI/ML Team**: Manages AICL workflows (experiments)
- Clear boundaries, independent evolution

### 5. **Multi-Environment Support**
```bash
# Dev environment
terraform apply -var="env=dev" azure-infra.tf
python run.py rag-pipeline.aicl --vars="endpoint=$DEV_ENDPOINT"

# Prod environment
terraform apply -var="env=prod" azure-infra.tf
python run.py rag-pipeline.aicl --vars="endpoint=$PROD_ENDPOINT"
```

---

## Implementation Roadmap

To integrate Azure AI Foundry Terraform with AICL:

### Phase 1: Azure Provider Support ✅ (Already Exists!)

**Good News**: AICL already has an Azure OpenAI provider at `providers/azure_openai/`!

**Current Capabilities**:
- ✅ Embeddings via Azure OpenAI (`azure_openai_embedding`)
- ✅ Deployment-based model access (Azure pattern)
- ✅ Environment variable configuration
- ✅ API version support (default: 2024-02-01)

**Existing Provider Configuration**:
```yaml
# providers/azure_openai/config.yaml
provider:
  name: azure_openai
  capabilities:
    types: [llm, embeddings]
    operations: [chat, embed, create_embedding]
  
  environment:
    required_vars:
      - AZURE_OPENAI_API_KEY
      - AZURE_OPENAI_ENDPOINT
    optional_vars:
      - AZURE_OPENAI_API_VERSION
      - AZURE_OPENAI_DEPLOYMENT_NAME
```

**Already Works in AICL**:
```hcl
resource "azure_openai_embedding" "embed_docs" {
  deployment = "text-embedding-3-small"  # Azure deployment name
  texts      = ["Hello", "World"]
  dimensions = 1536
}
```

**What Needs Enhancement**:
1. ✅ Add chat completion support (embeddings work, chat needs implementation)
2. ✅ Document how to use with Terraform-provisioned Azure resources
3. ✅ Add managed identity authentication option

### Phase 2: Complete Chat Support in Azure Provider

**Extend** the existing `providers/azure_openai/server.py`:

```python
# Add to existing AzureOpenAIProvider class
def _chat_completion(self, resource_id, config, type_name):
    """Chat completion using Azure OpenAI API"""
    deployment = config.get('deployment')
    messages = config.get('messages', [])
    temperature = config.get('temperature', 0.7)
    max_tokens = config.get('max_tokens', 1000)
    
    url = f"{self.endpoint}/openai/deployments/{deployment}/chat/completions"
    headers = {
        "api-key": self.api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    response = requests.post(
        f"{url}?api-version={self.api_version}",
        headers=headers,
        json=payload
    )
    # ... handle response
```

**New AICL Resource Support**:
```hcl
resource "azure_openai_chat" "answer" {
  deployment  = "gpt-4o"  # Azure deployment from Terraform
  temperature = 0.7
  max_tokens  = 500
  
  messages = [
    {
      role    = "user"
      content = "Explain recursion"
    }
  ]
}
```

### Phase 3: Terraform Output Integration
**Connect the Two Systems**:

```bash
# 1. Provision Azure infrastructure
terraform apply azure-infra.tf
terraform output -json > azure-outputs.json

# 2. Pass outputs to AICL
python run.py rag-pipeline.aicl \
  --vars-file=azure-outputs.json
```

**Auto-detection** in `run.py`:
```python
# Check if Terraform outputs exist
if os.path.exists("azure-outputs.json"):
    with open("azure-outputs.json") as f:
        azure_vars = json.load(f)
        # Inject as AICL variables
        config["variables"].update({
            "azure_foundry_endpoint": azure_vars["foundry_endpoint"]["value"],
            "azure_foundry_key": azure_vars["foundry_key"]["value"]
        })
```

### Phase 4: Unified State Management
**Track Both Layers**:

```json
{
  "terraform_state": {
    "azure_ai_foundry": {
      "id": "/subscriptions/.../ai-foundry-123",
      "endpoint": "https://ai-foundry-123.azure.com",
      "deployments": ["gpt-4o", "text-embedding-3-small"]
    }
  },
  "aicl_state": {
    "resources": {
      "azure_openai_chat-query": {
        "uses_deployment": "gpt-4o",
        "tokens_used": 1250,
        "cost": 0.015
      }
    }
  }
}
```

### Phase 5: Enterprise Features
- **Private Networking**: AICL respects Azure private endpoints
- **Managed Identity**: Use Azure AD auth instead of API keys
- **Cost Allocation**: Tag AICL resources with Azure cost centers
- **Compliance**: Inherit Azure security policies

---

## Comparison: Current AICL vs Azure-Integrated AICL

### Current AICL (Direct API):
```hcl
# rag-pipeline.aicl
resource "openai_chat" "answer" {
  model   = "gpt-4o"
  api_key = env.OPENAI_API_KEY  # Direct OpenAI API
  
  messages = [...]
}
```

### Azure-Integrated AICL (Using Existing Provider):
```hcl
# rag-pipeline.aicl
# Set Azure credentials from Terraform outputs
variable "azure_endpoint" {
  default = "https://ai-foundry-123.openai.azure.com"
}

variable "azure_api_key" {
  default = env.AZURE_OPENAI_API_KEY
}

resource "azure_openai_embedding" "embed" {
  deployment = "text-embedding-3-small"  # Azure deployment name
  texts      = ["Document content"]
  dimensions = 1536
}

# Future: Chat completion (Phase 2)
resource "azure_openai_chat" "answer" {
  deployment  = "gpt-4o"  # From Terraform deployment
  temperature = 0.7
  
  messages = [...]
}
```

**Advantages**:
- ✅ Enterprise security (private networking, RBAC)
- ✅ Cost tracking in Azure Cost Management
- ✅ Compliance with corporate policies
- ✅ Unified monitoring (Azure Monitor + AICL metrics)
- ✅ Multi-region deployment

**When to Use Each**:
- **Direct AICL**: Prototyping, personal projects, multi-cloud
- **Azure-Integrated**: Enterprise, production, compliance-heavy

---

## Next Steps

### For AICL Project:
1. ✅ **Azure OpenAI Provider exists** (`providers/azure_openai/`) - embeddings working
2. ⏳ **Add chat completion** to Azure provider (Phase 2)
3. ⏳ **Support Terraform Outputs** (read `terraform output -json`) (Phase 3)
4. ⏳ **Managed Identity Auth** (use Azure credentials) (Phase 5)
5. ✅ **Document Azure Integration** (this document)

### For Users:
1. **Use Current AICL**: Works great with any API (OpenAI, Naga, etc.)
2. **Evaluate Azure Terraform**: If you need enterprise features
3. **Integrate When Needed**: Start simple, add Azure when scaling

### Example Projects:
- `examples/azure-integration/` - Full Azure + AICL setup
- `examples/multi-cloud/` - Mix Azure + OpenAI + Naga
- `examples/enterprise-rag/` - Production-grade RAG with Azure

---

## Conclusion

**Azure AI Foundry Terraform** and **AICL** are complementary tools:
- Azure Terraform = Infrastructure layer (cloud resources)
- AICL = Application layer (AI workflows)

They can work together to provide end-to-end AI infrastructure-as-code, from cloud provisioning to AI experimentation. The current AICL works independently, but adding Azure provider support would enable enterprise integration for production use cases.

**Think of it as**:
- Azure Terraform: "Build the AI factory"
- AICL: "Run experiments in the factory"
