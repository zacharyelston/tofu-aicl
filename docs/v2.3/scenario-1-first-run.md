# Scenario 1: First-Time Setup (20 points)

## User Story

**As a** new AICL user  
**I want to** run my first configuration  
**So that** I can see if AICL works for me

## Context

- User has just installed/cloned AICL
- Has a simple `hello.aicl` file
- Knows nothing about configuration
- No `.env` or config files exist

## User Journey

### Step 1: Check Installation

```bash
./aicl_modular --help
```

**Expected:**
- ✅ Command works (not "command not found")
- ✅ Shows usage instructions
- ✅ Exit code 0

**Points:** 5
- Executable works: 3 pts
- Help is clear: 2 pts

---

### Step 2: Run First Config

```bash
./aicl_modular run hello.aicl
```

**Expected:**
- ✅ Runs without requiring config files
- ✅ Uses sensible defaults
- ✅ Shows progress/feedback
- ✅ Exit code 0 on success

**Points:** 10
- Works with defaults: 5 pts
- Clear output: 3 pts
- Success indication: 2 pts

---

### Step 3: See Results

```bash
ls terraform.tfstate.d/
```

**Expected:**
- ✅ State directory was created
- ✅ Has experiment results
- ✅ User can find output

**Points:** 5
- State created: 3 pts
- Output accessible: 2 pts

---

## Success Criteria

**Excellent (18-20 pts):**
- ✅ Works perfectly on first try
- ✅ No configuration needed
- ✅ Clear success feedback
- ✅ Helpful error messages

**Good (15-17 pts):**
- ✅ Works but requires some setup
- ✅ Output is visible
- ⚠️ Could be clearer

**Poor (0-14 pts):**
- ❌ Crashes
- ❌ Cryptic errors
- ❌ Requires complex setup

---

## Common Issues

### Issue: "Module not found"
**Expected:** Clear error explaining dependencies need installation

### Issue: "Permission denied"
**Expected:** Helpful message about making script executable

### Issue: No output
**Expected:** Progress indicator or log messages

---

## UX Scoring (Bonus +5 pts)

**+2 pts:** Welcome message or first-run tips  
**+2 pts:** Progress indicators during execution  
**+1 pt:** Success message with next steps

---

## Validation Script

```bash
#!/bin/bash
# test_scenario_1.sh

echo "=== Scenario 1: First-Time Setup ==="

# Clean slate
rm -rf terraform.tfstate.d/ logs/ .env config.yaml

# Test 1: Help works
echo "Test 1: Help command..."
./aicl_modular --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Help works"
    POINTS=$((POINTS + 5))
else
    echo "❌ Help failed"
fi

# Test 2: Run works
echo "Test 2: First run..."
./aicl_modular run examples/hello.aicl > output.log 2>&1
if [ $? -eq 0 ]; then
    echo "✅ First run successful"
    POINTS=$((POINTS + 10))
else
    echo "❌ First run failed"
    cat output.log
fi

# Test 3: State created
echo "Test 3: State directory..."
if [ -d "terraform.tfstate.d" ]; then
    echo "✅ State directory created"
    POINTS=$((POINTS + 5))
else
    echo "❌ No state directory"
fi

echo "=== Score: $POINTS / 20 ==="
```

---

## Comparison Metrics

When comparing AI models:

| Metric | What It Shows |
|--------|--------------|
| Works immediately | Setup complexity |
| Clear output | UX quality |
| Error messages | Debugging help |
| Documentation | User guidance |
| Time to first success | Onboarding friction |

---

## Next Scenario

Once user successfully runs first config → **Scenario 2: Run Simple Config**
