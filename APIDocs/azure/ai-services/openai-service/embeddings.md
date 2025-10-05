# Azure OpenAI Embeddings API

## Endpoint
```
POST https://{endpoint}/openai/deployments/{deployment-id}/embeddings?api-version=2024-10-21
```

## Authentication
```http
Authorization: Bearer {api-key}
Content-Type: application/json
```

## Request Body
```json
{
  "input": [
    "The quick brown fox jumps over the lazy dog",
    "Azure OpenAI provides enterprise-grade AI capabilities"
  ],
  "model": "text-embedding-ada-002",
  "encoding_format": "float",
  "dimensions": 1536
}
```

## Response
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [
        0.0023064255,
        -0.009327292,
        -0.0028842222,
        "... (1536 dimensions total)"
      ]
    },
    {
      "object": "embedding", 
      "index": 1,
      "embedding": [
        0.0019865301,
        -0.007834521,
        -0.0031245678,
        "... (1536 dimensions total)"
      ]
    }
  ],
  "model": "text-embedding-ada-002",
  "usage": {
    "prompt_tokens": 16,
    "total_tokens": 16
  }
}
```

## Python SDK Example
```python
import openai
from azure.identity import DefaultAzureCredential

# Azure authentication
credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")

client = openai.AzureOpenAI(
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key=token.token,
    api_version="2024-10-21"
)

response = client.embeddings.create(
    input=["Your text to embed"],
    model="text-embedding-ada-002"
)

embeddings = response.data[0].embedding
```

## JavaScript SDK Example
```javascript
import { OpenAI } from 'openai';
import { DefaultAzureCredential } from '@azure/identity';

const credential = new DefaultAzureCredential();
const token = await credential.getToken('https://cognitiveservices.azure.com/.default');

const client = new OpenAI({
  apiKey: token.token,
  baseURL: 'https://your-resource.openai.azure.com/openai/deployments/text-embedding-ada-002',
  defaultQuery: { 'api-version': '2024-10-21' },
  defaultHeaders: {
    'Authorization': `Bearer ${token.token}`
  }
});

const response = await client.embeddings.create({
  input: ['Your text to embed'],
  model: 'text-embedding-ada-002'
});

const embeddings = response.data[0].embedding;
```

## Available Models

### text-embedding-ada-002
- **Dimensions**: 1536
- **Max tokens**: 8191
- **Use cases**: General-purpose embeddings
- **Performance**: High quality, cost-effective

### text-embedding-3-small
- **Dimensions**: 1536 (configurable)
- **Max tokens**: 8191
- **Use cases**: Improved performance over ada-002
- **Features**: Configurable dimensions

### text-embedding-3-large
- **Dimensions**: 3072 (configurable)
- **Max tokens**: 8191
- **Use cases**: Highest quality embeddings
- **Features**: Best performance, higher cost

## Key Parameters

### Required
- **input**: Text or array of texts to embed
- **model**: Embedding model deployment name

### Optional
- **encoding_format**: float (default) or base64
- **dimensions**: Reduce embedding dimensions (model-dependent)
- **user**: User identifier for tracking

## Batch Processing
```python
# Process large datasets efficiently
def embed_in_batches(texts, batch_size=100):
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        response = client.embeddings.create(
            input=batch,
            model="text-embedding-ada-002"
        )
        
        batch_embeddings = [data.embedding for data in response.data]
        embeddings.extend(batch_embeddings)
        
        print(f"Processed batch {i//batch_size + 1}")
    
    return embeddings
```

## Error Handling
```python
try:
    response = client.embeddings.create(
        input=["Text to embed"],
        model="text-embedding-ada-002"
    )
except openai.RateLimitError:
    print("Rate limit exceeded, waiting...")
    time.sleep(60)
except openai.InvalidRequestError as e:
    print(f"Invalid request: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Cost Optimization
- **Batch requests**: Process multiple texts in single API calls
- **Right-size dimensions**: Use smaller dimensions when possible
- **Cache embeddings**: Store and reuse embeddings for repeated texts
- **Model selection**: Choose appropriate model for use case
