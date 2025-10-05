# Data API

Access Replit's GraphQL API for user information, Repl metadata, and platform data.

## Key Methods
- `data.currentUser()` - Get current user information
- `data.currentRepl()` - Get current workspace metadata
- `data.userById()` / `data.userByUsername()` - Get other user info
- `data.replById()` / `data.replByUrl()` - Get other Repl info

## tofu-aicl Integration
Critical for context-aware AI workflows that need workspace and user information.

## Files
- `user-methods.md` - User-related API methods
- `repl-methods.md` - Repl/workspace-related methods
- `tofu-aicl-integration.md` - Provider implementation examples