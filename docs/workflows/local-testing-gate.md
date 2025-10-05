# Local Testing Gate

## Principle

**No commit without passing tests. No push without local validation.**

Tests run in CI are for proof, not discovery. You should already know they pass because you tested locally first.

## The Gate

```
Code Written → Tests Written → Tests Run Locally → ALL PASS → Commit Allowed
                                                  ↓
                                               ANY FAIL → Fix Now
```

## Pre-Commit Testing Workflow

### 1. Write Code for ONE Thing

```python
# providers/replit/js_bridge.py
class JavaScriptBridge:
    def execute(self, js_code: str, timeout: int = 10):
        """Execute JavaScript and return parsed JSON"""
        # Implementation here
        pass
```

### 2. Write Test IMMEDIATELY

```python
# tests/providers/replit/test_js_bridge.py
def test_execute_simple_code():
    """Test basic JavaScript execution"""
    bridge = JavaScriptBridge()
    result = bridge.execute('console.log(JSON.stringify({test: true}))')

    assert result.success is True
    assert result.data == {"test": True}
```

### 3. Run Test Locally

```bash
# Run specific test file
python -m pytest tests/providers/replit/test_js_bridge.py -v

# Expected: PASS
# If FAIL: Fix immediately, don't proceed
```

### 4. Expand Testing

```python
# Add edge cases
def test_execute_with_timeout():
    """Test timeout handling"""
    bridge = JavaScriptBridge()
    result = bridge.execute('while(true){}', timeout=1)

    assert result.success is False
    assert 'timeout' in result.error.lower()

def test_execute_invalid_json():
    """Test invalid JSON handling"""
    bridge = JavaScriptBridge()
    result = bridge.execute('console.log("not json")')

    assert result.success is False
    assert 'json' in result.error.lower()
```

### 5. Run Full Test Suite

```bash
# Run all tests in the module
python -m pytest tests/providers/replit/ -v

# Run with coverage
python -m pytest tests/providers/replit/ --cov=providers/replit --cov-report=term-missing

# Expected output:
# ===================== test session starts ======================
# tests/providers/replit/test_js_bridge.py::test_execute_simple_code PASSED
# tests/providers/replit/test_js_bridge.py::test_execute_with_timeout PASSED
# tests/providers/replit/test_js_bridge.py::test_execute_invalid_json PASSED
# ===================== 3 passed in 0.82s =======================
#
# Coverage: 87%
```

## Testing Checklist

Before ANY commit:

```markdown
## Unit Tests
- [ ] All new functions have tests
- [ ] Happy path tested
- [ ] Error cases tested
- [ ] Edge cases tested
- [ ] Coverage >80%

## Integration Tests
- [ ] Component works with dependencies
- [ ] End-to-end flow tested
- [ ] Example usage works

## Local Execution
- [ ] All tests pass: python -m pytest tests/
- [ ] No warnings
- [ ] No errors
- [ ] Coverage meets threshold
```

## Test Organization

```
tests/
└── providers/
    └── replit/
        ├── test_js_bridge.py          # JavaScript bridge unit tests
        ├── test_extension.py          # Extension resource tests
        ├── test_auth_session.py       # Auth session tests
        └── integration/
            └── test_full_workflow.py  # End-to-end tests
```

## Running Tests at Different Scopes

### Single Test
```bash
# Run one specific test
python -m pytest tests/providers/replit/test_js_bridge.py::test_execute_simple_code -v
```

### Test File
```bash
# Run all tests in a file
python -m pytest tests/providers/replit/test_js_bridge.py -v
```

### Test Directory
```bash
# Run all tests in provider
python -m pytest tests/providers/replit/ -v
```

### Full Suite
```bash
# Run everything
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=. --cov-report=html

# Fast fail (stop on first failure)
python -m pytest tests/ -x
```

## Test Quality Standards

### Good Test Structure

```python
def test_feature_name():
    """Clear description of what is being tested"""
    # Arrange - Set up test data
    bridge = JavaScriptBridge()
    js_code = 'console.log(JSON.stringify({result: 42}))'

    # Act - Execute the function
    result = bridge.execute(js_code)

    # Assert - Verify the outcome
    assert result.success is True
    assert result.data['result'] == 42
    assert result.execution_time_ms < 1000
```

### Test Coverage Goals

- **Unit Tests**: >80% coverage
- **Integration Tests**: All critical paths
- **Edge Cases**: Error conditions, boundaries
- **Performance**: Key operations meet timing requirements

## Common Testing Patterns

### Testing Errors

```python
def test_handles_execution_error():
    """Verify error handling"""
    bridge = JavaScriptBridge()

    with pytest.raises(JavaScriptExecutionError):
        bridge.execute('throw new Error("test")')
```

### Testing Timeouts

```python
def test_timeout_enforcement():
    """Verify timeout protection"""
    bridge = JavaScriptBridge(default_timeout=1)

    start = time.time()
    result = bridge.execute('while(true){}')
    duration = time.time() - start

    assert result.success is False
    assert duration < 2  # Should timeout around 1 second
```

### Testing with Mocks

```python
from unittest.mock import patch, MagicMock

def test_subprocess_error_handling():
    """Test handling of subprocess failures"""
    bridge = JavaScriptBridge()

    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired('node', 10)

        result = bridge.execute('console.log("test")')

        assert result.success is False
        assert 'timeout' in result.error.lower()
```

## Pre-Commit Hooks (Automated Gate)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "Running pre-commit tests..."

# Run tests
python -m pytest tests/ -x

if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Commit rejected."
    echo "Fix failing tests before committing."
    exit 1
fi

echo "✅ All tests passed. Proceeding with commit."
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Red Flags

🚩 Committing without running tests
🚩 "I'll fix the tests later"
🚩 "Tests pass in CI, that's good enough"
🚩 Skipping tests because "it's a small change"
🚩 Not testing error conditions
🚩 Coverage dropping below 80%

## Recovery from Untested Code

If you already committed without tests:

```bash
# 1. Don't push yet
git log --oneline -1  # See your commit

# 2. Write the missing tests
# ... create test file ...

# 3. Run tests
python -m pytest tests/ -v

# 4. Amend the commit to include tests
git add tests/
git commit --amend --no-edit

# 5. Now you can push
git push origin feature/your-branch
```

## CI Pipeline Expectations

When you push, CI will run the SAME tests:

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest tests/ -v --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**You already know this will pass because you tested locally.**

CI is just proving to others that your local environment matches production.

## Success Metrics

- ✅ 100% of commits have passing tests
- ✅ Zero "fix tests" commits
- ✅ Zero CI failures (tests already passed locally)
- ✅ Coverage stays >80%
- ✅ Test runtime <30 seconds for typical changes