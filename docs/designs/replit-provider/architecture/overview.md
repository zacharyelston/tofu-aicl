# System Architecture

## Component Overview

```mermaid
graph TB
    subgraph "AICL Engine Process"
        Engine[Engine Core]
        Executor[Executor]
    end

    subgraph "Replit Provider Process (Python)"
        Provider[ReplitProvider<br/>gRPC Server]
        JSBridge[JavaScript Bridge]
        ExtMgr[Extension Manager]
        AuthMgr[Auth Manager]
        DataMgr[Data Manager]
    end

    subgraph "Node.js Subprocess"
        NodeExec[Node.js Runtime]
        ReplitLib[@replit/extensions]
    end

    subgraph "Replit Workspace"
        ReplitAPI[Replit Extensions API]
        Workspace[Workspace Context]
    end

    Engine -->|gRPC Request| Provider
    Provider -->|Route by type| ExtMgr
    Provider -->|Route by type| AuthMgr
    Provider -->|Route by type| DataMgr

    ExtMgr -->|Execute JS| JSBridge
    AuthMgr -->|Execute JS| JSBridge
    DataMgr -->|Execute JS| JSBridge

    JSBridge -->|subprocess.run| NodeExec
    NodeExec -->|import| ReplitLib
    ReplitLib -->|API Calls| ReplitAPI

    ReplitAPI -->|Read| Workspace
    ReplitAPI -->|JSON Response| NodeExec
    NodeExec -->|stdout JSON| JSBridge
    JSBridge -->|Parse Result| Provider
    Provider -->|gRPC Response| Engine

    style Provider fill:#e1f5ff
    style JSBridge fill:#fff4e6
    style NodeExec fill:#e8f5e9
```

## Components

### AICL Engine
- Orchestrates provider lifecycle
- Manages resource provisioning
- Handles dependency resolution

### Replit Provider
- Python gRPC server
- Implements ProviderServicer interface
- Routes requests to resource managers

### JavaScript Bridge
- Executes Node.js code via subprocess
- Parses JSON responses
- Handles errors and timeouts

### Resource Managers
- **Extension Manager**: Handles replit_extension lifecycle
- **Auth Manager**: JWT token management
- **Data Manager**: Workspace/user data fetching

### Node.js Runtime
- Executes JavaScript code
- Imports @replit/extensions library
- Returns JSON to Python

### Replit Extensions API
- Init, auth, data APIs
- WebSocket/HTTP communication
- Workspace context access

## Communication Protocols

- **Engine ↔ Provider**: gRPC (protobuf)
- **Provider ↔ Node.js**: subprocess stdin/stdout (JSON)
- **Node.js ↔ Replit**: HTTP/WebSocket (JavaScript promises)