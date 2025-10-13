# Architecture Overview

## High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   User Interface Layer                       │
│              (CLI / Web Dashboard / API)                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       AICL Engine Core                       │
│  ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌────────────────┐ │
│  │  Parser  │→│Evaluator │→│ Planner │→│   Executor     │ │
│  └──────────┘ └──────────┘ └─────────┘ └────────────────┘ │
│                                              ↓               │
│                                    ┌──────────────────┐     │
│                                    │  State Manager   │     │
│                                    └──────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Provider Layer (gRPC)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │   LLM    │ │ Embedder │ │ VectorDB │ │  RAG Service │  │
│  │Providers │ │Providers │ │Providers │ │   Providers  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│         External Services (OpenAI, Pinecone, etc)           │
└─────────────────────────────────────────────────────────────┘
```

## Architectural Patterns

### 1. Configuration-as-Data
- Metadata externalized to YAML/HCL
- No hardcoded provider logic
- Schema-validated configurations
- Fail-fast validation at load time

### 2. Provider Plugin Architecture
- gRPC-based microservices
- Auto-discovery from file system
- Isolated provider processes
- Graceful failure handling

### 3. Layered Architecture
```
Presentation Layer  → CLI, Web UI
Application Layer   → Engine (Parser, Evaluator, Planner, Executor)
Domain Layer        → Resources, Providers, State
Infrastructure      → gRPC, Storage, Observability
```

### 4. Storage Abstraction
- Interface: `StorageBackend` (abstract base)
- Implementations: InMemory, SQLite, PostgreSQL
- Strategy pattern for tier selection

### 5. Immutable State
- State files are snapshots
- State locking for concurrent operations
- Copy-on-write semantics

## Execution Flow

### Standard Workflow
```
User writes .aicl file
         ↓
Parser reads HCL → AST
         ↓
Evaluator resolves variables/expressions
         ↓
Planner builds dependency graph → topological sort
         ↓
Executor provisions resources (via gRPC providers)
         ↓
State Manager persists resource state
         ↓
Output results (stdout/JSON/database)
```

### Provider Lifecycle
```
1. Discovery    → Scan providers/ directory
2. Validation   → Schema check config.yaml
3. Registration → Load into registry
4. Launch       → Start gRPC server subprocess
5. Invoke       → Send RPC requests
6. Shutdown     → Graceful termination + cleanup
```

### Matrix Experiment Flow
```
Load test-variables.yaml
         ↓
Generate AICL configs (template expansion)
         ↓
Execute experiments (parallel or sequential)
         ↓
Collect metrics (cost, latency, quality)
         ↓
Grade with LLM-as-Judge
         ↓
Store results in database
         ↓
Generate comparative analysis
```

## Concurrency Model

### Parallel Execution
- Independent resources execute concurrently
- Dependency graph determines safe parallelism
- Configurable max concurrency

### Provider Isolation
- Each provider = separate process
- gRPC handles inter-process communication
- No shared state between providers

### State Locking
- File-based locks for state files
- Prevents concurrent modifications
- Lease timeout for crashed processes

## Error Handling Strategy

### Fail-Fast
- Configuration errors abort before execution
- Schema validation at parse time
- Provider availability check before plan

### Graceful Degradation
- Provider failures marked in state
- Partial execution allowed (with warnings)
- Retry logic for transient errors

### Rollback
- State snapshots before operations
- Automatic rollback on critical failures
- Manual state recovery commands

## Observability Architecture

### Distributed Tracing (OpenTelemetry)
- Span per resource operation
- Provider call tracking
- End-to-end workflow visibility

### Metrics Collection
- Token usage (input/output)
- API call latency
- Cost per operation
- Success/failure rates

### Logging
- Structured logs (JSON format)
- Log levels: DEBUG, INFO, WARN, ERROR
- Contextual information (request IDs, resource names)
