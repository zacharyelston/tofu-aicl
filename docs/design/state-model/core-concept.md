# State as DNA: Core Concept

## The Analogy

State is like DNA unrolled - a complete, linear representation of the entire system.

**DNA Properties:**
- Encodes complete information
- Can be read sequentially
- Contains structure and history
- Self-describing

**State Properties:**
- Records complete lineage
- Shows current reality
- Contains execution history
- Can recreate the system

## Traditional vs DNA State

### Traditional Terraform State
```json
{
  "resources": {
    "pinecone_index": {"id": "abc123", "dimension": 1536}
  }
}
```
Only current inventory.

### DNA State
```json
{
  "lineage": [
    {"action": "provision", "resource": "pinecone_index", "result": {...}},
    {"action": "execute", "pipeline": "ingest", "result": {...}}
  ],
  "current_state": {
    "infrastructure": {...},
    "outputs": {...}
  }
}
```
Complete history + current state.

## Benefits

1. **Reproducibility**: Read state → recreate system
2. **Comparison**: Diff states → compare experiments
3. **Debugging**: See complete lineage
4. **Audit**: Full trail of what happened

## State Lifecycle

```
Apply → Recording (DNA being written)
     → Complete (DNA fully unrolled)
     → Reading (analyze, compare)
     → Destroy (cleanup using DNA)
```
