# Docker Runner Specification

**File:** `cli/runners/docker.py`  
**Lines:** ~70  
**Dependencies:** `subprocess`, `pathlib`, `loguru`, `rich`

## Purpose

Execute AICL configurations in Docker containers with:
- Volume mounting (state, experiments, custom)
- Environment variable injection
- Safe attribute access (Dynaconf compatibility)
- Interactive shell support

## Class: `DockerRunner`

### Constructor

```python
def __init__(self, settings):
    """
    Initialize Docker runner
    
    Args:
        settings: Dynaconf settings object
    """
    self.settings = settings
    self.image = settings.runtime.docker_image
```

### Method: `run()`

```python
def run(
    self,
    config_file: Path,
    workdir: Path,
    experiment_id: str,
    mounts: Optional[List[str]] = None
) -> int:
    """
    Execute AICL configuration in Docker
    
    Args:
        config_file: Path to .aicl configuration
        workdir: Working directory
        experiment_id: Experiment identifier
        mounts: Additional volume mounts (format: "host:container:mode")
        
    Returns:
        Exit code (0 = success, non-zero = failure)
        
    Side Effects:
        - Creates state directory if not exists
        - Runs Docker container
        - Logs command and results
    """
```

### Method: `_build_command()`

```python
def _build_command(
    self,
    config_file: Path,
    workdir: Path,
    mounts: Optional[List[str]]
) -> List[str]:
    """
    Build Docker run command
    
    Private helper method
    
    Returns:
        List of command arguments for subprocess.run()
    """
```

### Method: `shell()`

```python
def shell(self, workdir: Path = Path(".")) -> None:
    """
    Start interactive Docker shell
    
    Args:
        workdir: Working directory to mount
        
    Side Effects:
        - Runs interactive Docker container
        - Blocks until user exits
    """
```

## Docker Command Structure

```bash
docker run --rm \
  --env-file .env \
  -v /path/to/state:/app/terraform.tfstate.d \
  -v /path/to/experiments:/app/experiments \
  -v /custom/mount:/app/mount:ro \
  tofu-aicl:latest \
  python3 run.py config.aicl
```

## Volume Mounts

### Automatic Mounts

1. **State Directory** (read-write)
   - Host: `{settings.paths.state_dir}`
   - Container: `/app/terraform.tfstate.d`
   - Purpose: Persist state across runs

2. **Experiments Directory** (read-write)
   - Host: `{settings.paths.experiments_dir}`
   - Container: `/app/experiments`
   - Purpose: Store experiment results

### Custom Mounts

Format: `"host_path:container_path:mode"`
- Mode: `ro` (read-only) or `rw` (read-write)
- Example: `./data:/app/data:ro`

## Safe Attribute Access

**CRITICAL:** Dynaconf doesn't support `.get()` on attributes.

```python
# ❌ WRONG - Will crash
docker_mounts = self.settings.docker.get('mounts', [])

# ✅ CORRECT - Safe access
docker_config = getattr(self.settings, 'docker', None)
docker_mounts = getattr(docker_config, 'mounts', []) if docker_config else []
```

## Error Handling

```python
# Command execution
try:
    result = subprocess.run(cmd, capture_output=False, text=True)
    if result.returncode != 0:
        logger.error("Docker execution failed", code=result.returncode)
    return result.returncode
except Exception as e:
    logger.exception("Docker error", error=str(e))
    return 1
```

## Test Cases

### Test 1: Basic Execution
```python
runner = DockerRunner(settings)
result = runner.run(
    config_file=Path("test.aicl"),
    workdir=Path("."),
    experiment_id="test-001",
    mounts=None
)
assert result == 0
```

### Test 2: Custom Mounts
```python
runner = DockerRunner(settings)
result = runner.run(
    config_file=Path("test.aicl"),
    workdir=Path("."),
    experiment_id="test-001",
    mounts=["./data:/app/data:ro"]
)
# Verify mount in command
assert "-v" in runner._build_command(...)
assert "./data:/app/data:ro" in runner._build_command(...)
```

