# Error Conditions

## gRPC Error Codes

### INVALID_ARGUMENT (Code 3)
**When:** Invalid configuration parameters
- Name too long (>255 chars)
- Invalid version format (not semver)
- Invalid timeout (<1000ms or >60000ms)
- Invalid permissions (not in [read, write, execute])

**Response:** Detailed validation error message

**Example:**
```
INVALID_ARGUMENT: Extension name must be 1-255 chars, got 300
```

---

### FAILED_PRECONDITION (Code 9)
**When:** Required dependencies not met
- Auth session without extension initialized
- Workspace data without extension

**Response:** Clear dependency message

**Example:**
```
FAILED_PRECONDITION: Replit extension must be initialized before authentication
```

---

### DEADLINE_EXCEEDED (Code 4)
**When:** Operation timeout
- JavaScript bridge execution > timeout
- Replit API call hangs
- Network latency excessive

**Response:** Timeout details

**Example:**
```
DEADLINE_EXCEEDED: Extension handshake timed out after 5000ms
```

---

### INTERNAL (Code 13)
**When:** Unexpected provider error
- JavaScript execution fails
- JSON parsing fails
- Unexpected exception

**Response:** Sanitized error message

**Example:**
```
INTERNAL: Failed to parse JavaScript output: Unexpected token
```

---

### NOT_FOUND (Code 5)
**When:** Resource doesn't exist
- Destroying non-existent resource
- Workspace/user data not accessible

**Response:** Resource identifier

**Example:**
```
NOT_FOUND: Resource ext-abc123 not found
```

---

### UNAVAILABLE (Code 14)
**When:** Service unavailable
- Network failures after retries
- Replit API down

**Response:** Retry information

**Example:**
```
UNAVAILABLE: Failed to connect to Replit API after 3 retries
```

## Retry Strategy

### Automatic Retries
- Max retries: 3
- Backoff: Exponential (100ms, 200ms, 400ms)
- Retry on: Network errors, API errors
- NO retry on: Timeouts, validation errors

### Error Logging
All errors logged with:
- Error code
- Sanitized message
- Execution time
- Request type