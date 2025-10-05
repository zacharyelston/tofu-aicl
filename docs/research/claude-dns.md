# Design Review & State as DNA Implementation Plan

## Context

This document captures the design review conversation and subsequent decision to implement git-based state management with the "State as DNA" model for tofu-aicl.

## Original Request

A comprehensive design review was requested for the tofu-aicl codebase to identify issues early in development and ensure proper architectural direction.

## Design Review Summary

The complete design review identified **10 critical issues** across three categories:

### Critical Path Issues (Week 1)
1. **Dependency Resolution** - Fundamentally broken reference parsing
2. **HCL Parsing** - Too simplistic, lacks evaluation context  
3. **State Management** - Race conditions and fuzzy matching
4. **Resource ID Generation** - Inconsistent, causes collisions

### Architectural Issues (Week 2)
5. **Provisioning vs Execution** - No clear separation
6. **gRPC Protocol Bloat** - Single interface does too much
7. **Execution History** - No observability or tracking

### Best Practices Missing (Week 3)
8. **Validation Layer** - No schema validation
9. **Error Handling** - Inconsistent patterns
10. **Testing Framework** - Security issues with `eval()`

See the complete review in Redmine wiki: `Design_Review_2025-10-04`

## State as DNA Decision

### The Key Insight

During the review discussion, we realized that **state should be the "DNA unrolled"** - a complete flattened view of the entire process, not just an inventory of resources.

This insight led to several important design decisions:

1. **State is a comprehensive report**, containing:
   - Complete lineage (append-only history)
   - Current state (point-in-time snapshot)
   - Full execution context

2. **Git is the perfect backend** for this model because:
   - Experimentation is the primary use case
   - State files are valuable artifacts to version
   - Comparing experiments via `git diff` is essential
   - Team coordination through PRs is natural

3. **Three distinct types of state**:
   - Infrastructure (persistent resources)
   - Provider state (runtime services)
   - Execution history (pipeline results)

### Decision: Git-Based State by Default

**Question:** "Should we update the design to make git the primary state backend?"

**Answer:** Yes! With modular documentation in a feature branch.

## Implementation

### Branch Created
`feature/state-as-dna-design` - Created from `main` branch

### Documentation Structure

Created comprehensive modular documentation in `docs/design/state-as-dna/`:

```
docs/design/state-as-dna/
├── README.md                    # Overview and navigation
├── 01-core-model.md            # The DNA metaphor explained
├── 02-git-backend.md           # Why git is perfect
├── 03-state-structure.md       # JSON format with lineage
├── 04-lifecycle.md             # State through execution phases
├── 05-remote-backend.md        # When to use S3/DynamoDB
├── 06-implementation.md        # Code changes needed
└── diagrams/
    ├── state-lifecycle.mmd     # State transition diagram
    ├── state-separation.mmd    # Three types of state
    └── git-workflow.mmd        # Git collaboration flow
```

### Key Features of the Design

1. **Append-Only Lineage**
   - Every action recorded with timestamp
   - Complete audit trail
   - Reproducibility built-in

2. **Git Integration**
   - State files in `terraform.tfstate.d/`
   - Standard git workflows
   - PR reviews for experiments
   - Natural conflict resolution

3. **Backwards Compatible**
   - Phase 1: Add lineage support
   - Phase 2: Add backend abstraction  
   - Phase 3: Integrate with engine
   - Phase 4: Optional S3 backend

### State File Example

```json
{
  "version": "1.0",
  "experiment_id": "rag_experiment_001",
  "metadata": {...},
  "lineage": [
    {
      "timestamp": "2025-10-05T10:00:01Z",
      "action": "provision",
      "resource": "pinecone_index.embeddings",
      "result": {"id": "...", "status": "ready"}
    },
    {
      "timestamp": "2025-10-05T10:00:05Z",
      "action": "execute",
      "pipeline": "ingest_docs",
      "step": "load_files",
      "result": {"documents": 23}
    }
  ],
  "current_state": {
    "infrastructure": {...},
    "outputs": {...}
  }
}
```

## Next Steps

### Immediate Actions

1. ✅ **Documentation Complete** - Modular design docs created
2. ✅ **Branch Created** - `feature/state-as-dna-design`
3. ✅ **Committed** - All design files committed

### Pending Actions

1. **Review Documentation** - Team review of design docs
2. **Create Redmine Wiki Page** - Document "State as DNA" design in Redmine
3. **Create Implementation Issues** - Break down implementation into tasks
4. **Begin Phase 1** - Implement lineage tracking in StateManager

### Implementation Phases

**Phase 1: Lineage Support** (1-2 days)
- Implement State dataclasses with lineage
- Update StateManager to track actions
- Maintain backwards compatibility

**Phase 2: Backend Abstraction** (1-2 days)
- Create StateBackend interface
- Implement LocalGitBackend
- Add git commit tracking

**Phase 3: Engine Integration** (2-3 days)
- Update Engine to record actions
- Add lineage entries for all operations
- Update tests

**Phase 4: Optional Remote** (2-3 days)
- Implement S3Backend
- Add configuration support
- Documentation

## Benefits of This Approach

1. **Reproducibility** - Complete DNA to recreate experiments
2. **Comparison** - Easy diff between experiments
3. **Debugging** - Full history of what happened
4. **Collaboration** - Git-native workflows
5. **Simplicity** - No external dependencies for 90% of use cases

## References

- **Redmine Wiki**: `Design_Review_2025-10-04`
- **Git Branch**: `feature/state-as-dna-design`
- **Design Docs**: `docs/design/state-as-dna/`
- **Related Issues**: #967, #968, #969, #970, #971 (Redmine)

---

**Status**: Design complete, implementation pending
**Date**: October 5, 2025
**Decision**: Git-based state with lineage tracking is the default backend
