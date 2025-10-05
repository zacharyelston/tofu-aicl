# tofu.aicl - Declarative AI Infrastructure

This project provides a declarative, container-based framework for defining, provisioning, and experimenting with AI infrastructure (RAG pipelines, agents, etc.) using HCL syntax.

## Core Concepts

- **Declarative AI Infrastructure**: Define AI systems (RAG, agents, validators) as code using HCL.
- **Container-Native Architecture**: All providers (LLMs, Vector DBs, etc.) run as isolated, containerized gRPC services.
- **Ephemeral & Just-In-Time**: Spin up AI infrastructure on-demand for a specific task and tear it down automatically.
- **Algorithmic Experimentation**: Test multiple configurations simultaneously and evaluate the best-performing setup.

## Getting Started

1.  **Build Provider Containers:**

    ```bash
    ./scripts/build_providers.sh
    ```

2.  **Run an Experiment:**

    ```bash
    ./scripts/run_experiment.sh
    ```

This will parse the `example.aicl` file, spin up the necessary provider containers, execute the plan, and then tear everything down.