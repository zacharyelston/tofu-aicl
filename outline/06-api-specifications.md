# API Specifications

## gRPC Provider API

### Service: Provider

All providers must implement this service interface.

---

### Method: CreateResource

Create a new resource.

**Request**:
```protobuf
message ResourceRequest {
  string type = 1;                  // Resource type (e.g., "llm_completion")
  string name = 2;                  // Resource name (e.g., "answer")
  map<string, string> config = 3;   // Configuration attributes
  map<string, string> metadata = 4; // Metadata (tags, etc)
}
```

**Response**:
```protobuf
message ResourceResponse {
  string id = 1;                    // Unique resource ID
  string type = 2;                  // Resource type
  map<string, string> attributes = 3; // Resource attributes (outputs)
  string status = 4;                // "success" | "failed"
  string error_message = 5;         // Error details (if failed)
}
```

**Example Usage**:
```python
request = ResourceRequest(
    type="llm_completion",
    name="answer",
    config={
        "model": "gpt-4o-mini",
        "prompt": "What is AI?",
        "temperature": "0.7",
        "max_tokens": "100"
    }
)

response = provider_stub.CreateResource(request)
# response.attributes["content"] = "AI is..."
# response.attributes["usage.total_tokens"] = "150"
```

---

### Method: ReadResource

Read an existing resource.

**Request**:
```protobuf
message ResourceID {
  string id = 1;  // Resource ID to read
}
```

**Response**:
```protobuf
message ResourceResponse {
  // Same as CreateResource response
}
```

---

### Method: UpdateResource

Update an existing resource.

**Request**:
```protobuf
message ResourceRequest {
  // Same as CreateResource, but for existing resource
}
```

**Response**:
```protobuf
message ResourceResponse {
  // Same as CreateResource response
}
```

---

### Method: DeleteResource

Delete a resource.

**Request**:
```protobuf
message ResourceID {
  string id = 1;  // Resource ID to delete
}
```

**Response**:
```protobuf
message DeleteResponse {
  bool success = 1;    // true if deleted successfully
  string message = 2;  // Optional message
}
```

---

### Method: GetCapabilities

Query provider capabilities.

**Request**:
```protobuf
message Empty {}
```

**Response**:
```protobuf
message Capabilities {
  repeated string resource_types = 1;  // Supported types
  repeated string operations = 2;      // Supported operations
  map<string, string> metadata = 3;    // Provider metadata
}
```

**Example Response**:
```json
{
  "resource_types": ["llm_completion", "text_embedding"],
  "operations": ["create", "read"],
  "metadata": {
    "provider": "openai",
    "version": "1.0.0"
  }
}
```

---

## Resource-Specific Attributes

### LLM Completion

**Type**: `llm_completion`

**Input Attributes** (config):
- `model`: Model ID (e.g., "gpt-4o-mini")
- `prompt`: Input prompt text
- `temperature`: 0.0 - 2.0 (randomness)
- `max_tokens`: Maximum output tokens
- `top_p`: Nucleus sampling (optional)
- `frequency_penalty`: -2.0 to 2.0 (optional)
- `presence_penalty`: -2.0 to 2.0 (optional)

**Output Attributes**:
- `content`: Generated text
- `usage.prompt_tokens`: Input tokens used
- `usage.completion_tokens`: Output tokens used
- `usage.total_tokens`: Total tokens
- `cost`: Estimated cost in USD
- `finish_reason`: "stop" | "length" | "error"

---

### Text Embedding

**Type**: `text_embedding`

**Input Attributes**:
- `model`: Embedding model (e.g., "text-embedding-3-small")
- `input`: Text to embed (string or array)

**Output Attributes**:
- `embedding`: Float array (dimensions vary by model)
- `dimensions`: Embedding size (e.g., 1536)
- `usage.total_tokens`: Tokens used
- `cost`: Estimated cost in USD

---

### Vector Index

**Type**: `vector_index`

**Input Attributes**:
- `name`: Index name
- `dimension`: Vector dimensions (e.g., 1536)
- `metric`: "cosine" | "euclidean" | "dotproduct"
- `namespace`: Optional namespace

**Output Attributes**:
- `id`: Index ID
- `status`: "ready" | "initializing"
- `total_vectors`: Count of stored vectors

---

### Vector Upsert

**Type**: `vector_upsert`

**Input Attributes**:
- `index`: Index name/ID
- `vectors`: Array of float arrays
- `ids`: Array of vector IDs (optional, auto-generated if omitted)
- `metadata`: Array of metadata objects (optional)
- `namespace`: Optional namespace

