# Provider System Specification

## Provider Architecture

### Design Principles
1. **Abstraction**: Unified interface for heterogeneous AI services
2. **Isolation**: Each provider runs in separate process
3. **Auto-Discovery**: Drop-in configuration files
4. **Extensibility**: Easy to add new providers

### Communication Protocol: gRPC

#### Why gRPC?
- Language-agnostic (protocol buffers)
- High performance (binary serialization)
- Bi-directional streaming support
- Built-in load balancing, retries

---

## gRPC Service Definition

### Proto File: `provider.proto`

```protobuf
syntax = "proto3";

package aicl.provider;

service Provider {
  rpc CreateResource(ResourceRequest) returns (ResourceResponse);
  rpc ReadResource(ResourceID) returns (ResourceResponse);
  rpc UpdateResource(ResourceRequest) returns (ResourceResponse);
  rpc DeleteResource(ResourceID) returns (DeleteResponse);
  rpc GetCapabilities(Empty) returns (Capabilities);
}

message ResourceRequest {
  string type = 1;          // e.g., "llm_completion"
  string name = 2;          // e.g., "answer"
  map<string, string> config = 3;  // Resource configuration
  map<string, string> metadata = 4;
}

message ResourceResponse {
  string id = 1;
  string type = 2;
  map<string, string> attributes = 3;
  string status = 4;        // "success" | "failed"
  string error_message = 5;
}

message ResourceID {
  string id = 1;
}

message DeleteResponse {
  bool success = 1;
  string message = 2;
}

message Capabilities {
  repeated string resource_types = 1;
  repeated string operations = 2;
  map<string, string> metadata = 3;
}

message Empty {}
```

---

## Provider Lifecycle

### 1. Discovery Phase
```
Scan providers/ directory
  → Find config.yaml files
  → Validate schema
  → Register in ProviderRegistry
```

### 2. Initialization Phase
```
When provider is needed:
  → Check if already running (port check)
  → If not: Start subprocess
  → Wait for gRPC server ready
  → Establish client connection
```

### 3. Execution Phase
```
For each resource operation:
  → Get provider client
  → Send gRPC request
  → Wait for response (with timeout)
  → Handle success/error
```

### 4. Shutdown Phase
```
On engine shutdown:
  → Send graceful shutdown signal
  → Wait for provider cleanup (max 5s)
  → Force kill if timeout
  → Close gRPC channels
```

---

## Provider Configuration Schema

### config.yaml Structure

```yaml
provider:
  # Identity
  name: string                    # Unique identifier (lowercase, underscores)
  display_name: string            # Human-readable name
  version: string                 # Semantic version (e.g., "1.0.0")
  source: string                  # Registry path (e.g., "aicl/openai")
  description: string
  
  # Runtime
  runtime:
    entrypoint: string            # Executable file (e.g., "server.py")
    default_port: int             # gRPC port (50051-50100)
    mode: enum                    # subprocess | docker | both
    args: string[]                # Optional CLI arguments
    env: map<string, string>      # Optional environment variables
  
  # Environment
  environment:
    required_vars: string[]       # Must be set (e.g., API keys)
    optional_vars: string[]       # Optional settings
  
  # Capabilities
  capabilities:
    types: string[]               # Resource types (e.g., ["llm", "embeddings"])
    operations: string[]          # Supported operations
  
  # Models (references to catalog)
  model_ids: string[]             # IDs from v2/config/models.yaml
```

### Validation Rules
- `name`: Must be unique, lowercase, alphanumeric + underscores
- `default_port`: 50001-60000 range, unique per provider
- `mode`: One of `subprocess`, `docker`, `both`
- `model_ids`: Must exist in model catalog

---

## Provider Implementation Guide

### Minimal Provider (Python Example)

```python
# providers/my_provider/server.py
import grpc
from concurrent import futures
from v2.runtime import create_provider_server
import provider_pb2
import provider_pb2_grpc

class MyProvider(provider_pb2_grpc.ProviderServicer):
    def CreateResource(self, request, context):
        # Implement resource creation logic
        return provider_pb2.ResourceResponse(
            id=f"{request.type}.{request.name}",
            type=request.type,
            attributes={"status": "created"},
            status="success"
        )
    
    def ReadResource(self, request, context):
        # Implement resource read logic
        pass
    
    def UpdateResource(self, request, context):
        # Implement resource update logic
        pass
    
    def DeleteResource(self, request, context):
        # Implement resource deletion logic
        pass
    
    def GetCapabilities(self, request, context):
        return provider_pb2.Capabilities(
            resource_types=["my_resource"],
            operations=["create", "read", "update", "delete"]
        )

if __name__ == '__main__':
    create_provider_server(MyProvider())
```

### Provider Registration (Automatic)

1. Create directory: `providers/my_provider/`
2. Add `config.yaml`
3. Add `server.py` (or other entrypoint)
4. Provider auto-discovered on next engine run

---

## Built-in Providers

### 1. OpenAI Provider
- **Types**: llm, embeddings
- **Operations**: chat_completion, text_embedding
- **Models**: gpt-4o, gpt-4o-mini, text-embedding-3-small, etc
- **Config**: Requires `OPENAI_API_KEY`

### 2. Naga.ai Provider
- **Types**: llm, embeddings
- **Operations**: chat_completion, text_embedding
- **Models**: OpenAI-compatible models at lower cost
- **Config**: Requires `NAGA_API_KEY`

### 3. OpenRouter Provider
- **Types**: llm
- **Operations**: chat_completion
- **Models**: 50+ models (Claude, Mistral, Gemini, etc)
- **Config**: Requires `OPENROUTER_API_KEY`

### 4. Pinecone Provider
- **Types**: vector_db
- **Operations**: create_index, upsert_vectors, query_vectors
- **Config**: Requires `PINECONE_API_KEY`, `PINECONE_HOST_URL`

### 5. Ragie.io Provider
- **Types**: rag_service
- **Operations**: upload_document, retrieve_context
- **Config**: Requires `RAGIE_API_KEY`

### 6. File Loader Provider
- **Types**: document_loader
- **Operations**: load_file, load_directory
- **Config**: None (local file system)

### 7. Text Splitter Provider
- **Types**: text_processor
- **Operations**: chunk_text
- **Config**: None

### 8. Command Assertion Provider
- **Types**: testing
- **Operations**: assert_output
- **Config**: None

### 9. Azure OpenAI Provider
- **Types**: llm, embeddings
- **Operations**: chat_completion, text_embedding
- **Config**: Requires Azure credentials

---

## Provider Best Practices

### Error Handling
- Return descriptive error messages
- Use gRPC status codes appropriately
- Log errors internally for debugging

### Resource Management
- Clean up on shutdown
- Release API connections
- Close file handles

### Configuration
- Validate required environment variables at startup
- Provide sensible defaults
- Document all configuration options

### Testing
- Unit tests for each operation
- Integration tests with mock gRPC
- End-to-end tests with real APIs (optional)
