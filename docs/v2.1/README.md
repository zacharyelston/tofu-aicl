# AICL CLI Spec v2.1: Progressive Complexity

**Approach:** Build in layers, each level independently testable

## Philosophy

Instead of micromanaging implementation details, we test **progressive capability**:
- Level 1: Can you configure?
- Level 2: Can you execute?
- Level 3: Can you integrate?
- Level 4: Can you polish?

Each level is **independent** - no cascading failures if you skip Level 4.

## Levels

| Level | Focus | Time | Points | Files |
|-------|-------|------|--------|-------|
| 1 | Foundation | 30 min | 40 | config.py, logging.py |
| 2 | Execution | 45 min | 50 | docker.py, local.py |
| 3 | CLI | 30 min | 40 | run.py, aicl_modular |
| 4 | Polish | 30 min | 20 | output.py, state.py |

**Total:** 150 points (easy to score out of 100%)

## Level Specs

- `level-1-foundation.md` - Config + Logging
- `level-2-execution.md` - Docker + Local runners
- `level-3-cli.md` - Commands + Entry point
- `level-4-polish.md` - Output + State (optional)

## Grading

```python
if passed_level_1 and passed_level_2 and passed_level_3:
    score = 80  # Fully functional CLI
    
if passed_level_4:
    score += 20  # Beautiful UX

# Bonus for speed
if time_minutes < 90:
    score += 10
```

## Benefits

✅ **Independent testing** - Level 2 doesn't break if Level 4 fails  
✅ **Clear progression** - See where models get stuck  
✅ **Flexible** - Can stop at Level 3 and still have working CLI  
✅ **Easy maintenance** - Only 4 spec files vs 10+  
✅ **Better comparison** - "Model A: All levels in 45 min, Model B: Stuck at Level 2"

## Usage

```bash
# Test each level
pytest tests/level1/ --grade
pytest tests/level2/ --grade
pytest tests/level3/ --grade
pytest tests/level4/ --grade

# Full evaluation
python grade_progressive.py --model claude
```
