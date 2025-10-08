# Dependency Resolution Example

## Overview

This document demonstrates how dependency resolution works in AICL v1 versus v2, showing the improvements in clarity, error handling, and debugging capabilities.

## Current v1 Dependency Resolution

### The Problem Scenario
```hcl
# experiments/index_codebase_to_pinecone.aicl
resource "loader_files" "aicl_source" {
  path = "./src"
  glob = "**/*.py"
}

resource "splitter_text" "code_chunks" {
  documents = resource.loader_files.aicl_source.attributes.documents
  #           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  #           This reference causes cryptic errors
  chunk_size = 1500
}
```

### v1 Resolution Process (Broken)
```python
# src/aicl/executor.py (current implementation)
def _resolve_dependencies(self, config_attrs, state_manager):
    all_resources = state_manager.get_all_resources_as_dict()

    for key, value in config_attrs.items():
        if isinstance(value, str) and 'resource.' in value:
            clean_value = value.strip('${}').strip()
            parts = clean_value.split('.')[1:]  # Skip 'resource'

            try:
                # This traversal logic is fragile and error-prone
                resolved_value = all_resources
                for part in parts:
                    if isinstance(resolved_value, dict):
                        resolved_value = resolved_value[part]
                    else:
                        raise KeyError(f"Cannot traverse non-dict for part '{part}'")
                config_attrs[key] = resolved_value
            except KeyError as e:
                # Cryptic error with no context
                raise Exception(f"Could not resolve reference '{value}'. Part '{e.args[0]}' not found.")
```

### v1 Error Experience
```
Exception: Could not resolve reference 'resource.loader_files.aicl_source.attributes.documents'.
Part 'aicl_source' not found.

# What you DON'T know:
# - What resources ARE available?
# - What are their actual names in state?
# - What does the state structure look like?
# - Is this a naming issue or a dependency order issue?
```

### v1 State Structure (The Root Cause)
```json
{
  "resources": {
    "loader-src": {  // Provider generates this ID, not "aicl_source"!
      "id": "loader-src",
      "type": "loader_files",
      "provider": "loader",
      "attributes": {
        "documents": [...]
      }
    }
  }
}
```

## AICL v2 Dependency Resolution

### v2 Resolution Architecture
```python
# src/aicl/v2/application/dependency_resolver.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from ..domain.resource import ResourceDefinition, ResourceState
from ..domain.exceptions import DependencyResolutionError

class DependencyResolver(ABC):
    """Abstract interface for dependency resolution"""

    @abstractmethod
    def build_execution_plan(self, workflow_config: Dict) -> List[ResourceDefinition]:
        """Build topologically sorted execution plan"""
        pass

    @abstractmethod
    def resolve_references(self, config: Dict[str, Any],
                          current_state: Dict[str, ResourceState]) -> Dict[str, Any]:
        """Resolve resource references in configuration"""
        pass

class HclDependencyResolver(DependencyResolver):
    """HCL-specific dependency resolution with rich error context"""

    def resolve_references(self, config: Dict[str, Any],
                          current_state: Dict[str, ResourceState]) -> Dict[str, Any]:
        """Resolve references with comprehensive error handling"""
        resolved_config = config.copy()

        for key, value in config.items():
            if isinstance(value, str) and self._is_resource_reference(value):
                try:
                    resolved_value = self._resolve_single_reference(value, current_state)
                    resolved_config[key] = resolved_value
                except Exception as e:
                    # Rich error context with actionable information
                    raise DependencyResolutionError(
                        reference=value,
                        available_resources=list(current_state.keys()),
                        execution_state=current_state,
                        original_error=e
                    )

        return resolved_config

    def _resolve_single_reference(self, reference: str,
                                 current_state: Dict[str, ResourceState]) -> Any:
        """Resolve a single resource reference with detailed validation"""
        # Parse: resource.loader_files.aicl_source.attributes.documents
        parts = self._parse_reference(reference)

        resource_type = parts[1]      # loader_files
        resource_name = parts[2]      # aicl_source
        attribute_path = parts[3:]    # ['attributes', 'documents']

        # Validate resource exists
        if resource_name not in current_state:
            available_names = list(current_state.keys())
            similar_names = self._find_similar_names(resource_name, available_names)

            raise DependencyResolutionError(
                f"Resource '{resource_name}' not found in state",
                available_resources=available_names,
                suggestions=similar_names,
                execution_state=current_state
            )

        resource_state = current_state[resource_name]

        # Validate resource type matches
        if resource_state.type_name != resource_type:
            raise DependencyResolutionError(
                f"Resource '{resource_name}' is type '{resource_state.type_name}', "
                f"not '{resource_type}' as referenced",
                available_resources=list(current_state.keys()),
                execution_state=current_state
            )

        # Validate resource is in correct state
        if resource_state.status != ResourceStatus.APPLIED:
            raise DependencyResolutionError(
                f"Resource '{resource_name}' is in state '{resource_state.status.value}', "
                f"not 'applied'. Dependencies must be applied before use.",
                available_resources=list(current_state.keys()),
                execution_state=current_state
            )

        # Navigate attribute path safely
        current_value = resource_state.to_dict()
        for part in attribute_path:
            if isinstance(current_value, dict) and part in current_value:
                current_value = current_value[part]
            else:
                available_keys = list(current_value.keys()) if isinstance(current_value, dict) else []
                raise DependencyResolutionError(
                    f"Attribute '{part}' not found in resource '{resource_name}'",
                    available_attributes=available_keys,
                    resource_structure=resource_state.to_dict(),
                    execution_state=current_state
                )

        return current_value
```

