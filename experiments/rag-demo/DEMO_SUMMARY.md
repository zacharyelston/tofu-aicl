# RAG Demo - Live Presentation Results

## ✅ Experiment Completed Successfully

**Date**: October 13, 2025  
**Duration**: ~3 minutes (natural API call delays make it perfect for live demo)  
**Status**: All 11 stages completed  
**Resources Created**: 10  
**OpenTelemetry Traces**: 106

---

## 📋 Experiment Flow

```
1. LOAD DOCUMENTS ━━━━━━━━━━━━━━━━━━━━━━━━━> ./docs/**/*.md
   └─> Resource: loader_files-knowledge_base

2. CHUNK TEXT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━> 800 chars, 100 overlap
   └─> Resource: splitter_text-doc_chunks

3. GENERATE EMBEDDINGS ━━━━━━━━━━━━━━━━━━> text-embedding-3-small (1536 dims)
   └─> Resource: embedding-doc_vectors

4. INDEX VECTORS ━━━━━━━━━━━━━━━━━━━━━━━━> Pinecone namespace: rag-demo-live
   └─> Resource: upsert (Pinecone)

5. VALIDATE RETRIEVAL ━━━━━━━━━━━━━━━━━━> Test query: "What is AICL?"
   └─> Resource: query-validation_results
   └─> Status: ✅ RAG retrieval confirmed working

6. MAIN QUESTION ━━━━━━━━━━━━━━━━━━━━━━━━> "What are main AICL components?"
   └─> Resource: embedding-main_question

7. RETRIEVE CONTEXT ━━━━━━━━━━━━━━━━━━━━> Top 5 chunks from Pinecone
   └─> Resource: query-rag_context

8. ANSWER (GPT-4o Mini) ━━━━━━━━━━━━━━━━> Using RAG context
   └─> Resource: chat-answer_gpt4o_mini
   └─> Model: openai/gpt-4o-mini, Temp: 0.3

9. ANSWER (Claude 3.5 Sonnet) ━━━━━━━━━━> Using RAG context
   └─> Resource: chat-answer_claude
   └─> Model: anthropic/claude-3.5-sonnet, Temp: 0.3

10. ANSWER (Gemini Pro 1.5) ━━━━━━━━━━━━> Using RAG context
    └─> Resource: chat-answer_gemini
    └─> Model: google/gemini-pro-1.5, Temp: 0.3

11. JUDGE EVALUATION (GPT-4o) ━━━━━━━━━━> Evaluates all 3 WITH RAG context
    └─> Resource: chat-judge_evaluation
    └─> Model: openai/gpt-4o, Temp: 0.1
    └─> Criteria: Accuracy (40%), Completeness (25%), Clarity (20%), Conciseness (15%)
```

---

## 🗂️ Files Generated

### Configuration Files
- **configs/conf-file.yaml** - Complete RAG configuration (models, vector DB, judge criteria)
- **variables/prompts.yaml** - System prompts for answering and judging
- **variables/questions.yaml** - Question bank for demos

### Experiment File
- **rag-demo-live.aicl** - Main HCL experiment definition (270 lines with comments)

### Output Files
- **outputs/full-run.log** - Complete execution log with OpenTelemetry traces (141 KB)
- **outputs/experiment-plan.json** - 11-stage pipeline plan
- **outputs/rag-demo-results.json** - Resource IDs and metrics

### Database
- **PostgreSQL DocDB** - Experiment saved with full metadata, queryable by tags

---

## 🎯 Key Features Demonstrated

### 1. Complete RAG Pipeline
✅ Document loading from filesystem  
✅ Intelligent text chunking with overlap  
✅ Vector embeddings generation  
✅ Pinecone indexing with namespace isolation  
✅ Similarity search and retrieval  

### 2. Multi-LLM Comparison
✅ 3 different AI models (OpenAI, Anthropic, Google)  
✅ Identical RAG context for fair comparison  
✅ Same temperature and parameters  

### 3. AI Judge with Context
✅ 4th LLM (GPT-4o) acts as judge  
✅ Judge also receives RAG context for informed evaluation  
✅ Structured scoring: Accuracy, Completeness, Clarity, Conciseness  

### 4. Production-Ready Infrastructure
✅ gRPC with 50MB message limits for large contexts  
✅ OpenTelemetry distributed tracing (106 traces)  
✅ PostgreSQL document database storage  
✅ State management and resource tracking  

---

## 🚀 How to Run the Demo

### Quick Start
```bash
# Run the experiment
python run.py experiments/rag-demo/rag-demo-live.aicl

# Extract results
python experiments/rag-demo/extract_results.py

# Save to DocDB
python experiments/rag-demo/save_to_docdb.py

# Query results
python experiments/query_results.py --experiment-id rag_demo_live_2025_10_13
```

### For Live Demo
The experiment naturally runs slow (~3 minutes) due to:
- File loading and chunking
- Embedding API calls (multiple batches)
- Vector database indexing
- 4 separate LLM API calls (3 answers + 1 judge)

