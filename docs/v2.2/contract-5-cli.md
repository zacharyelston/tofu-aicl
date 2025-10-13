# Contract: CLI Interface (30 points)

## Interface

```bash
aicl_modular [OPTIONS] COMMAND [ARGS]
```

## Behavior Specification

### 1. Must provide help (5 pts)

**Given:** User runs `./aicl_modular --help`  
**Then:** 
- Exits with code 0
- Shows available commands
- Shows usage instructions

---

### 2. Must support run command (15 pts)

**Given:** Valid config file `test.aicl`  
**When:** `./aicl_modular run test.aicl`  
**Then:**
- Executes configuration
- Returns exit code 0 on success
- Returns non-zero on failure

**Given:** Docker flag  
**When:** `./aicl_modular run --docker test.aicl`  
**Then:** Executes in Docker (not locally)

**Given:** Missing file  
**When:** `./aicl_modular run missing.aicl`  
**Then:**
- Shows error message
- Returns non-zero exit code

---

### 3. Must support global options (10 pts)

**Given:** Verbose flag  
**When:** `./aicl_modular --verbose run test.aicl`  
**Then:** Shows DEBUG level logs

**Given:** Config file option  
**When:** `./aicl_modular --config custom.yaml run test.aicl`  
**Then:** Loads custom config

**Given:** Env file option  
**When:** `./aicl_modular --env-file custom.env run test.aicl`  
**Then:** Loads custom environment

---

## Validation Tests

```bash
# Test 1: Help works
./aicl_modular --help
[ $? -eq 0 ] || exit 1

# Test 2: Run command
./aicl_modular run test.aicl
[ $? -eq 0 ] || exit 1

# Test 3: Docker flag
./aicl_modular run --docker test.aicl 2>&1 | grep -q "docker"
[ $? -eq 0 ] || exit 1

# Test 4: Error handling
./aicl_modular run missing.aicl
[ $? -ne 0 ] || exit 1  # Should fail

# Test 5: Verbose mode
./aicl_modular --verbose run test.aicl 2>&1 | grep -q "DEBUG"
[ $? -eq 0 ] || exit 1
```

## Don't Care About

- CLI framework (Typer, argparse, click, custom)
- Command structure (subcommands vs flags)
- Help text format
- Error message wording
- Progress indicators
- Colors or formatting

## Pass Criteria

✅ Help command works  
✅ Run command executes  
✅ Options are respected  
✅ Exit codes correct  
✅ Error handling present

## Points

- Help text: 5 pts
- Run execution: 10 pts
- Docker flag: 5 pts
- Global options: 7 pts
- Error handling: 3 pts

**Total: 30 points**
