# Ragie.io Integration Guide

**Ragie** is a fully managed RAG-as-a-Service platform that handles document ingestion, automatic indexing, and intelligent retrieval. This integration allows AICL to leverage Ragie's enterprise-grade RAG capabilities.

## Overview

Ragie.io provides:
- **Multimodal document ingestion** (PDFs, videos, audio, images, text, PowerPoint, Word)
- **Automatic indexing** (vector, keyword, and summary indexes)
- **Intelligent retrieval** with hybrid search and re-ranking
- **Enterprise security** (SOC 2, HIPAA, GDPR compliant)
- **Data connectors** (Google Drive, Notion, Confluence)

## Setup

### 1. Get API Key

1. Sign up at https://www.ragie.ai (free tier available)
2. Navigate to your dashboard settings
3. Generate an API key
4. Store it in Replit Secrets as `RAGIE_API_KEY`

### 2. Provider Configuration

The Ragie provider is pre-configured in AICL's provider registry:

```hcl
terraform {
  required_providers {
    ragie = { source = "aicl/ragie" }
  }
}
```

## Resource Types

### 1. `ragie_upload` - Document Upload

Upload a document to Ragie for indexing.

**Attributes:**
- `file_path` (required): Path to file to upload
- `name` (optional): Document name (defaults to filename)
- `partition` (optional): Partition identifier for data isolation
- `mode` (optional): Processing mode - `"fast"` (text only, default) or `"hi_res"` (includes images/tables)
- `metadata` (optional): Key-value metadata for filtering
- `external_id` (optional): External identifier for the document

**Example:**

```hcl
resource "ragie_upload" "docs" {
  file_path = "README.md"
  name = "Project Documentation"
  partition = "my-project"
  mode = "fast"
  metadata = {
    type = "documentation"
    version = "1.0"
    author = "team"
  }
  aiclResourceName = "docs"
}
```

**Output Attributes:**
- `document_id`: Ragie document ID
- `status`: Processing status (`"partitioning"`, `"ready"`, etc.)
- `chunk_count`: Number of chunks created
- `page_count`: Number of pages processed
- `partition`: Partition the document belongs to
- `created_at`: Timestamp

### 2. `ragie_retrieval` - Semantic Search

Query Ragie for relevant document chunks.

**Attributes:**
- `query` (required): Natural language search query
- `top_k` (optional): Number of results to return (default: 8)
- `rerank` (optional): Enable re-ranking for better relevance (default: true)
- `recency_bias` (optional): Favor recent documents (default: false)
- `filter` (optional): Metadata filter object
- `partition` (optional): Search within specific partition

**Example:**

```hcl
resource "ragie_retrieval" "search" {
  query = "How does authentication work?"
  top_k = 5
  rerank = true
  partition = "my-project"
  filter = {
    type = "documentation"
  }
  aiclResourceName = "search"
}
```

**Output Attributes:**
- `chunks`: Array of retrieved chunks with text, score, document_id, metadata
- `num_results`: Number of chunks returned
- `query`: Original query

### 3. Aliases

- `ragie_document` = `ragie_upload`
- `ragie_query` = `ragie_retrieval`

## Complete RAG Pipeline Example

```hcl
terraform {
  required_providers {
    ragie = { source = "aicl/ragie" }
    naga = { source = "aicl/naga" }
  }
}

# Upload documentation to Ragie
resource "ragie_upload" "codebase" {
  file_path = "replit.md"
  name = "AICL Framework Docs"
  partition = "aicl-docs"
  mode = "fast"
  metadata = {
    type = "documentation"
    framework = "aicl"
  }
  aiclResourceName = "codebase"
}

# Query Ragie for relevant context
resource "ragie_retrieval" "context" {
  query = "What are the available providers?"
  top_k = 5
  rerank = true
  partition = "aicl-docs"
  aiclResourceName = "context"
}

# Generate answer using retrieved context
resource "naga_chat" "answer" {
  model = "gpt-4o-2024-08-06"
  messages = [
    {
      role = "system"
      content = "Answer questions based on the provided context."
    },
    {
      role = "user"
      content = "Question: ${resource.ragie_retrieval.context.attributes.query}\n\nContext: ${resource.ragie_retrieval.context.attributes.chunks}\n\nProvide a detailed answer."
    }
  ]
  max_tokens = 500
  temperature = 0.7
  aiclResourceName = "answer"
}
```

## Important Considerations

### Asynchronous Processing

⚠️ **Ragie processes documents asynchronously.** After upload, documents have status `"partitioning"` and take time to be indexed.