**Output Attributes**:
- `upserted_count`: Number of vectors inserted
- `ids`: Array of vector IDs

---

### Vector Query

**Type**: `vector_query`

**Input Attributes**:
- `index`: Index name/ID
- `vector`: Query vector (float array)
- `top_k`: Number of results (default: 10)
- `namespace`: Optional namespace
- `filter`: Metadata filter (optional)

**Output Attributes**:
- `results`: Array of matches
  - `id`: Vector ID
  - `score`: Similarity score
  - `metadata`: Associated metadata

---

### File Load

**Type**: `file_load`

**Input Attributes**:
- `path`: File path (local or URL)
- `encoding`: Text encoding (default: "utf-8")

**Output Attributes**:
- `content`: File content
- `size_bytes`: File size
- `mime_type`: Content type

---

### Text Splitter

**Type**: `text_chunks`

**Input Attributes**:
- `content`: Text to split
- `chunk_size`: Characters per chunk (default: 500)
- `overlap`: Overlap between chunks (default: 50)
- `separators`: Split delimiters (default: ["\n\n", "\n", " "])

**Output Attributes**:
- `chunks`: Array of text chunks
- `count`: Number of chunks
- `metadata`: Array of chunk metadata (positions, etc)

---

## CLI API

### Commands

#### `aicl run <config.aicl>`
Execute a single configuration file.

**Flags**:
- `--var key=value`: Set variable values
- `--state <path>`: State file location (default: `terraform.tfstate`)
- `--auto-approve`: Skip confirmation prompts
- `--parallelism <n>`: Max parallel operations (default: 10)

**Example**:
```bash
aicl run pipeline.aicl --var model=gpt-4o --auto-approve
```

---

#### `aicl plan <config.aicl>`
Show execution plan without applying.

**Example**:
```bash
aicl plan pipeline.aicl
```

**Output**:
```
Plan: 5 to create, 0 to update, 0 to delete

+ resource.llm_completion.answer
+ resource.text_embedding.query
+ resource.vector_query.context
...
```

---

#### `aicl destroy <config.aicl>`
Delete all resources.

**Example**:
```bash
aicl destroy pipeline.aicl --auto-approve
```

---

#### `aicl validate <config.aicl>`
Validate configuration syntax.

**Example**:
```bash
aicl validate pipeline.aicl
Success! Configuration is valid.
```

---

#### `aicl experiment run <suite_name>`
Run matrix experiments.

**Example**:
```bash
aicl experiment run smoke_test
```

**Output**:
```
Running 3 experiments...
[1/3] gpt-4o-mini @ temp=0.0 ✓ (2.1s, $0.0015)
[2/3] gpt-4o-mini @ temp=0.5 ✓ (2.3s, $0.0018)
[3/3] gpt-4o @ temp=0.0 ✓ (3.1s, $0.0082)

Total cost: $0.0115
Average latency: 2.5s
```

---

#### `aicl experiment stats`
Show experiment statistics.

**Example**:
```bash
aicl experiment stats --db experiments.db
```

---

#### `aicl providers list`
List available providers.

**Example**:
```bash
aicl providers list

Available Providers:
- openai (OpenAI) - llm, embeddings
- naga (Naga.ai) - llm, embeddings
- pinecone (Pinecone) - vector_db
...
```

---

#### `aicl models list`
Show model catalog.

**Example**:
```bash
aicl models list --type chat

Chat Models:
- gpt-4o (OpenAI) - $2.50/1M tokens, Quality: 9.5/10
- gpt-4o-mini (OpenAI) - $0.15/1M tokens, Quality: 8.5/10
...
```

---

## Web API (Future)

### REST Endpoints

#### POST /api/v1/executions
Create new execution.

**Request**:
```json
{
  "config": "base64_encoded_aicl",
  "variables": {"model": "gpt-4o"},
  "auto_approve": true
}
```

**Response**:
```json
{
  "execution_id": "exec-123",
  "status": "running",
  "created_at": "2025-10-11T12:00:00Z"
}
```

---

#### GET /api/v1/executions/{id}
Get execution status.

**Response**:
```json
{
  "execution_id": "exec-123",
  "status": "completed",
  "resources": 5,
  "cost": 0.0115,
  "duration_ms": 2500
}
```

---

#### GET /api/v1/experiments
List experiments.

**Response**:
```json
{
  "experiments": [
    {
      "id": "exp-456",
      "name": "Model Comparison",
      "count": 12,
      "status": "completed",
      "best_result": {
        "config": {"model": "gpt-4o-mini", "temperature": 0.3},
        "quality_score": 8.5,
        "cost": 0.002
      }
    }
  ]
}
```
