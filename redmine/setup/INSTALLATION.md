# Redmine Integration Setup

Complete guide to setting up Redmine for AICL AI model testing.

## Prerequisites

- Redmine instance (version 4.0+)
- Python 3.8+
- Admin access to Redmine
- API access enabled

## Quick Start

### 1. Configure Redmine Project

Create project "AICL AI Testing" with custom fields:
- Model Name (list)
- Spec Version (list: v2.1, v2.2, v2.3)
- Score (integer: 0-150)
- Execution Time (float)
- Test Status (list)

Create trackers:
- Test Run, Scenario Test, Level Test, Contract Test

### 2. Install Dependencies

```bash
cd redmine/
python3 -m venv venv
source venv/bin/activate
pip install python-redmine requests
```

### 3. Configure

```bash
cp config.example.json config.json
# Edit with your Redmine URL and API key
```

### 4. Run

```bash
python scripts/redmine_test_manager.py
```

### 5. Test

Create a "Test Run" issue in Redmine, watch automation execute it!

See full docs in `/docs/REDMINE_INTEGRATION.md`
