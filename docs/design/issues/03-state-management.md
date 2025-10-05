# Issue 03: State Management Race Conditions

**Priority:** CRITICAL  
**Week:** 1

## Problem

State manager has fuzzy matching and no locking:

```python
def get_resource_by_name(self, name: str):
    for res in self.current_state.resources.values():
        if name in res.id:  # Substring match - dangerous!
            return res
```

**Issues:**
1. Substring matching is ambiguous
2. No locking for concurrent access
3. Partial state on failure
4. No transactions

## Example Failures

```python
# Resource IDs: "docs", "docs_v2"
state.get_resource_by_name("docs")  # Which one?
```

## Solution

Use exact lookups with composite keys:

```python
class StateManager:
    def __init__(self):
        self.resources_by_id = {}  # id -> ResourceState
        self.resources_by_key = {}  # (type, name) -> id
    
    def add_resource(self, resource: ResourceState):
        # Generate stable ID
        resource_id = f"{resource.type}_{resource.name}"
        
        # Store with exact lookups
        self.resources_by_id[resource_id] = resource
        self.resources_by_key[(resource.type, resource.name)] = resource_id
    
    def get_resource_exact(self, type: str, name: str):
        resource_id = self.resources_by_key.get((type, name))
        if not resource_id:
            return None
        return self.resources_by_id[resource_id]
    
    def save_atomic(self):
        # Write to temp file
        temp = self.state_file.with_suffix('.tmp')
        with open(temp, 'w') as f:
            json.dump(self.to_dict(), f)
        
        # Atomic rename
        temp.replace(self.state_file)
```

## Locking (Optional)

For shared state, add file locking:

```python
import fcntl

def with_lock(self):
    lock_file = self.state_file.with_suffix('.lock')
    with open(lock_file, 'w') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
```

## Tests Needed

- Exact lookup by (type, name)
- No ambiguous matches
- Atomic save/rollback
- Concurrent access (if needed)
