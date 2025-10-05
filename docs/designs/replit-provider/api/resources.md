# Resource Type Specifications

## 1. replit_extension

**Purpose:** Initialize Replit extension and establish handshake with workspace

### Configuration Schema
```python
class ReplitExtensionConfig:
    name: str                    # Required: Extension display name (1-255 chars)
    version: str                 # Optional: Semver version (default: "1.0.0")
    auto_start: bool            # Optional: Auto-start on init (default: true)
    handshake_timeout: int      # Optional: Timeout in ms (default: 5000, max: 60000)
```

### Validation Rules
- `name`: Required, 1-255 characters, pattern: `^[a-zA-Z0-9\s\-_]+$`
- `version`: Optional, must match semver pattern if provided: `^\d+\.\d+\.\d+$`
- `auto_start`: Optional boolean
- `handshake_timeout`: Optional integer, range 1000-60000

### State Schema
```python
class ReplitExtensionState:
    id: str                      # Format: "ext-{uuid}"
    type: str                    # Always "replit_extension"
    status: str                  # "initialized" | "handshake_complete" | "failed"
    attributes: dict = {
        "name": str,
        "version": str,
        "handshake_status": str,  # "pending" | "complete" | "failed"
        "initialized_at": str,    # ISO 8601 timestamp
        "dispose_available": bool  # Whether cleanup function is registered
    }
```

### Example
```hcl
resource "replit_extension" "ai_workflow" {
  name = "AI Workflow Manager"
  version = "1.0.0"
  auto_start = true
  handshake_timeout = 5000
}
```

---

## 2. replit_authenticated_session

**Purpose:** Authenticate user and manage JWT token for secure operations

### Configuration Schema
```python
class ReplitAuthSessionConfig:
    required_permissions: list[str]  # Optional: Permissions to verify
    token_format: str               # Optional: "jwt" (default, only supported format)
```

### Validation Rules
- `required_permissions`: Optional list of strings, valid values: ["read", "write", "execute"]
- `token_format`: Optional, must be "jwt" if provided

### State Schema
```python
class ReplitAuthSessionState:
    id: str                      # Format: "auth-{user_id}"
    type: str                    # Always "replit_authenticated_session"
    status: str                  # "authenticated" | "failed"
    attributes: dict = {
        "user_id": str,          # Replit user ID
        "username": str,         # Replit username
        "token_hash": str,       # First 16 chars of SHA256(token) for debugging
        "authenticated_at": str, # ISO 8601 timestamp
        "permissions_verified": list[str]  # Permissions that were verified
    }
```

### Example
```hcl
resource "replit_authenticated_session" "user" {
  required_permissions = ["read", "write"]

  depends_on = [replit_extension.ai_workflow]
}
```

---

## 3. replit_workspace_data (Data Source)

**Purpose:** Read-only access to current workspace and user information

### Configuration Schema
```python
class ReplitWorkspaceDataConfig:
    include_files: bool          # Optional: Include file list (default: false)
    include_user: bool          # Optional: Include user info (default: true)
    include_metadata: bool      # Optional: Include workspace metadata (default: true)
```

### Validation Rules
- All fields optional booleans

### State Schema
```python
class ReplitWorkspaceDataState:
    id: str                      # Format: "workspace-{repl_id}"
    type: str                    # Always "replit_workspace_data"
    status: str                  # "ready" | "failed"
    attributes: dict = {
        # Workspace data
        "repl_id": str,
        "title": str,
        "language": str,
        "url": str,
        "created_at": str,       # ISO 8601
        "updated_at": str,       # ISO 8601

        # User data (if include_user=true)
        "user_id": str,
        "username": str,

        # File data (if include_files=true)
        "file_count": int,
        "files": list[dict],     # [{"name": str, "type": str}]

        # Metadata (if include_metadata=true)
        "metadata": dict
    }
```

### Example
```hcl
data "replit_workspace_data" "current" {
  include_files = true
  include_user = true
  include_metadata = true
}
```