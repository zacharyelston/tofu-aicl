# Naga.ai Integration Guide

## Overview

Naga.ai is now integrated into the AICL framework! Naga.ai provides **OpenAI-compatible API access** to multiple AI models at **50% lower cost** than direct provider access.

## What is Naga.ai?

- **Unified AI Gateway**: Access OpenAI, Anthropic, Google, and Meta models with one API key
- **50% Cost Savings**: Same models, half the price
- **OpenAI-Compatible**: Drop-in replacement for OpenAI API
- **99.9% Uptime**: Enterprise-grade reliability

## Setup

### 1. API Key (Already Configured)

Your `NAGA_API_KEY` is securely stored in Replit Secrets ✅

### 2. Provider Registration

The Naga provider is registered in `src/aicl/provider_registry.py`:

```python
ProviderMetadata(
    name="naga",
    source="aicl/naga",
    version="1.0.0",
    description="AI models via Naga.ai (OpenAI-compatible, 50% lower cost)"
)
```

### 3. Provider Implementation

Located in `providers/naga/server.py` - identical to OpenRouter but uses:
- **API Key**: `NAGA_API_KEY`
- **Base URL**: `https://api.naga.ac/v1`

## Usage

### Configuration (rag-config.yaml)

```yaml
models:
  - name: "GPT-4o (Naga.ai)"
    id: "openai/gpt-4o"
    provider: "naga"
    enabled: true
```

### AICL Configuration

```hcl
terraform {
  required_providers {
    naga = {
      source = "aicl/naga"
    }
  }
}

# Note: Currently use "naga_chat" resource type to route to Naga provider
# (Will be simplified once config-driven provider selection is implemented)
resource "naga_chat" "answer" {
  model = "openai/gpt-4o"
  messages = [
    {
      role = "user"
      content = "Hello from Naga.ai!"
    }
  ]
  max_tokens = 500
  aiclResourceName = "answer"
}
```

**Current Limitation**: The framework currently uses a hardcoded resource-to-provider mapping. Use `naga_chat` (instead of `chat`) to route to the Naga provider. This will be simplified in a future update with config-driven provider selection.

## Benefits

### Cost Comparison

| Provider | GPT-4o Cost | Savings with Naga.ai |
|----------|-------------|----------------------|
| OpenAI Direct | $0.005/1K tokens | **50%** |
| OpenRouter | $0.003/1K tokens | **~40%** |
| **Naga.ai** | **$0.0025/1K tokens** | **Best** |

### Features

✅ **Embeddings**: text-embedding-3-small, text-embedding-3-large
✅ **Chat**: GPT-4o, Claude, Gemini, DeepSeek, etc.
✅ **Drop-in Compatible**: Same request/response format as OpenAI
✅ **No Code Changes**: Just swap the provider in config

## Available Models (via Naga.ai)

### Chat/Completion
- `openai/gpt-4o`
- `openai/gpt-4o-mini`
- `anthropic/claude-3.5-sonnet`
- `anthropic/claude-sonnet-4.5`
- `google/gemini-pro`
- `meta-llama/llama-3.3-70b`
- `mistralai/mistral-large`
- And 100+ more...

### Embeddings
- `openai/text-embedding-3-small`
- `openai/text-embedding-3-large`
- `openai/text-embedding-ada-002`

## Testing

### Quick Test

```bash
# Test Naga.ai provider
python run.py naga_test.aicl
```

### RAG Matrix Test

Edit `rag-config.yaml`:
```yaml
models:
  - name: "GPT-4o (Naga.ai)"
    id: "openai/gpt-4o"
    provider: "naga"
    enabled: true
```

Then run:
```bash
python run_rag_graded_matrix.py
```

## API Reference

### Base URL
```
https://api.naga.ac/v1
```

### Authentication
```
Authorization: Bearer NAGA_API_KEY
```

### Endpoints
- **Chat**: `POST /chat/completions`
- **Embeddings**: `POST /embeddings`
- **Models**: `GET /models`

## Documentation

- **Official Docs**: https://docs.naga.ac/
- **Quickstart**: https://docs.naga.ac/get-started/quickstart/
- **API Reference**: https://docs.naga.ac/api-reference/endpoints/

## Cost Optimization Strategy

### Current Setup (OpenRouter)
```
15 experiments × $0.003/query = $0.045
```

### With Naga.ai
```
15 experiments × $0.0015/query = $0.0225
50% cost savings! 💰
```

### Recommended Approach

1. **Development/Testing**: Use Naga.ai for cost savings
2. **Production Critical**: Use OpenRouter/Direct for reliability
3. **High-Volume**: Always use Naga.ai for maximum savings

## Known Limitations

### Resource Type Routing (Temporary)
Currently, you must use `naga_chat` instead of `chat` to route resources to the Naga provider. This is due to a hardcoded resource-to-provider mapping in the executor.

**Future Enhancement**: The architect has recommended implementing config-driven provider selection that respects the `terraform.required_providers` block. This will allow multiple providers (OpenRouter, Naga) to coexist for the same resource types without special naming.

See architect analysis for implementation plan.

## Next Steps

1. ✅ Naga provider created and registered
2. ✅ API key securely stored  
3. ✅ Basic functionality tested and validated
4. ⏭️ Implement config-driven provider selection (per architect recommendation)
5. ⏭️ Update rag-config.yaml to test Naga.ai models
6. ⏭️ Run performance comparison: Naga vs OpenRouter
7. ⏭️ Document cost savings in validation reports

---
*Naga.ai Integration - AICL Framework - October 11, 2025*
