# Core Engine Design

The `AICLEngine` is the heart of the `tofu-aicl` framework. It is designed as a state machine that moves through a well-defined lifecycle: `plan`, `apply`, and `destroy`.

## State Management

The engine is responsible for loading the current state from a state file, updating it as resources are changed, and persisting it back to disk. This ensures that the framework is idempotent and can recover from failures.

## Provider Orchestration

The engine communicates with providers via gRPC. It is responsible for starting and stopping the provider containers, passing them their configuration, and calling the appropriate RPC methods to execute the desired changes.