# Issue 05: No Clear Provisioning vs Execution Separation

**Priority:** HIGH  
**Week:** 2

## Problem

Everything is modeled as a "resource" using Terraform-like Apply/Destroy, even data processing:

```hcl
resource "loader_files" "docs" {  # This is execution, not provisioning!
  path = "./docs"
}
```

Creates semantic confusion:
- What does "destroy" mean for loaded files?
- Is this idempotent?
- Should results be in state?

## Solution

Introduce `pipeline` blocks for execution:

```hcl
# Provisioning (persistent)
resource "pinecone_index" "embeddings" {
  dimension = 1536
}

# Execution (ephemeral)
pipeline "process" {
  step "load" {
    provider = file_loader
    path = "./docs"
  }
  
  step "split" {
    provider = text_splitter
    input = step.load.output
  }
}
```

## Implementation

### Parser Updates
```python
# Parse pipeline blocks
pipelines = parsed_config.get('pipeline', [])
for pipeline_block in pipelines:
    for name, config in pipeline_block.items():
        # Execute pipeline
```

### Engine Updates
```python
class AICLEngine:
    def apply(self):
        # Phase 1: Provision resources
        self._provision_resources()
        
        # Phase 2: Execute pipelines
        self._execute_pipelines()
    
    def _execute_pipelines(self):
        for pipeline in self.pipelines:
            for step in pipeline.steps:
                # Call Execute RPC, not Apply
                provider.stub.Execute(...)
```

### State Updates
```python
# Execution results go to lineage, not infrastructure
state.lineage.append({
    "action": "execute",
    "pipeline": pipeline_name,
    "step": step_name,
    "result": {...}
})
```

## Migration Path

1. Add pipeline parsing
2. Update engine to handle pipelines
3. Refactor providers to use Execute
4. Update examples to use pipelines
5. Deprecate resource-based execution

See: [resource-vs-pipeline.md](../architecture/resource-vs-pipeline.md)
