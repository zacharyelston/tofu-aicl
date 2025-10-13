# Redmine Workflows for Scenario Testing

## Integration with v2.3 Scenario-Based Testing

Each scenario becomes a tracked Redmine issue with automated execution and reporting.

## Scenario → Issue Mapping

### Scenario 1: First-Time Setup
```
Tracker: Scenario Test
Subject: [MODEL] Scenario 1 - First-Time Setup
Parent: Test Run #123
Description:
  Test that new user can run first config without setup
  
Custom Fields:
  Scenario ID: 1
  Max Points: 20
  Model: [from parent]
  
Acceptance Criteria:
  - Help command works
  - First run executes
  - State directory created
```

**Automation Updates:**
```python
# Start
issue.status = 'Running'
issue.notes = "⏳ Running first-time setup test..."

# Progress
issue.notes = "✅ Test 1/3: Help works"
issue.notes = "✅ Test 2/3: First run successful"
issue.notes = "✅ Test 3/3: State created"

# Complete
issue.status = 'Complete'
issue.custom_fields['score'] = 20
issue.notes = """
## ✅ Scenario 1 Complete

**Score:** 20/20 (100%)

### Tests:
- ✅ Help command: 5/5
- ✅ First run: 10/10
- ✅ State creation: 5/5

**UX Bonus:** +2 pts for welcome message
"""
```

---

## Workflow for Complete Test Run

### Step 1: Human Creates Parent Issue

**Redmine UI:**
```
Tracker: Test Run
Subject: Claude 3.5 - Complete Scenario Testing
Description:
  Full evaluation of Claude 3.5 Sonnet using all scenarios
  
Model: Claude 3.5 Sonnet
Spec Version: v2.3
Assigned To: automation-bot
Priority: Normal
```

### Step 2: Automation Creates Child Issues

**Python creates 6 child issues:**
```python
parent_issue = redmine.issue.get(123)

scenarios = [
    {'name': 'First-Time Setup', 'points': 20},
    {'name': 'Simple Run', 'points': 25},
    {'name': 'Debugging', 'points': 20},
    {'name': 'Docker Mode', 'points': 15},
    {'name': 'State Query', 'points': 15},
    {'name': 'Production', 'points': 25}
]

for i, scenario in enumerate(scenarios, 1):
    child = redmine.issue.create(
        project_id='aicl-testing',
        tracker_id='scenario-test',
        subject=f"{parent_issue.model} - Scenario {i}: {scenario['name']}",
        parent_issue_id=parent_issue.id,
        custom_fields=[
            {'id': 'scenario_id', 'value': i},
            {'id': 'max_points', 'value': scenario['points']},
            {'id': 'model', 'value': parent_issue.model}
        ]
    )
```

### Step 3: Execute Each Scenario

**Sequential execution with updates:**
```python
for scenario_issue in parent_issue.children:
    # Update status
    scenario_issue.status = 'Running'
    scenario_issue.notes = f"⏳ Executing {scenario_issue.subject}..."
    scenario_issue.save()
    
    # Run scenario
    result = run_scenario(
        scenario_id=scenario_issue.custom_fields['scenario_id'],
        model=scenario_issue.custom_fields['model']
    )
    
    # Post results
    scenario_issue.status = 'Complete' if result.passed else 'Failed'
    scenario_issue.custom_fields['score'] = result.score
    scenario_issue.notes = format_scenario_result(result)
    scenario_issue.save()
    
    # Attach artifacts
    attach_file(scenario_issue, f"logs/scenario_{scenario_id}.log")
    attach_file(scenario_issue, f"output/scenario_{scenario_id}.txt")
```

### Step 4: Aggregate Results

**Update parent issue:**
```python
# Calculate totals
total_score = sum(child.custom_fields['score'] for child in parent_issue.children)
total_possible = sum(child.custom_fields['max_points'] for child in parent_issue.children)

# Update parent
parent_issue.status = 'Complete'
parent_issue.custom_fields['score'] = total_score
parent_issue.notes = f"""
## 📊 Test Run Complete

**Total Score:** {total_score} / {total_possible} ({total_score/total_possible*100:.1f}%)
**Grade:** {calculate_grade(total_score, total_possible)}

### Scenario Results:
{create_results_table(parent_issue.children)}

### Summary:
- Passed: {count_passed} / {len(parent_issue.children)}
- Failed: {count_failed}
- Average Score: {average_score:.1f}%

### Next Actions:
- Review failed scenarios
- Check logs for details
- Compare with other models
"""

# Create comparison chart
chart_url = create_comparison_chart(parent_issue)
parent_issue.notes += f"\n![Comparison Chart]({chart_url})"
parent_issue.save()
```

