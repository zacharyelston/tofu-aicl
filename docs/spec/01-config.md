# Configuration Module Specification

**File:** `cli/config.py`  
**Lines:** ~50  
**Dependencies:** `dynaconf`, `pydantic`, `pathlib`

## Purpose

Load and validate application configuration with clear precedence:
1. CLI arguments (highest)
2. Environment variables (`AICL_*`)
3. Config files (`~/.aicl/config.yaml`)
4. Built-in defaults (lowest)

## Interface

### Function: `load_settings()`

```python
def load_settings(
    config_file: str = None,
    env_file: str = None
) -> Dynaconf:
    """
    Load configuration from multiple sources
    
    Args:
        config_file: Path to YAML config file (optional)
        env_file: Path to .env file (optional)
        
    Returns:
        Dynaconf settings object with validated config
        
    Raises:
        ValidationError: If configuration invalid
    """
```

### Configuration Structure

```yaml
runtime:
  mode: local              # or 'docker'
  docker_image: tofu-aicl:latest
  provider_mode: subprocess

paths:
  state_dir: ./terraform.tfstate.d
  experiments_dir: ./experiments
  providers_dir: ./providers

docker:
  auto_pull: false
  remove_after: true
  mounts: []
  network: bridge

observability:
  enabled: true
  log_level: INFO
```

## Pydantic Models

### RuntimeConfig

```python
class RuntimeConfig(BaseModel):
    mode: str = "local"
    docker_image: str = "tofu-aicl:latest"
    provider_mode: str = "subprocess"
```

### PathsConfig

```python
class PathsConfig(BaseModel):
    state_dir: Path = Path("./terraform.tfstate.d")
    experiments_dir: Path = Path("./experiments")
    providers_dir: Path = Path("./providers")
```

## Validators

```python
Validator('runtime.mode', is_in=['local', 'docker'], default='local')
Validator('runtime.docker_image', default='tofu-aicl:latest')
Validator('paths.state_dir', default='./terraform.tfstate.d')
```

## Configuration Sources

### 1. Files (in order)
- `~/.aicl/config.yaml`
- `.aicl.yaml`
- `aicl.yaml`

### 2. Environment Variables
- Prefix: `AICL_`
- Example: `AICL_RUNTIME_MODE=docker`
- Format: `AICL_SECTION_KEY=value`

### 3. .env File
- Automatically loaded if present
- Standard dotenv format

## Error Handling

```python
# Invalid mode
ValidationError: runtime.mode must be in ['local', 'docker']

# Missing required path
ValidationError: paths.state_dir is required

# Invalid YAML
FileParseError: config.yaml syntax error at line 5
```

## Test Cases

### Test 1: Default Configuration
```python
settings = load_settings()
assert settings.runtime.mode == "local"
assert settings.runtime.docker_image == "tofu-aicl:latest"
assert settings.paths.state_dir == "./terraform.tfstate.d"
```

### Test 2: Custom Config File
```python
settings = load_settings(config_file="custom.yaml")
assert settings.runtime.mode == "docker"  # from file
```

### Test 3: Environment Override
```python
os.environ["AICL_RUNTIME_MODE"] = "docker"
settings = load_settings()
assert settings.runtime.mode == "docker"  # env wins
```

### Test 4: Validation Failure
```python
# Invalid mode
with pytest.raises(ValidationError):
    settings = load_settings()
    settings.runtime.mode = "invalid"
    settings.validators.validate()
```

## Success Criteria

- ✅ Loads from all sources (file, env, defaults)
- ✅ Correct precedence order
- ✅ Validates configuration
- ✅ Clear error messages
- ✅ Pydantic models type-safe
- ✅ File size < 60 lines

## Example Implementation

```python
"""Configuration management with Dynaconf"""

from pathlib import Path
from dynaconf import Dynaconf, Validator
from pydantic import BaseModel, Field


def load_settings(config_file: str = None, env_file: str = None) -> Dynaconf:
    """Load configuration with precedence: CLI > ENV > File > Defaults"""
    settings = Dynaconf(
        envvar_prefix="AICL",
        settings_files=['~/.aicl/config.yaml', '.aicl.yaml', 'aicl.yaml'],
        environments=True,
        load_dotenv=True,
        merge_enabled=True,
        validators=[
            Validator('runtime.mode', is_in=['local', 'docker'], default='local'),
            Validator('runtime.docker_image', default='tofu-aicl:latest'),
            Validator('paths.state_dir', default='./terraform.tfstate.d'),
        ]
    )
    
    if config_file:
        settings.configure(SETTINGS_FILE_FOR_DYNACONF=str(config_file))
    
    if env_file:
        settings.configure(DOTENV_PATH_FOR_DYNACONF=str(env_file))
    
    settings.validators.validate()
    return settings


class RuntimeConfig(BaseModel):
    """Runtime configuration"""
    mode: str = "local"
    docker_image: str = "tofu-aicl:latest"
    provider_mode: str = "subprocess"


class PathsConfig(BaseModel):
    """Paths configuration"""
    state_dir: Path = Field(default=Path("./terraform.tfstate.d"))
    experiments_dir: Path = Field(default=Path("./experiments"))
    providers_dir: Path = Field(default=Path("./providers"))
```

## Grading

| Criterion | Points | Requirements |
|-----------|--------|--------------|
| Dynaconf setup | 5 | Correct config sources |
| Validators | 5 | All 3 validators present |
| Pydantic models | 5 | Both models with types |
| File handling | 3 | Custom file support |
| Env handling | 3 | AICL_ prefix works |
| Error handling | 4 | Clear error messages |
| Code quality | 5 | Clean, documented |

**Total:** 30 points
