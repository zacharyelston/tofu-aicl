# Redmine Integration for AI Model Testing

## Overview

Use Redmine as the **human interaction layer** for managing AI model comparison experiments.

**Workflow:**
1. Human creates "Test Run" issue in Redmine
2. Automation picks up issue, runs tests
3. Results posted back to Redmine
4. Human reviews, provides feedback
5. Repeat/iterate

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Redmine   │ ◄─API──►│  Test Runner │ ◄──────►│  AI Models  │
│  Web UI     │         │  Automation  │         │ (Claude/GPT)│
└─────────────┘         └──────────────┘         └─────────────┘
      │                        │
      │                        ▼
      │                  ┌──────────┐
      └─────────────────►│  Results │
       (human reviews)   │  Storage │
                         └──────────┘
```

## Redmine Project Structure

### Project: "AICL AI Testing"

**Trackers:**
- Test Run - Overall experiment
- Scenario Test - Individual scenario
- Level Test - Progressive level (v2.1)
- Contract Test - Behavior contract (v2.2)
- Bug - Issues found
- Enhancement - Improvements discovered

**Custom Fields:**
- Model Name (Claude 3.5, GPT-4, Gemini Pro)
- Spec Version (v2.1, v2.2, v2.3)
- Score (0-150)
- Execution Time (minutes)
- Test Status (Pending, Running, Complete, Failed)

**Issue Statuses:**
- New → Queued → Running → Complete / Failed

---

## Integration Points

### 1. Create Test Run (Human → Redmine)

**Human Action:** Create issue via Redmine UI

```
Tracker: Test Run
Subject: Test Claude 3.5 with v2.3 Scenarios
Description:
  Model: Claude 3.5 Sonnet
  Approach: v2.3 Scenario-Based
  Scenarios: All (1-6)
  
Custom Fields:
  Model Name: Claude 3.5
  Spec Version: v2.3
  Test Status: New
```

### 2. Automation Picks Up (Redmine → Test Runner)

**Python Automation:**
```python
# redmine_watcher.py
from redminelib import Redmine

redmine = Redmine('https://redmine.example.com', key='YOUR_API_KEY')

# Watch for new test runs
for issue in redmine.issue.filter(
    project_id='aicl-testing',
    tracker_id='test-run',
    status_id='new'
):
    # Update status
    issue.status_id = STATUS_QUEUED
    issue.save()
    
    # Queue test execution
    run_test_async(
        model=issue.custom_fields['model_name'],
        spec_version=issue.custom_fields['spec_version'],
        issue_id=issue.id
    )
```

### 3. Execute Tests (Test Runner)

**Automated Execution:**
```python
# test_runner.py
def run_test(model, spec_version, issue_id):
    # Update Redmine: Running
    update_issue(issue_id, status='running', 
                 notes="Starting test execution...")
    
    # Load spec
    if spec_version == 'v2.3':
        scenarios = load_scenarios('docs/v2.3/')
        results = run_scenarios(model, scenarios)
    elif spec_version == 'v2.1':
        levels = load_levels('docs/v2.1/')
        results = run_levels(model, levels)
    
    # Post results back to Redmine
    post_results(issue_id, results)
```

### 4. Post Results (Test Runner → Redmine)

**Update Issue with Results:**
```python
# Update main issue
issue = redmine.issue.get(issue_id)
issue.status_id = STATUS_COMPLETE
issue.custom_fields = [
    {'id': 'score', 'value': results.total_score},
    {'id': 'execution_time', 'value': results.duration_minutes}
]
issue.notes = f"""
## Test Results

**Score:** {results.total_score} / 150
**Time:** {results.duration_minutes} minutes
**Grade:** {results.grade}

### Details:
{format_results_table(results)}

See attached files for full output.
"""
issue.save()

# Attach logs
issue.uploads = [
    {'path': 'logs/execution.log'},
    {'path': 'results/summary.json'}
]

