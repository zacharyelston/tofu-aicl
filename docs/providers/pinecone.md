# Pinecone Provider

This document describes the `pinecone` provider for `tofu-aicl`.

## Configuration

The provider is configured by setting the `PINECONE_API_KEY` environment variable. It does not take any configuration arguments within the HCL `provider` block.

## Resources

### `pinecone_index`

Manages a serverless index in Pinecone.

#### Example Usage

```hcl
resource "pinecone_index" "my_index" {
  name      = "my-index-name"
  dimension = 1536
  metric    = "cosine"
}
```

#### Arguments

*   `name` (Required): The name of the index.
*   `dimension` (Required): The dimension of the vectors to be stored in the index.
*   `metric` (Optional): The distance metric to use. Defaults to `cosine`.