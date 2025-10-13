# Logging Module Specification

**File:** `cli/logging_setup.py`  
**Lines:** ~30  
**Dependencies:** `loguru`, `sys`

## Purpose

Configure structured logging with:
- Console output (colored, formatted)
- File rotation (automatic)
- Context data (structured logging)
- Debug and production modes

## Interface

### Function: `setup_logging()`

```python
def setup_logging(verbose: bool = False) -> logger:
    """
    Configure Loguru logger with console and file handlers
    
    Args:
        verbose: Enable DEBUG level output
        
    Returns:
        Configured logger instance
        
    Side Effects:
        - Removes default Loguru handler
        - Adds stderr console handler
        - Adds rotating file handler (logs/aicl_{time}.log)
    """
```

## Log Format

```
<green>2025-10-11 15:47:32</green> | <level>INFO    </level> | <cyan>module</cyan>:<cyan>function</cyan> | <level>message</level>
```

Example output:
```
2025-10-11 15:47:32 | INFO     | aicl:run | Starting AICL run | config=exp.aicl
2025-10-11 15:47:33 | DEBUG    | docker:_build | Docker command | cmd="docker run..."
2025-10-11 15:47:35 | SUCCESS  | aicl:run | Run completed | experiment_id=exp-001
2025-10-11 15:47:36 | ERROR    | validator:check | Validation failed | error="missing field"
```

## Log Levels

| Level | Usage | Verbose Required |
|-------|-------|------------------|
| DEBUG | Detailed diagnostics | Yes |
| INFO | Normal operations | No |
| SUCCESS | Successful completions | No |
| WARNING | Non-critical issues | No |
| ERROR | Errors (recoverable) | No |
| CRITICAL | Fatal errors | No |

## File Handler

- **Path:** `logs/aicl_{time}.log`
- **Rotation:** 10 MB per file
- **Retention:** 1 week
- **Level:** DEBUG (always)
- **Format:** Same as console (no colors)

## Console Handler

- **Output:** `sys.stderr`
- **Level:** DEBUG if verbose, else INFO
- **Colorize:** True
- **Backtrace:** True
- **Diagnose:** True

## Structured Logging

```python
# Good: Context data
logger.info("Starting run", config=config_file, experiment_id=exp_id)
# Output: Starting run | config=exp.aicl experiment_id=exp-001

# Good: Error with context
logger.error("Validation failed", error=str(e), file=config_file)
# Output: Validation failed | error="missing field" file=exp.aicl

# Bad: String concatenation
logger.info(f"Starting run with {config_file}")  # DON'T DO THIS
```

## Test Cases

### Test 1: Basic Setup
```python
logger = setup_logging(verbose=False)
logger.info("Test message")
# Should appear on stderr
```

### Test 2: Verbose Mode
```python
logger = setup_logging(verbose=True)
logger.debug("Debug message")
# Should appear (verbose=True enables DEBUG)
```

### Test 3: File Creation
```python
setup_logging()
logger.info("Test")
assert Path("logs").exists()
assert len(list(Path("logs").glob("aicl_*.log"))) > 0
```

### Test 4: Structured Data
```python
logger = setup_logging()
logger.info("Testing", key1="value1", key2="value2")
# Output should contain: key1=value1 key2=value2
```

### Test 5: Log Rotation
```python
logger = setup_logging()
# Write 11 MB of logs
for i in range(100000):
    logger.info("x" * 100)
# Should create multiple files
assert len(list(Path("logs").glob("aicl_*.log"))) > 1
```

## Success Criteria

- ✅ Removes default Loguru handler
- ✅ Console output to stderr
- ✅ File output with rotation
- ✅ Colored console output
- ✅ Structured logging works
- ✅ Verbose mode enables DEBUG
- ✅ File size < 35 lines

## Example Implementation

```python
"""Logging configuration"""

import sys
from loguru import logger


def setup_logging(verbose: bool = False) -> logger:
    """Configure structured logging with Loguru"""
    logger.remove()  # Remove default handler
    
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> | "
        "<level>{message}</level>"
    )
    
    level = "DEBUG" if verbose else "INFO"
    
    # Console handler
    logger.add(
        sys.stderr,
        format=log_format,
        level=level,
        colorize=True,
    )
    
    # File handler
    logger.add(
        "logs/aicl_{time}.log",
        rotation="10 MB",
        retention="1 week",
        level="DEBUG",
        format=log_format,
    )
    
    return logger
```

## Common Pitfalls

### ❌ Don't
```python
# String formatting
logger.info(f"Running {config}")

# Python's logging module
import logging
logging.info("message")
```

### ✅ Do
```python
# Structured logging
logger.info("Running", config=config)

# Use returned logger
logger = setup_logging()
logger.info("message")
```

## Grading

| Criterion | Points | Requirements |
|-----------|--------|--------------|
| Handler removal | 2 | Removes default |
| Console handler | 4 | Correct format, colors |
| File handler | 4 | Rotation, retention |
| Log format | 3 | Matches spec |
| Verbose mode | 2 | DEBUG when True |
| Structured logging | 3 | Context data works |
| Code quality | 2 | Clean, minimal |

**Total:** 20 points