### Test 3: State Directory Creation
```python
state_dir = Path("./test-state")
state_dir.rmdir()  # Ensure doesn't exist

runner = DockerRunner(settings)
runner.run(Path("test.aicl"), Path("."), "test-001")

assert state_dir.exists()
```

### Test 4: Safe Attribute Access
```python
# Settings without docker.mounts
settings_minimal = load_settings()
del settings_minimal.docker

runner = DockerRunner(settings_minimal)
# Should not crash
cmd = runner._build_command(Path("test.aicl"), Path("."), None)
assert isinstance(cmd, list)
```

### Test 5: Interactive Shell
```python
runner = DockerRunner(settings)
# Should open shell (manual test)
runner.shell(workdir=Path("."))
```

## Success Criteria

- ✅ Builds correct Docker command
- ✅ Mounts state directory (creates if needed)
- ✅ Supports custom mounts
- ✅ Safe attribute access (no crashes)
- ✅ Logs command for debugging
- ✅ Returns correct exit code
- ✅ Interactive shell works
- ✅ File size < 90 lines

## Example Implementation

```python
"""Docker runner"""

import subprocess
from pathlib import Path
from typing import List, Optional
from loguru import logger
from rich.console import Console

console = Console()


class DockerRunner:
    """Execute AICL in Docker containers"""
    
    def __init__(self, settings):
        self.settings = settings
        self.image = settings.runtime.docker_image
    
    def run(
        self,
        config_file: Path,
        workdir: Path,
        experiment_id: str,
        mounts: Optional[List[str]] = None
    ) -> int:
        """Execute configuration in Docker"""
        logger.info("Running in Docker", image=self.image)
        
        cmd = self._build_command(config_file, workdir, mounts)
        
        with console.status("[bold blue]Running Docker container..."):
            result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode != 0:
            logger.error("Docker execution failed", code=result.returncode)
        
        return result.returncode
    
    def _build_command(
        self,
        config_file: Path,
        workdir: Path,
        mounts: Optional[List[str]]
    ) -> List[str]:
        """Build Docker command"""
        cmd = ["docker", "run", "--rm"]
        
        # Environment
        if Path(".env").exists():
            cmd.extend(["--env-file", ".env"])
        
        # State directory mount
        state_dir = Path(self.settings.paths.state_dir)
        state_dir.mkdir(parents=True, exist_ok=True)
        cmd.extend(["-v", f"{state_dir.absolute()}:/app/terraform.tfstate.d"])
        
        # Custom mounts (safe access for Dynaconf)
        docker_config = getattr(self.settings, 'docker', None)
        docker_mounts = getattr(docker_config, 'mounts', []) if docker_config else []
        for mount in (mounts or docker_mounts):
            cmd.extend(["-v", mount])
        
        # Image and command
        cmd.extend([
            self.image,
            "python3", "run.py", str(config_file)
        ])
        
        logger.debug("Docker command", cmd=" ".join(cmd))
        return cmd
    
    def shell(self, workdir: Path = Path(".")):
        """Start interactive shell"""
        logger.info("Starting Docker shell")
        
        cmd = [
            "docker", "run", "--rm", "-it",
            "--env-file", ".env",
            "-v", f"{workdir.absolute()}:/app/work",
            "-w", "/app/work",
            "--entrypoint", "/bin/bash",
            self.image,
        ]
        
        subprocess.run(cmd)
```

## Grading

| Criterion | Points | Requirements |
|-----------|--------|--------------|
| Command building | 8 | Correct Docker args |
| Volume mounts | 6 | State + custom mounts |
| Safe access | 5 | No crashes on missing attrs |
| Error handling | 3 | Returns exit codes |
| Logging | 3 | Debug command logged |
| Shell method | 2 | Interactive works |
| Code quality | 3 | Clean, documented |

**Total:** 30 points
