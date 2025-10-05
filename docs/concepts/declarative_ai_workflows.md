# Concept: Declarative AI Workflows

Traditional AI development often involves writing complex, imperative scripts to chain together different models and services. This approach is brittle, hard to reproduce, and difficult to manage.

`tofu-aicl` introduces a declarative approach. Instead of writing code to *do* things, you write HCL to *define* the desired state of your AI system. The framework then takes care of the complex orchestration needed to achieve that state.

This has several advantages:

*   **Reproducibility:** The same `.aicl` file will always produce the same result.
*   **Modularity:** Each component of the workflow is a self-contained resource.
*   **Readability:** The HCL syntax provides a clear, high-level view of the entire workflow.