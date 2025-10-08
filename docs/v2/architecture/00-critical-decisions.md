# AICL v2 Critical Architectural Decisions

## Overview

This document captures the critical architectural decisions made for AICL v2, providing clear direction for implementation and eliminating ambiguity in the design.

## Decision Summary

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| **State Compatibility** | ❌ **Break Compatibility** | No existing users, clean slate approach |
| **Async Migration** | 🚀 **Big-Bang Conversion** | Aggressive timeline, avoid hybrid complexity |
| **Provider Interface** | 🔄 **Require Provider Updates** | Clean architecture, consistent patterns |
| **Timeline** | ⚡ **Aggressive (11 days)** | No users to impact, focused sprint approach |

## Detailed Decisions

### 1. State Compatibility: BREAK COMPATIBILITY ❌

**Decision**: Complete break from v1 state format, no backward compatibility.

**Rationale**:
- No existing users to impact
- v1 state structure is fundamentally flawed (provider IDs vs AICL names)
- Clean slate allows optimal v2 design
- Eliminates migration complexity and technical debt

**Implementation Impact**:
- No state migration utilities needed
- No hybrid state support
- Clean v2 state format from day one
- Simplified testing (no compatibility scenarios)

**Example**:
```json
// v1 State (ABANDONED)
{
  "resources": {
    "loader-src": {  // Provider-generated ID
      "id": "loader-src",
      "type": "loader_files"
    }
  }
}

// v2 State (NEW FORMAT)
{
  "workflow_id": "index_codebase_20251006",
  "resources": {
    "aicl_source": {  // AICL resource name
      "resource_id": "aicl_source",
      "type_name": "loader_files",
      "status": "applied"
    }
  }
}
```

### 2. Async Migration: BIG-BANG CONVERSION 🚀

**Decision**: Convert entire codebase to async/await in one phase, no gradual migration.

**Rationale**:
- Aggressive timeline favors focused approach
- Hybrid sync/async creates complexity and bugs
- No users means no gradual rollout needed
- Cleaner architecture with consistent async patterns

**Implementation Impact**:
- All interfaces use `async def` from day one
- All provider calls are async
- Event bus is async
- State operations are async
- No sync compatibility layer

**Example**:
```python
# v2 Interface (ALL ASYNC)
class ResourceExecutor(ABC):
    @abstractmethod
    async def execute_resource(self, resource_def: ResourceDefinition,
                              config: Dict) -> ResourceState:
        pass

class StateStore(ABC):
    @abstractmethod
    async def save_resource_state(self, state: ResourceState) -> None:
        pass

    @abstractmethod
    async def get_resource(self, resource_id: str) -> Optional[ResourceState]:
        pass
```

### 3. Provider Interface: REQUIRE PROVIDER UPDATES 🔄

**Decision**: Update all providers to new v2 interface, no adapter layer.

**Rationale**:
- Consistent with "break compatibility" decision
- Clean architecture without legacy baggage
- Only ~5 providers exist (manageable scope)
- Better long-term maintainability
- Aggressive timeline benefits from simplicity

**Implementation Impact**:
- All providers must implement new async interface
- Consistent error handling across providers
- Unified configuration patterns
- No adapter complexity

**Provider Update Required**:
```python
# OLD v1 Provider Interface (DEPRECATED)
class FileLoaderProvider(provider_pb2_grpc.ProviderServicer):
    def ApplyResourceChange(self, request, context):
        # Sync gRPC implementation
        return provider_pb2.ApplyResourceChangeResponse(new_state=state)

# NEW v2 Provider Interface (REQUIRED)
class FileLoaderProvider(ResourceProvider):
    async def execute_resource(self, resource_def: ResourceDefinition,
                              config: Dict[str, Any]) -> ResourceState:
        # Async implementation with rich error handling
        try:
            documents = await self._load_files(config['path'], config['glob'])
            return ResourceState(
                resource_id=resource_def.name,  # Use AICL name!
                type_name=resource_def.type_name,
                provider="file_loader",
                attributes={"documents": documents},
                metadata={"execution_time_ms": execution_time},
                status=ResourceStatus.APPLIED
            )
        except Exception as e:
            raise ProviderExecutionError(
                provider_name="file_loader",
                resource_name=resource_def.name,
                original_error=e,
                context=self._build_error_context()
            )
```

