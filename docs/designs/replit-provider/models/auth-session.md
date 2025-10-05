# AuthSession Data Model

## Schema

```python
from dataclasses import dataclass
from datetime import datetime
import hashlib

@dataclass
class AuthSession:
    """
    Represents an authenticated user session with Replit
    """
    id: str                          # Unique identifier (auth-{user_id})
    user_id: str                     # Replit user ID
    username: str                    # Replit username
    token: str                       # JWT token (stored securely)
    token_hash: str                  # SHA256 hash for logging
    authenticated_at: datetime       # Timestamp of authentication
    permissions_verified: list[str]  # Verified permissions

    def __post_init__(self):
        """Hash token on initialization"""
        self.token_hash = hashlib.sha256(self.token.encode()).hexdigest()[:16]

    def verify_permissions(self, required: list[str]) -> bool:
        """Check if session has required permissions"""
        return all(perm in self.permissions_verified for perm in required)
```

## Validation Rules

- **id**: Format `auth-{user_id}`
- **user_id**: Non-empty string
- **username**: Non-empty string
- **token**: JWT format (validated by Replit API)
- **permissions_verified**: List of strings, valid values: read, write, execute

## Security Considerations

- **token**: NEVER logged in plain text
- **token_hash**: First 16 chars of SHA256 hash, safe for logging
- Token stored in memory only, never persisted to disk

## Example

```python
session = AuthSession(
    id="auth-user-xyz789",
    user_id="user-xyz789",
    username="zacelston",
    token="eyJhbGciOiJIUzI1NiIs...",  # Full JWT
    authenticated_at=datetime(2025, 10, 5, 10, 31, 0),
    permissions_verified=["read", "write"]
)
# session.token_hash automatically set to "a3f5c8e9d2b1f4a6"
```

## Security Rules

```python
# ❌ FORBIDDEN
logger.info(f"Token: {session.token}")

# ✅ CORRECT
logger.info(f"Token hash: {session.token_hash}")
```