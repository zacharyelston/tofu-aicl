# AICL v2 Architecture Design Document

## Executive Summary

AICL v2 represents a complete architectural redesign based on extensive research into infrastructure-as-code patterns (Terraform), workflow orchestration systems (Temporal, Kestra, Prefect), and domain-driven design principles. The current monolithic architecture has proven difficult to debug, test, and extend. This design addresses these fundamental issues through modular, research-backed patterns.

## Current Architecture Problems

### Critical Issues Identified
1. **Tight Coupling**: `AICLEngine` class manages parsing, state, providers, and execution
2. **Hidden Dependencies**: Resource references resolved at runtime with cryptic errors
3. **Mixed Concerns**: Container management mixed with business logic
4. **Poor Error Handling**: Generic exceptions without actionable context
5. **No Interfaces**: Direct coupling to concrete implementations
6. **Monolithic Design**: Single failure point brings down entire pipeline

### Debugging Nightmare Evidence
- Hours spent chasing `KeyError: 'attributes'` due to state structure assumptions
- Docker networking issues masked by business logic errors
- Resource dependency resolution failures with no context
- Provider connection errors buried in execution flow

## Research Foundation

### Terraform Patterns
- **Dependency Inversion**: Modules receive dependencies, don't create them
- **Explicit Dependencies**: All inputs declared in module interface
- **State Management**: Atomic operations with rollback capability

### Workflow Orchestration Insights
- **Kestra**: Message-driven architecture with worker pools
- **Temporal**: Event sourcing with deterministic replay
- **Prefect**: Clean separation of orchestration and execution

### Domain-Driven Design
- **Hexagonal Architecture**: Business logic isolated from infrastructure
- **Ports and Adapters**: Clear boundaries between layers
- **Dependency Inversion**: High-level modules don't depend on low-level modules

## AICL v2 Architecture

### Core Design Principles

1. **Single Responsibility**: Each component does one thing exceptionally well
2. **Dependency Inversion**: Business logic depends on abstractions, not implementations
3. **Explicit Dependencies**: All dependencies are injected, never hidden
4. **Fail Fast**: Errors surface immediately with actionable context
5. **Testable in Isolation**: Every component can be unit tested independently
6. **Event-Driven**: Loose coupling through message passing
7. **Deterministic State**: All state transitions are reproducible

### Layer Architecture

```
┌─────────────────────────────────────────┐
│           Infrastructure Layer          │
│  (gRPC, Files, Containers, HTTP)       │
├─────────────────────────────────────────┤
│           Application Layer             │
│     (Orchestration, Use Cases)         │
├─────────────────────────────────────────┤
│             Domain Layer                │
│      (Business Logic, Entities)        │
└─────────────────────────────────────────┘
```

### Domain Layer

Pure business logic with no infrastructure dependencies.

```python
class WorkflowExecution:
    """Represents a single AICL workflow execution"""
    def __init__(self, workflow_id: str, config: WorkflowConfig):
        self.workflow_id = workflow_id
        self.config = config
        self.state = ExecutionState.PENDING
        self.events: List[ExecutionEvent] = []

class ResourceDefinition:
    """Immutable resource definition from HCL"""
    def __init__(self, type_name: str, name: str, config: Dict[str, Any]):
        self.type_name = type_name
        self.name = name
        self.config = config
        self.dependencies = self._extract_dependencies(config)

class ResourceState:
    """Current state of a resource"""
    def __init__(self, resource_id: str, type_name: str, attributes: Dict, metadata: Dict):
        self.resource_id = resource_id
        self.type_name = type_name
        self.attributes = attributes
        self.metadata = metadata
        self.status = ResourceStatus.UNKNOWN
        self.created_at = datetime.utcnow()
```

### Application Layer

Orchestration logic that coordinates domain objects without knowing about infrastructure.

```python
class WorkflowOrchestrator:
    """Coordinates workflow execution without knowing about infrastructure"""
    def __init__(self,
                 dependency_resolver: DependencyResolver,
                 resource_executor: ResourceExecutor,
                 state_store: StateStore,
                 event_bus: EventBus):
        self._dependency_resolver = dependency_resolver
        self._resource_executor = resource_executor
        self._state_store = state_store
        self._event_bus = event_bus

    async def execute_workflow(self, workflow: WorkflowExecution) -> ExecutionResult:
        """Execute workflow with full error recovery and state management"""
        try:
            # 1. Build execution plan
            execution_plan = self._dependency_resolver.build_execution_plan(workflow.config)

            # 2. Execute resources in dependency order
            for resource_def in execution_plan:
                resolved_config = self._dependency_resolver.resolve_references(
                    resource_def.config,
                    self._state_store.get_current_state()
                )

                result = await self._resource_executor.execute_resource(
                    resource_def,
                    resolved_config
                )

                # 3. Update state atomically
                await self._state_store.save_resource_state(result)

                # 4. Publish event for observability
                await self._event_bus.publish(ResourceExecutedEvent(resource_def, result))

            return ExecutionResult.success(workflow.workflow_id)

        except Exception as e:
            # Comprehensive error context
            error_context = ExecutionErrorContext(
                workflow_id=workflow.workflow_id,
                failed_resource=resource_def.name if 'resource_def' in locals() else None,
                execution_state=self._state_store.get_current_state(),
                original_error=e
            )
            await self._event_bus.publish(WorkflowFailedEvent(error_context))
            return ExecutionResult.failure(error_context)
```

