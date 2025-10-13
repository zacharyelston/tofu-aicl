# RAG Demo - Live Presentation

## Overview
This experiment demonstrates a complete RAG (Retrieval-Augmented Generation) pipeline with multi-LLM comparison and AI-powered evaluation.

## Experiment Flow

```
1. LOAD DOCUMENTS
   └─> Load ./docs/**/*.md files

2. CHUNK TEXT
   └─> Split into 800-char chunks (100-char overlap)

3. GENERATE EMBEDDINGS
   └─> OpenAI text-embedding-3-small (1536 dims)

4. INDEX VECTORS
   └─> Store in Pinecone (namespace: rag-demo-live)

5. VALIDATE RETRIEVAL
   └─> Test query to confirm RAG is working

6. MAIN QUESTION
   └─> "What are the main architectural components of the AICL engine?"

7. RETRIEVE CONTEXT
   └─> Get top 5 relevant chunks from Pinecone

8. GET 3 ANSWERS
   ├─> GPT-4o Mini (OpenRouter)
   ├─> Claude 3.5 Sonnet (OpenRouter)
   └─> Gemini Pro 1.5 (OpenRouter)

9. JUDGE EVALUATION
   └─> GPT-4o evaluates all 3 answers WITH RAG context
```

## Files

- **configs/conf-file.yaml**: Complete experiment configuration
- **variables/prompts.yaml**: System prompts for answering and judging
- **variables/questions.yaml**: Question bank for demos
- **rag-demo-live.aicl**: Main experiment orchestration

## Running the Experiment

```bash
# Run the experiment
python run.py experiments/rag-demo/rag-demo-live.aicl

# Outputs will be saved to:
# - experiments/rag-demo/outputs/rag-demo-live-results.json
# - experiments/rag-demo/states/rag-demo-live.tfstate
# - PostgreSQL DocDB (queryable via experiments/query_results.py)
```

## Expected Outputs

### 1. Plan Output
- Shows dependency graph
- Lists all resources to be created
- Displays execution order

### 2. Apply Output
- Real-time resource creation
- Embedding progress
- Vector indexing status
- LLM response streaming

### 3. State File
- Complete resource state
- Vector IDs and metadata
- Model responses
- Token usage

### 4. Results JSON
```json
{
  "validation_results": "...",
  "retrieved_context": "...",
  "answer_gpt4o_mini": "...",
  "answer_claude": "...",
  "answer_gemini": "...",
  "judge_verdict": {
    "evaluations": [...],
    "winner": "model_name",
    "winner_reasoning": "..."
  },
  "total_tokens": {...}
}
```

## Key Features for Demo

1. **Verbose Output**: Each step clearly labeled and visible
2. **RAG Validation**: Test query confirms retrieval is working
3. **Multi-LLM Comparison**: 3 models with identical RAG context
4. **Judge with Context**: Evaluator also uses RAG for fair assessment
5. **Complete Traceability**: All inputs, outputs, and state persisted

## Judging Criteria

The GPT-4o judge evaluates on:
- **Accuracy (40%)**: Correct use of context, no hallucinations
- **Completeness (25%)**: Addresses all question parts
- **Clarity (20%)**: Well-structured, easy to understand
- **Conciseness (15%)**: Appropriate detail level

## Questions Used

**Main Question:**
> "What are the main architectural components of the AICL engine and how do they work together?"

**Validation Question:**
> "What is AICL and what problem does it solve?"

## Models Compared

1. **GPT-4o Mini** (OpenAI) - Fast, cost-effective
2. **Claude 3.5 Sonnet** (Anthropic) - Strong reasoning
3. **Gemini Pro 1.5** (Google) - Large context window

## Judge Model

**GPT-4o** (OpenAI) - Most capable model for fair evaluation with access to source context
