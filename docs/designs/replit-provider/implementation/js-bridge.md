# JavaScript Bridge Implementation

## Core Module

**File:** `providers/replit/js_bridge.py`

```python
import subprocess
import json
import logging
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class JSExecutionResult:
    """Result of JavaScript execution"""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    execution_time_ms: float

class JavaScriptBridge:
    """
    Execute JavaScript code via Node.js subprocess and parse JSON results.

    Enables communication between Python provider and Replit's
    JavaScript-based Extensions API.
    """

    def __init__(self, node_path: str = "node", default_timeout: int = 10):
        self.node_path = node_path
        self.default_timeout = default_timeout

    def execute(self, js_code: str, timeout: Optional[int] = None) -> JSExecutionResult:
        """Execute JavaScript code and parse JSON output"""
        start_time = time.time()
        timeout = timeout or self.default_timeout

        try:
            result = subprocess.run(
                [self.node_path, '-e', js_code],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            execution_time = (time.time() - start_time) * 1000

            if result.returncode != 0:
                logger.error(f"JavaScript execution failed: {result.stderr}")
                return JSExecutionResult(
                    success=False,
                    data=None,
                    error=result.stderr,
                    execution_time_ms=execution_time
                )

            try:
                data = json.loads(result.stdout)
                logger.info(f"JavaScript executed in {execution_time:.2f}ms")
                return JSExecutionResult(
                    success=True,
                    data=data,
                    error=None,
                    execution_time_ms=execution_time
                )
            except json.JSONDecodeError as e:
                return JSExecutionResult(
                    success=False,
                    data=None,
                    error=f"Invalid JSON: {str(e)}",
                    execution_time_ms=execution_time
                )

        except subprocess.TimeoutExpired:
            execution_time = (time.time() - start_time) * 1000
            return JSExecutionResult(
                success=False,
                data=None,
                error=f"Execution timed out after {timeout}s",
                execution_time_ms=execution_time
            )
```

## Retry Logic

```python
def execute_with_retry(
    self,
    js_code: str,
    max_retries: int = 3,
    timeout: Optional[int] = None
) -> JSExecutionResult:
    """Execute with exponential backoff retry"""

    for attempt in range(max_retries):
        result = self.execute(js_code, timeout)

        if result.success:
            return result

        # Don't retry on timeout or invalid JSON
        if "timed out" in (result.error or ""):
            return result
        if "Invalid JSON" in (result.error or ""):
            return result

        # Exponential backoff
        if attempt < max_retries - 1:
            backoff_ms = 100 * (2 ** attempt)
            logger.info(f"Retrying in {backoff_ms}ms (attempt {attempt + 1}/{max_retries})")
            time.sleep(backoff_ms / 1000)

    return result
```

## Usage Examples

```python
# Simple execution
bridge = JavaScriptBridge()
result = bridge.execute("""
const { init } = require('@replit/extensions');
(async () => {
    const dispose = await init();
    console.log(JSON.stringify({ success: true }));
})();
""")

if result.success:
    print(f"Success in {result.execution_time_ms}ms")
    print(result.data)

# With retry
result = bridge.execute_with_retry(js_code, max_retries=3)
```