# Replit Provider Design Specification (continued)

## Implementation Roadmap (continued)

**Phase 3: Authentication (Week 2)** (continued)
- [ ] Implement `replit_authenticated_session` resource
- [ ] JWT token management
- [ ] Token hashing for security
- [ ] Permission verification logic
- [ ] Integration tests

**Phase 4: Data Source (Week 2-3)**
- [ ] Implement `replit_workspace_data` data source
- [ ] Parallel data fetching (user + workspace)
- [ ] File list handling
- [ ] Caching strategy (optional)
- [ ] Integration tests

**Phase 5: Provider Integration (Week 3)**
- [ ] Register provider in `provider_registry.py`
- [ ] gRPC server setup
- [ ] State management
- [ ] End-to-end testing with engine
- [ ] Documentation

**Phase 6: Demo & Release (Week 4)**
- [ ] Create demo .aicl files
- [ ] Performance testing
- [ ] Security audit
- [ ] Documentation complete
- [ ] Release v1.0.0

---

## Testing Strategy

### Unit Tests

**File:** `providers/replit/test_js_bridge.py`
```python
import unittest
from providers.replit.js_bridge import JavaScriptBridge

class TestJavaScriptBridge(unittest.TestCase):
    def setUp(self):
        self.bridge = JavaScriptBridge()

    def test_simple_execution(self):
        """Test basic JavaScript execution"""
        js_code = "console.log(JSON.stringify({result: 42}))"
        result = self.bridge.execute(js_code)

        self.assertTrue(result.success)
        self.assertEqual(result.data['result'], 42)

    def test_timeout_handling(self):
        """Test timeout enforcement"""
        js_code = "setTimeout(() => {}, 10000)"
        result = self.bridge.execute(js_code, timeout=1)

        self.assertFalse(result.success)
        self.assertIn("timed out", result.error)

    def test_error_handling(self):
        """Test JavaScript error capture"""
        js_code = "throw new Error('Test error')"
        result = self.bridge.execute(js_code)

        self.assertFalse(result.success)
        self.assertIn("Test error", result.error)

    def test_retry_logic(self):
        """Test retry with exponential backoff"""
        # Simulate transient failure then success
        js_code = """
        const attempts = parseInt(process.env.ATTEMPT || '0');
        if (attempts < 2) {
            process.env.ATTEMPT = String(attempts + 1);
            process.exit(1);
        }
        console.log(JSON.stringify({success: true}));
        """

        result = self.bridge.execute_with_retry(js_code, max_retries=3)
        self.assertTrue(result.success)
```

**File:** `providers/replit/test_provider.py`
```python
import unittest
from unittest.mock import Mock, patch
from providers.replit.provider import ReplitProvider
from proto import provider_pb2
from google.protobuf.struct_pb2 import Struct, Value

class TestReplitProvider(unittest.TestCase):
    def setUp(self):
        self.provider = ReplitProvider()

    def test_extension_creation(self):
        """Test replit_extension resource creation"""
        config = Struct()
        config["name"] = Value(string_value="Test Extension")
        config["version"] = Value(string_value="1.0.0")

        request = provider_pb2.ApplyResourceChangeRequest(
            type_name="replit_extension",
            config=config
        )

        with patch.object(self.provider, '_execute_js') as mock_js:
            mock_js.return_value = {
                "success": True,
                "dispose_available": True
            }

            response = self.provider.ApplyResourceChange(request, None)

            self.assertEqual(response.new_state.id, "ext-")
            self.assertIn("ext-", response.new_state.id)

    def test_auth_without_extension(self):
        """Test authentication fails without extension"""
        config = Struct()
        config["required_permissions"] = Value(list_value=["read"])

        request = provider_pb2.ApplyResourceChangeRequest(
            type_name="replit_authenticated_session",
            config=config
        )

        context = Mock()
        self.provider.ApplyResourceChange(request, context)

        context.abort.assert_called_with(
            grpc.StatusCode.FAILED_PRECONDITION,
            unittest.mock.ANY
        )

    def test_workspace_data_fetch(self):
        """Test workspace data retrieval"""
        config = Struct()
        config["include_files"] = Value(bool_value=True)

        request = provider_pb2.ReadDataSourceRequest(
            type_name="replit_workspace_data",
            config=config
        )

        with patch.object(self.provider, '_execute_js') as mock_js:
            mock_js.return_value = {
                "user": {"id": "user-123", "username": "test"},
                "repl": {"id": "repl-456", "title": "Test Repl"}
            }

            response = self.provider.ReadDataSource(request, None)

            self.assertEqual(response.state.type, "replit_workspace_data")
            self.assertIn("repl_id", response.state.attributes)
```

