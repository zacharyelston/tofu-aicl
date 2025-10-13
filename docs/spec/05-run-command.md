# Run Command Specification

**File:** `cli/commands/run.py`  
**Lines:** ~40  
**Dependencies:** `pathlib`, `typing`, `loguru`, runners, utils

## Purpose

Orchestrate run execution by delegating to appropriate runner.

## Function: `run_command()`

```python
def run_command(
    config_file: Path,
    workdir: Path,
    experiment_id: str,
    docker: Optional[bool],
    mount: Optional[List[str]],
    settings
) -> int:
    """Run AICL configuration
    
    Determines execution mode and delegates to runner
    """
```

## Logic

```python
# Determine mode
use_docker = docker if docker is not None else settings.runtime.mode == "docker"

# Delegate
if use_docker:
    runner = DockerRunner(settings)
    result = runner.run(config_file, workdir, experiment_id, mount)
else:
    runner = LocalRunner(settings)
    result = runner.run(config_file, workdir, experiment_id)

# Log success
if result == 0:
    print_success("Execution complete!")
    logger.success("Run completed", experiment_id=experiment_id)

return result
```

## Test Cases

### Test 1: Docker Mode
```python
result = run_command(Path("test.aicl"), Path("."), "test", docker=True, None, settings)
# Should use DockerRunner
```

### Test 2: Local Mode
```python
result = run_command(Path("test.aicl"), Path("."), "test", docker=False, None, settings)
# Should use LocalRunner
```

### Test 3: Auto Mode
```python
settings.runtime.mode = "docker"
result = run_command(Path("test.aicl"), Path("."), "test", None, None, settings)
# Should use DockerRunner (from settings)
```

## Success Criteria

- ✅ Delegates to correct runner
- ✅ Respects CLI override
- ✅ Falls back to settings
- ✅ Logs appropriately
- ✅ File size < 45 lines

## Grading

| Criterion | Points |
|-----------|--------|
| Runner selection | 6 |
| CLI override | 4 |
| Logging | 3 |
| Code quality | 2 |

**Total:** 15 points