# Create child issues for failures
for failure in results.failures:
    redmine.issue.create(
        project_id='aicl-testing',
        tracker_id='bug',
        subject=f"Failure: {failure.name}",
        parent_issue_id=issue.id,
        description=failure.details
    )
```

---

## Workflow Examples

### Example 1: Scenario-Based Test (v2.3)

**Step 1: Human Creates Issue**
```
Tracker: Test Run
Subject: Claude 3.5 - Scenario Testing
Model: Claude 3.5
Spec: v2.3
Priority: Normal
```

**Step 2: Automation Runs**
- Creates 6 child issues (one per scenario)
- Executes each scenario
- Updates child issues with results

**Step 3: Results Posted**
```
Parent Issue: "Claude 3.5 - Scenario Testing"
  Status: Complete
  Score: 148/150 (99%)
  Time: 42 minutes
  
  Child Issues:
  ├─ ✅ Scenario 1: First Run (20/20)
  ├─ ✅ Scenario 2: Simple Run (25/25)
  ├─ ✅ Scenario 3: Debugging (20/20)
  ├─ ✅ Scenario 4: Docker Mode (15/15)
  ├─ ✅ Scenario 5: State Query (15/15)
  └─ ⚠️  Scenario 6: Production (23/25)
```

**Step 4: Human Reviews**
- Sees overall score
- Drills into Scenario 6 to see why 2 points lost
- Leaves comment: "Check error handling in prod scenario"

---

### Example 2: Progressive Levels (v2.1)

**Step 1: Human Creates Issue**
```
Tracker: Test Run
Subject: GPT-4 - Progressive Testing
Model: GPT-4
Spec: v2.1
```

**Step 2: Automation Creates Hierarchy**
```
Parent: "GPT-4 - Progressive Testing"
├─ Level 1: Foundation (40 pts)
│  ├─ Config (20 pts)
│  └─ Logging (20 pts)
├─ Level 2: Execution (50 pts)
│  ├─ Docker Runner (30 pts)
│  └─ Local Runner (20 pts)
├─ Level 3: CLI (40 pts)
└─ Level 4: Polish (20 pts)
```

**Step 3: Results Show Failure at Level 2**
```
✅ Level 1: Complete (40/40)
❌ Level 2: Failed (20/50) - Docker runner broken
⏸️  Level 3: Skipped
⏸️  Level 4: Skipped
```

**Step 4: Human Action**
- Creates Enhancement: "Improve Docker runner spec"
- Links to failed test
- Re-runs after fixing spec

---

## Redmine API Automation

### Python Script: `redmine_test_manager.py`

```python
#!/usr/bin/env python3
"""
Redmine Test Manager
Watches for new test runs and executes them
"""

from redminelib import Redmine
import time
import json
from pathlib import Path

# Redmine connection
REDMINE_URL = "https://redmine.example.com"
REDMINE_KEY = "YOUR_API_KEY"
PROJECT_ID = "aicl-testing"

redmine = Redmine(REDMINE_URL, key=REDMINE_KEY)

def watch_for_tests():
    """Main loop: watch for new test runs"""
    while True:
        # Find new test runs
        issues = redmine.issue.filter(
            project_id=PROJECT_ID,
            tracker_id=get_tracker_id('Test Run'),
            status_id=get_status_id('New')
        )
        
        for issue in issues:
            print(f"Found new test: {issue.subject}")
            execute_test(issue)
        
        time.sleep(30)  # Check every 30 seconds

def execute_test(issue):
    """Execute a test run"""
    # Update status
    issue.status_id = get_status_id('Running')
    issue.notes = "⏳ Test execution started..."
    issue.save()
    
    # Get parameters
    model = issue.custom_fields.get('model_name')
    spec_version = issue.custom_fields.get('spec_version')
    
    try:
        # Run tests
        if spec_version == 'v2.3':
            results = run_scenario_tests(model)
        elif spec_version == 'v2.1':
            results = run_progressive_tests(model)
        elif spec_version == 'v2.2':
            results = run_contract_tests(model)
        
        # Post results
        post_success(issue, results)
        
    except Exception as e:
        post_failure(issue, str(e))

