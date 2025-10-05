# Pinecone Index Management - tofu-aicl Integration

## Provider Resource
```hcl
resource "pinecone_serverless_index" "vector_db" {
  name = "ai-knowledge-base"
  dimension = 1536
  metric = "cosine"
  
  cloud = "aws"
  region = "us-east-1"
  
  deletion_protection = "enabled"
  
  tags = {
    environment = var.environment
    project = "ai-workflows"
    cost_center = "engineering"
  }
}

data "pinecone_index" "existing" {
  name = "legacy-vectors"
}
```

## Provider Implementation
```python
def ApplyResourceChange(self, request, context):
    config = MessageToDict(request.config)
    
    if request.type_name == "pinecone_serverless_index":
        pc = Pinecone(api_key=self._get_api_key())
        
        try:
            # Check if index exists
            existing_indexes = pc.list_indexes()
            index_exists = any(idx.name == config["name"] for idx in existing_indexes)
            
            if not index_exists:
                # Create new serverless index
                pc.create_index(
                    name=config["name"],
                    dimension=config["dimension"],
                    metric=config.get("metric", "cosine"),
                    spec=ServerlessSpec(
                        cloud=config.get("cloud", "aws"),
                        region=config.get("region", "us-east-1")
                    ),
                    deletion_protection=config.get("deletion_protection", "disabled")
                )
                
                # Wait for index to be ready
                while not pc.describe_index(config["name"]).status.ready:
                    time.sleep(1)
            
            # Get index details
            index_info = pc.describe_index(config["name"])
            
            state = provider_pb2.ResourceState(
                id=config["name"],
                type="pinecone_serverless_index",
                status="ready" if index_info.status.ready else "initializing"
            )
            
            state.attributes.update({
                "name": index_info.name,
                "dimension": index_info.dimension,
                "metric": index_info.metric,
                "host": index_info.host,
                "cloud": index_info.spec.serverless.cloud,
                "region": index_info.spec.serverless.region,
                "deletion_protection": index_info.deletion_protection,
                "created_at": index_info.status.created_at,
                "ready": index_info.status.ready
            })
            
            return provider_pb2.ApplyResourceChangeResponse(new_state=state)
            
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Pinecone index error: {str(e)}")

def ReadResource(self, request, context):
    if request.type_name == "pinecone_index":
        pc = Pinecone(api_key=self._get_api_key())
        
        try:
            index_info = pc.describe_index(request.id)
            
            state = provider_pb2.ResourceState(
                id=request.id,
                type="pinecone_index",
                status="ready" if index_info.status.ready else "not_ready"
            )
            
            state.attributes.update({
                "name": index_info.name,
                "dimension": index_info.dimension,
                "metric": index_info.metric,
                "host": index_info.host,
                "total_vector_count": index_info.status.total_vector_count
            })
            
            return provider_pb2.ReadResourceResponse(state=state)
            
        except Exception as e:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Index not found: {str(e)}")
```

## Advanced Configuration
```hcl
resource "pinecone_serverless_index" "hybrid_search" {
  name = "hybrid-vectors"
  dimension = 1536
  metric = "dotproduct"
  
  # Multi-region setup
  cloud = "aws"
  region = "us-west-2"
  
  # Production settings
  deletion_protection = "enabled"
  
  # Metadata indexing for filtering
  metadata_config = {
    indexed_fields = ["category", "source", "timestamp"]
  }
  
  tags = {
    environment = "production"
    backup_policy = "daily"
    retention = "1year"
  }
}

# Index for different embedding models
resource "pinecone_serverless_index" "openai_embeddings" {
  name = "openai-ada-002"
  dimension = 1536  # OpenAI ada-002 dimension
  metric = "cosine"
  cloud = "aws"
  region = "us-east-1"
}

resource "pinecone_serverless_index" "cohere_embeddings" {
  name = "cohere-embed-v3"
  dimension = 1024  # Cohere embed-english-v3.0 dimension
  metric = "cosine"
  cloud = "aws"
  region = "us-east-1"
}
```

## Use Cases

### RAG Knowledge Base
```hcl
resource "pinecone_serverless_index" "knowledge_base" {
  name = "company-docs"
  dimension = 1536
  metric = "cosine"
  cloud = "aws"
  region = "us-east-1"
  
  tags = {
    use_case = "rag"
    data_source = "confluence_sharepoint"
  }
}
```

### Recommendation System
```hcl
resource "pinecone_serverless_index" "recommendations" {
  name = "user-preferences"
  dimension = 768
  metric = "dotproduct"
  cloud = "gcp"
  region = "us-central1"
  
  tags = {
    use_case = "recommendations"
    data_source = "user_behavior"
  }
}
```

### Semantic Search
```hcl
resource "pinecone_serverless_index" "semantic_search" {
  name = "product-catalog"
  dimension = 384  # Sentence transformers dimension
  metric = "cosine"
  cloud = "azure"
  region = "eastus"
  
  tags = {
    use_case = "search"
    data_source = "product_database"
  }
}
```

## Cost Optimization
- **Right-sizing**: Choose appropriate dimensions for your embeddings
- **Regional deployment**: Deploy close to your application
- **Deletion protection**: Prevent accidental data loss
- **Tagging strategy**: Enable cost allocation and tracking
