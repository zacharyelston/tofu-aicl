# Test Suite

Comprehensive unit and integration tests for the AICL framework.

## Running Tests

### All Tests
```bash
pytest
```

### Unit Tests Only
```bash
pytest tests/unit/
```

### Integration Tests Only
```bash
pytest tests/integration/
```

### With Coverage
```bash
pytest --cov=src/aicl --cov-report=html
```

## Test Structure

### Unit Tests (`tests/unit/`)
- **test_parser.py**: HCL configuration parsing
- **test_evaluator.py**: Variable interpolation and context building
- **test_planner.py**: Dependency resolution and topological sorting
- **test_state_manager.py**: State persistence and resource management

### Integration Tests (`tests/integration/`)
- **test_engine.py**: End-to-end engine workflows

### Feature Tests
- **test_cli.py**: CLI argument parsing and output configuration
- **test_experiment_docdb.py**: PostgreSQL document database storage

## Test Coverage

Current coverage focuses on core components:
- ✅ Parser: HCL file parsing and validation
- ✅ Evaluator: Variable and resource interpolation
- ✅ Planner: Dependency graph and execution order
- ✅ State Manager: Resource state persistence
- ✅ CLI: Output destinations and flags (20 tests)
- ✅ DocDB: Experiment storage and retrieval

## Adding Tests

### Unit Test Template
```python
import pytest
from src.aicl.module import Class

class TestClass:
    def test_feature(self):
        # Arrange
        instance = Class()
        
        # Act
        result = instance.method()
        
        # Assert
        assert result == expected
```

### Integration Test Template
```python
import pytest
import tempfile

class TestFeature:
    def test_end_to_end_workflow(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup test environment
            # Execute workflow
            # Verify results
            pass
```

## Fixtures

Common fixtures are defined in `tests/conftest.py`:
- `sample_hcl_config`: Basic HCL configuration
- `sample_state`: Sample resource state

## CI/CD Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Pre-deployment checks

Minimum required: 80% code coverage
