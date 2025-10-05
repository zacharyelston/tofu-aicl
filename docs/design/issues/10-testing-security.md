# Issue 10: Testing Framework Security Risk

**Priority:** HIGH  
**Week:** 3

## Problem

Test framework uses `eval()` on user input - **DANGEROUS!**

```python
condition = assertion.get('condition')
result = eval(condition, {}, eval_context)  # SECURITY RISK!
```

Even if you trust `.test-cl` files, this is bad practice.

## Solution

Build safe expression evaluator or define assertion operators:

### Option 1: Safe Operators

```hcl
assert {
  operator = "equals"
  actual   = self.output.count
  expected = 47
}

assert {
  operator = "contains"
  actual   = self.output.documents
  expected = "README.md"
}

assert {
  operator = "matches_regex"
  actual   = self.output.version
  expected = "^\\d+\\.\\d+\\.\\d+$"
}
```

### Option 2: Simple Parser

```python
class SafeExpressionEvaluator:
    OPERATORS = {
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.gt,
        '<': operator.lt,
        'in': lambda a, b: a in b,
        'contains': lambda a, b: b in a
    }
    
    def evaluate(self, expr: str, context: dict) -> bool:
        # Parse: "self.output.count > 10"
        tokens = self.tokenize(expr)
        left = self.resolve_path(tokens[0], context)
        op = tokens[1]
        right = self.parse_value(tokens[2])
        
        return self.OPERATORS[op](left, right)
```

### Option 3: Sandboxed eval

```python
from RestrictedPython import compile_restricted, safe_globals

def safe_eval(expr, context):
    code = compile_restricted(expr, '<string>', 'eval')
    return eval(code, {"__builtins__": safe_globals}, context)
```