### 4. Timeline: AGGRESSIVE (11 days) ⚡

**Decision**: Maintain aggressive 11-day timeline with focused sprint approach.

**Rationale**:
- No users means no gradual rollout constraints
- Breaking changes eliminate compatibility complexity
- Big-bang approach reduces hybrid state complexity
- Focused team can move quickly without legacy concerns

**Implementation Strategy**:
- **Days 1-2**: Foundation (domain models, interfaces)
- **Days 3-4**: Application layer (orchestration, dependency resolution)
- **Days 5-7**: Infrastructure (providers, state, events) + Provider Updates
- **Days 8-9**: Integration testing and validation
- **Days 10-11**: Documentation and deployment

**Risk Mitigation**:
- Daily standups and progress tracking
- Clear acceptance criteria for each phase
- Rollback plan (revert to v1 if needed)
- Focused scope (no nice-to-have features)

## Implementation Principles

### 1. Clean Slate Approach
- No legacy compatibility code
- Optimal v2 design without constraints
- Modern async/await patterns throughout
- Rich error handling from day one

### 2. Aggressive Execution
- Daily deliverables and validation
- Focused team with clear responsibilities
- Minimal meetings, maximum coding time
- Clear go/no-go decisions at each phase

### 3. Quality Gates
- All tests must pass before proceeding
- Performance benchmarks at each phase
- Code review for all major components
- Documentation updated in real-time

## Provider Migration Plan

### Providers to Update (5 total)
1. **file_loader** - Load files from filesystem
2. **text_splitter** - Split text into chunks
3. **openrouter** - Generate embeddings via OpenRouter API
4. **pinecone** - Vector database operations
5. **command_assertion** - Execute shell commands

### Provider Update Template
```python
# Template for v2 provider interface
class ProviderTemplate(ResourceProvider):
    async def execute_resource(self, resource_def: ResourceDefinition,
                              config: Dict[str, Any]) -> ResourceState:
        """Execute resource with v2 patterns"""
        start_time = time.time()

        try:
            # 1. Validate configuration
            self._validate_config(config)

            # 2. Execute provider logic
            result = await self._execute_provider_logic(config)

            # 3. Build resource state
            execution_time = int((time.time() - start_time) * 1000)

            return ResourceState(
                resource_id=resource_def.name,  # CRITICAL: Use AICL name
                type_name=resource_def.type_name,
                provider=self.provider_name,
                attributes=result,
                metadata={
                    "execution_time_ms": execution_time,
                    "provider_version": self.version
                },
                status=ResourceStatus.APPLIED
            )

        except Exception as e:
            raise ProviderExecutionError(
                provider_name=self.provider_name,
                resource_name=resource_def.name,
                original_error=e
            )
```

## Success Criteria

### Technical Validation
- [ ] All 5 providers updated and tested
- [ ] Complete async/await implementation
- [ ] New state format working correctly
- [ ] Rich error handling functional
- [ ] Performance meets v1 benchmarks

### Timeline Validation
- [ ] Phase 1 complete by Day 2
- [ ] Phase 2 complete by Day 4
- [ ] Phase 3 + Provider updates complete by Day 7
- [ ] Integration testing complete by Day 9
- [ ] Full system ready by Day 11

## Risk Assessment

### High Risk (Mitigated by Decisions)
- ~~State migration complexity~~ → ELIMINATED (breaking compatibility)
- ~~Hybrid sync/async bugs~~ → ELIMINATED (big-bang conversion)
- ~~Provider compatibility~~ → CONTROLLED (only 5 providers to update)
- ~~Timeline pressure~~ → MANAGED (aggressive but focused scope)

### Remaining Risks
- **Team availability** → Ensure dedicated team for 11 days
- **Scope creep** → Strict adherence to core functionality only
- **Integration issues** → Daily integration testing

## Next Steps

1. **Immediate**: Update implementation plan with these decisions
2. **Day 1**: Begin foundation layer with async interfaces
3. **Day 5**: Start provider updates in parallel with infrastructure
4. **Daily**: Validate progress against timeline and quality gates

These decisions eliminate the major architectural ambiguities and provide clear direction for aggressive implementation.
