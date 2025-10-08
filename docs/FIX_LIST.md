# Fix List - Priority Order

## CRITICAL FIXES (Must Fix Now)

### 1. Fix Executor.py Import and ResourceState Bug
**File**: `src/aicl/executor.py`
**Lines**: 1-3, 36-39

**Current (Wrong)**:
```python
import proto.provider_pb2 as provider_pb2
# ...
resource_state = provider_pb2.ResourceState(...)
```

**Should Be**:
```python
from aicl.state.manager import ResourceState
# ...
resource_state = ResourceState(...)
```

### 2. Fix _handle_diagnostics Missing Variable
**File**: `src/aicl/core/engine.py`
**Line**: 107

**Current (Wrong)**:
```python
print(f"  [{severity}] {diag.summary}: {diag.detail}")
```

**Should Be**:
```python
severity = provider_pb2.Diagnostic.Severity.Name(diag.severity)
print(f"  [{severity}] {diag.summary}: {diag.detail}")
```

### 3. Fix HCL Interpolation Parsing
**File**: `src/aicl/executor.py`
**Lines**: 18-25

**Current (Wrong)**:
```python
if isinstance(value, str) and value.startswith('resource.'):
    parts = value.split('.')
```

**Should Be**:
```python
if isinstance(value, str) and ('resource.' in value):
    # Strip ${} wrapper if present
    clean_value = value.strip('${}').strip()
    if clean_value.startswith('resource.'):
        parts = clean_value.split('.')
```

### 4. Fix Planner Dependency Detection
**File**: `src/aicl/planner.py`
**Lines**: 22-27

**Same Issue**: Need to strip `${}` wrapper before checking for `resource.` prefix.

## HIGH PRIORITY FIXES

### 5. Test on Host System First
**Action**: Bypass Docker container for engine, run directly on host

**Steps**:
1. Create Python virtual environment
2. Install dependencies
3. Run `python3 run.py rag_pipeline_test.aicl` directly
4. Debug provider connection issues without Docker-in-Docker complexity

### 6. Add Provider Startup Logging
**File**: `providers/*/server.py`

**Add to each provider**:
```python
import sys
print(f"Starting {provider_name} provider...", file=sys.stderr, flush=True)
# ... existing serve() code
print(f"{provider_name} provider listening on port {port}...", file=sys.stderr, flush=True)
```

### 7. Consolidate Duplicate Code
**Files**: `src/aicl/core/engine.py`, `src/aicl/executor.py`

**Duplicate**: `_dict_to_struct` method exists in both files

**Solution**: Create `src/aicl/utils.py` with shared utilities.

## MEDIUM PRIORITY FIXES

### 8. Remove Unused get_all_resources_as_dict
**File**: `src/aicl/state/manager.py`
**Lines**: 97-106

**Issue**: This method was added for HCL context evaluation but is never used.

**Action**: Remove it or document why it's needed for future use.

### 9. Simplify Executor Interface
**File**: `src/aicl/executor.py`

**Current**: `execute_node(node_id, resource_map)`
**Better**: `execute_node(node)` where node is a proper object with all needed data

### 10. Add Type Hints Throughout
**All Files**: Missing comprehensive type hints

**Benefits**: Better IDE support, catch bugs earlier

## ARCHITECTURAL IMPROVEMENTS

### 11. Separate Protobuf and Domain Models
**Issue**: Confusion between `provider_pb2.ResourceState` (protobuf) and `ResourceState` (dataclass)

**Solution**:
- Rename dataclass to `ManagedResourceState`
- Add clear conversion methods between protobuf and domain models

### 12. Add Integration Test Suite
**New File**: `tests/integration/test_rag_pipeline.py`

**Coverage**:
- Test file_loader provider independently
- Test text_splitter provider independently
- Test two-stage pipeline with mocked dependencies
- Test full pipeline end-to-end

### 13. Provider Registry Pattern
**New File**: `src/aicl/registry.py`

**Purpose**: Centralize provider metadata (images, versions, capabilities)

**Benefit**: Remove container image info from HCL files

## TESTING STRATEGY

### Phase 1: Fix Critical Bugs
1. Fix Executor imports
2. Fix diagnostics handler
3. Fix HCL interpolation parsing

### Phase 2: Verify on Host
1. Create venv
2. Install dependencies
3. Run experiment directly (no Docker wrapper)
4. Verify providers connect successfully

### Phase 3: Re-containerize
1. Once working on host, rebuild Docker image
2. Test in container with proper networking
3. Document Docker-in-Docker requirements

### Phase 4: Complete Refactoring
1. Add integration tests
2. Remove duplicate code
3. Complete migration to new components
4. Update documentation

## SUCCESS METRICS

- [ ] `file_loader_test.aicl` runs successfully
- [ ] `rag_pipeline_test.aicl` runs successfully with dependency resolution
- [ ] All providers connect without errors
- [ ] State files persist correctly
- [ ] Code passes linting with no errors
- [ ] Integration tests pass
