# AICL Experiment Testing Guide

This guide explains how to systematically test different variables in your RAG pipeline using the matrix experiment system.

## Overview

The AICL framework now includes a comprehensive testing system for experimenting with:
- **Chat Models** - Different LLMs with various parameters
- **Embedding Models** - Various embedding providers and dimensions
- **Vector Operations** - Retrieval settings and configurations
- **RAG Components** - Chunking, indexing, and retrieval strategies

## Files

### 1. `test-variables.yaml`
Master configuration defining all testable variables and their ranges.

**Sections:**
- `chat_models` - Model selection, temperature, max_tokens, top_p, penalties
- `embedding_models` - OpenAI, Google, Azure embeddings with quality scores
- `text_splitter` - Chunk size, overlap, separators
- `pinecone` - Vector database settings (top_k, namespaces)
- `ragie` - Managed RAG settings (rerank, recency_bias, partitions)
- `judge` - LLM-as-Judge models and criteria
- `experiment_design` - Pre-configured test patterns
- `test_suites` - Ready-to-run experiment suites

### 2. `generate_experiments.py`
Script to auto-generate AICL configs from test-variables.yaml.

**Commands:**
```bash
# Show summary of available tests
python generate_experiments.py summary

# Generate single-variable tests
python generate_experiments.py single

# Generate multi-variable grid search
python generate_experiments.py multi

# Generate specific test suite
python generate_experiments.py suite smoke_test
python generate_experiments.py suite comprehensive_test
python generate_experiments.py suite cost_optimization
python generate_experiments.py suite quality_optimization
```

## Testable Variables by Component

### 🤖 Chat Models

| Variable | Range | Impact | Recommendation |
|----------|-------|--------|----------------|
| **model** | 5+ options | Cost, quality, speed | Start with gpt-4o-mini, upgrade if needed |
| **temperature** | 0.0 - 2.0 | Randomness | 0.0 for factual, 0.7 for creative |
| **max_tokens** | 50 - 4096 | Response length | 300-500 for most RAG tasks |
| **top_p** | 0.0 - 1.0 | Diversity | 0.9-1.0 (alternative to temperature) |
| **frequency_penalty** | -2.0 - 2.0 | Repetition | 0.5-1.0 to reduce repetition |
| **presence_penalty** | -2.0 - 2.0 | Topic diversity | 0.5-1.0 for varied responses |

**Available Models:**
- `gpt-4o-2024-08-06` (Naga) - $2.50/1M - Best quality
- `gpt-4o-mini` (Naga) - $0.15/1M - Best value
- `claude-3.5-sonnet` (OpenRouter) - $3.00/1M - High quality
- `mistralai/mistral-large` (OpenRouter) - $2.00/1M - Judge winner
- `anthropic/claude-3-haiku` (OpenRouter) - $0.25/1M - Fast & cheap

### 📐 Embedding Models

| Model | Provider | Dimensions | Quality | Cost/1M | Best For |
|-------|----------|------------|---------|---------|----------|
| **text-embedding-3-large** | Naga | 3072 | 8/10 ⭐ | $0.000065 | High quality |
| **gemini-embedding-001** | Naga | 3072 | 7/10 | $0.00 | Google ecosystem |
| **text-embedding-3-small** | Naga | 1536 | 5/10 | $0.00001 | High volume |
| text-embedding-ada-002 | OpenAI | 1536 | - | $0.00010 | Legacy |

**Variables:**
- `model` - Choose embedding model
- `dimensions` - Reduce for some models (trade quality for speed)

### 📊 Vector Retrieval (Pinecone)

| Variable | Range | Impact | Recommendation |
|----------|-------|--------|----------------|
| **top_k** | 1 - 50 | Context amount | 3-10 for most tasks |
| **namespace** | Multiple | Data isolation | Separate prod/dev/staging |
| **include_metadata** | true/false | Response size | true for filtering |

### 🚀 Ragie (Managed RAG)

**Upload Variables:**
- `mode` - "fast" (text only) or "hi_res" (images/tables)
- `media_mode` - Audio/video processing settings
- `partition` - Multi-tenant data isolation
- `metadata` - Custom filtering metadata

**Retrieval Variables:**

| Variable | Range | Impact | Recommendation |
|----------|-------|--------|----------------|
| **top_k** | 1 - 50 | Chunks returned | 5-8 (default 8) |
| **rerank** | true/false | Quality vs speed | true for best quality |
| **recency_bias** | true/false | Time sensitivity | true for time-sensitive queries |
| **partition** | Multiple | Data scope | Match upload partition |

