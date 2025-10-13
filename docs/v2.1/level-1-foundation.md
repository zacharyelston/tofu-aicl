# Level 1: Foundation (40 points)

**Goal:** Load configuration and setup logging  
**Time:** ~30 minutes  
**Complexity:** ⭐ Basic

## What You're Building

Two simple modules that work independently:
1. `cli/config.py` - Load settings from files/env
2. `cli/logging_setup.py` - Setup structured logging

## Requirements

### Module 1: Configuration (`cli/config.py`)

**Must Do:**
- Function `load_settings()` that returns a settings object
- Load from file OR environment OR defaults
- Settings must have: `runtime.mode`, `runtime.docker_image`, `paths.state_dir`

**Don't Care:**
- What library you use (Dynaconf, ConfigParser, custom)
- How many lines of code
- Whether you use Pydantic or not

**Test:**
```python
from cli.config import load_settings

settings = load_settings()
assert hasattr(settings, 'runtime')
assert settings.runtime.mode in ['local', 'docker']
assert settings.runtime.docker_image
assert settings.paths.state_dir
```

**Points:** 20
- Loads defaults: 8 pts
- Loads from file: 6 pts
- Env override works: 6 pts

---

### Module 2: Logging (`cli/logging_setup.py`)

**Must Do:**
- Function `setup_logging(verbose: bool)` that returns a logger
- Logger writes to console
- Logger writes to file (`logs/` directory)
- Verbose mode shows DEBUG, normal mode shows INFO

**Don't Care:**
- What logging library (Loguru, stdlib, custom)
- Log format (as long as readable)
- How fancy the output is

**Test:**
```python
from cli.logging_setup import setup_logging
from pathlib import Path

logger = setup_logging(verbose=True)
logger.info("Test message")

# Should create log file
assert Path("logs").exists()
assert any(Path("logs").glob("*.log"))
```

**Points:** 20
- Console logging works: 6 pts
- File logging works: 6 pts
- Verbose mode works: 4 pts
- Structured data support: 4 pts

---

## Success Criteria

**Pass Level 1:**
- ✅ `load_settings()` returns valid config
- ✅ `setup_logging()` logs to console and file
- ✅ Both work independently
- ✅ Tests pass

**Fail Level 1:**
- ❌ Import errors
- ❌ Missing required attributes
- ❌ Crashes on default settings

---

## Example Minimal Implementation

### config.py (~15 lines)
```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Runtime:
    mode: str = "local"
    docker_image: str = "tofu-aicl:latest"

@dataclass
class Paths:
    state_dir: str = "./terraform.tfstate.d"

@dataclass
class Settings:
    runtime: Runtime = Runtime()
    paths: Paths = Paths()

def load_settings():
    return Settings()
```

### logging_setup.py (~10 lines)
```python
import logging
from pathlib import Path

def setup_logging(verbose=False):
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/aicl.log')
        ]
    )
    return logging.getLogger(__name__)
```

**That's it!** No fancy libraries required. Use what you're comfortable with.

---

## Comparison Metrics

When comparing AI models on Level 1:

| Metric | What It Shows |
|--------|--------------|
| Time to complete | Speed & efficiency |
| Lines of code | Conciseness vs verbosity |
| Library choices | Knowledge of ecosystem |
| Test pass rate | Correctness |
| Code quality | Understanding of best practices |

---

## Common Pitfalls

1. **Over-engineering** - Don't need Dynaconf for a simple dict
2. **Hard-coding** - Must support environment overrides
3. **No error handling** - What if log directory can't be created?
4. **Imports** - Both modules must import independently

---

## Next Level

Once Level 1 passes → **Level 2: Execution**
