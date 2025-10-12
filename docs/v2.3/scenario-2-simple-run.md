# Scenario 2: Run Simple Config (25 points)

## User Story

**As an** AICL user  
**I want to** execute different configurations  
**So that** I can test various AI workflows

## Context

- User has successfully completed Scenario 1
- Has multiple `.aicl` files to test
- Wants to run them locally (not Docker)
- May want to customize settings

## User Journey

### Step 1: Run with Default Settings

```bash
./aicl_modular run experiments/test1.aicl
```

**Expected:**
- ✅ Executes successfully
- ✅ Shows what's happening (logs)
- ✅ Exit code 0

**Points:** 8
- Execution works: 5 pts
- Visible progress: 3 pts

---

### Step 2: Run Multiple Configs

```bash
./aicl_modular run experiments/test1.aicl
./aicl_modular run experiments/test2.aicl
./aicl_modular run experiments/test3.aicl
```

**Expected:**
- ✅ Each runs independently
- ✅ State is kept separate
- ✅ No conflicts

**Points:** 7
- Multiple runs work: 5 pts
- State isolation: 2 pts

---

### Step 3: Customize Execution

```bash
# Custom working directory
./aicl_modular run --workdir /tmp test.aicl

# Custom experiment ID
./aicl_modular run --experiment-id my-test test.aicl

# Verbose output
./aicl_modular --verbose run test.aicl
```

**Expected:**
- ✅ Options are respected
- ✅ Behavior changes appropriately
- ✅ Verbose shows debug info

**Points:** 10
- Workdir option: 3 pts
- Experiment ID: 3 pts
- Verbose mode: 4 pts

---

## Success Criteria

**Excellent (23-25 pts):**
- ✅ All runs successful
- ✅ All options work
- ✅ Clear output
- ✅ State properly isolated

**Good (18-22 pts):**
- ✅ Basic runs work
- ⚠️ Some options missing/broken
- ✅ Usable but not perfect

**Poor (0-17 pts):**
- ❌ Runs fail
- ❌ Options don't work
- ❌ Confusing output

---

## Common Issues

### Issue: Configs interfere with each other
**Expected:** Each run uses separate state/experiment ID

### Issue: Can't find where results are
**Expected:** Clear log message showing output location

### Issue: Verbose flag doesn't work
**Expected:** DEBUG level logs appear when --verbose used

---

## UX Scoring (Bonus +5 pts)

**+2 pts:** Summary of what was executed  
**+2 pts:** Time taken for execution  
**+1 pt:** Links to output/state files

---

## Validation Script

```bash
#!/bin/bash
# test_scenario_2.sh

echo "=== Scenario 2: Simple Run ==="
POINTS=0

# Test 1: Basic run
echo "Test 1: Basic execution..."
./aicl_modular run examples/test1.aicl > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Basic run works"
    POINTS=$((POINTS + 8))
else
    echo "❌ Basic run failed"
fi

# Test 2: Multiple runs
echo "Test 2: Multiple executions..."
./aicl_modular run examples/test1.aicl > /dev/null 2>&1
./aicl_modular run examples/test2.aicl > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Multiple runs work"
    POINTS=$((POINTS + 7))
else
    echo "❌ Multiple runs failed"
fi

# Test 3: Verbose mode
echo "Test 3: Verbose output..."
OUTPUT=$(./aicl_modular --verbose run examples/test1.aicl 2>&1)
if echo "$OUTPUT" | grep -qi "debug"; then
    echo "✅ Verbose mode works"
    POINTS=$((POINTS + 4))
else
    echo "❌ No debug output"
fi

# Test 4: Custom experiment ID
echo "Test 4: Custom experiment ID..."
./aicl_modular run --experiment-id custom-test examples/test1.aicl > /dev/null 2>&1
if [ -d "terraform.tfstate.d/custom-test" ]; then
    echo "✅ Custom experiment ID works"
    POINTS=$((POINTS + 6))
else
    echo "❌ Custom ID not used"
fi

echo "=== Score: $POINTS / 25 ==="
```

---

## Comparison Metrics

| Metric | What It Shows |
|--------|--------------|
| Success rate | Reliability |
| Options implemented | Feature completeness |
| Output clarity | UX quality |
| Error handling | Robustness |
| Performance | Efficiency |

---

## Next Scenario

Once user can run multiple configs → **Scenario 3: Debug a Failure**
