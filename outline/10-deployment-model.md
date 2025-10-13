# Deployment Model Specification

## Dual-Tier Business Model

### Free CLI Tier
- Local execution
- In-memory storage (default) or SQLite (user-configured)
- Single-user
- All core features
- Community support

### Paid Web Tier
- Multi-tenant SaaS
- Managed PostgreSQL storage
- Web dashboard
- Team collaboration
- Advanced analytics
- Priority support
- API access

---

## CLI Deployment

### Distribution

#### Package Managers

**PyPI (Python)**:
```bash
pip install tofu-aicl
aicl --version
```

**Homebrew (macOS/Linux)**:
```bash
brew install tofu-aicl
aicl --version
```

**NPM (Alternative - if built with Node.js)**:
```bash
npm install -g tofu-aicl
aicl --version
```

#### Binary Releases

**GitHub Releases**:
- Compiled binaries for major platforms
- Linux (x64, ARM64)
- macOS (Intel, Apple Silicon)
- Windows (x64)

```bash
# Download and install
curl -L https://github.com/org/tofu-aicl/releases/latest/download/aicl-linux-x64 -o aicl
chmod +x aicl
sudo mv aicl /usr/local/bin/
```

---

### Installation Options

#### Minimal Install
```bash
pip install tofu-aicl
# Includes: core engine, basic providers
```

#### Full Install (with all providers)
```bash
pip install tofu-aicl[full]
# Includes: all official providers, dev tools
```

#### Development Install
```bash
git clone https://github.com/org/tofu-aicl.git
cd tofu-aicl
pip install -e .[dev]
# Includes: testing tools, docs generator
```

---

### Configuration

#### Default Config Locations

```
~/.aicl/
├── config.yaml          # Global configuration
├── providers/           # Custom provider directory
└── state/               # Default state file location
```

#### Global Config: ~/.aicl/config.yaml

```yaml
# Storage
storage:
  default: memory        # memory | sqlite | postgres
  sqlite_path: ~/.aicl/experiments.db

# Providers
providers:
  directory: ~/.aicl/providers
  auto_discover: true

# Execution
execution:
  max_parallelism: 10
  timeout_seconds: 300
  auto_approve: false

# Observability
observability:
  enabled: true
  exporter: otlp
  endpoint: http://localhost:4318
```

---

## Web Deployment (SaaS)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Load Balancer                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Web Application                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Auth/Users  │  │   Dashboard  │  │   API Server    │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Execution Workers                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Worker 1   │  │   Worker 2   │  │    Worker N     │   │
│  │ (AICL Engine)│  │ (AICL Engine)│  │  (AICL Engine)  │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  PostgreSQL  │  │     Redis    │  │  Object Store   │   │
│  │ (experiments)│  │    (cache)   │  │    (states)     │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

### Technology Stack (Web)

#### Frontend
- **Framework**: React or Vue.js
- **UI Library**: Tailwind CSS or Material-UI
- **State Management**: Redux or Zustand
- **API Client**: Axios or Fetch API

#### Backend API
- **Language**: Python (FastAPI) or Node.js (Express)
- **Authentication**: JWT tokens
- **API Docs**: OpenAPI/Swagger

#### Database
- **Primary**: PostgreSQL (experiments, users)
- **Cache**: Redis (sessions, query cache)
- **Object Store**: S3-compatible (state files, logs)

#### Workers
- **Queue**: Celery (Python) or Bull (Node.js)
- **Execution**: AICL Engine instances
- **Scaling**: Horizontal (add workers)

---

### Deployment Platforms

#### Option 1: Replit Deployments
```yaml
# .replit
run = "uvicorn main:app --host 0.0.0.0 --port 5000"

[deployment]
run = ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
deploymentTarget = "autoscale"
```

#### Option 2: Vercel/Netlify (Serverless)
```yaml
# vercel.json
{
  "builds": [
    {"src": "api/**/*.py", "use": "@vercel/python"}
  ],
  "routes": [
    {"src": "/api/(.*)", "dest": "api/$1"}
  ]
}
```

#### Option 3: Docker + Kubernetes
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aicl-web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aicl-web
  template:
    metadata:
      labels:
        app: aicl-web
    spec:
      containers:
      - name: web
        image: tofu-aicl:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
