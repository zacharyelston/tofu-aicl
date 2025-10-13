# Redmine Integration for AICL Testing

Complete automation for managing AI model testing via Redmine web interface.

## Overview

Humans interact via Redmine web UI, automation executes tests and reports results.

```
Human → Redmine UI → Test Manager → Executors → Results → Redmine UI → Human
```

## Architecture

```
redmine/
├── scripts/
│   ├── redmine_test_manager.py   # Main watcher
│   ├── scenario_executor.py      # v2.3 scenarios
│   ├── level_executor.py         # v2.1 progressive levels
│   └── contract_executor.py      # v2.2 behavior contracts
├── setup/
│   └── INSTALLATION.md           # Setup guide
└── config.example.json           # Configuration template
```

## Quick Start

### 1. Setup Redmine (one-time)

See `setup/INSTALLATION.md` for:
- Project creation
- Custom fields
- Trackers
- API access

### 2. Configure Automation

```bash
cd redmine/
cp config.example.json config.json

# Edit config.json with your:
# - Redmine URL
# - API key
# - Project ID
```

### 3. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install python-redmine requests
```

### 4. Run Automation

```bash
python scripts/redmine_test_manager.py
```

### 5. Create Test (via Redmine UI)

```
New Issue:
  Tracker: Test Run
  Subject: Claude 3.5 - v2.3 Testing
  Model: Claude 3.5 Sonnet
  Spec Version: v2.3
  Status: New

[Save]
```

Automation picks it up within 30 seconds!

## Supported Testing Approaches

### v2.3: Scenario-Based
- 6 real-world scenarios
- User workflow focus
- UX scoring
- Best for: Production readiness

### v2.1: Progressive Levels
- 4 independent levels
- Build incrementally
- Stop on failure
- Best for: Finding capability gaps

### v2.2: Contract-Based
- 7 behavior contracts
- Implementation freedom
- Pass/fail per contract
- Best for: Correctness validation

## Workflow Example

**Human creates issue** → **Automation:**

1. Status → Queued
2. Creates child issues (6 scenarios / 4 levels / 7 contracts)
3. Status → Running
4. Executes tests sequentially
5. Updates each child issue
6. Aggregates results
7. Status → Complete
8. Posts summary with grade

**Human reviews:**
- Overall score and grade
- Individual results
- Attached logs
- Comparison with other models

## Features

✅ **Web-based** - No CLI needed  
✅ **Real-time** - Live progress updates  
✅ **Historical** - All tests tracked  
✅ **Collaborative** - Team comments/discussion  
✅ **Automated** - Zero manual execution  
✅ **Traceable** - Complete audit trail

## Configuration

### config.json

```json
{
  "redmine_url": "https://your-redmine.com",
  "api_key": "YOUR_API_KEY",
  "project_id": "aicl-testing",
  "watch_interval": 30,
  
  "custom_field_ids": {
    "model_name": 1,
    "spec_version": 2,
    "score": 3
  }
}
```

### Environment Variables

```bash
export REDMINE_API_KEY="your_api_key"
export REDMINE_URL="https://your-redmine.com"
```

## Documentation

- **Architecture:** `/docs/REDMINE_INTEGRATION.md`
- **Workflows:** `/docs/v2.3/REDMINE_WORKFLOWS.md`
- **Setup Guide:** `setup/INSTALLATION.md`
- **Spec v2.1:** `/docs/v2.1/README.md`
- **Spec v2.2:** `/docs/v2.2/README.md`
- **Spec v2.3:** `/docs/v2.3/README.md`

## Deployment

### Local/Dev

```bash
# Run in terminal
python scripts/redmine_test_manager.py
```

### Production (systemd)

```bash
sudo cp setup/aicl-redmine.service /etc/systemd/system/
sudo systemctl enable aicl-redmine
sudo systemctl start aicl-redmine
```

### Docker

```bash
docker build -t aicl-redmine .
docker run -d --name aicl-redmine \
  -v $(pwd)/config.json:/app/config.json \
  aicl-redmine
```

## Troubleshooting

### Connection Issues

```bash
# Test Redmine API
curl -H "X-Redmine-API-Key: YOUR_KEY" \
  https://your-redmine.com/projects.json
```

### Permission Issues

Check API user has:
- Read access to project
- Create/edit issues
- Add attachments
- Update custom fields

### Missing Custom Fields

Run ID discovery:
```bash
python scripts/get_redmine_ids.py
```

Update `config.json` with correct IDs.

## Support

- Issues: Create issue in Redmine
- Logs: `logs/redmine_manager.log`
- Docs: `docs/REDMINE_INTEGRATION.md`
