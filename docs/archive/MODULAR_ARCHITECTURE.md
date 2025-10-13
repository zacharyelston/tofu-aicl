# Modular CLI Architecture

## Philosophy: Small Files, Clear Structure

Following your development rules: **modular, small files that are easy to edit**.

## Structure

```
cli/
├── __init__.py              # Package definition (5 lines)
├── config.py                # Configuration management (50 lines)
├── logging_setup.py         # Logging setup (30 lines)
├── commands/                # Each command in its own file
│   ├── run.py              # Run command (40 lines)
│   ├── validate.py         # Validate command (35 lines)
│   └── state.py            # State commands (60 lines)
├── runners/                 # Execution strategies
│   ├── docker.py           # Docker runner (70 lines)
│   └── local.py            # Local runner (45 lines)
└── utils/                   # Reusable utilities
    └── output.py           # Rich output helpers (50 lines)

aicl_modular                 # Main entry point (80 lines)
```

## File Sizes

| File | Lines | Purpose |
|------|-------|---------|
| `config.py` | 50 | Config loading only |
| `logging_setup.py` | 30 | Logging only |
| `runners/docker.py` | 70 | Docker execution |
| `runners/local.py` | 45 | Local execution |
| `commands/run.py` | 40 | Run orchestration |
| `commands/validate.py` | 35 | Validation |
| `commands/state.py` | 60 | State management |
| `utils/output.py` | 50 | Rich formatting |
| `aicl_modular` | 80 | Entry point |

**Total:** 460 lines across **9 focused files**  
**vs Old:** 500 lines in **1 monolithic file**

## Principles Applied

### 1. **Single Responsibility**

Each file does ONE thing:

```python
# cli/logging_setup.py - ONLY logging
def setup_logging(verbose: bool) -> logger:
    """Configure logging. That's it."""
    ...

# cli/runners/docker.py - ONLY Docker execution
class DockerRunner:
    """Run in Docker. Nothing else."""
    ...
```

### 2. **Easy to Find**

Want to change Docker behavior? → `cli/runners/docker.py`  
Want to modify validation? → `cli/commands/validate.py`  
Want to update output formatting? → `cli/utils/output.py`

### 3. **Easy to Test**

```python
# Test each file independently
from cli.runners.docker import DockerRunner
from cli.commands.validate import validate_command

def test_docker_runner():
    runner = DockerRunner(settings)
    # Test just the runner
```

### 4. **Easy to Extend**

Add a new command? Create one file:

```python
# cli/commands/export.py
def export_command(format: str) -> int:
    """Export results"""
    ...
```

Then import in `aicl_modular`:

```python
from cli.commands.export import export_command

@app.command()
def export(format: str):
    sys.exit(export_command(format))
```

## Comparison

### Old Monolithic (`aicl_improved`)

```python
# One 500-line file
# - Config loading
# - Logging setup
# - Docker runner
# - Local runner
# - All commands
# - Output utilities
# - Everything mixed together
```

**Problems:**
- ❌ Hard to find specific code
- ❌ Merge conflicts
- ❌ Can't test parts independently
- ❌ Overwhelming to edit

### New Modular (`aicl_modular`)

```python
cli/
├── config.py          # Just config
├── runners/
│   ├── docker.py      # Just Docker
│   └── local.py       # Just local
└── commands/
    ├── run.py         # Just run
    └── validate.py    # Just validate
```

**Benefits:**
- ✅ Find code instantly
- ✅ Minimal merge conflicts
- ✅ Test each piece
- ✅ Easy to edit

## Usage

```bash
# Same interface, better structure
./aicl_modular run experiment.aicl
./aicl_modular validate config.aicl
./aicl_modular state list
```

## Adding New Features

### Example: Add `aicl providers list` command

**Step 1:** Create command file (30 lines)
```python
# cli/commands/providers.py
from cli.utils.output import create_table

def list_providers(settings) -> int:
    """List providers - focused function"""
    providers = load_providers(settings)
    table = create_table(providers)
    console.print(table)
    return 0
```

**Step 2:** Wire it up (3 lines)
```python
# aicl_modular
from cli.commands.providers import list_providers

@app.command()
def providers(ctx: typer.Context):
    sys.exit(list_providers(ctx.obj["settings"]))
```

Done! No touching 500-line files.

## File Organization Rules

### What Goes Where

**`cli/config.py`**
- Configuration loading
- Settings validation
- Pydantic models

**`cli/logging_setup.py`**
- Loguru configuration
- Log formatting
- Log handlers

**`cli/commands/`**
- Command orchestration
- Delegates to runners/utils
- No business logic

**`cli/runners/`**
- Execution strategies
- Docker, local, cloud
- Business logic here

**`cli/utils/`**
- Reusable components
- Output formatting
- Helper functions

**`aicl_modular`**
- Typer app setup
- Command registration
- Global options

## Migration Path

```bash
# Start with modular version
./aicl_modular run exp.aicl

# Gradually move old code
# Each piece gets its own file

# Eventually deprecate monolithic version
```

## Maintenance Benefits

### Before (Monolithic)
```
Person A: editing run command
Person B: editing state command
→ MERGE CONFLICT in same 500-line file
```

### After (Modular)
```
Person A: editing cli/commands/run.py
Person B: editing cli/commands/state.py
→ NO CONFLICT, different files!
```

## Testing Strategy

```python
# Test individual pieces
def test_docker_command_builder():
    from cli.runners.docker import DockerRunner
    runner = DockerRunner(mock_settings)
    cmd = runner._build_command(...)
    assert cmd == expected

# Test command orchestration
def test_run_command():
    from cli.commands.run import run_command
    result = run_command(...)
    assert result == 0
```

## Conclusion

**Modular architecture is better because:**

1. ✅ **Small files** - Each file < 100 lines
2. ✅ **Easy to edit** - Find what you need fast
3. ✅ **Clear structure** - Organized by responsibility
4. ✅ **Less conflicts** - Work on different files
5. ✅ **Easy to test** - Import just what you need
6. ✅ **Easy to extend** - Add files, not lines

This follows your development rules perfectly!