### ✂️ Text Chunking

| Variable | Range | Impact | Recommendation |
|----------|-------|--------|----------------|
| **chunk_size** | 100 - 2000 | Context per chunk | 500-1000 chars |
| **chunk_overlap** | 0 - 500 | Context continuity | 50-200 chars |
| **separators** | Multiple | Split quality | Paragraph > line > word |

### ⚖️ LLM-as-Judge

**Judge Models:**
- `mistralai/mistral-large` - 9.7/10 reliability (your winner)
- `gpt-4o-2024-08-06` - Alternative judge
- `claude-3.5-sonnet` - Premium option

**Evaluation Criteria:**
- Accuracy (40%) - Factual correctness
- Completeness (30%) - Coverage
- Clarity (20%) - Structure
- Relevance (10%) - On-topic

## Test Suites

### 1. **Smoke Test** (2-5 minutes, 3 experiments)
Quick validation of basic functionality.

```bash
python generate_experiments.py suite smoke_test
python run_rag_graded_matrix.py experiments/suites/smoke_test/*.aicl
```

**Tests:**
- text-embedding-3-small + gpt-4o-mini
- text-embedding-3-large + gpt-4o
- gemini-embedding-001 + claude-3.5-sonnet

### 2. **Comprehensive Test** (30-60 minutes, 27 experiments)
Full evaluation across all major variables.

```bash
python generate_experiments.py suite comprehensive_test
python run_rag_graded_matrix.py experiments/suites/comprehensive_test/*.aicl
```

**Coverage:**
- 3 embeddings × 3 chat models × 3 temperatures

### 3. **Cost Optimization** (15-30 minutes, 12 experiments)
Find lowest cost with acceptable quality (score ≥ 7).

```bash
python generate_experiments.py suite cost_optimization
python run_rag_graded_matrix.py experiments/suites/cost_optimization/*.aicl
```

**Focus:**
- Naga vs OpenRouter providers
- gpt-4o-mini, gpt-4o, claude-3-haiku models

### 4. **Quality Optimization** (30-45 minutes, 18 experiments)
Maximize quality regardless of cost.

```bash
python generate_experiments.py suite quality_optimization
python run_rag_graded_matrix.py experiments/suites/quality_optimization/*.aicl
```

**Focus:**
- Best embeddings (text-embedding-3-large, gemini-embedding-001)
- Best chat models (gpt-4o, claude-3.5-sonnet)
- Temperature tuning (0.0, 0.3, 0.5)
- Rerank enabled/disabled

## Custom Experiments

### Single Variable Testing

Test one variable at a time while keeping others fixed:

```bash
python generate_experiments.py single
```

**Example tests:**
- Temperature: 0.0, 0.3, 0.7, 1.0
- Embedding: 3 models
- Top K: 3, 5, 10, 20

### Multi-Variable Grid Search

Test combinations of variables:

```bash
python generate_experiments.py multi
```

**Example grids:**
- Temperature (0.0, 0.5, 1.0) × Top K (3, 5, 10) = 9 experiments
- Embedding (2 models) × Top K (2 values) × Rerank (2 values) = 8 experiments

### A/B Testing

Compare specific variants:

**Naga vs OpenRouter:**
- Cost: $2.50 vs $5.00 per 1M tokens
- Quality: Compare performance

**Ragie vs Manual RAG:**
- Setup: Managed vs self-managed
- Maintenance: Automatic vs manual

## Metrics Tracked

### Performance
- `latency_ms` - Response time
- `tokens_per_second` - Throughput
- `end_to_end_time_ms` - Total time

### Cost
- `total_cost_usd` - Total experiment cost
- `cost_per_query` - Per-query cost
- `embedding_cost` - Embedding cost
- `chat_cost` - Chat model cost

### Quality
- `judge_score` - Overall quality (1-10)
- `accuracy_score` - Factual correctness
- `relevance_score` - On-topic rating
- `hallucination_count` - False information

### Resources
- `total_tokens` - All tokens used
- `prompt_tokens` - Input tokens
- `completion_tokens` - Output tokens
- `chunks_retrieved` - Context chunks

## Example Workflow

### Step 1: Define Test Goals

**Goal: Find optimal RAG configuration for production**

Constraints:
- Budget: < $0.01 per query
- Quality: ≥ 7/10 judge score
- Latency: < 3 seconds

### Step 2: Run Cost Optimization Suite

