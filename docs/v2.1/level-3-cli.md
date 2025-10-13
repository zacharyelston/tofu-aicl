# Level 3: CLI Integration (40 points)

**Goal:** Wire everything into a working command-line interface  
**Time:** ~30 minutes  
**Complexity:** ⭐⭐ Intermediate  
**Depends On:** Level 1 + Level 2

## What You're Building

Connect all the pieces:
1. `cli/commands/run.py` - Orchestrate execution
2. `aicl_modular` - Main entry point with Typer

## Requirements

### Command: Run (`cli/commands/run.py`)

**Must Do:**
- Function `run_command(config_file, workdir, experiment_id, docker, mount, settings) -> int`
- Determine mode (docker CLI arg > settings.runtime.mode)
- Delegate to correct runner
- Return exit code

**Logic:**
```python
if docker is not None:
    use_docker = docker
else:
    use_docker = (settings.runtime.mode == "docker")

if use_docker:
    runner = DockerRunner(settings)
else:
    runner = LocalRunner(settings)

return runner.run(...)
```

**Test:**
```python
# Test docker override
result = run_command(
    Path("test.aicl"), Path("."), "test", 
    docker=True, mount=None, settings
)
# Should use DockerRunner even if settings.mode='local'
```

**Points:** 20
- Runner selection logic: 8 pts
- CLI override works: 6 pts
- Delegates correctly: 4 pts
- Returns exit code: 2 pts

---

### Entry Point: CLI (`aicl_modular`)

**Must Do:**
- Executable script using Typer (or argparse, or click)
- Global options: `--verbose`, `--config`, `--env-file`
- Command: `run <config.aicl>` with options
- Sets up logging and config before commands run

**Minimum Commands:**
```bash
./aicl_modular --help                    # Shows help
./aicl_modular run test.aicl             # Runs locally
./aicl_modular --verbose run test.aicl   # Debug mode
./aicl_modular run --docker test.aicl    # Force Docker
```

**Test:**
```bash
# Help works
./aicl_modular --help
echo $?  # Should be 0

# Run works
./aicl_modular run test.aicl
echo $?  # Should be 0 on success

# Docker flag works
./aicl_modular run --docker test.aicl
# Should execute in Docker
```

**Points:** 20
- CLI framework setup: 6 pts
- Global options work: 5 pts
- Run command works: 6 pts
- Exit codes correct: 3 pts

---

## Success Criteria

**Pass Level 3:**
- ✅ `./aicl_modular --help` works
- ✅ `./aicl_modular run test.aicl` executes
- ✅ `--verbose` enables debug logging
- ✅ `--docker` forces Docker mode
- ✅ Exit codes are correct
- ✅ Can run end-to-end without errors

**Fail Level 3:**
- ❌ CLI crashes
- ❌ Commands don't work
- ❌ Wrong runner selected
- ❌ Options ignored

---

## Example Minimal Implementation

### run.py (~25 lines)
```python
from pathlib import Path
from cli.runners.docker import DockerRunner
from cli.runners.local import LocalRunner

def run_command(config_file, workdir, experiment_id, docker, mount, settings):
    # Determine mode
    use_docker = docker if docker is not None else (settings.runtime.mode == "docker")
    
    # Select runner
    if use_docker:
        runner = DockerRunner(settings)
        result = runner.run(config_file, workdir, experiment_id, mount)
    else:
        runner = LocalRunner(settings)
        result = runner.run(config_file, workdir, experiment_id)
    
    # Log result
    if result == 0:
        print("✅ Success!")
    else:
        print("❌ Failed")
    
    return result
```

### aicl_modular (~40 lines)
```python
#!/usr/bin/env python3
import sys
from pathlib import Path
import typer

from cli.config import load_settings
from cli.logging_setup import setup_logging
from cli.commands.run import run_command

app = typer.Typer()

@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = False,
    config_file: str = None,
    env_file: str = None
):
    """AICL CLI"""
    ctx.obj = {
        "settings": load_settings(config_file, env_file),
        "logger": setup_logging(verbose)
    }

@app.command()
def run(
    ctx: typer.Context,
    config_file: Path,
    workdir: Path = Path("."),
    experiment_id: str = "default",
    docker: bool = None,
    mount: list[str] = None
):
    """Run AICL configuration"""
    result = run_command(
        config_file, workdir, experiment_id,
        docker, mount, ctx.obj["settings"]
    )
    sys.exit(result)

if __name__ == "__main__":
    app()
```

---

## Comparison Metrics

| Metric | What It Shows |
|--------|--------------|
| CLI framework choice | Tool knowledge |
| Options handling | CLI best practices |
| Integration quality | System thinking |
| Error messages | User experience focus |

---

## Common Pitfalls

1. **No shebang** - Script won't be executable
2. **Options don't propagate** - Context must pass settings
3. **Exit codes ignored** - Always `sys.exit(result)`
4. **No help text** - Users won't know how to use it

---

## Completion

**At this point you have a FULLY FUNCTIONAL CLI!**

Users can:
- ✅ Run configurations locally or in Docker
- ✅ Override settings via CLI flags
- ✅ See debug output with `--verbose`
- ✅ Get help with `--help`

**This is 80/100 points - a solid B grade!**

---

## Next Level (Optional)

Level 4 adds polish (Rich output, state management) but Level 3 is a complete, working tool.

Want perfect? → **Level 4: Polish**
