# ADR 002: Provider Dependency Management

**Status:** Accepted

**Context:** Providers, such as the `pinecone` provider, have their own Python dependencies (e.g., `requests`). We need a way to manage these dependencies without creating conflicts or bloating the core engine.

**Decision:** Each provider will be a self-contained Docker image with its own `requirements.txt` file. The `AICLEngine` will be responsible for building and running these images, but it will have no knowledge of their internal dependencies.

**Consequences:**

*   **Pros:** Excellent dependency isolation. Providers can use any version of any library without affecting the core engine or other providers.
*   **Cons:** Slightly higher overhead due to the need to build and run Docker containers. This is a trade-off we accept for the sake of robustness and modularity.