```bash
python generate_experiments.py suite cost_optimization
python run_rag_graded_matrix.py experiments/suites/cost_optimization/*.aicl
```

### Step 3: Analyze Results

```bash
# Results are saved in experiments/results/
cat experiments/results/results_*.json
```

Find best configuration meeting constraints.

### Step 4: Fine-Tune Winner

Create custom experiments around the winner:

```yaml
# In test-variables.yaml, update single_variable:
- variable: "chat_model.temperature"
  fixed: {model: "gpt-4o-mini", max_tokens: 300}  # Winner from step 3
  test_values: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]  # Fine-tune temperature
```

```bash
python generate_experiments.py single
python run_rag_graded_matrix.py experiments/auto_generated/*.aicl
```

### Step 5: Validate Production Config

Run smoke test with final configuration:

```bash
# Update smoke_test in test-variables.yaml with production config
python generate_experiments.py suite smoke_test
python run_rag_graded_matrix.py experiments/suites/smoke_test/*.aicl
```

## Best Practices

### 1. Start Small
- Run smoke_test first (3 experiments, 2-5 min)
- Validate framework is working
- Get baseline metrics

### 2. Focus on Impact
- Test high-impact variables first (model, embedding, top_k)
- Fine-tune low-impact variables later (penalties, top_p)

### 3. Track Costs
- Monitor `cost_per_query` in results
- Set budget limits before comprehensive tests
- Use cheaper models for experimentation

### 4. Use Quality Thresholds
- Define minimum acceptable quality (e.g., 7/10)
- Filter results by threshold
- Optimize cost within quality bounds

### 5. Document Findings
- Save winning configurations
- Note trade-offs discovered
- Update test-variables.yaml with learnings

## Variable Interaction Effects

### Temperature × Model
- High temp (1.0+) increases creativity but may reduce accuracy
- Low temp (0.0-0.3) keeps responses factual
- Effect varies by model (Claude more stable at high temp)

### Top K × Embedding Quality
- Higher quality embeddings need fewer chunks (lower top_k)
- Lower quality embeddings benefit from more chunks (higher top_k)
- text-embedding-3-large performs well at top_k=3-5
- text-embedding-3-small may need top_k=10-15

### Rerank × Top K
- Rerank improves quality when top_k is high (10+)
- Rerank adds latency (~500ms) but increases accuracy
- Cost-effective with top_k=10-15, rerank=true

### Chunk Size × Chunk Overlap
- Larger chunks (1000+) need less overlap (0-50)
- Smaller chunks (200-500) benefit from more overlap (100-200)
- Too much overlap increases index size and cost

## Troubleshooting

### Low Quality Scores (<5/10)
- Increase embedding quality (use text-embedding-3-large)
- Increase top_k (try 10-20 chunks)
- Enable rerank (Ragie only)
- Lower temperature (0.0-0.3 for factual tasks)

### High Costs
- Use Naga provider (50% cheaper than OpenRouter)
- Use gpt-4o-mini instead of gpt-4o
- Reduce max_tokens (300-500 for most tasks)
- Reduce top_k (3-5 chunks)
- Use text-embedding-3-small for embeddings

### High Latency
- Disable rerank (Ragie)
- Reduce top_k
- Use faster models (gpt-4o-mini, claude-3-haiku)
- Reduce max_tokens

### Inconsistent Results
- Lower temperature (0.0-0.3)
- Use deterministic models (gpt-4o at temp=0)
- Increase chunk overlap for better context
- Check for async processing delays (Ragie)

---

## Summary

**Quick Start:**
```bash
# 1. View available tests
python generate_experiments.py summary

# 2. Run smoke test (2-5 min)
python generate_experiments.py suite smoke_test
python run_rag_graded_matrix.py experiments/suites/smoke_test/*.aicl

# 3. Analyze results
cat experiments/results/results_*.json

# 4. Run optimization suite based on goals
python generate_experiments.py suite cost_optimization  # or quality_optimization
python run_rag_graded_matrix.py experiments/suites/*/.*aicl
```

**Key Files:**
- `test-variables.yaml` - Variable definitions and ranges
- `generate_experiments.py` - Experiment generator
- `run_rag_graded_matrix.py` - Experiment runner with grading
- `experiments/results/` - Output directory

**Remember:**
- Start with smoke_test for validation
- Use cost_optimization to find best value
- Use quality_optimization for best performance
- Track metrics to inform decisions
- Document winning configurations

---

*AICL Experiment Testing Guide - October 11, 2025*
