# State Structure Example: v1 vs v2

## Overview

This document provides concrete examples of how resource state is structured in AICL v1 versus the proposed v2 architecture, highlighting the key improvements in error handling, type safety, and debugging capabilities.

## Current v1 State Structure

### ResourceState (v1)
```python
# src/aicl/state/manager.py (current)
@dataclass
class ResourceState:
    id: str                    # Provider-generated ID (e.g., "loader-src")
    type: str                  # Resource type (e.g., "loader_files")
    provider: str              # Provider name (e.g., "loader")
    attributes: dict           # Untyped attributes
    metadata: dict             # Untyped metadata
    status: str = "unknown"    # String status (no validation)
```

### Example v1 State File
```json
{
  "resources": {
    "loader-src": {
      "id": "loader-src",
      "type": "loader_files",
      "provider": "loader",
      "attributes": {
        "documents": [
          {"path": "src/main.py", "content": "..."},
          {"path": "src/utils.py", "content": "..."}
        ]
      },
      "metadata": {
        "created": "2025-10-06T22:00:00Z"
      },
      "status": "applied"
    }
  }
}
```

### v1 Problems Demonstrated

#### 1. Cryptic Dependency Resolution Errors
```python
# This fails with unclear error:
# KeyError: 'aicl_source' not found in state

# Why? Because AICL resource name != provider ID
resource "loader_files" "aicl_source" {  # AICL name: "aicl_source"
  path = "./src"
}
# But state stores it as: "loader-src"  # Provider ID: "loader-src"
```

#### 2. No Type Safety
```python
# Current code assumes structure exists:
documents = state.attributes['documents']  # Can throw KeyError
for doc in documents:                      # Can throw TypeError if not list
    content = doc['content']               # Can throw KeyError
```

#### 3. Poor Error Context
```python
# When something fails, you get:
# Exception: Referenced resource 'loader_files.aicl_source' not found in state
#
# No information about:
# - What resources ARE available
# - What the dependency chain looks like
# - What the actual state structure contains
```

## Proposed v2 State Structure

### ResourceState (v2)
```python
# src/aicl/v2/domain/resource.py (proposed)
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class ResourceStatus(Enum):
    PENDING = "pending"
    APPLYING = "applying"
    APPLIED = "applied"
    FAILED = "failed"
    DESTROYING = "destroying"
    DESTROYED = "destroyed"

class ResourceState:
    """Immutable resource state with rich metadata"""
    def __init__(self,
                 resource_id: str,           # AICL resource name (e.g., "aicl_source")
                 type_name: str,             # Resource type (e.g., "loader_files")
                 provider: str,              # Provider name (e.g., "loader")
                 attributes: Dict[str, Any], # Typed attributes
                 metadata: Dict[str, Any],   # Rich metadata
                 status: ResourceStatus = ResourceStatus.PENDING):
        self.resource_id = resource_id
        self.type_name = type_name
        self.provider = provider
        self.attributes = attributes
        self.metadata = metadata
        self.status = status
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        # Validate required attributes based on type
        self._validate_attributes()

    def _validate_attributes(self) -> None:
        """Type-specific validation"""
        if self.type_name == "loader_files":
            if "documents" not in self.attributes:
                raise ValueError(f"loader_files resource missing 'documents' attribute")
            if not isinstance(self.attributes["documents"], list):
                raise ValueError(f"loader_files 'documents' must be a list")

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Safe attribute access with defaults"""
        return self.attributes.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Serializable representation"""
        return {
            "resource_id": self.resource_id,
            "type_name": self.type_name,
            "provider": self.provider,
            "attributes": self.attributes,
            "metadata": self.metadata,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
```

### Example v2 State File
```json
{
  "workflow_id": "index_codebase_to_pinecone_20251006_220000",
  "resources": {
    "aicl_source": {
      "resource_id": "aicl_source",
      "type_name": "loader_files",
      "provider": "loader",
      "attributes": {
        "documents": [
          {
            "path": "src/main.py",
            "content": "...",
            "size_bytes": 1024,
            "last_modified": "2025-10-06T21:30:00Z"
          }
        ],
        "total_files": 15,
        "total_size_bytes": 45678
      },
      "metadata": {
        "execution_time_ms": 150,
        "provider_version": "1.0.0",
        "source_path": "./src",
        "glob_pattern": "**/*.py"
      },
      "status": "applied",
      "created_at": "2025-10-06T22:00:00Z",
      "updated_at": "2025-10-06T22:00:00Z"
    }
  },
  "execution_metadata": {
    "started_at": "2025-10-06T22:00:00Z",
    "completed_at": "2025-10-06T22:05:00Z",
    "total_execution_time_ms": 300000,
    "resources_executed": 4,
    "resources_failed": 0
  }
}
```

## v2 Improvements Demonstrated