---

## Human Interaction Points

### 1. Initial Creation
**Human does:**
- Creates Test Run issue via Redmine UI
- Sets model and spec version
- Optionally sets priority, due date
- Can add notes/requirements

**Automation responds:**
- Picks up issue
- Creates child issues
- Starts execution

### 2. During Execution
**Human can:**
- Watch live updates in Redmine
- See progress via issue notes
- Get email notifications
- Cancel if needed (change status to "Cancelled")

**Automation provides:**
- Real-time status updates
- Progress indicators
- Intermediate results

### 3. After Completion
**Human reviews:**
- Overall score and grade
- Individual scenario results
- Attached logs and outputs
- Comparison with other models

**Human actions:**
- Comment on results
- Report bugs found
- Suggest improvements
- Schedule retests

### 4. Iteration
**Human can:**
- Clone issue to retest
- Change spec version
- Test different model
- Run subset of scenarios

**Automation handles:**
- Re-execution
- Result comparison
- Trend tracking

---

## Sample Redmine Views

### Dashboard View
```
AICL AI Testing Dashboard

Recent Test Runs:
┌─────────┬──────────────┬─────────┬───────┬────────┐
│ ID      │ Model        │ Status  │ Score │ Grade  │
├─────────┼──────────────┼─────────┼───────┼────────┤
│ #125    │ Claude 3.5   │ ✅ Done │ 148   │ A+     │
│ #124    │ GPT-4        │ ⏳ Run  │ -     │ -      │
│ #123    │ Gemini Pro   │ ✅ Done │ 122   │ B+     │
│ #122    │ Claude 3     │ ❌ Fail │ 85    │ C      │
└─────────┴──────────────┴─────────┴───────┴────────┘

Top Performers:
1. Claude 3.5 Sonnet: 148/150 (99%)
2. GPT-4 Turbo: 135/150 (90%)
3. Gemini Pro: 122/150 (81%)
```

### Scenario Breakdown (Issue #125)
```
Test Run #125: Claude 3.5 - Complete Scenario Testing

Status: Complete
Score: 148/150 (99%)
Time: 42 minutes

Child Issues:
├─ #125-1 ✅ Scenario 1: First-Time Setup (20/20)
├─ #125-2 ✅ Scenario 2: Simple Run (25/25)
├─ #125-3 ✅ Scenario 3: Debugging (20/20)
├─ #125-4 ✅ Scenario 4: Docker Mode (15/15)
├─ #125-5 ✅ Scenario 5: State Query (15/15)
└─ #125-6 ⚠️  Scenario 6: Production (23/25)

Attachments:
- execution_summary.json
- full_logs.tar.gz
- comparison_chart.png
```

---

## Automation Architecture

```
┌────────────────────────────────────────────┐
│           Redmine Web UI                   │
│  (Human creates/reviews test runs)         │
└────────────────────────────────────────────┘
                    │
                    ▼ (API)
┌────────────────────────────────────────────┐
│      redmine_test_manager.py               │
│  - Watches for new Test Run issues         │
│  - Creates child Scenario issues           │
│  - Queues execution                        │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│      scenario_executor.py                  │
│  - Runs each scenario                      │
│  - Collects results                        │
│  - Updates Redmine issues                  │
└────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│      results_aggregator.py                 │
│  - Calculates totals                       │
│  - Creates charts/reports                  │
│  - Posts to parent issue                   │
└────────────────────────────────────────────┘
```

---

## Benefits of Redmine Integration

### For Humans:
✅ **No CLI needed** - Everything via web UI
✅ **Track history** - See all past test runs
✅ **Collaborate** - Team can comment, discuss
✅ **Notifications** - Email on completion
✅ **Reports** - Built-in charts and queries

### For Automation:
✅ **Structured** - Custom fields for metadata
✅ **Hierarchical** - Parent/child issues
✅ **Attachments** - Logs, results automatically saved
✅ **API-driven** - Full programmatic control
✅ **Audit trail** - All changes logged

### For Testing:
✅ **Reproducible** - Issue contains all test parameters
✅ **Comparable** - Easy to compare model results
✅ **Iterative** - Re-run tests with one click
✅ **Traceable** - Link bugs to specific test runs

---

## Setup Instructions

See `redmine/setup/INSTALLATION.md` for:
1. Redmine project configuration
2. Python automation deployment
3. Testing the integration
4. Troubleshooting

Would you like me to create the full automation scripts?
