# Example: Creating a Pinecone Index

This example demonstrates how to use the `pinecone` provider to declaratively create a serverless vector index.

## 1. Configuration File

Create a file named `pinecone_test.aicl` with the following content:

```hcl
terraform {
  required_providers {
    pinecone = {
      source  = "aicl/pinecone"
      version = "~> 1.0"
      container = {
        image = "aicl/pinecone:1.0.0"
      }
    }
  }
}

resource "pinecone_index" "session_memory" {
  name      = "tofu-aicl-memory"
  dimension = 1536
  metric    = "cosine"
}
```

## 2. Set Environment Variable

Ensure your Pinecone API key is available as an environment variable:

```bash
export PINECONE_API_KEY="YOUR_API_KEY"
```

## 3. Run the Experiment

Execute the end-to-end workflow using the `run_experiment.sh` script:

```bash
./scripts/run_experiment.sh pinecone_test.aicl
```

This will build the provider, start the container, and make the API call to create the `tofu-aicl-memory` index in your Pinecone account.