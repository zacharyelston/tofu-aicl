# Local Runner Specification

**File:** `cli/runners/local.py`  
**Lines:** ~45  
**Dependencies:** `pathlib`, `os`, `sys`, `loguru`, `rich`

## Purpose

Execute AICL configurations locally without Docker.

## Class: `LocalRunner`

### Constructor
```python
def __init__(self, settings):
    self.settings = settings
```

### Method: `run()`
```python
def run(self, config_file: Path, workdir: Path, experiment_id: str) -> int:
    """Execute configuration locally
    
    Returns:
        Exit code (0 = success, non-zero = failure)
    """
```

## Test Cases

### Test 1: Basic Execution
```python
runner = LocalRunner(settings)
result = runner.run(Path("test.aicl"), Path("."), "test-001")
assert result == 0
```

### Test 2: Working Directory Change
```python
original = os.getcwd()
runner = LocalRunner(settings)
runner.run(Path("test.aicl"), Path("/tmp"), "test")
assert os.getcwd() == original  # Restored
```

## Success Criteria

- ✅ Executes AICL engine
- ✅ Changes to workdir (and restores)
- ✅ Returns correct exit code
- ✅ Handles exceptions gracefully
- ✅ File size < 50 lines

## Grading

| Criterion | Points |
|-----------|--------|
| Execution | 8 |
| Directory handling | 5 |
| Error handling | 4 |
| Code quality | 3 |

**Total:** 20 points
