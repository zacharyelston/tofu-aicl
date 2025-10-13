# Test Criteria for AI Model Comparison

## Automated Tests

### Module Tests

```python
# Config (30 points)
test_config_loads_defaults()
test_config_loads_from_file()
test_config_env_override()
test_config_validation()

# Logging (20 points)
test_logging_setup()
test_logging_verbose_mode()
test_logging_file_creation()
test_logging_structured_data()

# Docker Runner (30 points)
test_docker_command_build()
test_docker_mounts()
test_docker_safe_access()
test_docker_execution()

# Local Runner (20 points)
test_local_execution()
test_local_directory_change()
test_local_error_handling()

# Commands (50 points total)
test_run_docker_mode()
test_run_local_mode()
test_validate_success()
test_state_list()
test_state_show()

# Output Utils (20 points)
test_print_functions()
test_resource_table()
test_syntax_highlighting()

# Entry Point (30 points)
test_cli_help()
test_cli_global_options()
test_cli_context_propagation()
test_cli_exit_codes()
```

## Manual Checks

### File Size Compliance
```bash
for file in cli/**/*.py aicl_modular; do
    lines=$(wc -l < $file)
    limit=100
    echo "$file: $lines lines (limit: $limit)"
done
```

### Import Independence
```python
# Each module should import independently
from cli.config import load_settings
from cli.runners.docker import DockerRunner
from cli.commands.run import run_command
```

### Modular Structure
```
cli/
├── commands/    # All command files present
├── runners/     # All runner files present
└── utils/       # All utility files present
```

## Grading Formula

**Total Score = Automated Tests (70%) + Code Quality (20%) + Size Compliance (10%)**

### Automated Tests (140 points * 0.7 = 98 points)
- Config: 30
- Logging: 20
- Docker: 30
- Local: 20
- Commands: 15
- Output: 20
- Entry: 30

### Code Quality (20 points)
- Clean code: 5
- Documentation: 5
- Error handling: 5
- Logging: 5

### Size Compliance (10 points)
- All files under limit: 10
- 1-2 files over: 7
- 3-4 files over: 4
- 5+ files over: 0

## Pass/Fail Thresholds

- **A Grade:** 90-100 points (Excellent)
- **B Grade:** 80-89 points (Good)
- **C Grade:** 70-79 points (Acceptable)
- **D Grade:** 60-69 points (Needs work)
- **F Grade:** <60 points (Does not meet spec)

## Example Comparison

```markdown
| Model | Total | Tests | Quality | Size | Time |
|-------|-------|-------|---------|------|------|
| Claude 3.5 | 95 | 92/98 | 18/20 | 10/10 | 45m |
| GPT-4 | 87 | 85/98 | 17/20 | 7/10 | 52m |
| Gemini Pro | 82 | 80/98 | 16/20 | 10/10 | 38m |
```

## Improvements Discovery

Track innovations found:
- Better error messages
- Cleaner abstractions
- Performance optimizations
- New features
- Bug fixes

Feed improvements back into spec for next iteration.