### Integration Tests

**File:** `providers/replit/test_integration.py`
```python
import unittest
import subprocess
import time
from providers.replit.provider import ReplitProvider

class TestReplitIntegration(unittest.TestCase):
    """Integration tests that run in actual Replit environment"""

    @unittest.skipUnless(
        os.environ.get('REPLIT_ENV') == 'true',
        "Integration tests require Replit environment"
    )
    def test_full_workflow(self):
        """Test complete extension -> auth -> data workflow"""
        provider = ReplitProvider()

        # 1. Create extension
        ext_request = self._create_extension_request("Integration Test")
        ext_response = provider.ApplyResourceChange(ext_request, None)
        self.assertIn("initialized", ext_response.new_state.status)

        # 2. Authenticate
        auth_request = self._create_auth_request()
        auth_response = provider.ApplyResourceChange(auth_request, None)
        self.assertEqual("authenticated", auth_response.new_state.status)

        # 3. Fetch data
        data_request = self._create_data_request()
        data_response = provider.ReadDataSource(data_request, None)
        self.assertIn("repl_id", data_response.state.attributes)

        # 4. Cleanup
        destroy_request = self._create_destroy_request(
            ext_response.new_state.id
        )
        provider.DestroyResource(destroy_request, None)

    def _create_extension_request(self, name):
        # Helper to create extension request
        pass
```

### Performance Tests

**File:** `providers/replit/test_performance.py`
```python
import unittest
import time
from providers.replit.js_bridge import JavaScriptBridge

class TestPerformance(unittest.TestCase):
    def test_js_bridge_latency(self):
        """Verify JS bridge meets <500ms typical latency"""
        bridge = JavaScriptBridge()
        js_code = "console.log(JSON.stringify({test: true}))"

        latencies = []
        for _ in range(10):
            result = bridge.execute(js_code)
            latencies.append(result.execution_time_ms)

        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

        self.assertLess(avg_latency, 500, "Average latency too high")
        self.assertLess(p95_latency, 1000, "P95 latency too high")

    def test_concurrent_operations(self):
        """Test multiple concurrent JS executions"""
        import concurrent.futures

        bridge = JavaScriptBridge()

        def execute_js(i):
            result = bridge.execute(
                f"console.log(JSON.stringify({{id: {i}}}))"
            )
            return result.success

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(execute_js, i) for i in range(20)]
            results = [f.result() for f in futures]

        self.assertEqual(sum(results), 20, "Not all executions succeeded")
```

---

## Security Considerations

### Token Management

**Security Rules:**
1. **NEVER log JWT tokens in plain text**
   ```python
   # ❌ FORBIDDEN
   logger.info(f"Token: {token}")

   # ✅ CORRECT
   token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
   logger.info(f"Token hash: {token_hash}")
   ```

2. **Store tokens in memory only**
   ```python
   # ❌ FORBIDDEN
   with open('tokens.txt', 'w') as f:
       f.write(token)

   # ✅ CORRECT
   self._active_sessions[user_id] = AuthSession(token=token)
   ```

3. **Clear tokens on destruction**
   ```python
   def DestroyResource(self, request, context):
       session_id = request.current_state.id
       if session_id in self._active_sessions:
           del self._active_sessions[session_id]  # Clear from memory
   ```

### Input Validation

**Validation Strategy:**
```python
def _validate_extension_config(self, config: dict) -> None:
    """Validate extension configuration"""

    # Required fields
    if 'name' not in config:
        raise ValueError("Extension name is required")

    # Name validation
    name = config['name']
    if not 1 <= len(name) <= 255:
        raise ValueError(f"Name length must be 1-255, got {len(name)}")

    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        raise ValueError(f"Invalid name format: {name}")

    # Version validation (if provided)
    if 'version' in config:
        version = config['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            raise ValueError(f"Invalid semver version: {version}")

    # Timeout validation
    timeout = config.get('handshake_timeout', 5000)
    if not 1000 <= timeout <= 60000:
        raise ValueError(f"Timeout must be 1000-60000ms, got {timeout}")
```

