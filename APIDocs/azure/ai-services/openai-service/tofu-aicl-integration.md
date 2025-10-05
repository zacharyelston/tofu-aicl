# Azure OpenAI - tofu-aicl Integration

## Provider Resource
```hcl
resource "azure_openai_chat_completion" "ai_assistant" {
  endpoint = var.azure_openai_endpoint
  deployment_id = "gpt-4"
  
  messages = [
    {
      role = "system"
      content = "You are an expert software architect."
    },
    {
      role = "user" 
      content = var.user_prompt
    }
  ]
  
  max_tokens = 1000
  temperature = 0.7
  
  # Azure-specific configuration
  content_filter_enabled = true
  managed_identity_enabled = true
}
```

## Provider Implementation
```python
def ApplyResourceChange(self, request, context):
    config = MessageToDict(request.config)
    
    if request.type_name == "azure_openai_chat_completion":
        # Azure authentication
        credential = DefaultAzureCredential()
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {credential.get_token('https://cognitiveservices.azure.com/.default').token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": config["messages"],
            "max_tokens": config.get("max_tokens", 1000),
            "temperature": config.get("temperature", 0.7),
            "stream": False
        }
        
        # Make API call
        response = requests.post(
            f"{config['endpoint']}/openai/deployments/{config['deployment_id']}/chat/completions",
            headers=headers,
            json=payload,
            params={"api-version": "2024-10-21"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            state = provider_pb2.ResourceState(
                id=f"chat-{uuid.uuid4().hex[:8]}",
                type="azure_openai_chat_completion",
                status="completed"
            )
            
            state.attributes.update({
                "response_id": result["id"],
                "model": result["model"],
                "content": result["choices"][0]["message"]["content"],
                "prompt_tokens": result["usage"]["prompt_tokens"],
                "completion_tokens": result["usage"]["completion_tokens"],
                "total_tokens": result["usage"]["total_tokens"],
                "finish_reason": result["choices"][0]["finish_reason"]
            })
            
            return provider_pb2.ApplyResourceChangeResponse(new_state=state)
        else:
            context.abort(grpc.StatusCode.INTERNAL, f"Azure OpenAI API error: {response.text}")
```

## Enterprise Authentication
```python
# Managed Identity authentication
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

# System-assigned managed identity
credential = ManagedIdentityCredential()

# User-assigned managed identity
credential = ManagedIdentityCredential(client_id="your-client-id")

# Service principal authentication
credential = ClientSecretCredential(
    tenant_id="your-tenant-id",
    client_id="your-client-id", 
    client_secret="your-client-secret"
)
```

## Use Cases
- **Conversational AI**: Customer service chatbots
- **Code Generation**: Automated code creation and review
- **Content Creation**: Technical documentation generation
- **Data Analysis**: Natural language queries to data
- **Decision Support**: AI-powered recommendations