### v2 Error Handling
```python
# src/aicl/v2/domain/exceptions.py
class DependencyResolutionError(Exception):
    """Rich error context for dependency resolution failures"""

    def __init__(self, message: str, available_resources: List[str] = None,
                 suggestions: List[str] = None, available_attributes: List[str] = None,
                 resource_structure: Dict = None, execution_state: Dict = None,
                 original_error: Exception = None):
        self.available_resources = available_resources or []
        self.suggestions = suggestions or []
        self.available_attributes = available_attributes or []
        self.resource_structure = resource_structure or {}
        self.execution_state = execution_state or {}
        self.original_error = original_error

        super().__init__(self._build_comprehensive_message(message))

    def _build_comprehensive_message(self, base_message: str) -> str:
        """Build actionable error message with context"""
        lines = [
            "AICL Dependency Resolution Failed",
            "=" * 40,
            f"Error: {base_message}",
            ""
        ]

        if self.available_resources:
            lines.extend([
                "Available Resources:",
                *[f"  - {name}" for name in sorted(self.available_resources)],
                ""
            ])

        if self.suggestions:
            lines.extend([
                "Did you mean:",
                *[f"  - {suggestion}" for suggestion in self.suggestions],
                ""
            ])

        if self.available_attributes:
            lines.extend([
                "Available Attributes:",
                *[f"  - {attr}" for attr in sorted(self.available_attributes)],
                ""
            ])

        if self.resource_structure:
            lines.extend([
                "Resource Structure:",
                json.dumps(self.resource_structure, indent=2),
                ""
            ])

        lines.extend([
            "Troubleshooting Tips:",
            "1. Check resource name spelling and case sensitivity",
            "2. Ensure the referenced resource is defined before this one",
            "3. Verify the resource has been successfully applied",
            "4. Check the attribute path matches the resource structure"
        ])

        return "\n".join(lines)
```

### v2 Error Experience (Much Better!)
```
AICL Dependency Resolution Failed
========================================
Error: Resource 'aicl_source' not found in state

Available Resources:
  - loader-src

Did you mean:
  - loader-src (similar to 'aicl_source')

Troubleshooting Tips:
1. Check resource name spelling and case sensitivity
2. Ensure the referenced resource is defined before this one
3. Verify the resource has been successfully applied
4. Check the attribute path matches the resource structure

Resource Details:
{
  "loader-src": {
    "resource_id": "loader-src",
    "type_name": "loader_files",
    "status": "applied",
    "attributes": {
      "documents": [...]
    }
  }
}
```

## v2 State Consistency Fix

### Consistent Naming Strategy
```python
# src/aicl/v2/infrastructure/grpc_executor.py
class GrpcResourceExecutor(ResourceExecutor):
    """gRPC executor that maintains AICL resource naming"""

    async def execute_resource(self, resource_def: ResourceDefinition,
                              config: Dict) -> ResourceState:
        """Execute resource and return state with AICL resource name"""
        provider = await self._provider_registry.get_provider(resource_def.type_name)

        # Execute provider
        grpc_response = await self._execute_grpc_request(provider, resource_def, config)

        # Convert response to domain model using AICL resource name
        return ResourceState(
            resource_id=resource_def.name,  # Use AICL name, not provider ID!
            type_name=resource_def.type_name,
            provider=resource_def.provider,
            attributes=self._extract_attributes(grpc_response),
            metadata=self._extract_metadata(grpc_response),
            status=self._convert_status(grpc_response.status)
        )
```