### 1. Clear Dependency Resolution
```python
# v2 uses AICL resource names consistently
resource "loader_files" "aicl_source" {  # AICL name: "aicl_source"
  path = "./src"
}

# State stores it as: "aicl_source"  # Same name!
# Dependency resolution works intuitively:
resource "splitter_text" "code_chunks" {
  documents = resource.loader_files.aicl_source.attributes.documents
  #                                 ^^^^^^^^^^^
  #                                 Matches state key exactly
}
```

### 2. Type Safety and Validation
```python
# v2 provides safe access patterns:
resource_state = state_store.get_resource("aicl_source")
if resource_state and resource_state.status == ResourceStatus.APPLIED:
    documents = resource_state.get_attribute("documents", [])
    total_files = resource_state.get_attribute("total_files", 0)

    # Type validation happens at state creation
    # No runtime KeyError or TypeError surprises
```

### 3. Rich Error Context
```python
# When dependency resolution fails in v2:
class DependencyResolutionError(Exception):
    def __init__(self, reference: str, available_resources: List[str],
                 execution_state: Dict[str, ResourceState]):
        self.reference = reference
        self.available_resources = available_resources
        self.execution_state = execution_state

        super().__init__(self._build_error_message())

    def _build_error_message(self) -> str:
        return f"""
        Dependency Resolution Failed
        ===========================
        Failed Reference: {self.reference}

        Available Resources:
        {chr(10).join(f"  - {name} ({state.type_name}, {state.status.value})"
                      for name, state in self.execution_state.items())}

        Suggestion: Check if the resource name matches exactly and the resource
        has been successfully applied before this dependency.

        Resource Details:
        {json.dumps({name: state.to_dict() for name, state in self.execution_state.items()}, indent=2)}
        """

# Example error output:
# DependencyResolutionError:
# Dependency Resolution Failed
# ===========================
# Failed Reference: resource.loader_files.aicl_source.attributes.documents
#
# Available Resources:
#   - aicl_source (loader_files, applied)
#   - code_chunks (splitter_text, pending)
#
# Suggestion: Check if the resource name matches exactly and the resource
# has been successfully applied before this dependency.
```

## Migration Path

### Automatic State Migration
```python
# src/aicl/v2/infrastructure/state_migration.py
class StateV1ToV2Migrator:
    def migrate_state_file(self, v1_state_path: str, v2_state_path: str) -> None:
        """Migrate v1 state format to v2 with validation"""
        with open(v1_state_path, 'r') as f:
            v1_data = json.load(f)

        v2_data = {
            "workflow_id": f"migrated_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "resources": {},
            "execution_metadata": {
                "migrated_from": "v1",
                "migration_time": datetime.utcnow().isoformat()
            }
        }

        # Map v1 provider IDs back to AICL resource names
        name_mapping = self._build_name_mapping(v1_data)

        for provider_id, v1_resource in v1_data.get("resources", {}).items():
            aicl_name = name_mapping.get(provider_id, provider_id)

            v2_resource = ResourceState(
                resource_id=aicl_name,  # Use AICL name, not provider ID
                type_name=v1_resource["type"],
                provider=v1_resource["provider"],
                attributes=v1_resource["attributes"],
                metadata=v1_resource.get("metadata", {}),
                status=ResourceStatus(v1_resource.get("status", "unknown"))
            )

            v2_data["resources"][aicl_name] = v2_resource.to_dict()

        # Atomic write with backup
        self._atomic_write(v2_state_path, v2_data)
```

## Testing Examples

### v1 Testing Challenges
```python
# Hard to test because of tight coupling and no interfaces
def test_dependency_resolution_v1():
    # Must mock entire Docker environment
    # Must mock gRPC providers
    # Must create real state files
    # Brittle and slow
    pass
```

### v2 Testing Advantages
```python
# Easy to test with dependency injection
def test_dependency_resolution_v2():
    # Mock state store
    mock_state_store = MockStateStore()
    mock_state_store.add_resource(ResourceState(
        resource_id="aicl_source",
        type_name="loader_files",
        provider="loader",
        attributes={"documents": [{"path": "test.py", "content": "test"}]},
        metadata={}
    ))

    # Test dependency resolver in isolation
    resolver = HclDependencyResolver()
    resolved = resolver.resolve_references(
        {"documents": "${resource.loader_files.aicl_source.attributes.documents}"},
        mock_state_store.get_all_resources()
    )

    assert resolved["documents"] == [{"path": "test.py", "content": "test"}]
```

## Summary

The v2 state structure provides:

1. **Consistent Naming**: AICL resource names used throughout
2. **Type Safety**: Validation and safe access patterns
3. **Rich Metadata**: Comprehensive execution information
4. **Better Errors**: Actionable error messages with context
5. **Testability**: Easy to mock and test in isolation
6. **Migration Path**: Automatic migration from v1 to v2

This addresses the core debugging nightmare we experienced with cryptic `KeyError` messages and provides a solid foundation for the modular v2 architecture.
