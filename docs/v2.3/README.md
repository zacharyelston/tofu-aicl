# AICL CLI Spec v2.3: Scenario-Based Testing

**Approach:** Test real-world user workflows

## Philosophy

Instead of testing code units or contracts, test **complete user journeys**:
- What does a user want to do?
- Can they do it?
- Is the experience good?

Each scenario is a story with:
- User goal
- Steps to achieve it
- Expected outcome
- Scoring rubric

## Scenarios

| Scenario | User Story | Points | Time |
|----------|-----------|--------|------|
| 1 | First-time setup | 20 | 5 min |
| 2 | Run simple config | 25 | 5 min |
| 3 | Debug a failure | 20 | 10 min |
| 4 | Switch to Docker | 15 | 5 min |
| 5 | Query state | 15 | 5 min |
| 6 | Production workflow | 25 | 15 min |

**Total:** 120 points (bonus for UX: +30)

## Scenario Files

- `scenario-1-first-run.md` - New user getting started
- `scenario-2-simple-run.md` - Basic execution
- `scenario-3-debugging.md` - Troubleshooting
- `scenario-4-docker-mode.md` - Container execution
- `scenario-5-state-query.md` - Data inspection
- `scenario-6-production.md` - Real-world usage

## Grading

```python
for scenario in scenarios:
    # Run the scenario
    result = execute_scenario(scenario)
    
    # Grade on:
    # 1. Functional (does it work?)
    # 2. UX (is it pleasant?)
    # 3. Errors (helpful messages?)
    
    if result.works:
        score += scenario.functional_points
    if result.good_ux:
        score += scenario.ux_points
    if result.clear_errors:
        score += scenario.error_points
```

## Benefits

✅ **User-focused** - Tests real workflows  
✅ **Integration** - Everything must work together  
✅ **UX scoring** - Rewards good user experience  
✅ **Realistic** - Catches issues specs miss  
✅ **Story-based** - Easy to understand

## Usage

```bash
# Run scenarios manually
bash test_scenario_1.sh
bash test_scenario_2.sh

# Automated testing
python run_scenarios.py --all

# With user feedback
python run_scenarios.py --interactive
```

## Comparison Approach

When comparing AI models with scenarios:

| Model | Scenario 1 | Scenario 2 | Scenario 3 | UX Score | Total |
|-------|-----------|-----------|-----------|----------|-------|
| Claude | ✅ 20/20 | ✅ 25/25 | ✅ 18/20 | 25/30 | 88 |
| GPT-4 | ✅ 20/20 | ✅ 22/25 | ⚠️ 15/20 | 22/30 | 79 |
| Gemini | ✅ 18/20 | ✅ 25/25 | ❌ 10/20 | 20/30 | 73 |

Shows:
- Which models handle real workflows
- Where UX breaks down
- Edge case handling
