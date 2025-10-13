# Contract: Configuration (25 points)

## Interface

```python
load_settings(config_file: str = None, env_file: str = None) -> SettingsObject
```

## Behavior Specification

### 1. Must load from multiple sources (10 pts)

**Given:** No arguments  
**When:** `settings = load_settings()`  
**Then:** Returns settings with defaults

**Given:** `config.yaml` exists  
**When:** `settings = load_settings("config.yaml")`  
**Then:** Loads from file

**Given:** `AICL_RUNTIME_MODE=docker` in environment  
**When:** `settings = load_settings()`  
**Then:** Environment overrides defaults

---

### 2. Must have required attributes (8 pts)

**Given:** Any valid settings object  
**Then:** Must have:
- `settings.runtime.mode` (string: "local" or "docker")
- `settings.runtime.docker_image` (string)
- `settings.paths.state_dir` (string or Path)

---

### 3. Must validate values (7 pts)

**Given:** Invalid mode  
**When:** `settings.runtime.mode = "invalid"`  
**Then:** Should raise error or log warning

**Given:** Missing required field  
**Then:** Should use sensible default

---

## Validation Tests

```python
# Test 1: Default loading
def test_defaults():
    settings = load_settings()
    assert settings.runtime.mode in ["local", "docker"]
    assert settings.runtime.docker_image
    assert settings.paths.state_dir

# Test 2: File loading
def test_file_loading():
    with open("test.yaml", "w") as f:
        f.write("runtime:\n  mode: docker\n")
    
    settings = load_settings("test.yaml")
    assert settings.runtime.mode == "docker"

# Test 3: Environment override
def test_env_override():
    os.environ["AICL_RUNTIME_MODE"] = "docker"
    settings = load_settings()
    assert settings.runtime.mode == "docker"
```

## Don't Care About

- Which config library (Dynaconf, ConfigParser, custom)
- How settings are stored (class, dict, dataclass)
- File format (YAML, JSON, TOML, INI)
- Validation method (Pydantic, custom, assertions)
- Number of files
- Lines of code

## Pass Criteria

✅ All 3 validation tests pass  
✅ Required attributes present  
✅ Multi-source loading works  
✅ Precedence correct (CLI > ENV > File > Default)

## Points

- Default loading: 4 pts
- File loading: 3 pts
- Environment override: 3 pts
- Required attributes: 8 pts
- Validation: 7 pts

**Total: 25 points**
