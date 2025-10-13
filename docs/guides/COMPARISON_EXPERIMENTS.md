# Multi-Provider Comparison Experiments

## Overview

AICL now supports comparative experiments that test the same question across multiple AI providers and use LLM-as-Judge to evaluate quality, accuracy, and value.

## Quick Start

### Simple Model Comparison (Working)

```bash
python run_simple_comparison.py
```

Compares:
- GPT-4o (temp=0.7) - Highest quality
- GPT-4o-mini (temp=0.7) - Best value  
- GPT-4o (temp=1.2) - Most creative

### Results Example

```
🏆 Winner: GPT-4o (88/100)
💰 Best Value: GPT-4o-mini (82/100, ~10x cheaper)
📊 Rankings:
  1. GPT-4o: 88/100 ($0.000548)
  2. GPT-4o creative: 85/100 ($0.000638)
  3. GPT-4o-mini: 82/100 ($0.000042)
```

## How It Works

### 1. Parallel Execution

```hcl
# Send same question to multiple providers
resource "openai_chat" "gpt4o" { ... }
resource "openai_chat" "gpt4o_mini" { ... }  
resource "openai_chat" "gpt4o_creative" { ... }
```

### 2. Collect Responses

Each provider generates a response with:
- Content (answer text)
- Usage (token counts)
- Cost (estimated)

### 3. LLM-as-Judge Evaluation

```hcl
resource "openai_chat" "judge" {
  model = "gpt-4o"
  temperature = 0.0
  
  messages = [{
    role = "user"
    content = <<-EOT
      Compare these responses:
      RESPONSE 1: ${resource.openai_chat.gpt4o.attributes.content}
      RESPONSE 2: ${resource.openai_chat.gpt4o_mini.attributes.content}
      ...
      
      Evaluate on: Accuracy, Clarity, Completeness, Conciseness
      Return JSON rankings
    EOT
  }]
}
```

### 4. Structured Results

Judge returns JSON:
```json
{
  "winner": "Response 1",
  "rankings": [...],
  "reasoning": "...",
  "best_for_cost": "Response 2"
}
```

## Use Cases

### 1. Model Selection

Find the best model for your use case:
- Accuracy vs Cost tradeoff
- Speed vs Quality comparison
- Creative vs Deterministic outputs

### 2. Prompt Optimization

Test different:
- Temperature settings
- System prompts
- Max tokens

### 3. Provider Benchmarking

Compare across:
- Different providers (OpenAI, Anthropic, etc)
- Different model versions
- Different pricing tiers

### 4. Quality Assurance

Ensure consistent:
- Response quality
- Factual accuracy
- Appropriate tone

## Available Experiments

### Working ✅

1. **experiments/provider-comparison-simple.aicl**
   - 3 OpenAI model variants
   - Temperature comparison
   - Cost-quality tradeoff analysis

### In Development 🔧

2. **experiments/provider-comparison.aicl**
   - OpenAI vs Naga vs Claude
   - Cross-provider comparison
   - (Requires Naga/Claude provider fixes)

## Creating Custom Comparisons

### Template

```hcl
terraform {
  required_providers {
    openai = { source = "aicl/openai" }
  }
}

variable "test_question" {
  type = string
  default = "Your question here"
}

# Test each variant
resource "openai_chat" "variant1" { ... }
resource "openai_chat" "variant2" { ... }

# Judge the results
resource "openai_chat" "judge" {
  messages = [{
    content = <<-EOT
      Compare:
      ${resource.openai_chat.variant1.attributes.content}
      ${resource.openai_chat.variant2.attributes.content}
      
      Evaluate and rank them
    EOT
  }]
}
```

### Best Practices

1. **Use consistent temperature for fair comparison**
   - Unless testing temperature itself

2. **Set judge temperature to 0.0**
   - For consistent, deterministic evaluation

3. **Define clear evaluation criteria**
   - Scientific accuracy
   - Clarity for audience
   - Conciseness
   - Engagement

4. **Track costs**
   - Monitor token usage
   - Calculate per-response costs
   - Identify best value

## Evaluation Metrics

### Standard Criteria (100 points)

- **Accuracy (40)**: Technical correctness
- **Clarity (30)**: Understandability for target audience
- **Completeness (20)**: Covers all aspects
- **Conciseness (10)**: Appropriate length

### Custom Criteria

Add your own:
- Code quality (for programming questions)
- Creative writing style
- Professional tone
- Safety/ethics considerations

## Integration with Self-Building

Comparison experiments can help the self-building system:

1. **Choose best provider** for code generation
2. **Optimize quality scores** through A/B testing
3. **Reduce costs** by finding best value models
4. **Improve prompts** via iterative comparison

## Cost Tracking

Automatic cost estimation for:
- **GPT-4o**: $2.50/$10 per 1M tokens (input/output)
- **GPT-4o-mini**: $0.15/$0.60 per 1M tokens
- **Claude 3 Haiku**: $0.25/$1.25 per 1M tokens

## Next Steps

1. Fix Naga/Claude providers for cross-provider comparison
2. Add streaming comparison for real-time evaluation
3. Implement batch experiments (test suites)
4. Create comparison dashboards

---

**Status**: ✅ Working for OpenAI models  
**Last Updated**: October 13, 2025
