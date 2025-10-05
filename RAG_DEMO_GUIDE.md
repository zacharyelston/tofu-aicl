# 🚀 RAG Demo Guide - Step-by-Step Tutorial

## What This Demo Does

This demo shows how to build a **Retrieval-Augmented Generation (RAG)** system using declarative AICL syntax:

1. **Index Documentation**: Load 6,500+ lines of Replit API docs into a vector database
2. **Query with Context**: Ask a question and retrieve relevant documentation
3. **Generate Code**: Use AI to write code based on the retrieved documentation

**Query**: "How do I authenticate a user and get their workspace data using the Replit Extensions API?"

**Result**: Production-quality Python code with type hints, error handling, and proper structure

---

## Prerequisites

Make sure you have these API keys set in Replit Secrets:
- `OPENROUTER_API_KEY` - For AI models (get from https://openrouter.ai)
- `PINECONE_API_KEY` - For vector database (get from https://pinecone.io)
- `PINECONE_HOST_URL` - Your Pinecone index endpoint

---

## Step 1: Index Documentation (One-time setup)

**File**: `replit_rag_index.aicl`

This pipeline:
- Loads all `.md` files from `APIDocs/replit/`
- Splits text into 1000-char chunks with 200-char overlap
- Generates embeddings using OpenAI's text-embedding-3-small
- Uploads vectors to Pinecone namespace "replit-api-docs"

**Run it**:
```bash
python run.py replit_rag_index.aicl
```

**Expected Output**:
```
Applying changes...
  + Resource 'replit_docs' (loader-replit) created successfully.
    → Loaded 41 document(s)
  + Resource 'chunks' (text-splitter) created successfully.
    → Created 50 chunk(s)
  + Resource 'doc_embeddings' () created successfully.
    → Generated 50 embedding(s)
  + Resource 'index_docs' () created successfully.
    → Upserted 50 vector(s) to namespace 'replit-api-docs'
Apply complete.
```

---

## Step 2: Query and Generate Code

**File**: `replit_rag_query.aicl`

This pipeline:
1. **Embeds the query**: "How do I authenticate a user and get their workspace data?"
2. **Searches Pinecone**: Retrieves top 5 most relevant documentation chunks
3. **Generates code**: Claude 3.5 Sonnet writes Python code using the retrieved docs as context

**Run it**:
```bash
python run.py replit_rag_query.aicl
```

**Expected Output**:
```
Query: "How do I authenticate a user and get their workspace data using the Replit Extensions API?"

Applying changes...
  + Resource 'query_vector' () created successfully.
    → Generated 1 embedding vector (1536 dimensions)
  + Resource 'search_docs' () created successfully.
    → Retrieved 5 document(s)
    → Top match: APIDocs/replit/02-auth-api.md (score: 0.876)
  + Resource 'write_feature' (chat-write_feature) created successfully.
    → Response: Here's a complete Python function that uses the Replit Extensions API...
Apply complete.
```

---

## Step 3: View Generated Code

**Run the demo script**:
```bash
python demo_rag_output.py
```

This displays:
- The documentation chunks that were retrieved
- The complete AI-generated Python code
- Structured output with proper formatting

**Sample Output**:
```python
from typing import TypedDict, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class WorkspaceInfo:
    id: str
    title: str
    current_user: str

def get_replit_workspace_data() -> ReplitResponse:
    """
    Authenticates with Replit and retrieves workspace information.
    """
    # ... complete implementation with error handling
```

---

## Understanding the AICL Files

### 📄 replit_rag_index.aicl - Indexing Pipeline

```hcl
terraform {
  required_providers {
    loader = { source = "aicl/file_loader" }
    text_splitter = { source = "aicl/text_splitter" }
    openrouter = { source = "aicl/openrouter" }
    pinecone = { source = "aicl/pinecone" }
  }
}

resource "loader_files" "replit_docs" {
  path = "./APIDocs/replit"
  glob = "**/*.md"
}

resource "text_splitter" "chunks" {
  documents = "${resource.loader_files.replit_docs.attributes.documents}"
  chunk_size = 1000
  chunk_overlap = 200
}

resource "embedding" "doc_embeddings" {
  model = "openai/text-embedding-3-small"
  texts = "${resource.text_splitter.chunks.attributes.chunks}"
}

resource "upsert" "index_docs" {
  vectors = "${resource.embedding.doc_embeddings.attributes.embeddings}"
  namespace = "replit-api-docs"
}
```

**Key Features**:
- **Declarative**: Just describe what you want, not how to do it
- **Dependencies**: Resources automatically execute in the right order
- **Interpolation**: `${resource.type.name.attributes.field}` syntax references other resources

### 🔍 replit_rag_query.aicl - Query Pipeline

```hcl
resource "embedding" "query_vector" {
  model = "openai/text-embedding-3-small"
  text = "How do I authenticate a user and get their workspace data using the Replit Extensions API?"
}

resource "query" "search_docs" {
  vector = "${resource.embedding.query_vector.attributes.vector}"
  top_k = 5
  namespace = "replit-api-docs"
}

resource "chat" "write_feature" {
  model = "anthropic/claude-3.5-sonnet"
  messages = [
    {
      role = "system"
      content = "You are an expert developer. Use the provided documentation context to write accurate code."
    },
    {
      role = "user"
      content = "Based on this documentation:\n\n${resource.query.search_docs.attributes.results}\n\nWrite a complete Python function..."
    }
  ]
}
```

**Flow**:
1. Query → Embedding → Vector (1536 dimensions)
2. Vector → Pinecone Search → Top 5 Docs
3. Docs + Prompt → Claude → Generated Code

---

## Try Your Own Query

Edit `replit_rag_query.aicl` and change the query:

```hcl
resource "embedding" "query_vector" {
  model = "openai/text-embedding-3-small"
  text = "How do I access the file system in a Replit extension?"  # <-- Change this
}
```

Then run:
```bash
python run.py replit_rag_query.aicl
python demo_rag_output.py
```

---

## Available Providers

| Provider | Resource Types | Description |
|----------|---------------|-------------|
| `file_loader` | `loader_files` | Load documents from filesystem |
| `text_splitter` | `text_splitter` | Split text into chunks |
| `openrouter` | `embedding`, `chat` | AI models via OpenRouter |
| `pinecone` | `upsert`, `query` | Vector database operations |

---

## Troubleshooting

### "Provider not found" error
Make sure provider names in `required_providers` match the resource types:
- `loader` → `loader_files`
- `text_splitter` → `text_splitter`
- `openrouter` → `embedding`, `chat`
- `pinecone` → `upsert`, `query`

### Empty responses
1. Check that indexing completed: `python run.py replit_rag_index.aicl`
2. Verify Pinecone namespace: "replit-api-docs"
3. Ensure API keys are set in Replit Secrets

### No output displayed
Run the demo script to see full output:
```bash
python demo_rag_output.py
```

---

## What's Next?

1. **Index your own docs**: Change the `path` in `replit_rag_index.aicl`
2. **Try different models**: Use `anthropic/claude-3-opus` or `openai/gpt-4`
3. **Adjust chunking**: Modify `chunk_size` and `chunk_overlap` for better retrieval
4. **Add filters**: Use Pinecone metadata filtering for specific doc types

---

## Architecture

```
┌─────────────────┐
│  AICL Config    │  Define what you want
│  (HCL syntax)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AICL Engine    │  Parse, Plan, Execute
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Providers (gRPC subprocesses)  │
│                                 │
│  ┌──────────┐  ┌──────────┐   │
│  │ OpenRouter│  │ Pinecone  │   │
│  └──────────┘  └──────────┘   │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  External APIs  │
│  (OpenAI, etc)  │
└─────────────────┘
```

---

## Demo Complete! 🎉

You've successfully:
- ✅ Indexed documentation into a vector database
- ✅ Retrieved relevant docs based on a query
- ✅ Generated production-quality code with AI
- ✅ Learned declarative AI infrastructure with AICL

**Want to learn more?** Check out other examples:
- `demo_simple.aicl` - Basic chat completion
- `rag_index.aicl` - Index AICL source code
- `rag_query.aicl` - Query AICL documentation