### v2 State Structure (Consistent)
```json
{
  "workflow_id": "index_codebase_20251006",
  "resources": {
    "aicl_source": {  // Uses AICL resource name consistently!
      "resource_id": "aicl_source",
      "type_name": "loader_files",
      "provider": "loader",
      "attributes": {
        "documents": [...],
        "total_files": 15
      },
      "status": "applied"
    }
  }
}
```

## Execution Plan Generation

### v2 Dependency Graph Building
```python
# src/aicl/v2/application/execution_planner.py
class ExecutionPlanner:
    """Build execution plans with dependency validation"""

    def build_execution_plan(self, workflow_config: Dict) -> List[ResourceDefinition]:
        """Build topologically sorted execution plan"""
        resources = self._extract_resources(workflow_config)
        dependency_graph = self._build_dependency_graph(resources)

        # Validate no circular dependencies
        self._validate_no_cycles(dependency_graph)

        # Topological sort for execution order
        execution_order = self._topological_sort(dependency_graph)

        return [resources[name] for name in execution_order]

    def _build_dependency_graph(self, resources: Dict[str, ResourceDefinition]) -> Dict[str, List[str]]:
        """Build dependency graph with validation"""
        graph = defaultdict(list)

        for resource_name, resource_def in resources.items():
            dependencies = self._extract_dependencies(resource_def.config)

            for dep_reference in dependencies:
                dep_name = self._parse_dependency_name(dep_reference)

                # Validate dependency exists
                if dep_name not in resources:
                    available = list(resources.keys())
                    similar = self._find_similar_names(dep_name, available)

                    raise DependencyResolutionError(
                        f"Resource '{resource_name}' depends on '{dep_name}' which is not defined",
                        available_resources=available,
                        suggestions=similar
                    )

                graph[dep_name].append(resource_name)

        return graph
```

## Testing Improvements

### v1 Testing Challenges
```python
# Hard to test - requires full Docker environment
def test_dependency_resolution_v1():
    # Must start real Docker containers
    # Must create real state files
    # Must mock gRPC providers
    # Brittle, slow, and hard to debug
    pass
```

### v2 Testing Advantages
```python
# Easy to test with dependency injection
def test_dependency_resolution_v2():
    # Arrange
    mock_state = {
        "aicl_source": ResourceState(
            resource_id="aicl_source",
            type_name="loader_files",
            provider="loader",
            attributes={"documents": [{"path": "test.py"}]},
            metadata={},
            status=ResourceStatus.APPLIED
        )
    }

    resolver = HclDependencyResolver()
    config = {"documents": "resource.loader_files.aicl_source.attributes.documents"}

    # Act
    resolved = resolver.resolve_references(config, mock_state)

    # Assert
    assert resolved["documents"] == [{"path": "test.py"}]

def test_dependency_resolution_error_context():
    """Test that errors provide actionable context"""
    mock_state = {
        "loader-src": ResourceState(...)  # Different name than expected
    }

    resolver = HclDependencyResolver()
    config = {"documents": "resource.loader_files.aicl_source.attributes.documents"}

    with pytest.raises(DependencyResolutionError) as exc_info:
        resolver.resolve_references(config, mock_state)

    error = exc_info.value
    assert "aicl_source" in str(error)
    assert "loader-src" in error.available_resources
    assert "loader-src" in error.suggestions  # Similar name suggestion
```

## Summary

v2 dependency resolution provides:

1. **Consistent Naming**: AICL resource names used throughout the system
2. **Rich Error Context**: Actionable error messages with suggestions
3. **Type Safety**: Validation at every step of resolution
4. **Testability**: Easy to test with mocked dependencies
5. **Performance**: Efficient graph algorithms for large workflows
6. **Debugging**: Clear execution plans and dependency visualization

This eliminates the debugging nightmare of cryptic dependency errors and provides a solid foundation for complex AI workflows.
