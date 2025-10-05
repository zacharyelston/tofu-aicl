# Design Review: 2025-10-04

## Critical Issues Identified

### 1. **Incomplete Refactoring - Broken State**
**Severity**: CRITICAL

**Problem**: The engine was partially refactored to use `Parser`, `Planner`, and `Executor` components, but the refactoring is incomplete and has introduced bugs.

**Evidence**:
- `Executor` class uses wrong import: `provider_pb2.ResourceState` instead of `StateManager.ResourceState`
- `Executor` creates resource state incorrectly (line 36-39 in executor.py)
- Engine still has duplicate logic that should be in Executor
- `_handle_diagnostics` missing `severity` variable definition (line 107 in engine.py)

**Impact**: The experiment cannot run successfully due to these bugs.

### 2. **Dependency Resolution Not Working**
**Severity**: CRITICAL

**Problem**: The manual dependency resolution in both `Planner` and `Executor` assumes HCL interpolations are strings starting with `resource.`, but the `hcl2` library parses them differently.

**Evidence**:
- Debug output showed: `{'documents': '${resource.loader_files.docs.attributes.documents}'}`
- The `${}` syntax is not being stripped
- The resolution logic splits on `.` but doesn't handle the `${}` wrapper

**Root Cause**: We're trying to manually parse HCL interpolations instead of using the library's built-in capabilities.

### 3. **Provider Container Networking Issue**
**Severity**: HIGH

**Problem**: Provider containers start successfully but the engine cannot connect to them via gRPC.

**Evidence**:
- Container status: `running`
- Container logs: empty (no startup message)
- Connection refused on `127.0.0.1:{port}`

**Possible Causes**:
- Provider server not actually starting (silent failure)
- Port mapping issue between host and container
- Network namespace isolation in Docker-in-Docker scenario

### 4. **Executor Class Design Flaw**
**Severity**: HIGH

**Problem**: The `Executor` class has incorrect imports and creates resource states using the wrong class.

**Issues**:
- Line 36: Uses `provider_pb2.ResourceState` instead of the `ResourceState` from `aicl.state.manager`
- Missing import: `from aicl.state.manager import ResourceState`
- The `ResourceState` protobuf message and the Python dataclass are different types

### 5. **Missing Error Variable in Diagnostics Handler**
**Severity**: MEDIUM

**Problem**: `_handle_diagnostics` method references undefined `severity` variable.

**Location**: `src/aicl/core/engine.py`, line 107

**Fix**: Should be `severity = provider_pb2.Diagnostic.Severity.Name(diag.severity)`

### 6. **Duplicate Logic Across Components**
**Severity**: MEDIUM

**Problem**: The refactoring created duplicate code:
- `_dict_to_struct` exists in both `AICLEngine` and `Executor`
- Dependency resolution logic exists in both `Planner` and `Executor`
- State management scattered across multiple classes

**Impact**: Violates DRY principle, makes maintenance harder.

### 7. **HCL Interpolation Syntax Not Handled**
**Severity**: HIGH

**Problem**: The `hcl2` library preserves the `${}` syntax in interpolations, but our code expects clean `resource.` prefixes.

**Evidence**: Debug output showed `'${resource.loader_files.docs.attributes.documents}'` as a string.

**Solution Needed**: Either:
- Strip `${}` before parsing
- Use `hcl2` library's evaluation context (if it exists)
- Implement proper HCL expression evaluation

## Architectural Concerns

### 1. **Premature Modularization**
The refactoring into `Parser`, `Planner`, and `Executor` was done before the core functionality was working. This violated the principle of "make it work, then make it better."

### 2. **Lack of Integration Tests**
We have no automated tests to catch regressions during refactoring. Each change requires manual verification.

### 3. **Docker-in-Docker Complexity**
Running the engine inside a container that needs to start other containers adds significant complexity and networking challenges.

### 4. **State Management Confusion**
There are two different `ResourceState` types:
- Protobuf message: `provider_pb2.ResourceState`
- Python dataclass: `aicl.state.manager.ResourceState`

This causes confusion and bugs.

## Recommendations

### Immediate Actions (Priority 1)

1. **Fix Executor Import Bug**
   - Add correct import for `ResourceState` from `aicl.state.manager`
   - Fix line 36-39 to use the correct class

2. **Fix Diagnostics Handler**
   - Add missing `severity` variable definition

3. **Fix HCL Interpolation Parsing**
   - Strip `${}` wrapper from interpolation strings
   - Update dependency resolution to handle this correctly

4. **Test Outside Docker First**
   - Get the experiment working on the host system first
   - Then containerize once it's proven to work

### Short-Term Actions (Priority 2)

1. **Consolidate Duplicate Code**
   - Move `_dict_to_struct` to a utility module
   - Centralize dependency resolution in one place

2. **Add Integration Tests**
   - Create automated tests for the core engine
   - Test each provider independently

3. **Simplify Networking**
   - Consider using Docker networks instead of host networking
   - Add health check endpoints to providers

### Long-Term Actions (Priority 3)

1. **Complete Refactoring Properly**
   - Finish migrating all logic to the new components
   - Remove duplicate code from `AICLEngine`

2. **Implement Proper HCL Evaluation**
   - Research `hcl2` library's evaluation context capabilities
   - Implement native HCL expression evaluation

3. **Add Observability**
   - Add structured logging
   - Add metrics for provider startup times
   - Add tracing for dependency resolution

## Conclusion

The project has a solid foundation, but the recent refactoring introduced several critical bugs. The highest priority is to fix the immediate bugs and get the `rag_pipeline_test.aicl` experiment working. Once that's proven, we can continue with proper refactoring using a test-driven approach.