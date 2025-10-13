# Replit Provider Challenge

## 🎯 The Ultimate Self-Building Test

Generate a **production-grade Replit provider** that enables AICL to manage Replit infrastructure from declarative config. This is AICL building the platform it runs on! 🤯

---

## What We're Building

### Complete Replit Platform Provider

A provider with **3 resource types** for full Replit control:

### 1. `replit_deployment` - Deploy Applications

**Capabilities**:
- Autoscale (scales with traffic)
- Reserved VM (fixed compute)
- Scheduled (cron jobs)
- Static (static sites)

**Example**:
```hcl
resource "replit_deployment" "my_app" {
  name = "production-api"
  type = "autoscale"
  environment = {
    DATABASE_URL = resource.replit_database.db.connection_string
    API_KEY      = "secret-key"
  }
}
```

### 2. `replit_database` - PostgreSQL Databases

**Capabilities**:
- Serverless PostgreSQL
- Automatic connection strings
- 10 GiB storage limit
- Managed backups

**Example**:
```hcl
resource "replit_database" "db" {
  name        = "production-db"
  type        = "postgresql"
  max_size_gb = 5
}

output "db_connection" {
  value = resource.replit_database.db.connection_string
}
```

### 3. `replit_agent` - Spawn Replit Agents

**Capabilities**:
- Slack bots
- Telegram bots
- Email automations
- Scheduled workflows

**Example**:
```hcl
resource "replit_agent" "slack_bot" {
  name        = "support-bot"
  integration = "slack"
  prompt      = "Answer customer questions using our knowledge base"
  schedule    = "every 5 minutes"
}
```

---

## Why This is Hard

This tests AICL's ability to:

✅ **Implement 3 resource types** in one provider  
✅ **GraphQL API integration** (Replit Extensions API)  
✅ **Multi-operation support** (create, read, update, delete)  
✅ **State management** across resource types  
✅ **Production patterns** (circuit breaker, retries, auth)  
✅ **Security** (token handling, connection encryption)  
✅ **6 test files** (deployments, database, agents, API, integration, security)  

**Estimated complexity**: 800-1000 lines across 7 files

---

## Generated Files

### 1. **Specification** (~300 lines)
Technical spec for all 3 resource types, API integration, auth flow

### 2. **`providers/replit/server.py`** (~300-400 lines)
Main provider implementation:
- ReplitProvider class (gRPC servicer)
- DeploymentHandler
- DatabaseHandler  
- AgentHandler
- Resource lifecycle management

### 3. **`providers/replit/api_client.py`** (~250-300 lines)
Replit API client:
- GraphQL query builder
- Deployment API calls
- Database API calls
- Agent API calls
- Circuit breaker + retries
- Authentication

### 4. **`providers/replit/config.yaml`** (~25 lines)
Provider configuration:
- Metadata (name, version, port)
- Resource types
- Capabilities
- Environment variables

### 5. **`providers/replit/test_*.py`** (~400-500 lines)
Comprehensive test suite:
- `test_replit_deployments.py` - All deployment types
- `test_replit_database.py` - Database lifecycle
- `test_replit_agent.py` - Agent creation
- `test_replit_api_client.py` - API mocking
- `test_replit_integration.py` - End-to-end
- `test_replit_security.py` - Security validation

### 6. **Requirements** (~10 lines)
Python dependencies (aiohttp, GraphQL client, etc.)

### 7. **`examples/replit-deployment-example.aicl`** (~50 lines)
Real-world usage example

---

## Replit 2025 Platform Capabilities

The provider integrates with:

### Deployments
- **Autoscale**: Pay per compute unit, scales automatically
- **Reserved VM**: Fixed $10/mo, consistent performance
- **Scheduled**: Cron jobs, $0.000061/second
- **Static**: Free (up to 100 GiB transfer)

### Databases
- **PostgreSQL**: Serverless, managed
- **Pricing**: Pay for compute time + storage
- **Limits**: 10 GiB per database

### Agents & Automations (Beta)
- **Slack bots**: Q&A, research assistants
- **Telegram bots**: Customer service
- **Email**: Automated reports
- **Scheduled**: Monitoring, summaries

### Extensions API
- **GraphQL endpoint**: `https://replit.com/graphql`
- **Filesystem API**: Create/read files
- **Shell API**: Execute commands
- **Authentication**: REPLIT_TOKEN

---

## Quality Criteria (100 points)

### Correctness (40 points)
- ✅ All 3 resource types work
- ✅ GraphQL integration correct
- ✅ CRUD operations complete
- ✅ State management proper
- ✅ Authentication works

### Code Quality (30 points)
- ✅ Clean architecture
- ✅ Async/await patterns
- ✅ Type hints throughout
- ✅ No duplication
- ✅ AICL conventions

### Best Practices (20 points)
- ✅ Circuit breaker
- ✅ Retry with backoff
- ✅ Security (no token leaks)
- ✅ Resource cleanup
- ✅ Error hierarchy

### Maintainability (10 points)
- ✅ Clear structure
- ✅ Good naming
- ✅ 6 test files
- ✅ Easy to extend

### Decision Thresholds
- **≥ 90**: ACCEPT (Production-ready!)
- **80-89**: ACCEPT (Good, deploy it)
- **70-79**: REVISE (Needs work)
- **< 70**: REJECT (Start over)

---

## Running the Challenge

### Prerequisites

