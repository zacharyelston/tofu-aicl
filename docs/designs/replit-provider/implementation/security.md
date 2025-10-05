# Security Considerations

## Token Management

### Rule 1: Never Log Plain Text Tokens

```python
# ❌ FORBIDDEN
logger.info(f"Token: {session.token}")
print(f"JWT: {token}")

# ✅ CORRECT
token_hash = hashlib.sha256(session.token.encode()).hexdigest()[:16]
logger.info(f"Token hash: {token_hash}")
```

### Rule 2: Memory-Only Storage

```python
# ❌ FORBIDDEN - Never persist tokens
with open('tokens.txt', 'w') as f:
    f.write(token)

db.execute("INSERT INTO tokens VALUES (?)", (token,))

# ✅ CORRECT - In-memory only
self._active_sessions[user_id] = AuthSession(token=token)
```

### Rule 3: Clear on Destruction

```python
def DestroyResource(self, request, context):
    session_id = request.current_state.id
    if session_id in self._active_sessions:
        del self._active_sessions[session_id]  # Clear from memory
```

## Input Validation

### Configuration Validation

```python
def _validate_extension_config(self, config: dict) -> None:
    # Required fields
    if 'name' not in config:
        raise ValueError("Extension name is required")

    # Name validation
    name = config['name']
    if not 1 <= len(name) <= 255:
        raise ValueError(f"Name length must be 1-255, got {len(name)}")

    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        raise ValueError(f"Invalid name format: {name}")

    # Version validation
    if 'version' in config:
        version = config['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            raise ValueError(f"Invalid semver version: {version}")

    # Timeout validation
    timeout = config.get('handshake_timeout', 5000)
    if not 1000 <= timeout <= 60000:
        raise ValueError(f"Timeout must be 1000-60000ms, got {timeout}")
```

## Error Sanitization

### Remove Sensitive Information

```python
def _sanitize_error(self, error: Exception) -> str:
    """Sanitize error message for client"""
    error_str = str(error)

    # Remove file paths
    error_str = re.sub(r'/Users/[^/]+/.*?\.py', '[path]', error_str)

    # Remove JWT tokens
    error_str = re.sub(
        r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
        '[token]',
        error_str
    )

    # Remove API keys
    error_str = re.sub(r'sk-[A-Za-z0-9]{48}', '[api_key]', error_str)

    return error_str
```

## JWT Token Hashing

### Secure Logging Pattern

```python
import hashlib

class AuthSession:
    def __post_init__(self):
        """Hash token on initialization"""
        self.token_hash = hashlib.sha256(self.token.encode()).hexdigest()[:16]

# Usage
logger.info(f"Session created: {session.token_hash}")  # Safe for logging
# Output: "Session created: a3f5c8e9d2b1f4a6"
```

## Response Validation

### Validate Before Returning

```python
def _execute_js(self, js_code: str) -> dict:
    """Execute JS and validate response"""
    result = self.js_bridge.execute(js_code)

    if not result.success:
        raise RuntimeError(f"JavaScript execution failed: {result.error}")

    # Validate response structure
    if not isinstance(result.data, dict):
        raise ValueError("Expected dict response from JavaScript")

    # Validate required fields
    if 'success' not in result.data:
        raise ValueError("Response missing 'success' field")

    return result.data
```

## Security Checklist

- [ ] All JWT tokens hashed before logging
- [ ] No tokens stored in files or databases
- [ ] Error messages sanitized (no file paths, tokens, keys)
- [ ] All configuration validated before use
- [ ] API responses validated before returning
- [ ] Cleanup functions clear sensitive data
- [ ] No plain text secrets in logs or output