### Error Sanitization

**Error Handling:**
```python
def _sanitize_error(self, error: Exception) -> str:
    """Sanitize error message for client"""

    # Remove sensitive information
    error_str = str(error)

    # Remove file paths
    error_str = re.sub(r'/Users/[^/]+/.*?\.py', '[path]', error_str)

    # Remove tokens
    error_str = re.sub(r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*', '[token]', error_str)

    # Remove API keys
    error_str = re.sub(r'sk-[A-Za-z0-9]{48}', '[api_key]', error_str)

    return error_str
```

---

## Monitoring & Observability

### Logging Strategy

**Log Levels:**
- **DEBUG**: Detailed execution flow, configuration values
- **INFO**: Resource operations, state transitions, performance metrics
- **WARNING**: Retries, degraded performance, non-critical errors
- **ERROR**: Failed operations, critical errors, security issues

**Example Logging:**
```python
import logging

logger = logging.getLogger(__name__)

class ReplitProvider:
    def ApplyResourceChange(self, request, context):
        logger.info(f"Creating resource: {request.type_name}")
        start_time = time.time()

        try:
            # ... operation ...

            duration = (time.time() - start_time) * 1000
            logger.info(f"Resource created in {duration:.2f}ms")

        except Exception as e:
            logger.error(f"Failed to create resource: {self._sanitize_error(e)}")
            raise
```

### Metrics to Track

**Performance Metrics:**
- JavaScript bridge execution time (p50, p95, p99)
- Resource provisioning duration by type
- API call success rate
- Retry count per operation

**Resource Metrics:**
- Active extensions count
- Active auth sessions count
- Data source fetch frequency

**Error Metrics:**
- Errors by type (validation, timeout, API, internal)
- Retry success rate
- Failed resource provisions

**Example Metrics Collection:**
```python
from dataclasses import dataclass
from typing import Dict
import time

@dataclass
class ProviderMetrics:
    js_execution_times: list[float]
    resource_creation_times: Dict[str, list[float]]
    errors_by_type: Dict[str, int]
    retry_count: int

    def record_js_execution(self, duration_ms: float):
        self.js_execution_times.append(duration_ms)

    def record_resource_creation(self, resource_type: str, duration_ms: float):
        if resource_type not in self.resource_creation_times:
            self.resource_creation_times[resource_type] = []
        self.resource_creation_times[resource_type].append(duration_ms)

    def record_error(self, error_type: str):
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1

    def get_summary(self) -> dict:
        return {
            "js_bridge": {
                "p50": self._percentile(self.js_execution_times, 0.5),
                "p95": self._percentile(self.js_execution_times, 0.95),
                "count": len(self.js_execution_times)
            },
            "resources": {
                rtype: {
                    "avg": sum(times) / len(times),
                    "count": len(times)
                }
                for rtype, times in self.resource_creation_times.items()
            },
            "errors": self.errors_by_type,
            "retries": self.retry_count
        }

    def _percentile(self, data: list[float], p: float) -> float:
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * p)
        return sorted_data[index]
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] All POC tests passed (3/3)
- [ ] Design spec approved by tech lead
- [ ] Unit tests written and passing (>80% coverage)
- [ ] Integration tests passing in Replit environment
- [ ] Performance benchmarks meet requirements
- [ ] Security audit completed
- [ ] Documentation complete

### Deployment Steps
1. [ ] Create feature branch: `feature/replit-provider`
2. [ ] Implement JavaScript bridge module
3. [ ] Implement resource handlers
4. [ ] Run full test suite
5. [ ] Update provider registry
6. [ ] Create demo .aicl files
7. [ ] Update project README
8. [ ] Submit PR for review
9. [ ] Address review feedback
10. [ ] Merge to main
11. [ ] Tag release: `v1.0.0-replit-provider`

### Post-Deployment
- [ ] Monitor metrics for first 24 hours
- [ ] Collect user feedback
- [ ] Document any issues in GitHub
- [ ] Update design spec with amendments if needed

---

## Known Limitations & Future Enhancements

### Current Limitations

1. **No Token Refresh**
   - JWT tokens expire but no auto-refresh mechanism
   - **Workaround**: User must re-authenticate
   - **Future**: Implement automatic token refresh

2. **No Offline Support**
   - Provider requires active Replit workspace connection
   - **Workaround**: Only use in active Replit environment
   - **Future**: Add offline mode with cached data

3. **Single Workspace Only**
   - Can only access current workspace, not other user repls
   - **Workaround**: Run in target workspace
   - **Future**: Add multi-workspace support

4. **No File Write Operations**
   - Read-only workspace access via Data API
   - **Workaround**: Use file_loader provider for writes
   - **Future**: Implement File System API for write operations

5. **Limited Permission Model**
   - Basic read/write/execute permissions
   - **Workaround**: Request all permissions
   - **Future**: Granular permission system

### Future Enhancements

**Phase 2 Features (Post v1.0.0):**
- [ ] UI Extension API integration
- [ ] Commands API for custom commands
- [ ] File System API for file operations
- [ ] Themes API for workspace customization
- [ ] Real-time workspace events (WebSocket)
- [ ] Multi-workspace support
- [ ] Token auto-refresh mechanism
- [ ] Workspace state caching
- [ ] Advanced permission management

**Phase 3 Features:**
- [ ] Collaborative features (team awareness)
- [ ] Workspace analytics
- [ ] Resource usage tracking
- [ ] Cost optimization features

---

## Appendix A: JavaScript Code Examples

### Extension Initialization

```javascript
// Complete extension initialization with error handling
const { init } = require('@replit/extensions');

