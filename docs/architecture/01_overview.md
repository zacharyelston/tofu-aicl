# Architecture Overview

This document describes the high-level architecture of the `tofu-aicl` framework. It is a container-native system that uses a central engine to orchestrate specialized, single-purpose providers via gRPC.

## Workflow Diagram

```mermaid
graph TD
    subgraph User
        A[example.aicl] -- HCL Config --> B(AICLEngine);
    end

    subgraph AICLEngine
        B -- Parses --> C{Resource Graph};
        C -- Starts --> D[Provider Container];
        C -- gRPC Call --> E(Provider Server);
    end

    subgraph Provider Container
        D -- Hosts --> E;
        E -- REST API Call --> F[External API];
    end

    subgraph External Services
        F -- e.g., Pinecone, OpenRouter --> G(Cloud Service);
    end
```

## Core Components

*   **AICLEngine:** The central orchestrator. It parses HCL files, manages state, and communicates with provider containers.
*   **Provider Containers:** Lightweight Docker containers that each expose a single gRPC service for a specific API (e.g., `pinecone`, `openrouter`).
*   **gRPC Protocol:** The universal API contract (`provider.proto`) that all providers must implement.
*   **.aicl Files:** Declarative HCL files that define the desired state of the AI infrastructure.