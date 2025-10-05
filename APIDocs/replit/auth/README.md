# Auth API (Experimental)

Secure authentication for Replit extensions with JWT token management.

## Key Methods
- `auth.getAuthToken()` - Get JWT token for current user
- `auth.verifyAuthToken(token)` - Verify and decode JWT token
- `auth.authenticate()` - Full user authentication

## tofu-aicl Integration
Essential for securing AI workflows and tracking user access to expensive AI resources.

## Files
- `methods.md` - Detailed method documentation
- `security.md` - Security considerations and best practices
- `tofu-aicl-integration.md` - Provider implementation examples