(async () => {
    try {
        console.log('Initializing extension...');

        const dispose = await init({
            name: 'AI Workflow Manager',
            version: '1.0.0'
        });

        console.log(JSON.stringify({
            success: true,
            message: 'Extension initialized successfully',
            dispose_available: typeof dispose === 'function',
            timestamp: new Date().toISOString()
        }));

        // Store dispose function reference for cleanup
        global.disposeExtension = dispose;

    } catch (error) {
        console.log(JSON.stringify({
            success: false,
            error: error.message,
            stack: error.stack,
            timestamp: new Date().toISOString()
        }));
        process.exit(1);
    }
})();
```

### Authentication

```javascript
// Complete authentication flow
const { experimental } = require('@replit/extensions');
const { auth } = experimental;

(async () => {
    try {
        // Authenticate user
        const authResult = await auth.authenticate();

        // Get JWT token
        const token = await auth.getAuthToken();

        // Verify token (optional)
        const verification = await auth.verifyAuthToken(token);

        console.log(JSON.stringify({
            success: true,
            user: {
                id: authResult.user.id,
                username: authResult.user.username,
                email: authResult.user.email || null
            },
            token: token,
            token_payload: verification.payload,
            authenticated_at: new Date().toISOString()
        }));

    } catch (error) {
        console.log(JSON.stringify({
            success: false,
            error: error.message,
            error_type: error.constructor.name
        }));
        process.exit(1);
    }
})();
```

### Workspace Data Fetch

```javascript
// Comprehensive workspace data fetch
const { data } = require('@replit/extensions');

(async () => {
    try {
        // Fetch user and repl data in parallel
        const [userResult, replResult] = await Promise.all([
            data.currentUser({
                includePreferences: true,
                includeProfile: true
            }),
            data.currentRepl({
                includeFiles: true,
                includeOwner: true,
                includeMetadata: true
            })
        ]);

        console.log(JSON.stringify({
            success: true,
            user: {
                id: userResult.user.id,
                username: userResult.user.username,
                email: userResult.user.email || null,
                preferences: userResult.user.preferences || {}
            },
            repl: {
                id: replResult.repl.id,
                title: replResult.repl.title,
                language: replResult.repl.language,
                url: replResult.repl.url,
                description: replResult.repl.description || '',
                timeCreated: replResult.repl.timeCreated,
                timeUpdated: replResult.repl.timeUpdated,
                owner: {
                    id: replResult.repl.owner?.id,
                    username: replResult.repl.owner?.username
                },
                fileCount: replResult.repl.files?.length || 0,
                files: (replResult.repl.files || []).map(f => ({
                    name: f.name,
                    type: f.type,
                    path: f.path
                })),
                metadata: replResult.repl.metadata || {}
            },
            fetched_at: new Date().toISOString()
        }));

    } catch (error) {
        console.log(JSON.stringify({
            success: false,
            error: error.message,
            partial_data: {
                user_fetched: !!userResult,
                repl_fetched: !!replResult
            }
        }));
        process.exit(1);
    }
})();
```

---

## Appendix B: Example .aicl Configurations

### Example 1: Basic Workspace Context

```hcl
# basic-workspace-context.aicl
# Demonstrates getting workspace information