def run_scenario_tests(model):
    """Run scenario-based tests"""
    scenarios = load_scenarios('docs/v2.3/')
    results = {'scenarios': [], 'total': 0}
    
    for scenario in scenarios:
        # Execute scenario
        result = execute_scenario(model, scenario)
        results['scenarios'].append(result)
        results['total'] += result.score
    
    return results

def post_success(issue, results):
    """Post successful results back to Redmine"""
    # Format results
    notes = f"""
## ✅ Test Complete

**Total Score:** {results['total']} / 150
**Grade:** {calculate_grade(results['total'])}

### Results:
{format_table(results)}

### Next Steps:
- Review detailed logs
- Check failed scenarios
- Compare with other models
"""
    
    # Update issue
    issue.status_id = get_status_id('Complete')
    issue.custom_fields = [
        {'id': 'score', 'value': results['total']},
        {'id': 'test_status', 'value': 'Complete'}
    ]
    issue.notes = notes
    issue.save()
    
    # Attach logs
    upload_file(issue, 'logs/execution.log')
    upload_file(issue, 'results/summary.json')

def post_failure(issue, error):
    """Post failure back to Redmine"""
    issue.status_id = get_status_id('Failed')
    issue.notes = f"""
## ❌ Test Failed

**Error:** {error}

**Action Required:**
- Check logs
- Fix issue
- Re-run test
"""
    issue.save()

if __name__ == "__main__":
    print("Starting Redmine Test Manager...")
    watch_for_tests()
```

---

## Benefits

### For Humans:
✅ **Familiar Interface** - Use Redmine web UI (no CLI needed)  
✅ **Visual Progress** - See status updates in real-time  
✅ **History** - All tests tracked in one place  
✅ **Collaboration** - Team can comment, discuss  
✅ **Reports** - Built-in reporting, charts

### For Automation:
✅ **API-Driven** - Python can watch/update issues  
✅ **Structured Data** - Custom fields for metadata  
✅ **Attachments** - Logs, results automatically attached  
✅ **Notifications** - Email alerts on completion  
✅ **Queries** - Find past results easily

---

## Redmine Setup

### 1. Create Project
```
Name: AICL AI Testing
Identifier: aicl-testing
Modules: Issues, Files, Wiki
```

### 2. Create Trackers
- Test Run
- Scenario Test
- Level Test
- Contract Test
- Bug
- Enhancement

### 3. Create Custom Fields
```
Model Name: List (Claude 3.5, GPT-4, Gemini Pro, etc.)
Spec Version: List (v2.1, v2.2, v2.3)
Score: Integer (0-150)
Execution Time: Float (minutes)
Test Status: List (Pending, Running, Complete, Failed)
```

### 4. Create Workflows
```
New → Queued → Running → Complete
                       └→ Failed → New (retry)
```

### 5. Set Permissions
- Developers: Create/edit issues
- Automation: API access (admin or custom role)
- Viewers: Read-only access

---

## Integration Files

Create these files for full integration:

```
redmine/
├── redmine_test_manager.py   # Main automation
├── scenario_runner.py         # v2.3 execution
├── level_runner.py            # v2.1 execution
├── contract_runner.py         # v2.2 execution
├── results_formatter.py       # Format results for Redmine
├── config.yaml                # Redmine connection config
└── README.md                  # Setup instructions
```

---

## Next Steps

1. Set up Redmine project with trackers/fields
2. Create Python automation scripts
3. Configure API key and permissions
4. Test with sample issue
5. Deploy automation as service (systemd, Docker, etc.)
6. Document workflow for team

Would you like me to create the full integration code?
