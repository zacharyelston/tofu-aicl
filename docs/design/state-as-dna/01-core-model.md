# Core Model: State as DNA

## The DNA Metaphor

State represents the complete "genetic code" of your AI infrastructure:
- **DNA = Complete Instructions** - Everything needed to recreate the system
- **Unrolled = Flattened View** - All steps visible in sequence
- **Lineage = Execution History** - How we got to current state

## Two Components

### 1. Lineage (The Process)
Append-only log of all actions:
- Provisioning infrastructure
- Executing pipelines  
- Configuration changes
- Resource modifications

### 2. Current State (The Result)
Point-in-time snapshot:
- Infrastructure resources
- Output values
- Computed results
- Resource attributes

## State is NOT Just Inventory

Traditional infrastructure tools (Terraform) use state for:
- ✅ Tracking what exists
- ✅ Planning changes
- ✅ Managing dependencies

tofu-aicl state ALSO includes:
- ✅ Complete execution history
- ✅ Data processing results
- ✅ Experiment parameters
- ✅ Performance metrics

## Key Insight

> State is a **comprehensive report**, not just a resource inventory.

This makes state itself a valuable artifact for:
- Experiment reproducibility
- Result comparison
- Debugging issues
- Understanding workflows

## Separation of Concerns

State manages THREE types of information:

1. **Infrastructure State** (`.tfstate`)
   - Persistent resources (Pinecone indices, LLM configs)
   - Idempotent operations
   - Survives across runs

2. **Provider State** (Runtime)
   - Active gRPC servers
   - Container instances
   - Ephemeral during execution

3. **Execution History** (`.execlog`)
   - Pipeline runs
   - Data transformations
   - Processing results
   - NOT idempotent

## Benefits

- **Reproducibility**: Read state → recreate exact system
- **Debugging**: See complete history of what happened
- **Comparison**: Diff states to compare experiments
- **Documentation**: State documents itself

## Next Steps

See `02-git-backend.md` for why git is the perfect backend for this model.
