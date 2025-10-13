# Level 4: Polish (20 points) - OPTIONAL

**Goal:** Beautiful output and state management  
**Time:** ~30 minutes  
**Complexity:** ⭐ Basic (but optional)  
**Depends On:** Level 3 (working CLI)

## What You're Building

Optional quality-of-life improvements:
1. `cli/utils/output.py` - Rich terminal formatting
2. `cli/commands/state.py` - State queries

**Note:** Level 4 is entirely optional. Level 3 gives you a fully working CLI worth 80 points. This adds the final 20 for perfection.

## Requirements

### Polish 1: Rich Output (`cli/utils/output.py`)

**Must Do:**
- Function `print_success(message)` - Green with ✅
- Function `print_error(message)` - Red with ❌
- Function `create_resource_table(resources)` - Formatted table

**Don't Care:**
- Whether you use Rich library or ANSI codes
- Exact colors or formatting
- How fancy it is

**Test:**
```python
from cli.utils.output import print_success, create_resource_table

print_success("Done!")  # Should be green with ✅

resources = {"res-1": Resource(...)}
table = create_resource_table(resources)
# Should display nicely
```

**Points:** 10
- Success/error functions: 4 pts
- Table formatting: 4 pts
- Colors work: 2 pts

---

### Polish 2: State Commands (`cli/commands/state.py`)

**Must Do:**
- Function `list_state(experiment_id, settings) -> int`
- Function `show_resource(resource_id, experiment_id, settings) -> int`
- Reads from state directory
- Displays resources

**Don't Care:**
- How you parse state files
- Output format
- Error handling

**Test:**
```bash
./aicl_modular state list
# Shows resources

./aicl_modular state show resource-1
# Shows resource details
```

**Points:** 10
- List command works: 5 pts
- Show command works: 4 pts
- Handles missing state: 1 pt

---

## Success Criteria

**Pass Level 4:**
- ✅ Success/error messages are colored
- ✅ Tables display nicely
- ✅ State commands work
- ✅ No crashes

**Fail Level 4:**
- ❌ No visual improvement over print()
- ❌ State commands crash
- ❌ Ugly output

---

## Example Minimal Implementation

### output.py (~20 lines)
```python
from rich.console import Console
from rich.table import Table

console = Console()

def print_success(message):
    console.print(f"✅ [green]{message}[/green]")

def print_error(message):
    console.print(f"❌ [red]{message}[/red]")

def create_resource_table(resources):
    table = Table(title="Resources")
    table.add_column("ID", style="cyan")
    table.add_column("Status", style="green")
    
    for res_id, resource in resources.items():
        table.add_row(res_id, resource.status)
    
    return table
```

### state.py (~30 lines)
```python
import json
from pathlib import Path
from cli.utils.output import create_resource_table, print_error

def list_state(experiment_id, settings):
    state_file = Path(settings.paths.state_dir) / experiment_id / "state.json"
    
    if not state_file.exists():
        print_error(f"No state for {experiment_id}")
        return 1
    
    with open(state_file) as f:
        state = json.load(f)
    
    table = create_resource_table(state.get("resources", {}))
    console.print(table)
    return 0

def show_resource(resource_id, experiment_id, settings):
    state_file = Path(settings.paths.state_dir) / experiment_id / "state.json"
    
    with open(state_file) as f:
        state = json.load(f)
    
    resource = state["resources"].get(resource_id)
    if not resource:
        print_error(f"Resource {resource_id} not found")
        return 1
    
    console.print(resource)
    return 0
```

---

## Why This is Optional

Level 4 doesn't add core functionality - it makes things prettier.

**Without Level 4:**
- CLI works ✅
- Executes configs ✅
- All features present ✅
- Just... ugly terminal output

**With Level 4:**
- Same functionality
- Beautiful colors ✨
- Formatted tables 📊
- State queries 🔍

If time is limited or model struggles, skip Level 4. **The CLI still works!**

---

## Final Scoring

```
Level 1: 40 pts (Foundation)
Level 2: 50 pts (Execution)
Level 3: 40 pts (CLI)
Level 4: 20 pts (Polish)
-------
Total:  150 pts

Convert to 100-point scale:
Score = (points / 150) * 100

80+ points = A (Level 3 complete)
90+ points = A+ (with some Level 4)
100 points = Perfect (all levels)
```

---

## Completion

**You've built a complete, production-ready CLI tool!**

Users can:
- ✅ Configure via files/env
- ✅ Run locally or in Docker
- ✅ Debug with verbose mode
- ✅ Query state
- ✅ See beautiful output

**Congratulations! 🎉**
