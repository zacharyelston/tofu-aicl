# State Lifecycle

## Four Phases

### 1. Recording (During Apply)
State is being written, lineage grows with each step.

```python
state_manager.start_action("provision", "pinecone_index.embeddings")
# ... provision resource ...
state_manager.record_result({"id": "abc123", "status": "ready"})
```

Lineage appends, infrastructure updates.

### 2. Complete (After Apply)
State is stable, complete DNA is available.

```json
{
  "lineage": [...],  // Complete sequence
  "infrastructure": {...},  // Final state
  "outputs": {...}  // Results
}
```

Perfect for:
- Analysis
- Comparison
- Debugging
- Reproduction

### 3. Reading (Between Apply/Destroy)
State is read-only, used for understanding system.

```bash
# Compare experiments
git diff exp_001.tfstate exp_002.tfstate

# Analyze results
cat exp_001.tfstate | jq '.outputs'

# Understand lineage
cat exp_001.tfstate | jq '.lineage[]'
```

### 4. Destroying (During Destroy)
State guides teardown process.

```python
# Read infrastructure from state
for resource_id in state.infrastructure:
    provider.DeleteResource(resource_id)

# State cleared after destroy
state.infrastructure = {}
state.lineage.append({"action": "destroy", ...})
```

## State Transitions

```
[None] --apply--> [Recording] --complete--> [Stable]
                                               |
[Destroyed] <--destroy-- [Stable] --analyze-- [Stable]
```

## Idempotency

- **Provision**: Running apply twice = same infrastructure state
- **Execute**: Running pipeline twice = two lineage entries
- **Destroy**: Clears infrastructure, preserves lineage history (optional)