**Implications:**
- Immediate queries after upload may return 0 results
- For production use, implement polling or use pre-indexed documents
- Check `chunk_count` to verify indexing is complete

**Recommended approach:**
1. Upload documents in a separate AICL run
2. Wait for processing to complete (check Ragie dashboard)
3. Run queries in subsequent AICL executions

### Document Lifecycle

Documents persist in Ragie until explicitly deleted:
- AICL `destroy` will attempt to delete documents via Ragie API
- Document IDs are returned in upload response for manual cleanup
- Use partitions to organize and bulk-delete documents

### Metadata Filtering

Filter retrieval by metadata:

```hcl
resource "ragie_retrieval" "filtered" {
  query = "security features"
  filter = {
    department = { "$in" = ["engineering", "security"] }
    status = "published"
  }
  aiclResourceName = "filtered"
}
```

Supported operators: `$in`, `$eq`, `$ne`, `$gt`, `$lt`, etc.

### Partitions

Partitions provide logical data isolation:
- Useful for multi-tenant applications
- Separate dev/staging/prod data
- Enable focused retrieval within a subset of documents

```hcl
# Upload to partition
resource "ragie_upload" "tenant_doc" {
  file_path = "customer-data.pdf"
  partition = "customer-abc-123"
  aiclResourceName = "tenant_doc"
}

# Query within partition
resource "ragie_retrieval" "tenant_search" {
  query = "contract terms"
  partition = "customer-abc-123"
  aiclResourceName = "tenant_search"
}
```

## Supported File Types

**Plain Text:** `.eml`, `.html`, `.json`, `.md`, `.msg`, `.rst`, `.rtf`, `.txt`, `.xml`

**Images:** `.png`, `.webp`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.heic`

**Documents:** `.csv`, `.doc`, `.docx`, `.epub`, `.odt`, `.pdf`, `.ppt`, `.pptx`, `.tsv`, `.xlsx`, `.xls`

**Media:** Audio and video files (with mode configuration)

**Limitations:**
- PDF files over 2000 pages not supported in `hi_res` mode
- Use `fast` mode for text-only extraction

## Processing Modes

### `fast` (Default)
- Text extraction only
- Up to 20x faster than `hi_res`
- Lower cost
- Recommended for most use cases

### `hi_res`
- Extracts images and tables
- Processes embedded visuals
- Supported for: Word, PDF, Images, PowerPoint
- Higher cost and processing time

### Media Modes
For audio/video files, use JSON object:
```hcl
mode = {
  audio = true
  video = "audio_video"  # Options: "audio_only", "video_only", "audio_video"
  static = "hi_res"
}
```

## API Reference

**Base URL:** `https://api.ragie.ai`

**Authentication:** Bearer token (RAGIE_API_KEY)

**Endpoints:**
- `POST /documents` - Upload document
- `POST /retrievals` - Query/retrieve
- `DELETE /documents/{id}` - Delete document

## Pricing

- **Free tier** available for development
- **Starter** for small projects
- **Pro** for production workloads
- **Enterprise** for scale

Usage-based: pages ingested, retrievals, storage

Visit https://www.ragie.ai/pricing for details.

## Resources

- **Documentation:** https://docs.ragie.ai
- **API Reference:** https://docs.ragie.ai/reference
- **Dashboard:** https://app.ragie.ai
- **Discord:** https://discord.com/invite/QmT6vSGP5a
- **GitHub:** https://github.com/ragieai

## Comparison: Ragie vs Manual RAG

| Aspect | Ragie (Managed) | Manual (OpenAI + Pinecone) |
|--------|-----------------|----------------------------|
| **Setup** | Single provider | Multiple providers + orchestration |
| **Indexing** | Automatic | Manual chunking, embedding, upsert |
| **Retrieval** | Hybrid + rerank | Vector search only |
| **Multimodal** | Built-in | Requires custom processing |
| **Connectors** | Google Drive, Notion, Confluence | Manual sync |
| **Cost** | Usage-based | Embedding + DB costs |
| **Maintenance** | Managed | Self-managed |
| **Use Case** | Production RAG apps | Custom pipelines, experiments |

**When to use Ragie:**
- ✅ Production RAG applications
- ✅ Multimodal documents (PDFs with images, videos)
- ✅ Need for data connectors (Google Drive, etc.)
- ✅ Enterprise security requirements

**When to use Manual RAG:**
- ✅ Custom embedding models
- ✅ Experimental pipelines
- ✅ Cost optimization through provider selection
- ✅ Fine-grained control over chunking/indexing

---

*Ragie Integration - AICL Framework - October 11, 2025*
