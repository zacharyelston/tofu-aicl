# Pinecone Vector Operations - tofu-aicl Integration

## Provider Resources
```hcl
resource "pinecone_vector_upsert" "knowledge_base" {
  index_name = pinecone_serverless_index.vector_db.name
  namespace = "documents"
  
  vectors = [
    {
      id = "doc_${var.document_id}"
      values = var.embedding_vector
      metadata = {
        title = var.document_title
        source = var.document_source
        category = var.document_category
        timestamp = timestamp()
      }
    }
  ]
}

data "pinecone_vector_query" "semantic_search" {
  index_name = pinecone_serverless_index.vector_db.name
  namespace = "documents"
  
  vector = var.query_embedding
  top_k = 10
  include_metadata = true
  
  filter = {
    category = { "$eq" = "technical_docs" }
    timestamp = { "$gte" = "2024-01-01" }
  }
}
```

## Provider Implementation
```python
def ApplyResourceChange(self, request, context):
    config = MessageToDict(request.config)
    
    if request.type_name == "pinecone_vector_upsert":
        pc = Pinecone(api_key=self._get_api_key())
        index = pc.Index(host=self._get_index_host(config["index_name"]))
        
        try:
            # Prepare vectors for upsert
            vectors = []
            for vector_config in config["vectors"]:
                vector = {
                    "id": vector_config["id"],
                    "values": vector_config["values"]
                }
                
                if "metadata" in vector_config:
                    vector["metadata"] = vector_config["metadata"]
                
                if "sparse_values" in vector_config:
                    vector["sparse_values"] = vector_config["sparse_values"]
                
                vectors.append(vector)
            
            # Perform upsert operation
            upsert_response = index.upsert(
                vectors=vectors,
                namespace=config.get("namespace", "")
            )
            
            state = provider_pb2.ResourceState(
                id=f"upsert-{uuid.uuid4().hex[:8]}",
                type="pinecone_vector_upsert",
                status="completed"
            )
            
            state.attributes.update({
                "index_name": config["index_name"],
                "namespace": config.get("namespace", ""),
                "upserted_count": upsert_response.upserted_count,
                "vector_ids": [v["id"] for v in vectors],
                "upserted_at": datetime.utcnow().isoformat()
            })
            
            return provider_pb2.ApplyResourceChangeResponse(new_state=state)
            
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Vector upsert error: {str(e)}")

def ReadResource(self, request, context):
    if request.type_name == "pinecone_vector_query":
        pc = Pinecone(api_key=self._get_api_key())
        index = pc.Index(host=self._get_index_host(request.config["index_name"]))
        
        try:
            query_config = MessageToDict(request.config)
            
            # Perform vector query
            query_response = index.query(
                vector=query_config["vector"],
                top_k=query_config.get("top_k", 10),
                namespace=query_config.get("namespace", ""),
                filter=query_config.get("filter", {}),
                include_metadata=query_config.get("include_metadata", True),
                include_values=query_config.get("include_values", False)
            )
            
            state = provider_pb2.ResourceState(
                id=f"query-{uuid.uuid4().hex[:8]}",
                type="pinecone_vector_query",
                status="completed"
            )
            
            # Process matches
            matches = []
            for match in query_response.matches:
                match_data = {
                    "id": match.id,
                    "score": match.score
                }
                if hasattr(match, 'metadata') and match.metadata:
                    match_data["metadata"] = dict(match.metadata)
                if hasattr(match, 'values') and match.values:
                    match_data["values"] = list(match.values)
                matches.append(match_data)
            
            state.attributes.update({
                "matches": json.dumps(matches),
                "match_count": len(matches),
                "namespace": query_config.get("namespace", ""),
                "queried_at": datetime.utcnow().isoformat()
            })
            
            return provider_pb2.ReadResourceResponse(state=state)
            
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Vector query error: {str(e)}")
```

## Batch Operations
```hcl
resource "pinecone_vector_batch_upsert" "document_embeddings" {
  index_name = pinecone_serverless_index.vector_db.name
  namespace = "documents"
  
  # Process vectors in batches for performance
  batch_size = 100
  
  vectors = [
    for doc in var.documents : {
      id = "doc_${doc.id}"
      values = doc.embedding
      metadata = {
        title = doc.title
        content_type = doc.type
        word_count = doc.word_count
        created_at = doc.created_at
      }
    }
  ]
}
```

## Hybrid Search Configuration
```hcl
resource "pinecone_vector_upsert" "hybrid_vectors" {
  index_name = pinecone_serverless_index.hybrid_db.name
  namespace = "hybrid_search"
  
  vectors = [
    {
      id = "hybrid_doc_${var.doc_id}"
      # Dense vector from embedding model
      values = var.dense_embedding
      # Sparse vector from BM25 or SPLADE
      sparse_values = {
        indices = var.sparse_indices
        values = var.sparse_values
      }
      metadata = {
        title = var.document_title
        keywords = var.extracted_keywords
        search_type = "hybrid"
      }
    }
  ]
}
```

## Real-time Vector Operations
```python
# Streaming vector upsert for real-time applications
def stream_vector_upsert(self, request_iterator, context):
    pc = Pinecone(api_key=self._get_api_key())
    
    for request in request_iterator:
        config = MessageToDict(request.config)
        index = pc.Index(host=self._get_index_host(config["index_name"]))
        
        try:
            # Real-time upsert
            index.upsert(
                vectors=[{
                    "id": config["vector"]["id"],
                    "values": config["vector"]["values"],
                    "metadata": config["vector"].get("metadata", {})
                }],
                namespace=config.get("namespace", "")
            )
            
            yield provider_pb2.StreamResponse(
                status="success",
                message=f"Vector {config['vector']['id']} upserted"
            )
            
        except Exception as e:
            yield provider_pb2.StreamResponse(
                status="error",
                message=f"Error upserting vector: {str(e)}"
            )
```

## Use Cases

### RAG Document Ingestion
```hcl
resource "pinecone_vector_upsert" "rag_documents" {
  index_name = pinecone_serverless_index.knowledge_base.name
  namespace = "company_docs"
  
  vectors = [
    for chunk in var.document_chunks : {
      id = "chunk_${chunk.doc_id}_${chunk.chunk_id}"
      values = chunk.embedding
      metadata = {
        document_id = chunk.doc_id
        chunk_index = chunk.chunk_id
        text_content = chunk.text
        source_url = chunk.source_url
        last_updated = chunk.updated_at
      }
    }
  ]
}
```

### Recommendation System
```hcl
resource "pinecone_vector_upsert" "user_preferences" {
  index_name = pinecone_serverless_index.recommendations.name
  namespace = "user_vectors"
  
  vectors = [
    {
      id = "user_${var.user_id}"
      values = var.user_preference_vector
      metadata = {
        user_id = var.user_id
        preferences = var.user_preferences
        last_interaction = timestamp()
        segment = var.user_segment
      }
    }
  ]
}
```

### Semantic Search
```hcl
data "pinecone_vector_query" "product_search" {
  index_name = pinecone_serverless_index.product_catalog.name
  namespace = "products"
  
  vector = var.search_query_embedding
  top_k = 20
  include_metadata = true
  
  filter = {
    category = { "$in" = var.allowed_categories }
    price = { "$lte" = var.max_price }
    in_stock = { "$eq" = true }
  }
}
```

## Performance Optimization
- **Batch operations**: Group multiple vectors for better throughput
- **Namespace strategy**: Organize vectors for efficient querying
- **Metadata indexing**: Index frequently filtered fields
- **Connection pooling**: Reuse connections for better performance
