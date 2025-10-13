# Configuration Format Specification

## HCL Configuration Language

### File Extension
- `.aicl` (AI Configuration Language)
- Based on HCL (HashiCorp Configuration Language)

### Basic Structure

```hcl
# Variables
variable "name" {
  type    = string
  default = "value"
}

# Provider configuration
provider "provider_name" {
  config_key = "value"
}

# Resources
resource "resource_type" "resource_name" {
  attribute = "value"
}

# Data sources
data "data_type" "data_name" {
  attribute = "value"
}

# Outputs
output "output_name" {
  value = expression
}
```

---

## Block Types

### 1. Variable Block

Define configurable parameters

```hcl
variable "model_name" {
  type        = string
  default     = "gpt-4o-mini"
  description = "LLM model to use"
}

variable "temperature" {
  type    = number
  default = 0.7
}

variable "use_caching" {
  type    = bool
  default = true
}

variable "tags" {
  type    = list(string)
  default = ["production", "experiment"]
}

variable "metadata" {
  type = map(string)
  default = {
    owner = "team-ai"
    env   = "prod"
  }
}
```

**Supported Types**:
- `string`
- `number`
- `bool`
- `list(type)`
- `map(type)`

---

### 2. Provider Block

Configure provider settings

```hcl
provider "openai" {
  api_key = env("OPENAI_API_KEY")
  
  # Optional settings
  organization = "org-123"
  timeout      = 30
}

provider "pinecone" {
  api_key = env("PINECONE_API_KEY")
  host    = env("PINECONE_HOST_URL")
}
```

**Special Functions**:
- `env("VAR")`: Read environment variable
- `file("path")`: Read file content

---

### 3. Resource Block

Define infrastructure resources

```hcl
resource "llm_completion" "answer" {
  provider    = provider.openai
  model       = var.model_name
  temperature = var.temperature
  
  prompt = <<-EOT
    What is the capital of France?
    Please provide a brief answer.
  EOT
  
  max_tokens = 100
}

resource "text_embedding" "query_vector" {
  provider = provider.openai
  model    = "text-embedding-3-small"
  input    = "machine learning tutorial"
}

resource "vector_index" "knowledge_base" {
  provider   = provider.pinecone
  name       = "my-index"
  dimension  = 1536
  metric     = "cosine"
}
```

**Naming Convention**:
- Type: lowercase, underscores (e.g., `llm_completion`)
- Name: lowercase, underscores, alphanumeric (e.g., `my_answer_1`)

---

### 4. Data Block

Read existing resources (no creation)

```hcl
data "file" "prompt_template" {
  provider = provider.file_loader
  path     = "./prompts/template.txt"
}

data "vector_query" "similar_docs" {
  provider  = provider.pinecone
  index     = resource.vector_index.knowledge_base.id
  vector    = resource.text_embedding.query_vector.embedding
  top_k     = 5
}
```

**Difference from Resource**:
- Data sources are read-only
- Resources are created/managed by engine

---

### 5. Output Block

Export values for use in other tools

```hcl
output "answer_text" {
  value = resource.llm_completion.answer.content
}

output "total_tokens" {
  value = resource.llm_completion.answer.usage.total_tokens
}

output "cost_estimate" {
  value = resource.llm_completion.answer.cost
}
```

---

## Interpolation and References

### Variable References
```hcl
var.variable_name
var.model_name
var.temperature
```

### Resource References
```hcl
resource.type.name.attribute
resource.llm_completion.answer.content
resource.text_embedding.query_vector.embedding
```

### Provider References
```hcl
provider.provider_name
provider.openai
provider.pinecone
```

### Environment Variables
```hcl
env("VARIABLE_NAME")
env("OPENAI_API_KEY")
```

### File Content
```hcl
file("path/to/file.txt")
file("./prompts/system.txt")
```

---

## Template Syntax (Matrix Experiments)

### Jinja2-Style Templates

```hcl
resource "llm_completion" "experiment" {
  provider    = provider.openai
  model       = "{{ model_name }}"
  temperature = {{ temperature }}
  
  prompt = "{{ prompt_template }}"
}
```

### Template Variables File (YAML)

```yaml
# test-variables.yaml
chat_models:
  models:
    - name: "gpt-4o"
    - name: "gpt-4o-mini"
  
  temperature:
    min: 0.0
    max: 1.0
    step: 0.5

prompts:
  - "What is machine learning?"
  - "Explain neural networks simply."
```

### Expansion Logic
- Single variable: 1 config per value
- Multiple variables: Cartesian product (all combinations)
- Example: 2 models × 3 temperatures × 2 prompts = 12 experiments

---

## Complete Example: RAG Pipeline

```hcl
variable "question" {
  type    = string
  default = "What are transformers in machine learning?"
}

variable "embedding_model" {
  type    = string
  default = "text-embedding-3-small"
}

variable "llm_model" {
  type    = string
  default = "gpt-4o-mini"
}

provider "openai" {
  api_key = env("OPENAI_API_KEY")
}

provider "pinecone" {
  api_key = env("PINECONE_API_KEY")
  host    = env("PINECONE_HOST_URL")
}

# Load documents
data "file" "document" {
  provider = provider.file_loader
  path     = "./knowledge/ml-guide.pdf"
}

# Split into chunks
resource "text_chunks" "doc_chunks" {
  provider   = provider.text_splitter
  content    = data.file.document.content
  chunk_size = 500
  overlap    = 50
}

# Create embeddings for chunks
resource "text_embedding" "chunk_embeddings" {
  provider = provider.openai
  model    = var.embedding_model
  input    = resource.text_chunks.doc_chunks.chunks
}

# Store in vector database
resource "vector_upsert" "store_chunks" {
  provider  = provider.pinecone
  index     = "ml-knowledge"
  vectors   = resource.text_embedding.chunk_embeddings.embeddings
  metadata  = resource.text_chunks.doc_chunks.metadata
}

# Embed user question
resource "text_embedding" "question_vector" {
  provider = provider.openai
  model    = var.embedding_model
  input    = var.question
}

# Retrieve relevant chunks
data "vector_query" "relevant_context" {
  provider = provider.pinecone
  index    = "ml-knowledge"
  vector   = resource.text_embedding.question_vector.embedding
  top_k    = 3
}

# Generate answer
resource "llm_completion" "answer" {
  provider = provider.openai
  model    = var.llm_model
  
  prompt = <<-EOT
    Context: ${data.vector_query.relevant_context.results}
    
    Question: ${var.question}
    
    Answer based on the context above:
  EOT
  
  temperature = 0.3
  max_tokens  = 500
}

output "answer" {
  value = resource.llm_completion.answer.content
}

output "context_used" {
  value = data.vector_query.relevant_context.results
}

output "total_cost" {
  value = resource.llm_completion.answer.cost + 
          resource.text_embedding.question_vector.cost
}
```

---

## Configuration Validation

### Syntax Validation
- Valid HCL syntax
- Proper block structure
- Correct attribute types

### Semantic Validation
- All referenced variables exist
- Provider configurations complete
- Resource dependencies valid
- No circular dependencies

### Runtime Validation
- Required environment variables set
- Provider services accessible
- Resource quotas not exceeded
