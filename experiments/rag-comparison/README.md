# RAG Provider Comparison Experiments

## Overview

Systematic comparison of RAG performance across multiple LLM providers using tofu-aicl source code as test data. Each experiment generates complete lineage tracking with git commit context for reproducible research.

## Experiment Design

### Phase 1: Basic 3-Provider Comparison
- **Providers**: OpenAI, Azure OpenAI, OpenRouter
- **Test Data**: tofu-aicl source code (docs, src, examples)
- **Metrics**: Response quality, latency, cost, accuracy
- **State Files**: One per provider with full lineage

### Phase 2: 3x3 Matrix (Provider × Context Size)
- **Providers**: 3 LLM providers
- **Context Sizes**: Small (2K tokens), Medium (8K tokens), Large (16K tokens)
- **Total Experiments**: 9 combinations
- **State Files**: Descriptive names with git SHA

### Phase 3: 6x3 Fine-Grained Analysis
- **Providers**: 3 LLM providers  
- **Context Variations**: 6 different sizes/configurations per provider
- **Total Experiments**: 18 combinations
- **Advanced Metrics**: Token usage, embedding quality, retrieval accuracy

## State File Naming Convention

```
experiments/rag-comparison/states/
├── {provider}_{context_size}_{git_sha8}.tfstate
├── openai_small_a1b2c3d4.tfstate
├── azure_medium_a1b2c3d4.tfstate
└── openrouter_large_a1b2c3d4.tfstate
```

## Experiment Metadata

Each state file contains complete lineage including:
- Git commit SHA and branch
- Experiment parameters (provider, context size, etc.)
- Source code snapshot metadata
- Performance metrics and costs
- Timestamp and duration tracking
- Error diagnostics and warnings

## Directory Structure

```
experiments/rag-comparison/
├── README.md                    # This file
├── config/
│   ├── providers.yaml          # LLM provider configurations
│   ├── test-data.yaml          # Source code test data sets
│   └── experiments.yaml        # Experiment matrix definitions
├── scripts/
│   ├── run-experiment.py       # Main experiment runner
│   ├── compare-results.py      # Analysis and comparison
│   └── generate-report.py      # Results visualization
├── states/                     # State files with lineage
│   ├── phase1/                 # 3-provider comparison
│   ├── phase2/                 # 3x3 matrix
│   └── phase3/                 # 6x3 fine-grained
├── data/
│   ├── source-snapshots/       # Git snapshots of test data
│   └── embeddings/             # Generated embeddings cache
└── results/
    ├── comparisons/            # Side-by-side analysis
    ├── reports/                # Generated reports
    └── visualizations/         # Charts and graphs
```

## Key Features

### Git Integration
- Automatic git SHA capture in state files
- Source code snapshot preservation
- Commit-based experiment tracking
- Reproducible experiment recreation

### Comprehensive Lineage
- Every RAG operation recorded
- Provider API calls tracked with costs
- Embedding generation lineage
- Query processing history
- Error and diagnostic tracking

### Comparative Analysis
- Cross-provider performance metrics
- Cost analysis per experiment
- Quality scoring and ranking
- Statistical significance testing
- Trend analysis across variations

## Usage Examples

```bash
# Run basic 3-provider comparison
./scripts/run-experiment.py --phase 1 --providers openai,azure,openrouter

# Run 3x3 matrix with context variations
./scripts/run-experiment.py --phase 2 --context-sizes small,medium,large

# Generate comparison report
./scripts/compare-results.py --phase 1 --output results/phase1-comparison.html

# Analyze cost trends
./scripts/generate-report.py --metric cost --providers all
```

## State File Benefits

1. **Reproducibility**: Exact git SHA allows recreation of any experiment
2. **Traceability**: Complete lineage from source code to final results
3. **Cost Tracking**: Per-operation cost analysis across providers
4. **Error Analysis**: Diagnostic tracking for debugging failures
5. **Performance Metrics**: Duration and resource usage per step
6. **Comparative Research**: Side-by-side analysis of provider differences
