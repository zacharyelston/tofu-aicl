# Provider gRPC Methods

## ApplyResourceChange

**Purpose:** Create or update a Replit resource

### Parameters
```python
request: ApplyResourceChangeRequest
    type_name: str              # "replit_extension" | "replit_authenticated_session"
    config: Struct              # Resource configuration
    prior_state: Struct | None  # Previous state if updating
```

### Returns
```python
ApplyResourceChangeResponse:
    new_state: Struct  # Resource state with id, type, status, attributes
```

### Performance
- Extension initialization: < 10s
- Authentication: < 5s
- Overall timeout: 30s max

---

## ReadDataSource

**Purpose:** Fetch current workspace and user data

### Parameters
```python
request: ReadDataSourceRequest
    type_name: str   # "replit_workspace_data"
    config: Struct   # Data source configuration
```

### Returns
```python
ReadDataSourceResponse:
    state: Struct  # Data source state with workspace/user info
```

### Performance
- Data fetch: < 3s
- Overall timeout: 10s

---

## DestroyResource

**Purpose:** Clean up and dispose of Replit resources

### Parameters
```python
request: DestroyResourceRequest
    type_name: str        # Resource type to destroy
    current_state: Struct # Current resource state
```

### Returns
```python
DestroyResourceResponse: {}  # Empty on success
```

### Side Effects
- Extension: Calls dispose() function
- Auth session: Invalidates local token reference
- Logs destruction operation