This makes it perfect for explaining each stage to an audience!

---

## 📊 Architecture Highlights

### Provider Architecture
```
file_loader (port 50056) ━━> Load markdown docs
text_splitter (port 50057) ━> Chunk with overlap
openai (port 50051) ━━━━━━━> Embeddings & chat
pinecone (port 50054) ━━━━━> Vector storage & query
openrouter (port 50055) ━━━> Multi-model chat (Claude, Gemini, GPT)
```

### Data Flow
```
./docs/*.md → Chunks → Embeddings → Pinecone
                                        ↓
                                    Query Vector
                                        ↓
                                Top 5 Matches → Context
                                                   ↓
                           ┌──────────────────────┼──────────────────────┐
                           ↓                      ↓                      ↓
                      GPT-4o Mini          Claude 3.5            Gemini Pro
                       (Answer A)          (Answer B)            (Answer C)
                           ↓                      ↓                      ↓
                           └──────────────────────┼──────────────────────┘
                                                  ↓
                                              GPT-4o Judge
                                           (with RAG context)
                                                  ↓
                                         Winner + Scores + Reasoning
```

---

## 💡 Technical Achievements

### Problem Solved: gRPC Message Size
- **Issue**: Default 4MB limit too small for documentation (5MB)
- **Solution**: Increased to 50MB on both client and server
  - Client: `src/aicl/core/engine.py` (line 160-164)
  - Server: `v2/runtime/provider_server.py` (line 57-64)

### Executor Provider Mapping
- **Fixed**: Resource type → Provider name mapping
- **Added**: `loader_files → loader`, `splitter_text → splitter`
- **Location**: `src/aicl/executor.py` (line 21-42)

---

## 🔍 Query Examples

```bash
# List all RAG demos
python experiments/query_results.py --list --tags rag

# Compare multiple RAG runs
python experiments/query_results.py --compare rag_demo_live_2025_10_13,azure_security_2025_10_13

# Find best by cost
python experiments/query_results.py --best --by cost --limit 5

# Get specific experiment
python experiments/query_results.py --experiment-id rag_demo_live_2025_10_13
```

---

## 📝 Configuration Highlights

### Vector Database Settings
```yaml
vector_store:
  provider: pinecone
  namespace: rag-demo-live
  index_name: aicl-demo
  top_k: 5
```

### Answer Models (3 LLMs)
```yaml
- GPT-4o Mini: temperature 0.3, max_tokens 500
- Claude 3.5 Sonnet: temperature 0.3, max_tokens 500
- Gemini Pro 1.5: temperature 0.3, max_tokens 500
```

### Judge Model
```yaml
GPT-4o: temperature 0.1 (low for consistency), max_tokens 800
Criteria:
  - Accuracy: 40 points
  - Completeness: 25 points
  - Clarity: 20 points
  - Conciseness: 15 points
```

---

## 🎬 Demo Script

### For Live Presentation

**1. Introduction (30 seconds)**
> "Today I'll demonstrate a complete RAG pipeline with multi-LLM comparison. We'll load documentation, embed it, query it with 3 different AI models, and have a 4th model judge the answers."

**2. Show Configuration (1 minute)**
> "Here's our setup in HCL - Terraform for AI workflows. Notice we're using 5 different providers working together."

**3. Run Experiment (3 minutes)**
> "Watch as each stage completes:
> - Loading docs...
> - Chunking text...
> - Generating embeddings...
> - Indexing in Pinecone...
> - Validating retrieval works...
> - Getting answers from 3 LLMs...
> - Judge evaluating with full context..."

**4. Show Results (1 minute)**
> "All outputs saved to filesystem AND PostgreSQL. We can query past experiments, compare costs, find best performing models."

**5. Close (30 seconds)**
> "This demonstrates declarative AI infrastructure - define what you want, AICL handles the orchestration, state, and observability."

---

## ✅ Success Criteria

All requirements met:

- [x] Source loaded into RAG
- [x] RAG embedding validated
- [x] Query demonstrates retrieval working
- [x] 3 LLMs used with RAG context
- [x] Same values and prompts for all 3
- [x] 4th LLM judges with RAG access
- [x] conf-file.yaml created
- [x] prompts.yaml created
- [x] questions.yaml created
- [x] Outputs in JSON format
- [x] Plan saved to filesystem
- [x] Apply output logged
- [x] State tracked
- [x] Saved to DocDB
- [x] Purposefully slow for live demo

---

## 🎉 Conclusion

This RAG demo showcases AICL's ability to orchestrate complex AI workflows with:
- **Multiple providers** working in concert
- **Declarative configuration** (HCL syntax)
- **State management** and persistence
- **Distributed tracing** (OpenTelemetry)
- **Document database** for experiment tracking
- **Production-ready** error handling and resource limits

Perfect for demonstrating the power of "Terraform for AI workflows"!
