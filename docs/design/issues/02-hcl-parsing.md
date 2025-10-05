# Issue 02: HCL Parsing is Too Simplistic

**Priority:** CRITICAL  
**Week:** 1

## Problem

Current parser just loads HCL with no evaluation:

```python
class HCLParser:
    def parse(self):
        with open(self.file_path, 'r') as f:
            return hcl2.load(f)  # No variable interpolation!
```

**Issues:**
1. No variable interpolation
2. No function calls
3. No expression evaluation
4. Returns raw dict

## Example Failures

```hcl
variable "base_path" {
  default = "./data"
}

resource "loader_files" "docs" {
  path = "${var.base_path}/documents"  # Won't interpolate!
}
```

Path will literally be `"${var.base_path}/documents"` string.

## Solution

Build evaluation context:

```python
class HCLParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.variables = {}
        self.context = {}
    
    def parse(self):
        # Load raw HCL
        with open(self.file_path, 'r') as f:
            raw = hcl2.load(f)
        
        # Extract variables
        for var_block in raw.get('variable', []):
            for name, config in var_block.items():
                self.variables[name] = config.get('default')
        
        # Build evaluation context
        self.context = {
            'var': self.variables,
            'resource': {}  # Populated during execution
        }
        
        # Evaluate expressions
        return self._evaluate(raw)
    
    def _evaluate(self, obj):
        if isinstance(obj, str):
            return self._interpolate(obj)
        elif isinstance(obj, dict):
            return {k: self._evaluate(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._evaluate(item) for item in obj]
        return obj
    
    def _interpolate(self, s: str):
        # Handle ${var.name} syntax
        import re
        pattern = r'\$\{([^}]+)\}'
        
        def replacer(match):
            expr = match.group(1)
            # Safely evaluate expression in context
            return str(self._eval_expr(expr))
        
        return re.sub(pattern, replacer, s)
```

## Alternative

Use library that supports evaluation:
- `python-hcl2` with variable support
- Or build custom evaluator

## Tests Needed

- Variable interpolation: `${var.name}`
- Nested variables: `${var.base}/${var.sub}`
- Resource references: `${resource.foo.bar.id}`
- Function calls: `file("./config.json")`
