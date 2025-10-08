# Error Context Example: Rich Debugging Information

## Overview

This document demonstrates the dramatic improvement in error handling and debugging capabilities between AICL v1 and v2, showing how rich error context transforms debugging from hours of frustration to minutes of focused problem-solving.

## Current v1 Error Experience

### Typical v1 Error Scenario
```python
# What you see in v1:
Exception: Referenced resource 'loader_files.aicl_source' not found in state

# What you DON'T know:
# - What resources ARE available?
# - What's the actual state structure?
# - Is this a naming issue or execution order issue?
# - How do I fix this?
```

### v1 Error Sources
```python
# src/aicl/executor.py (current implementation)
def _resolve_dependencies(self, config_attrs, state_manager):
    try:
        # Fragile traversal logic
        resolved_value = all_resources[resource_type][resource_name]
    except KeyError:
        # Generic error with no context
        raise Exception(f"Referenced resource '{resource_type}.{resource_name}' not found in state")
```

### Real v1 Debugging Session (Hours Lost)
```
1. Exception: Referenced resource 'loader_files.aicl_source' not found in state
   → Check .aicl file: resource name looks correct

2. Check state file manually:
   → Find resource stored as "loader-src", not "aicl_source"
   → Why the name mismatch?

3. Dig into provider code:
   → Provider generates its own ID
   → No connection to AICL resource name

4. Try to fix by changing resource name:
   → Breaks other references
   → Creates more confusion

5. Eventually discover the root cause:
   → State uses provider IDs, not AICL names
   → No documentation of this behavior
   → No clear fix without architectural changes

Total time lost: 3-4 hours for a simple naming issue
```

## AICL v2 Rich Error Context

### v2 Error Architecture
```python
# src/aicl/v2/domain/exceptions.py
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

@dataclass
class ExecutionContext:
    """Rich context for error reporting"""
    workflow_id: str
    current_resource: Optional[str]
    execution_phase: str
    available_resources: List[str]
    resource_states: Dict[str, Any]
    dependency_chain: List[str]
    configuration: Dict[str, Any]
    timestamp: datetime

class AiclError(Exception):
    """Base exception with rich context"""
    def __init__(self, message: str, context: ExecutionContext = None,
                 suggestions: List[str] = None, related_docs: List[str] = None):
        self.context = context
        self.suggestions = suggestions or []
        self.related_docs = related_docs or []
        super().__init__(self._build_rich_message(message))

    def _build_rich_message(self, base_message: str) -> str:
        """Build comprehensive error message"""
        lines = [
            "🚨 AICL Execution Error",
            "=" * 50,
            f"Error: {base_message}",
            ""
        ]

        if self.context:
            lines.extend(self._format_context())

        if self.suggestions:
            lines.extend(self._format_suggestions())

        if self.related_docs:
            lines.extend(self._format_documentation())

        return "\n".join(lines)

class DependencyResolutionError(AiclError):
    """Specific error for dependency resolution with targeted help"""

    def __init__(self, reference: str, available_resources: List[str],
                 execution_state: Dict[str, Any], similar_names: List[str] = None,
                 context: ExecutionContext = None):
        self.reference = reference
        self.available_resources = available_resources
        self.execution_state = execution_state
        self.similar_names = similar_names or []

        message = f"Cannot resolve dependency reference: {reference}"
        suggestions = self._generate_suggestions()

        super().__init__(message, context, suggestions)

    def _generate_suggestions(self) -> List[str]:
        """Generate actionable suggestions based on error context"""
        suggestions = []

        if self.similar_names:
            suggestions.append(f"Did you mean one of: {', '.join(self.similar_names)}?")

        if not self.available_resources:
            suggestions.append("No resources have been executed yet. Check execution order.")

        suggestions.extend([
            "Check resource name spelling and case sensitivity",
            "Verify the resource is defined before this dependency",
            "Ensure the referenced resource executed successfully"
        ])

        return suggestions

class ProviderExecutionError(AiclError):
    """Provider-specific execution error with provider context"""

    def __init__(self, provider_name: str, resource_name: str,
                 grpc_error: Exception, provider_logs: str = "",
                 context: ExecutionContext = None):
        self.provider_name = provider_name
        self.resource_name = resource_name
        self.grpc_error = grpc_error
        self.provider_logs = provider_logs

        message = f"Provider '{provider_name}' failed executing resource '{resource_name}'"
        suggestions = self._generate_provider_suggestions()

        super().__init__(message, context, suggestions)

    def _generate_provider_suggestions(self) -> List[str]:
        """Provider-specific troubleshooting suggestions"""
        suggestions = [
            f"Check if {self.provider_name} provider container is running",
            f"Verify {self.provider_name} provider configuration",
            "Check provider logs for detailed error information"
        ]

        # Provider-specific suggestions
        if "connection refused" in str(self.grpc_error).lower():
            suggestions.append("Provider may not be started or accessible")
        elif "timeout" in str(self.grpc_error).lower():
            suggestions.append("Provider may be overloaded or unresponsive")

        return suggestions

class StateCorruptionError(AiclError):
    """State file corruption with recovery suggestions"""

    def __init__(self, state_file: str, corruption_details: str,
                 backup_available: bool = False, context: ExecutionContext = None):
        self.state_file = state_file
        self.corruption_details = corruption_details
        self.backup_available = backup_available

        message = f"State file corruption detected: {state_file}"
        suggestions = self._generate_recovery_suggestions()

        super().__init__(message, context, suggestions)

    def _generate_recovery_suggestions(self) -> List[str]:
        """State recovery suggestions"""
        suggestions = []

        if self.backup_available:
            suggestions.append("Backup state file available - consider restoring")

        suggestions.extend([
            "Check disk space and file permissions",
            "Verify state file is not being modified by another process",
            "Consider re-running workflow from clean state"
        ])

        return suggestions
```

