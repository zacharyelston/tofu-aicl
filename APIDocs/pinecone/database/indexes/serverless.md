# Pinecone Serverless Index Operations

## Create Serverless Index

### Endpoint
```
POST https://api.pinecone.io/indexes
```

### Authentication
```http
Api-Key: YOUR_API_KEY
X-Pinecone-API-Version: 2025-04
Content-Type: application/json
```

### Request Body
```json
{
  "name": "example-serverless-index",
  "vector_type": "dense",
  "dimension": 1536,
  "metric": "cosine",
  "spec": {
    "serverless": {
      "cloud": "aws",
      "region": "us-east-1"
    }
  },
  "tags": {
    "environment": "production"
  },
  "deletion_protection": "disabled"
}
```

### Python SDK Example
```python
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

pc = Pinecone(api_key="YOUR_API_KEY")

pc.create_index(
  name="docs-example1",
  dimension=1536,
  metric="cosine",
  spec=ServerlessSpec(
    cloud="aws",
    region="us-east-1",
  ),
  deletion_protection="disabled"
)
```

### JavaScript SDK Example
```javascript
import { Pinecone } from '@pinecone-database/pinecone'

const pc = new Pinecone({
  apiKey: 'YOUR_API_KEY'
});

await pc.createIndex({
  name: 'serverless-index',
  dimension: 1536,
  metric: 'cosine',
  spec: {
    serverless: {
      cloud: 'aws',
      region: 'us-east-1'
    }
  },
  deletionProtection: 'disabled',
});
```

## Key Parameters

### Required
- **name**: Unique index identifier
- **dimension**: Vector dimension (1-40,000)
- **metric**: Similarity metric (cosine, euclidean, dotproduct)
- **spec.serverless**: Serverless configuration

### Optional
- **vector_type**: dense (default) or sparse
- **tags**: Key-value metadata
- **deletion_protection**: enabled/disabled

## Supported Clouds and Regions

### AWS
- us-east-1, us-west-2, eu-west-1, ap-southeast-1

### GCP
- us-central1, us-east1, us-west1, europe-west1

### Azure
- eastus, westus2, northeurope, westeurope

## Similarity Metrics

### Cosine
- Range: [-1, 1]
- Best for: Normalized vectors, text embeddings
- Formula: 1 - cosine_distance

### Euclidean
- Range: [0, ∞]
- Best for: Computer vision, image embeddings
- Formula: sqrt(sum((a-b)²))

### Dot Product
- Range: (-∞, ∞)
- Best for: Recommendation systems
- Formula: sum(a*b)