```bash
# Required API keys
export OPENAI_API_KEY="sk-..."        # For code generation
export OPENROUTER_API_KEY="sk-..."   # For judging
export PINECONE_API_KEY="..."        # For RAG
export PINECONE_HOST_URL="https://..."

# Optional (auto-detected in Replit)
export REPLIT_TOKEN="..."             # For Replit API
```

### Execute

```bash
# Run the challenge
python run.py experiments/self-build/add-replit-provider.aicl

# This generates:
# 1. Technical specification
# 2. Provider implementation (~400 lines)
# 3. API client module (~300 lines)
# 4. Config file (~25 lines)
# 5. Comprehensive tests (~500 lines)
# 6. Dependencies list
# 7. Example usage
# 8. Quality evaluation by Claude
```

### Review Results

```bash
# Check quality score
cat output/quality_evaluation.json

# Expected:
{
  "overall_score": 85-95,
  "decision": "ACCEPT",
  "strengths": [
    "All 3 resource types correctly implemented",
    "GraphQL integration with proper auth",
    "Circuit breaker pattern",
    ...
  ],
  "replit_specific_notes": "Excellent Replit platform integration..."
}
```

### Apply if Score ≥ 85

```bash
# 1. Install dependencies
pip install aiohttp gql pytest-asyncio

# 2. Create provider directory
mkdir -p providers/replit

# 3. Copy generated files
# (from experiment output)

# 4. Set token (optional, may auto-detect)
export REPLIT_TOKEN="..."  # or leave blank in Replit

# 5. Run tests
pytest providers/replit/ -v

# 6. Try the example
python run.py examples/replit-deployment-example.aicl

# 7. Check auto-discovery
python -c "
from v2.config import ProviderConfigLoader
loader = ProviderConfigLoader()
print(loader.get('replit'))
"
```

---

## Success Criteria

### Must Have
- ✅ All 3 resource types work (deployment, database, agent)
- ✅ Can create autoscale deployments
- ✅ Database connection strings valid
- ✅ Agent webhooks functional
- ✅ GraphQL queries succeed
- ✅ All tests pass (30+ tests)
- ✅ Provider auto-discovers

### Bonus Features
- ✅ Custom domain support
- ✅ Database backup/restore
- ✅ Agent pause/resume
- ✅ Deployment rollback
- ✅ Metrics collection
- ✅ Cost estimation

---

## Real-World Use Cases

### 1. **CI/CD Pipeline**
```hcl
# Deploy on every commit
resource "replit_deployment" "staging" {
  name = "staging-${var.commit_sha}"
  type = "autoscale"
  environment = {
    DATABASE_URL = resource.replit_database.staging_db.connection_string
  }
}
```

### 2. **Database Per Feature Branch**
```hcl
resource "replit_database" "feature_db" {
  name = "feature-${var.branch_name}"
  type = "postgresql"
}
```

### 3. **Automated Customer Support**
```hcl
resource "replit_agent" "support" {
  name        = "customer-support"
  integration = "slack"
  prompt      = "Help customers with billing and technical questions"
}
```

### 4. **Scheduled Data Pipeline**
```hcl
resource "replit_deployment" "etl_job" {
  name = "daily-etl"
  type = "scheduled"
  schedule = "0 2 * * *"  # 2 AM daily
}
```

---

## Why This Matters

### AICL Building Replit!
This provider enables:
- 🚀 **Infrastructure as Code** for Replit
- 🚀 **Self-deployment** from AICL config
- 🚀 **Database management** programmatically
- 🚀 **Agent spawning** from experiments
- 🚀 **CI/CD pipelines** in HCL

**This is AICL managing the platform it runs on!**

---

## Comparison to Other Providers

| Aspect | Echo | Anthropic | Replit |
|--------|------|-----------|--------|
| Resource types | 1 | 1 | **3** |
| API complexity | None | High | **Very High** |
| External APIs | 0 | 1 | **3+** |
| Auth methods | None | API key | **Token + GraphQL** |
| State management | Trivial | Medium | **Complex** |
| Lines of code | 150 | 800 | **1000+** |
| Real-world value | Demo | High | **Critical** |

**Most complex provider yet!**

---

## Meta-Circular Magic 🪄

### The Self-Building Loop

1. **AICL runs** in Replit
2. **AICL generates** Replit provider
3. **Replit provider deploys** AICL apps
4. **AICL manages** Replit infrastructure
5. **AICL spawns agents** on Replit
6. **Agents improve** AICL

**It's turtles all the way down!** 🐢

---

## Expected Results

### If Score ≥ 85 ✅
**This proves**:
- Multi-resource providers work
- Complex API integration succeeds
- GraphQL generation is solid
- State management across resources
- **AICL can build platform integrations**

### If Score < 85 ⚠️
**We learn**:
- Multi-resource complexity limits
- GraphQL generation challenges
- State management issues
- Where to improve prompts

**Either way, massive learning!**

---

## Next Steps After Success

1. **Deploy AICL using AICL**:
   ```hcl
   resource "replit_deployment" "aicl_prod" {
     name = "tofu-aicl-production"
     type = "autoscale"
   }
   ```

2. **Create CI/CD pipeline**:
   - Deploy on push
   - Run tests
   - Auto-rollback on failure

3. **Spawn monitoring agent**:
   - Track deployments
   - Alert on failures
   - Report metrics to Slack

4. **Scale to other platforms**:
   - AWS provider
   - GCP provider
   - Azure provider

---

*Let's see if AICL can build a production provider for the very platform it's running on! 🚀*