### v2 Error Examples

#### 1. Dependency Resolution Error
```python
# v2 Error Output:
🚨 AICL Execution Error
==================================================
Error: Cannot resolve dependency reference: resource.loader_files.aicl_source.attributes.documents

📍 Execution Context:
Workflow ID: index_codebase_20251006_220000
Current Resource: code_chunks (splitter_text)
Execution Phase: dependency_resolution
Timestamp: 2025-10-06 22:15:30 UTC

📋 Available Resources:
  ✅ loader-src (loader_files) - applied
  ⏳ code_chunks (splitter_text) - pending

🔍 Resource Details:
{
  "loader-src": {
    "resource_id": "loader-src",
    "type_name": "loader_files",
    "status": "applied",
    "attributes": {
      "documents": [
        {"path": "src/main.py", "content": "..."},
        {"path": "src/utils.py", "content": "..."}
      ],
      "total_files": 15
    }
  }
}

💡 Suggestions:
  • Did you mean: loader-src (similar to 'aicl_source')?
  • Check resource name spelling and case sensitivity
  • Verify the resource is defined before this dependency
  • Ensure the referenced resource executed successfully

📚 Related Documentation:
  • docs/v2/examples/01-state-example.md - State structure explanation
  • docs/v2/examples/02-dependency-resolution.md - Dependency resolution guide

🔧 Quick Fix:
Change your reference from:
  documents = resource.loader_files.aicl_source.attributes.documents
To:
  documents = resource.loader_files.loader-src.attributes.documents
```

#### 2. Provider Execution Error
```python
# v2 Provider Error Output:
🚨 AICL Execution Error
==================================================
Error: Provider 'openrouter' failed executing resource 'code_vectors'

📍 Execution Context:
Workflow ID: index_codebase_20251006_220000
Current Resource: code_vectors (openrouter_embeddings)
Execution Phase: provider_execution
Timestamp: 2025-10-06 22:18:45 UTC

🔌 Provider Details:
Provider: openrouter
Container: openrouter_provider:latest
gRPC Error: StatusCode.UNAUTHENTICATED - API key not provided

📋 Provider Logs:
2025-10-06 22:18:45 ERROR: Missing required environment variable: OPENROUTER_API_KEY
2025-10-06 22:18:45 ERROR: Authentication failed for OpenRouter API

💡 Suggestions:
  • Check if openrouter provider container is running
  • Verify openrouter provider configuration
  • Check provider logs for detailed error information
  • Provider authentication failed - verify API key configuration

🔧 Quick Fix:
1. Set environment variable: export OPENROUTER_API_KEY=your_key_here
2. Or add to .env file: OPENROUTER_API_KEY=your_key_here
3. Restart the provider container

📚 Related Documentation:
  • docs/providers/openrouter.md - OpenRouter provider setup
  • docs/configuration/environment-variables.md - Environment configuration
```

#### 3. State Corruption Error
```python
# v2 State Error Output:
🚨 AICL Execution Error
==================================================
Error: State file corruption detected: .aicl/state.json

📍 Execution Context:
Workflow ID: index_codebase_20251006_220000
Current Resource: None
Execution Phase: state_loading
Timestamp: 2025-10-06 22:20:15 UTC

🗂️ Corruption Details:
Invalid JSON syntax at line 15, column 8
Expected ',' or '}' but found 'null'

💾 Backup Status:
✅ Backup available: .aicl/state.json.backup (2025-10-06 22:00:00)

💡 Suggestions:
  • Backup state file available - consider restoring
  • Check disk space and file permissions
  • Verify state file is not being modified by another process
  • Consider re-running workflow from clean state

🔧 Recovery Options:
1. Restore from backup:
   cp .aicl/state.json.backup .aicl/state.json

2. Start fresh (loses current state):
   rm .aicl/state.json
   aicl run experiments/index_codebase_to_pinecone.aicl

3. Manual repair:
   Edit .aicl/state.json and fix JSON syntax error at line 15

📚 Related Documentation:
  • docs/troubleshooting/state-recovery.md - State recovery procedures
  • docs/v2/examples/01-state-example.md - State file format
```

