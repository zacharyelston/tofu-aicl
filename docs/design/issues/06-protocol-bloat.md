# Issue 06: gRPC Protocol Tries to Do Too Much

**Priority:** MEDIUM  
**Week:** 2

## Problem

Every provider must implement 10+ RPC methods, most are stubs:

```python
def ReadResource(self, request, context):
    return provider_pb2.ReadResourceResponse()  # Empty stub
```

## Solution

Split into focused services or use optional methods:

```protobuf
// Option 1: Separate services
service LifecycleProvider {
  rpc ApplyResourceChange(...);
  rpc DeleteResource(...);
}

service ExecutionProvider {
  rpc Execute(...);
}

// Option 2: Feature flags
service Provider {
  rpc GetCapabilities() returns (Capabilities);  // NEW
  // Providers declare which RPCs they support
}
```

## Implementation

Providers declare capabilities:

```python
def GetCapabilities(self):
    return Capabilities(
        supports_lifecycle=True,
        supports_execution=True,
        supports_validation=False
    )
```

Engine checks before calling:

```python
caps = provider.GetCapabilities()
if caps.supports_execution:
    provider.Execute(...)
```