```

---

### Multi-Tenancy

#### User Isolation

```python
# All queries scoped to user
class ExperimentService:
    def __init__(self, user_id: str, storage: StorageBackend):
        self.user_id = user_id
        self.storage = storage
    
    def list_experiments(self):
        # Storage filters by user_id automatically
        return self.storage.list_experiments(user_id=self.user_id)
```

#### Resource Quotas

```python
# Per-user limits
class UserQuota:
    max_experiments_per_month: int = 100
    max_executions_per_experiment: int = 50
    max_parallel_experiments: int = 5
    max_storage_mb: int = 1000
    
    def check_quota(self, user: User) -> bool:
        current_usage = self.get_usage(user)
        return current_usage < self.max_experiments_per_month
```

---

### Pricing Tiers

#### Free Tier (CLI)
- ✓ Unlimited local experiments
- ✓ All core features
- ✓ Community support
- ✗ No cloud storage
- ✗ No collaboration

#### Starter ($29/month)
- ✓ 100 experiments/month
- ✓ Cloud storage (1GB)
- ✓ Web dashboard
- ✓ Email support
- ✗ No team features

#### Professional ($99/month)
- ✓ 1,000 experiments/month
- ✓ Cloud storage (10GB)
- ✓ Advanced analytics
- ✓ Team collaboration (5 users)
- ✓ Priority support
- ✓ API access

#### Enterprise (Custom)
- ✓ Unlimited experiments
- ✓ Unlimited storage
- ✓ SSO/SAML
- ✓ Unlimited team members
- ✓ Dedicated support
- ✓ On-premise deployment option
- ✓ SLA guarantee

---

## Provider Execution Modes

### Local (CLI)
```python
# Subprocess execution
provider_process = subprocess.Popen([
    'python', 'providers/openai/server.py'
])
```

### Docker (Isolated)
```python
# Docker container execution
client = docker.from_env()
container = client.containers.run(
    'aicl/provider-openai:latest',
    environment={'OPENAI_API_KEY': api_key},
    ports={'50051/tcp': 50051},
    detach=True
)
```

### Remote (Web/Cloud)
```python
# Remote gRPC connection
channel = grpc.insecure_channel('provider-openai.internal:50051')
stub = ProviderStub(channel)
```

---

## Security Considerations

### API Key Management

#### CLI: Environment Variables
```bash
export OPENAI_API_KEY="sk-..."
aicl run pipeline.aicl
```

#### Web: Encrypted Storage
```python
from cryptography.fernet import Fernet

class SecretStorage:
    def __init__(self, encryption_key: bytes):
        self.cipher = Fernet(encryption_key)
    
    def store_api_key(self, user_id: str, provider: str, key: str):
        encrypted = self.cipher.encrypt(key.encode())
        db.save(user_id, provider, encrypted)
    
    def retrieve_api_key(self, user_id: str, provider: str) -> str:
        encrypted = db.load(user_id, provider)
        return self.cipher.decrypt(encrypted).decode()
```

### Network Security
- **TLS**: All API communication encrypted
- **Authentication**: JWT tokens with expiry
- **Rate Limiting**: Per-user API limits
- **Input Validation**: Sanitize all user inputs

### Code Execution Isolation
- **Sandboxing**: Providers run in isolated processes
- **Resource Limits**: CPU, memory, timeout constraints
- **Untrusted Code**: Never execute user-provided Python
- **HCL Only**: Only parse/execute declarative HCL

---

## Monitoring and Observability

### Metrics to Track

```python
# Application metrics
experiments_total = Counter('experiments_total', 'Total experiments')
experiments_duration = Histogram('experiments_duration_seconds', 'Experiment duration')
api_cost_total = Counter('api_cost_total', 'Total API costs')

# Infrastructure metrics
provider_processes = Gauge('provider_processes', 'Active provider processes')
database_connections = Gauge('database_connections', 'Active DB connections')
```

### Logging

```python
import structlog

log = structlog.get_logger()

log.info(
    "experiment_started",
    experiment_id="exp-123",
    user_id="user-456",
    config_hash="abc123"
)
```

### Alerting

- High error rate (>5%)
- Slow response time (>10s p95)
- High costs (>$100/day)
- Provider failures
- Database connection issues
