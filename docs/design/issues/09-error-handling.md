# Issue 09: Error Handling Inconsistent

**Priority:** MEDIUM  
**Week:** 3

## Problem

Mixed error handling - some providers return diagnostics, some raise:

```python
# Sometimes catches
try:
    response = provider.stub.DeleteResource(req)
except grpc.RpcError as e:
    print(f"Error: {e.details()}")

# Sometimes doesn't
response = provider.stub.ApplyResourceChange(req)  # Could fail
```

## Solution

Standardize: Providers ALWAYS return diagnostics, engine handles gRPC errors:

```python
class ErrorHandler:
    @staticmethod
    def wrap_grpc_call(func):
        try:
            response = func()
            return response
        except grpc.RpcError as e:
            # Convert to diagnostic
            return Response(
                diagnostics=[
                    Diagnostic(
                        severity=ERROR,
                        summary="RPC Error",
                        detail=e.details()
                    )
                ]
            )

# Usage
response = ErrorHandler.wrap_grpc_call(
    lambda: provider.stub.ApplyResourceChange(req)
)

if response.diagnostics:
    for diag in response.diagnostics:
        if diag.severity == ERROR:
            raise Exception(diag.summary)
```

## Provider Rules

1. Never raise exceptions
2. Always return diagnostics
3. Use ERROR for failures, WARNING for issues
4. Provide detail in diagnostic.detail
