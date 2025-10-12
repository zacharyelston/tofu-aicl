# Scenario 6: Production Workflow (25 points)

## User Story

**As a** production AICL user  
**I want to** run experiments reliably  
**So that** I can trust AICL in my workflow

## Context

- User has been using AICL for weeks
- Runs multiple experiments daily
- Needs reliability and visibility
- Uses custom configurations

## User Journey

### Step 1: Production Run

```bash
# Load custom config
export AICL_RUNTIME_MODE=docker
export AICL_RUNTIME_DOCKER_IMAGE=tofu-aicl:prod

# Run with production settings
./aicl_modular \
  --config ~/.aicl/prod.yaml \
  --env-file .env.prod \
  run --docker \
  --experiment-id prod-$(date +%Y%m%d-%H%M%S) \
  --mount ./data:/data:ro \
  experiments/production.aicl
```

**Expected:**
- ✅ All options work together
- ✅ Custom config + env + CLI flags
- ✅ Proper precedence (CLI > ENV > File)
- ✅ Executes successfully

**Points:** 12
- Complex options work: 6 pts
- Precedence correct: 4 pts
- Reliability: 2 pts

---

### Step 2: Monitor Execution

```bash
# While running, in another terminal
./aicl_modular state list --experiment-id prod-20251011-184500
```

**Expected:**
- ✅ Can query state during execution
- ✅ Shows current resources
- ✅ Real-time visibility

**Points:** 5
- State queries work: 3 pts
- Real-time data: 2 pts

---

### Step 3: Error Recovery

```bash
# If run fails
echo $?  # Get exit code

# Check logs
tail -f logs/aicl_*.log

# Retry with different settings
./aicl_modular run --no-docker experiments/production.aicl
```

**Expected:**
- ✅ Non-zero exit code on failure
- ✅ Logs explain what happened
- ✅ Can switch execution modes
- ✅ State is preserved

**Points:** 8
- Exit codes correct: 2 pts
- Logs helpful: 3 pts
- Mode switching: 2 pts
- State preservation: 1 pt

---

## Success Criteria

**Excellent (23-25 pts):**
- ✅ Handles complex production scenarios
- ✅ All options work together
- ✅ Excellent visibility
- ✅ Reliable error recovery

**Good (18-22 pts):**
- ✅ Most scenarios work
- ⚠️ Some edge cases fail
- ✅ Usable in production

**Poor (0-17 pts):**
- ❌ Can't handle complexity
- ❌ Poor error handling
- ❌ Not production-ready

---

## Real-World Complexity

This scenario tests:
- **Multiple config sources** - File + Env + CLI
- **Precedence rules** - What overrides what?
- **State management** - Concurrent queries
- **Error handling** - What if Docker fails?
- **Logging** - Can you debug issues?
- **Flexibility** - Switch modes on the fly

---

## UX Scoring (Bonus +5 pts)

**+2 pts:** Progress indicators for long runs  
**+2 pts:** Estimated time remaining  
**+1 pt:** Email/webhook notifications on completion

---

## Validation Script

```bash
#!/bin/bash
# test_scenario_6.sh

echo "=== Scenario 6: Production Workflow ==="
POINTS=0

# Setup
export AICL_RUNTIME_MODE=docker
echo "runtime:\n  mode: local" > test.yaml

# Test 1: Complex options
echo "Test 1: Complex production run..."
./aicl_modular \
  --config test.yaml \
  run --docker \
  --experiment-id prod-test \
  examples/test1.aicl > output.log 2>&1

if [ $? -eq 0 ]; then
    # Check precedence (CLI --docker should override file 'local')
    if grep -qi "docker" output.log; then
        echo "✅ Complex options work, precedence correct"
        POINTS=$((POINTS + 12))
    else
        echo "⚠️  Options work but precedence wrong"
        POINTS=$((POINTS + 6))
    fi
else
    echo "❌ Complex run failed"
fi

# Test 2: State queries
echo "Test 2: State management..."
./aicl_modular state list --experiment-id prod-test > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ State queries work"
    POINTS=$((POINTS + 5))
else
    echo "❌ State queries failed"
fi

# Test 3: Error handling
echo "Test 3: Error recovery..."
./aicl_modular run missing.aicl > /dev/null 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "✅ Exit code correct on failure"
    POINTS=$((POINTS + 2))
fi

# Check logs exist and have content
if [ -f logs/aicl*.log ] && [ -s logs/aicl*.log ]; then
    echo "✅ Logs are helpful"
    POINTS=$((POINTS + 6))
else
    echo "❌ No useful logs"
fi

echo "=== Score: $POINTS / 25 ==="
echo "=== Production Ready: $([ $POINTS -ge 20 ] && echo 'YES' || echo 'NO') ==="
```

---

## Comparison Metrics

| Metric | What It Shows |
|--------|--------------|
| Complex scenario success | Production readiness |
| Precedence handling | Configuration mastery |
| Error recovery | Robustness |
| State management | Reliability |
| Logging quality | Debuggability |

---

## Completion

If Scenario 6 passes → **CLI is production-ready!** 🎉

User can:
- ✅ Run complex workflows
- ✅ Handle failures gracefully
- ✅ Debug issues effectively
- ✅ Trust AICL in production
