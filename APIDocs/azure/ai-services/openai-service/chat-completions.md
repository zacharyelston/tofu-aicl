# Azure OpenAI Chat Completions API

## Endpoint
```
POST https://{endpoint}/openai/deployments/{deployment-id}/chat/completions?api-version=2024-10-21
```

## Authentication
```http
Authorization: Bearer {api-key}
Content-Type: application/json
```

## Request Body
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful AI assistant."
    },
    {
      "role": "user", 
      "content": "Explain quantum computing"
    }
  ],
  "max_tokens": 1000,
  "temperature": 0.7,
  "stream": false
}
```

## Response
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Quantum computing is a revolutionary computing paradigm..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 100,
    "total_tokens": 120
  }
}
```

## Key Parameters
- **messages**: Array of conversation messages
- **max_tokens**: Maximum tokens in response
- **temperature**: Randomness in output (0.0-2.0)
- **stream**: Enable streaming responses
- **functions**: Function calling capabilities
    
## Azure-Specific Features
- **Content filtering**: Built-in safety controls
- **Data sources**: Integration with Azure AI Search
- **Managed identity**: Azure AD authentication
