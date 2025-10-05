# Pinecone Vector Upsert Operations

## Endpoint
```
POST https://{index-host}/vectors/upsert
```

## Authentication
```http
Api-Key: YOUR_API_KEY
Content-Type: application/json
```

## Request Body
```json
{
  "vectors": [
    {
      "id": "vec1",
      "values": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
      "metadata": {
        "genre": "comedy",
        "year": 2020,
        "source": "document_1"
      }
    },
    {
      "id": "vec2", 
      "values": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
      "metadata": {
        "genre": "documentary",
        "year": 2019,
        "source": "document_2"
      }
    }
  ],
  "namespace": "example-namespace"
}
```

## Python SDK Example
```python
from pinecone.grpc import PineconeGRPC as Pinecone

pc = Pinecone(api_key="YOUR_API_KEY")
index = pc.Index(host="INDEX_HOST")

index.upsert(
  vectors=[
    {
      "id": "vec1", 
      "values": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1], 
      "metadata": {"genre": "comedy", "year": 2020}
    },
    {
      "id": "vec2", 
      "values": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
      "metadata": {"genre": "documentary", "year": 2019}
    }
  ],
  namespace="example-namespace"
)
```

## JavaScript SDK Example
```javascript
import { Pinecone } from '@pinecone-database/pinecone'

const pc = new Pinecone({ apiKey: "YOUR_API_KEY" })
const index = pc.index("INDEX_NAME", "INDEX_HOST")

const records = [
  {
    id: 'vec1',
    values: [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
    metadata: { genre: "comedy", year: 2020 },
  },
  {
    id: 'vec2',
    values: [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
    metadata: { genre: "documentary", year: 2019 },
  }
]

await index.namespace('example-namespace').upsert(records);
```

## Batch Upsert
```python
# Upsert in batches for better performance
def upsert_in_batches(index, vectors, batch_size=100):
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"Upserted batch {i//batch_size + 1}")

# Example with large dataset
vectors = []
for i in range(1000):
    vectors.append({
        "id": f"vec_{i}",
        "values": [random.random() for _ in range(1536)],
        "metadata": {"batch": i // 100, "index": i}
    })

upsert_in_batches(index, vectors)
```

## Sparse Vector Upsert
```python
# Upsert sparse vectors for hybrid search
index.upsert(
  vectors=[
    {
      "id": "sparse_vec1",
      "sparse_values": {
        "indices": [1, 5, 10, 100, 1000],
        "values": [0.5, 0.3, 0.8, 0.2, 0.9]
      },
      "metadata": {"type": "sparse", "source": "bm25"}
    }
  ]
)
```

## Response
```json
{
  "upserted_count": 2
}
```

## Key Parameters

### Required
- **vectors**: Array of vector objects
- **vectors[].id**: Unique identifier for the vector
- **vectors[].values**: Dense vector values (array of floats)

### Optional
- **namespace**: Logical partition (default: "" - empty namespace)
- **vectors[].metadata**: Key-value pairs for filtering
- **vectors[].sparse_values**: Sparse vector representation

## Limits
- **Batch size**: Up to 100 vectors per request
- **Vector dimensions**: Must match index dimension
- **Metadata size**: Up to 40KB per vector
- **ID length**: Up to 512 characters

## Best Practices
- **Batch operations**: Upsert multiple vectors in single requests
- **Consistent metadata**: Use consistent metadata schema
- **Meaningful IDs**: Use descriptive, unique identifiers
- **Namespace strategy**: Organize data with namespaces for multitenancy
