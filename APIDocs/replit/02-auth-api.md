# Replit Extensions Auth API (Experimental)

## Overview
The Auth API provides secure authentication capabilities for Replit extensions, allowing you to verify user identity and obtain authentication tokens for secure operations.

## Key Features
- **JWT Token Generation**: Get unique JWT tokens for authenticated users
- **Token Verification**: Verify and decode JWT tokens securely
- **User Authentication**: Authenticate users within the extension context
- **Secure Identity Management**: Handle user identity securely

## Usage
```javascript
import { experimental } from '@replit/extensions';
const { auth } = experimental;
```

## Methods

### auth.getAuthToken()
Returns a unique JWT token for the current authenticated user.

```typescript
getAuthToken(): Promise<string>
```

**Example:**
```javascript
const token = await auth.getAuthToken();
console.log('User token:', token);
```

### auth.verifyAuthToken(token)
Verifies a provided JWT token and returns the decoded payload.

```typescript
verifyAuthToken(token: string): Promise<{ payload: any, protectedHeader: any }>
```

**Example:**
```javascript
const verification = await auth.verifyAuthToken(token);
console.log('User ID:', verification.payload.userId);
```

### auth.authenticate()
Performs full user authentication and returns authentication result.

```typescript
authenticate(): Promise<AuthenticateResult>
```

## Types
- **AuthenticatedUser**: User information after successful authentication
- **AuthenticateResult**: Result object containing authentication status and user data

## Integration with tofu-aicl

This API would be crucial for a Replit provider that needs to authenticate users for AI workflows:

```hcl
resource "replit_authenticated_session" "ai_user" {
  authentication_method = "jwt"
  required_permissions = ["read", "write", "execute"]

  # Use authentication for AI workflow access
  ai_workflow_access = true
}

resource "replit_secure_workspace" "protected_ai" {
  depends_on = [replit_authenticated_session.ai_user]

  name = "Secure AI Workspace"
  authentication_required = true

  # Only authenticated users can access AI models
  ai_model_access = {
    openrouter_enabled = true
    anthropic_enabled = true
    requires_auth = true
  }
}
```

## Provider Implementation
```python
class ReplitProvider(provider_pb2_grpc.ProviderServicer):
    def _authenticate_user(self, config):
        """Authenticate user in Replit workspace"""
        auth_script = """
        import { experimental } from '@replit/extensions';
        const { auth } = experimental;

        try {
            const result = await auth.authenticate();
            const token = await auth.getAuthToken();

            return {
                success: true,
                user: result.user,
                token: token
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
        """

        return self._execute_in_replit(auth_script)

    def ApplyResourceChange(self, request, context):
        config = MessageToDict(request.config)

        if request.type_name == "replit_authenticated_session":
            auth_result = self._authenticate_user(config)

            if not auth_result.get('success'):
                return self._create_error_response(
                    f"Authentication failed: {auth_result.get('error')}"
                )

            state = provider_pb2.ResourceState(
                id=f"auth-{auth_result['user']['id']}",
                type="replit_authenticated_session",
                status="authenticated"
            )

            state.attributes.update({
                "user_id": auth_result['user']['id'],
                "username": auth_result['user']['username'],
                "token_hash": hashlib.sha256(auth_result['token'].encode()).hexdigest()[:16],
                "authenticated_at": datetime.utcnow().isoformat()
            })

            return provider_pb2.ApplyResourceChangeResponse(new_state=state)
```

## Security Considerations
- **Token Storage**: Never store JWT tokens in plain text
- **Token Expiration**: Always check token validity before use
- **Secure Transmission**: Use HTTPS for all authentication requests
- **User Privacy**: Only request necessary user information

## Use Cases for AI Workflows
1. **Secure AI Model Access**: Authenticate users before allowing access to expensive AI models
2. **Workflow Ownership**: Associate AI-generated code with authenticated users
3. **Usage Tracking**: Track AI resource usage per authenticated user
4. **Collaborative AI**: Enable secure sharing of AI workflows between team members
5. **Audit Trails**: Maintain security logs of AI operations per user