resource "replit_extension" "context" {
  name = "Workspace Context Provider"
  version = "1.0.0"
}

data "replit_workspace_data" "current" {
  include_files = true
  include_user = true

  depends_on = [replit_extension.context]
}

output "workspace_info" {
  value = {
    title = data.replit_workspace_data.current.title
    language = data.replit_workspace_data.current.language
    owner = data.replit_workspace_data.current.username
    file_count = data.replit_workspace_data.current.file_count
  }
}
```

### Example 2: Authenticated AI Workflow

```hcl
# authenticated-ai-workflow.aicl
# Demonstrates authenticated user + AI integration

resource "replit_extension" "ai_assistant" {
  name = "AI Assistant"
  version = "1.0.0"
  handshake_timeout = 5000
}

resource "replit_authenticated_session" "user" {
  required_permissions = ["read", "write"]

  depends_on = [replit_extension.ai_assistant]
}

data "replit_workspace_data" "project" {
  include_files = true
  include_user = true

  depends_on = [replit_extension.ai_assistant]
}

resource "openrouter_chat" "code_review" {
  model = "anthropic/claude-3.5-sonnet"

  messages = [{
    role = "system"
    content = <<EOF
You are a code review assistant for ${data.replit_workspace_data.project.username}.
You are reviewing their ${data.replit_workspace_data.project.language} project: ${data.replit_workspace_data.project.title}
EOF
  }, {
    role = "user"
    content = "Please review the project structure and suggest improvements."
  }]

  context = jsonencode({
    authenticated_user = resource.replit_authenticated_session.user.username
    workspace_language = data.replit_workspace_data.project.language
    workspace_url = data.replit_workspace_data.project.url
    file_count = data.replit_workspace_data.project.file_count
  })

  depends_on = [
    replit_authenticated_session.user,
    replit_workspace_data.project
  ]
}

output "review" {
  value = resource.openrouter_chat.code_review.choices[0].message.content
}
```

### Example 3: Multi-Step AI Pipeline

```hcl
# ai-pipeline-with-context.aicl
# Demonstrates full pipeline with workspace context

resource "replit_extension" "pipeline" {
  name = "AI Pipeline Manager"
  version = "1.0.0"
}

resource "replit_authenticated_session" "dev" {
  required_permissions = ["read", "write"]
  depends_on = [replit_extension.pipeline]
}

data "replit_workspace_data" "workspace" {
  include_files = true
  include_user = true
  include_metadata = true
  depends_on = [replit_extension.pipeline]
}

# Step 1: Analyze workspace
resource "openrouter_chat" "analysis" {
  model = "anthropic/claude-3.5-sonnet"

  messages = [{
    role = "user"
    content = <<EOF
Analyze this ${data.replit_workspace_data.workspace.language} workspace:
- Title: ${data.replit_workspace_data.workspace.title}
- Files: ${data.replit_workspace_data.workspace.file_count}
- Owner: ${resource.replit_authenticated_session.dev.username}

Provide a technical analysis.
EOF
  }]
}

# Step 2: Generate improvements based on analysis
resource "openrouter_chat" "improvements" {
  model = "anthropic/claude-3.5-sonnet"

  messages = [{
    role = "user"
    content = <<EOF
Based on this analysis:
${resource.openrouter_chat.analysis.choices[0].message.content}

Suggest 5 specific improvements for the codebase.
EOF
  }]

  depends_on = [openrouter_chat.analysis]
}

output "pipeline_results" {
  value = {
    workspace = data.replit_workspace_data.workspace.title
    user = resource.replit_authenticated_session.dev.username
    analysis = resource.openrouter_chat.analysis.choices[0].message.content
    improvements = resource.openrouter_chat.improvements.choices[0].message.content
  }
}
```

---

## Document Control

**Template Version:** 1.0 (tofu-aicl Replit provider)
**Created:** October 5, 2025
**Last Modified:** October 5, 2025
**Next Review:** After implementation completion
**Owner:** Zac Elston
**Status:** DRAFT - Awaiting Approval

---

**END OF DESIGN SPECIFICATION**

This specification serves as the **complete contract** for Replit provider implementation. No code should be written that deviates from this specification without a formal amendment process.