## Error Context Collection

### Automatic Context Gathering
```python
# src/aicl/v2/application/error_handler.py
class ErrorContextCollector:
    """Automatically collect rich context for errors"""

    def __init__(self, state_store: StateStore, event_bus: EventBus):
        self._state_store = state_store
        self._event_bus = event_bus

    def collect_context(self, workflow_id: str, current_resource: str = None,
                       execution_phase: str = "unknown") -> ExecutionContext:
        """Collect comprehensive execution context"""

        # Get current state
        all_resources = self._state_store.get_all_resources()
        available_resources = [
            f"{name} ({state.type_name}) - {state.status.value}"
            for name, state in all_resources.items()
        ]

        # Build dependency chain
        dependency_chain = self._build_dependency_chain(current_resource, all_resources)

        # Get configuration context
        configuration = self._get_current_configuration(workflow_id)

        return ExecutionContext(
            workflow_id=workflow_id,
            current_resource=current_resource,
            execution_phase=execution_phase,
            available_resources=available_resources,
            resource_states={name: state.to_dict() for name, state in all_resources.items()},
            dependency_chain=dependency_chain,
            configuration=configuration,
            timestamp=datetime.utcnow()
        )

    def _build_dependency_chain(self, resource_name: str,
                               all_resources: Dict[str, ResourceState]) -> List[str]:
        """Build the dependency chain leading to current resource"""
        if not resource_name:
            return []

        # Trace dependencies backwards
        chain = []
        visited = set()

        def trace_dependencies(name: str):
            if name in visited or name not in all_resources:
                return

            visited.add(name)
            resource = all_resources[name]

            # Find resources this one depends on
            dependencies = self._extract_dependencies_from_config(resource.metadata.get('config', {}))
            for dep in dependencies:
                trace_dependencies(dep)
                if dep not in chain:
                    chain.append(dep)

            if name not in chain:
                chain.append(name)

        trace_dependencies(resource_name)
        return chain
```

### Integration with Workflow Orchestrator
```python
# src/aicl/v2/application/orchestrator.py
class WorkflowOrchestrator:
    """Orchestrator with comprehensive error handling"""

    def __init__(self, dependency_resolver: DependencyResolver,
                 resource_executor: ResourceExecutor, state_store: StateStore,
                 event_bus: EventBus, error_collector: ErrorContextCollector):
        self._dependency_resolver = dependency_resolver
        self._resource_executor = resource_executor
        self._state_store = state_store
        self._event_bus = event_bus
        self._error_collector = error_collector

    async def execute_workflow(self, workflow: WorkflowExecution) -> ExecutionResult:
        """Execute workflow with rich error context"""
        try:
            execution_plan = self._dependency_resolver.build_execution_plan(workflow.config)

            for resource_def in execution_plan:
                try:
                    # Collect context before execution
                    context = self._error_collector.collect_context(
                        workflow.workflow_id,
                        resource_def.name,
                        "resource_execution"
                    )

                    # Execute resource
                    result = await self._execute_resource_with_context(resource_def, context)

                    # Update state
                    await self._state_store.save_resource_state(result)

                except Exception as e:
                    # Enhance error with rich context
                    context = self._error_collector.collect_context(
                        workflow.workflow_id,
                        resource_def.name,
                        "error_handling"
                    )

                    # Convert to rich error based on type
                    rich_error = self._convert_to_rich_error(e, context, resource_def)

                    # Publish error event for observability
                    await self._event_bus.publish(WorkflowErrorEvent(rich_error, context))

                    raise rich_error

            return ExecutionResult.success(workflow.workflow_id)

        except Exception as e:
            # Top-level error handling
            if not isinstance(e, AiclError):
                context = self._error_collector.collect_context(workflow.workflow_id)
                e = AiclError(f"Unexpected workflow error: {str(e)}", context)

            return ExecutionResult.failure(e)
```

## Debugging Workflow Comparison

### v1 Debugging Process (Hours)
```
1. See generic error message
2. Manually inspect state files
3. Dig through provider logs
4. Try to understand code flow
5. Make educated guesses
6. Repeat until fixed
```

### v2 Debugging Process (Minutes)
```
1. Read rich error message with context
2. Follow suggested fixes
3. Use provided quick fixes
4. Reference related documentation
5. Problem solved
```

## Summary

v2 error handling provides:

1. **Rich Context**: Complete execution state and dependency information
2. **Actionable Suggestions**: Specific steps to resolve issues
3. **Quick Fixes**: Copy-paste solutions for common problems
4. **Documentation Links**: Direct links to relevant documentation
5. **Provider Integration**: Provider-specific error handling and logs
6. **State Recovery**: Backup and recovery procedures for state corruption
7. **Observability**: Error events for monitoring and alerting

This transforms debugging from a frustrating guessing game into a guided problem-solving process, dramatically reducing time to resolution and improving developer experience.