### Infrastructure Layer

Adapters that implement domain interfaces using specific technologies.

```python
class GrpcResourceExecutor(ResourceExecutor):
    """Adapter for gRPC-based AI providers"""
    def __init__(self, provider_registry: ProviderRegistry):
        self._provider_registry = provider_registry

    async def execute_resource(self, resource_def: ResourceDefinition, config: Dict) -> ResourceState:
        provider = await self._provider_registry.get_provider(resource_def.type_name)

        # Convert to provider-specific format
        request = self._build_grpc_request(resource_def, config)

        # Execute with retry and timeout
        response = await self._execute_with_retry(provider, request)

        # Convert back to domain model
        return self._convert_to_resource_state(response, resource_def)

class FileStateStore(StateStore):
    """File-based state persistence with atomic writes"""
    async def save_resource_state(self, resource_state: ResourceState) -> None:
        # Atomic write with backup
        temp_file = f"{self.state_file}.tmp"
        backup_file = f"{self.state_file}.backup"

        # Write to temp, move backup, move temp to final
        # This ensures we never lose state during writes
```

## Dependency Injection Container

Central registry for managing dependencies and configuration.

```python
class AiclContainer:
    """IoC container for dependency management"""
    def __init__(self, config: AiclConfig):
        self._config = config
        self._instances: Dict[Type, Any] = {}

    def get_orchestrator(self) -> WorkflowOrchestrator:
        return WorkflowOrchestrator(
            dependency_resolver=self.get_dependency_resolver(),
            resource_executor=self.get_resource_executor(),
            state_store=self.get_state_store(),
            event_bus=self.get_event_bus()
        )

    def get_dependency_resolver(self) -> DependencyResolver:
        if DependencyResolver not in self._instances:
            self._instances[DependencyResolver] = HclDependencyResolver()
        return self._instances[DependencyResolver]
```

## Error Handling and Observability

### Rich Error Context

```python
class ExecutionErrorContext:
    """Rich error context for debugging"""
    def __init__(self, workflow_id: str, failed_resource: str, execution_state: Dict, original_error: Exception):
        self.workflow_id = workflow_id
        self.failed_resource = failed_resource
        self.execution_state = execution_state
        self.original_error = original_error
        self.timestamp = datetime.utcnow()
        self.available_resources = list(execution_state.keys())

    def to_debug_report(self) -> str:
        return f"""
        AICL Execution Failed
        ====================
        Workflow: {self.workflow_id}
        Failed Resource: {self.failed_resource}
        Available Resources: {', '.join(self.available_resources)}

        Original Error: {self.original_error}

        Execution State:
        {json.dumps(self.execution_state, indent=2)}
        """
```

### Event-Driven Observability

```python
@dataclass
class ResourceExecutedEvent:
    resource_name: str
    execution_time: float
    output_size: int
    timestamp: datetime

@dataclass
class WorkflowFailedEvent:
    error_context: ExecutionErrorContext

@dataclass
class DependencyResolvedEvent:
    resource_name: str
    resolved_references: List[str]
```

## Benefits

### Debuggability
- Each component can be tested in isolation
- Rich error context with actionable information
- Event stream provides execution audit trail
- Clear separation makes issues easier to locate

### Flexibility
- Swap gRPC for HTTP providers without changing business logic
- Replace file storage with database without touching orchestration
- Add new provider types by implementing interfaces
- Configuration-driven provider management

### Reliability
- Atomic state operations prevent corruption
- Comprehensive error recovery
- Deterministic execution for reproducibility
- Event sourcing enables replay and debugging

### Performance
- Event-driven architecture enables async execution
- Resource execution can be parallelized safely
- State operations are optimized for the use case
- Provider connection pooling and reuse

## Testing Strategy

### Unit Testing
Each layer can be tested independently:
- Domain objects with pure business logic
- Application services with mocked dependencies
- Infrastructure adapters with integration tests

### Integration Testing
- End-to-end workflow execution
- Provider connectivity and error handling
- State persistence and recovery

### Property-Based Testing
- Dependency resolution correctness
- State transition invariants
- Error handling completeness

## Migration Compatibility

### Backward Compatibility
- Existing `.aicl` files work without changes
- Current provider containers remain compatible
- State format can be migrated automatically

### Gradual Migration
- New architecture can run alongside current system
- Individual components can be migrated incrementally
- Rollback strategy for each migration phase

## Conclusion

AICL v2 architecture addresses every pain point identified during the debugging sessions while following proven patterns from successful infrastructure and workflow systems. The modular design enables rapid development, easy debugging, and long-term maintainability.

The investment in proper architecture will pay dividends in development velocity, system reliability, and developer experience.
