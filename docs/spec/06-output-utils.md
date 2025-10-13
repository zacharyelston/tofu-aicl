# Output Utilities Specification

**File:** `cli/utils/output.py`  
**Lines:** ~50  
**Dependencies:** `rich`

## Purpose

Reusable Rich output components.

## Functions

### `print_success(message: str)`
```python
console.print(f"✅ [green]{message}[/green]")
```

### `print_error(message: str)`
```python
console.print(f"❌ [red]{message}[/red]")
```

### `print_info(message: str)`
```python
console.print(f"ℹ️  [blue]{message}[/blue]")
```

### `create_resource_table(resources: dict) -> Table`
```python
"""Create formatted resource table"""
table = Table(title="📊 Resources")
table.add_column("ID", style="cyan")
table.add_column("Type", style="green")
# ... add rows
return table
```

### `show_syntax(code: str, language: str, title: str)`
```python
"""Display syntax-highlighted code"""
syntax = Syntax(code, language, theme="monokai", line_numbers=True)
if title:
    console.print(Panel(syntax, title=title))
```

## Test Cases

### Test 1: Print Functions
```python
print_success("Done!")  # Green with ✅
print_error("Failed!")  # Red with ❌
print_info("Note")      # Blue with ℹ️
```

### Test 2: Resource Table
```python
resources = {
    "res-1": Resource(id="res-1", type="file", status="ready"),
    "res-2": Resource(id="res-2", type="text", status="pending")
}
table = create_resource_table(resources)
# Should have 4 columns, 2 rows
```

### Test 3: Syntax Highlighting
```python
code = '{"key": "value"}'
show_syntax(code, "json", "Test")
# Should display with colors and line numbers
```

## Success Criteria

- ✅ All 5 functions implemented
- ✅ Rich formatting works
- ✅ Reusable components
- ✅ File size < 60 lines

## Grading

| Criterion | Points |
|-----------|--------|
| Print functions | 6 |
| Table creation | 6 |
| Syntax highlighting | 5 |
| Code quality | 3 |

**Total:** 20 points
