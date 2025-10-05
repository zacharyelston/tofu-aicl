h1. gRPC Provider Protocol v1

This document outlines the gRPC service contract that all `tofu-aicl` providers must implement. It defines the RPC methods and data structures for resource lifecycle management, AI execution, and validation.

h2. Core Principles

* *Stateless Providers:* Provider containers should be stateless. All state is managed by the core engine and passed into RPC calls.
* *Rich Data Structures:* The protocol uses `google.protobuf.Struct` to handle complex, typed data for configurations and attributes, avoiding the limitations of simple key-value pairs.
* *Standardized Diagnostics:* All RPC responses include a `repeated Diagnostic` field for consistent error and warning reporting.

h2. Service Definition: `Provider`

```protobuf
service Provider {
  // --- Lifecycle Management ---
  rpc GetSchema(GetSchemaRequest) returns (GetSchemaResponse);
  rpc ValidateConfig(ValidateConfigRequest) returns (ValidateConfigResponse);
  rpc Configure(ConfigureRequest) returns (ConfigureResponse);

  // --- Resource Management ---
  rpc PlanResourceChange(PlanResourceChangeRequest) returns (PlanResourceChangeResponse);
  rpc ApplyResourceChange(ApplyResourceChangeRequest) returns (ApplyResourceChangeResponse);
  rpc ReadResource(ReadResourceRequest) returns (ReadResourceResponse);
  rpc DeleteResource(DeleteResourceRequest) returns (DeleteResourceResponse);

  // --- AI & Testing Workflow ---
  rpc Execute(ExecuteRequest) returns (stream ExecuteResponse);
  rpc Validate(ValidateRequest) returns (ValidateResponse);

  // --- Health & Metrics ---
  rpc HealthCheck(HealthCheckRequest) returns (HealthCheckResponse);
}
```

h2. Key RPC Methods

* `GetSchema`: Returns the provider's capabilities, including the resources it manages and their configuration schemas.
* `Configure`: Provides the provider with its configuration (e.g., API keys).
* `ApplyResourceChange`: The core method for creating and updating resources.
* `Execute`: The primary method for invoking a resource's AI capability (e.g., running inference).
* `Validate`: The entry point for the `test-cl` framework, used to run assertions.