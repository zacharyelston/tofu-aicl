# Level 2: Execution (50 points)

**Goal:** Execute AICL configs in Docker and locally  
**Time:** ~45 minutes  
**Complexity:** ⭐⭐ Intermediate  
**Depends On:** Level 1 (needs config, logging)

## What You're Building

Two runner classes that execute .aicl configurations:
1. `cli/runners/docker.py` - Execute in Docker container
2. `cli/runners/local.py` - Execute on local system

## Requirements

### Runner 1: Docker (`cli/runners/docker.py`)

**Must Do:**
- Class `DockerRunner(settings)` 
- Method `run(config_file, workdir, experiment_id, mounts=None) -> int`
- Builds and runs `docker run` command
- Mounts state directory
- Returns exit code (0 = success)

**Must Handle:**
- State directory doesn't exist (create it)
- Custom volume mounts
- Environment file (if exists)

**Don't Care:**
- How you build the command (string concat, list, f-strings)
- Whether you use subprocess or os.system
- Log format

**Test:**
```python
from cli.runners.docker import DockerRunner
from pathlib import Path

runner = DockerRunner(settings)
result = runner.run(
    config_file=Path("test.aicl"),
    workdir=Path("."),
    experiment_id="test-001",
    mounts=None
)
assert result == 0  # success
assert Path(settings.paths.state_dir).exists()  # created
```

**Points:** 30
- Builds correct docker command: 10 pts
- Mounts state directory: 8 pts
- Handles missing directories: 5 pts
- Returns correct exit code: 4 pts
- Custom mounts work: 3 pts

---

### Runner 2: Local (`cli/runners/local.py`)

**Must Do:**
- Class `LocalRunner(settings)`
- Method `run(config_file, workdir, experiment_id) -> int`
- Executes AICL engine locally
- Changes to workdir, then restores
- Returns exit code

**Must Handle:**
- Import errors (AICL engine not available)
- Working directory restoration
- Exceptions

**Don't Care:**
- How you import the engine
- Whether you use os.chdir or pathlib
- Error messages

**Test:**
```python
from cli.runners.local import LocalRunner
import os

cwd = os.getcwd()
runner = LocalRunner(settings)
result = runner.run(Path("test.aicl"), Path("/tmp"), "test")
assert os.getcwd() == cwd  # restored
```

**Points:** 20
- Executes engine: 8 pts
- Directory change/restore: 6 pts
- Error handling: 4 pts
- Exit code correct: 2 pts

---

## Success Criteria

**Pass Level 2:**
- ✅ DockerRunner builds valid docker command
- ✅ DockerRunner creates state directory
- ✅ LocalRunner executes without crashing
- ✅ Both return correct exit codes
- ✅ Tests pass

**Fail Level 2:**
- ❌ Docker command malformed
- ❌ State directory not created
- ❌ Working directory not restored
- ❌ Crashes on execution

---

## Example Minimal Implementation

### docker.py (~30 lines)
```python
import subprocess
from pathlib import Path

class DockerRunner:
    def __init__(self, settings):
        self.settings = settings
        self.image = settings.runtime.docker_image
    
    def run(self, config_file, workdir, experiment_id, mounts=None):
        # Create state directory
        state_dir = Path(self.settings.paths.state_dir)
        state_dir.mkdir(parents=True, exist_ok=True)
        
        # Build command
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{state_dir.absolute()}:/app/state",
            self.image,
            "python3", "run.py", str(config_file)
        ]
        
        # Add custom mounts
        if mounts:
            for mount in mounts:
                cmd.extend(["-v", mount])
        
        # Run
        result = subprocess.run(cmd)
        return result.returncode
```

### local.py (~20 lines)
```python
import os
import sys
from pathlib import Path

class LocalRunner:
    def __init__(self, settings):
        self.settings = settings
    
    def run(self, config_file, workdir, experiment_id):
        original_dir = os.getcwd()
        
        try:
            os.chdir(workdir)
            # Import and run AICL engine
            from src.aicl.core.engine import AICLEngine
            engine = AICLEngine(str(config_file))
            engine.run()
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1
        finally:
            os.chdir(original_dir)
```

---

## Comparison Metrics

| Metric | What It Shows |
|--------|--------------|
| Command correctness | Understanding of Docker |
| Error handling | Robustness |
| Code organization | Design patterns |
| Edge cases handled | Thoroughness |

---

## Common Pitfalls

1. **Forgot to create dirs** - State directory must exist
2. **Directory not restored** - Always use try/finally
3. **Hardcoded paths** - Use settings object
4. **No error handling** - What if Docker isn't installed?

---

## Next Level

Once Level 2 passes → **Level 3: CLI Integration**
