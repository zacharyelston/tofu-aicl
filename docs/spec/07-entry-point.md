# Entry Point Specification

**File:** `aicl_modular`  
**Lines:** ~80  
**Dependencies:** `typer`, `sys`, all cli modules

## Purpose

Main CLI entry point - orchestrates commands.

## Structure

```python
#!/usr/bin/env python3
import typer
from cli.config import load_settings
from cli.logging_setup import setup_logging
from cli.commands.run import run_command
# ... other imports

app = typer.Typer(name="aicl", help="🚀 AICL CLI")

@app.callback()
def main(ctx, verbose, config_file, env_file):
    """Global options"""
    ctx.obj = {
        "logger": setup_logging(verbose),
        "settings": load_settings(config_file, env_file)
    }

@app.command()
def run(ctx, config_file, workdir, experiment_id, docker, mount):
    """🚀 Run AICL configuration"""
    sys.exit(run_command(..., ctx.obj["settings"]))

@app.command()
def validate(ctx, config_file):
    """✅ Validate configuration"""
    sys.exit(validate_command(config_file))

# State sub-app
state_app = typer.Typer(help="📊 Manage state")
app.add_typer(state_app, name="state")

@state_app.command("list")
def state_list_cmd(ctx, experiment_id):
    """📋 List resources"""
    settings = ctx.parent.obj["settings"]  # CRITICAL
    sys.exit(list_state(experiment_id, settings))

@app.command()
def config(ctx):
    """⚙️  Show configuration"""
    show_syntax(ctx.obj["settings"].as_dict(), "yaml", "Config")
    return 0

if __name__ == "__main__":
    app()
```

## Critical Requirements

### 1. Context Propagation
```python
# WRONG
ctx.obj["settings"]  # Fails in sub-commands

# RIGHT
settings = ctx.parent.obj["settings"] if ctx.parent else ctx.obj["settings"]
```

### 2. Exit Codes
```python
# All commands must return/exit
sys.exit(command_function(...))
# Or
return 0
```

### 3. Type Annotations
```python
from typing import Annotated, Optional, List

config_file: Annotated[Path, typer.Argument()]
verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False
```

## Test Cases

### Test 1: Help Text
```bash
./aicl_modular --help
# Should show commands: run, validate, state, config
```

### Test 2: Global Options
```bash
./aicl_modular --verbose run test.aicl
# Should enable DEBUG logging
```

### Test 3: Sub-Commands
```bash
./aicl_modular state list
# Should access parent context correctly
```

### Test 4: Exit Codes
```bash
./aicl_modular run non-existent.aicl
echo $?  # Should be non-zero
```

## Success Criteria

- ✅ All commands registered
- ✅ Context propagates correctly
- ✅ Exit codes consistent
- ✅ Help text clear
- ✅ File size < 120 lines

## Grading

| Criterion | Points |
|-----------|--------|
| Command registration | 8 |
| Context handling | 8 |
| Exit codes | 6 |
| Type annotations | 4 |
| Code quality | 4 |

**Total:** 30 points
