# 🧪 AI Evaluation Framework - Experiment Guide

## Overview

The AICL Evaluation Framework allows you to systematically compare AI models and contexts by:
- Testing multiple models against the same criteria
- Experimenting with different context packaging (full vs. trimmed)
- Grading responses with objective criteria
- Capturing detailed metrics (tokens, characteristics, focus)

## Quick Start

### Example 1: Model Comparison

Compare Claude vs GPT-4 on the same technical question:

```bash
python run.py experiment_demo.aicl
```

**Output:**
```
  + Resource 'claude_evaluation' created successfully.
    → Score: 5.0/8.0 (62.5%) ❌ FAILED
    → Response: 130 words (contains code)

  + Resource 'gpt4_evaluation' created successfully.
    → Score: 8.0/8.0 (100.0%) ✅ PASSED
    → Response: 288 words
```

### Example 2: Context Packaging

Test how context size affects responses:

```bash
python run.py experiment_context_packaging.aicl
```

Tests full directory vs. trimmed context to see which produces better focused responses.

## Creating Experiments

### 1. Define Grading Criteria

```hcl
resource "grade" "my_evaluation" {
  response = "${resource.chat.my_response.attributes.response}"
  context = "..."  # Optional: context provided to model
  
  criteria = [
    {
      name = "explains_tokens"
      type = "contains"
      value = "token"
      weight = 2
    },
    {
      name = "mentions_security"
      type = "contains"
      value = "security"
      weight = 2
    },
    {
      name = "reasonable_length"
      type = "min_length"
      value = "200"
      weight = 1
    }
  ]
}
```

### 2. Criteria Types

| Type | Description | Value |
|------|-------------|-------|
| `contains` | Response must contain text | String to find |
| `not_contains` | Response must NOT contain text | String to avoid |
| `min_length` | Minimum character count | Integer |
| `max_length` | Maximum character count | Integer |

### 3. Captured Metrics

Every grade resource captures:

**Scoring:**
- `total_score`: Points achieved
- `max_score`: Maximum possible points
- `percentage`: Score as percentage
- `passed`: Boolean (true if perfect score)

**Characteristics:**
- `response_length`: Character count
- `word_count`: Word count
- `contains_code`: Boolean (detects code blocks)
- `context_size`: Size of provided context

**Focus Analysis:**
- `focus_keywords`: Top 20 terms from context that appear in response

## Experiment Patterns

### Pattern 1: Model Showdown

Test multiple models with identical prompts:

```hcl
# Test Claude
resource "chat" "claude_response" {
  model = "anthropic/claude-3.5-sonnet"
  messages = [{ role = "user", content = "..." }]
}

resource "grade" "claude_score" {
  response = "${resource.chat.claude_response.attributes.response}"
  criteria = [...]
}

# Test GPT-4
resource "chat" "gpt4_response" {
  model = "openai/gpt-4"
  messages = [{ role = "user", content = "..." }]
}

resource "grade" "gpt4_score" {
  response = "${resource.chat.gpt4_response.attributes.response}"
  criteria = [...]
}
```

### Pattern 2: Context Variations

Test how context affects responses:

```hcl
# Full context
resource "loader_files" "full" {
  path = "./docs"
  glob = "**/*.md"
}

resource "chat" "with_full" {
  model = "anthropic/claude-3.5-sonnet"
  messages = [{
    role = "user"
    content = "Context: ${resource.loader_files.full.attributes.documents}\n\nQuestion: ..."
  }]
}

# Trimmed context
resource "loader_files" "trimmed" {
  path = "./docs"
  glob = "**/specific*.md"
}

resource "chat" "with_trimmed" {
  model = "anthropic/claude-3.5-sonnet"  
  messages = [{
    role = "user"
    content = "Context: ${resource.loader_files.trimmed.attributes.documents}\n\nQuestion: ..."
  }]
}
```

### Pattern 3: Focus Testing

Test what models remember from documentation:

```hcl
resource "grade" "focus_evaluation" {
  response = "${resource.chat.my_response.attributes.response}"
  context = "${resource.loader_files.docs.attributes.documents}"
  
  criteria = [
    { name = "rule1", type = "contains", value = "authentication", weight = 1 },
    { name = "rule2", type = "contains", value = "authorization", weight = 1 },
    { name = "rule3", type = "contains", value = "permissions", weight = 1 }
  ]
}
```

The `focus_keywords` field shows which terms from the context the model actually used.

## Analyzing Results

### Reading Scores

```
  → Score: 5.0/8.0 (62.5%) ❌ FAILED
```
- **5.0/8.0**: Achieved 5 points out of 8 possible
- **62.5%**: Percentage score
- **❌ FAILED**: Didn't achieve perfect score

### Characteristics

```
  → Response: 130 words (contains code)
```
- **Word count**: Response length
- **(contains code)**: Detected code blocks

### Token Usage

```
  → Tokens: 441.0 total (41.0 prompt + 400.0 completion)
```
- **Total**: Combined prompt + completion
- **Prompt**: Input tokens
- **Completion**: Generated tokens

## Available Resources

### Chat Resource (OpenRouter)
Generate responses from AI models:
- `model`: Model identifier (e.g., "anthropic/claude-3.5-sonnet")
- `messages`: Array of chat messages
- `max_tokens`: Maximum response length

### Grade Resource (Evaluator)
Score responses against criteria:
- `response`: Text to evaluate
- `context`: Optional context provided to model
- `criteria`: Array of grading rules

### Loader Resource (File Loader)
Load documentation/context:
- `path`: Directory to load from
- `glob`: File pattern (e.g., "**/*.md")

## Tips for Effective Experiments

1. **Use Identical Prompts**: When comparing models, keep prompts exactly the same
2. **Weight Criteria**: Assign higher weights to more important criteria
3. **Test Variations**: Try different context sizes and formats
4. **Track Token Costs**: Monitor token usage to optimize experiments
5. **Iterate**: Start simple, add complexity as you learn patterns

## Example Experiments

### Experiment: Which model is more concise?

```hcl
criteria = [
  { name = "complete", type = "contains", value = "token", weight = 2 },
  { name = "concise", type = "max_length", value = "300", weight = 1 }
]
```

### Experiment: Which context works better?

Run with full docs vs. focused docs, compare scores.

### Experiment: What does each model focus on?

Check `focus_keywords` to see which documentation terms each model emphasizes.

## Next Steps

1. **Run demos**: `python run.py experiment_demo.aicl`
2. **Create your own**: Copy and modify experiment configs
3. **Catalog findings**: Track which models/contexts perform best for your use case
4. **Optimize**: Use insights to choose best model and context strategy

---

**Framework Components:**
- `providers/evaluator/server.py` - Grading and metrics engine
- `experiment_*.aicl` - Example experiment configs
- Enhanced executor displays scores, characteristics, and metrics
