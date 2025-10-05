# Design Review Summary

**Branch:** `design/state-as-dna`  
**Date:** 2025-10-05

## Executive Summary

tofu-aicl has a sound core architecture but needs critical fixes before further development. This design review proposes treating state as "DNA" - a complete, flattened record of system lifecycle - and using git as the primary state backend.

## Key Changes

### 1. State as DNA
- State is comprehensive report, not just inventory
- Includes lineage (what happened) + current state
- Git-tracked by default for versioning and comparison

### 2. Three-Layer Architecture
- **Infrastructure:** Persistent resources (Terraform-like)
- **Services:** Provider containers (Docker-like)  
- **Pipelines:** Data workflows (Airflow-like)

### 3. Git-Based State
- Primary backend: git (perfect for experimentation)
- Optional remote: S3/DynamoDB (edge cases only)
- "Locking" through merge conflicts

## Critical Issues (Fix Week 1)

1. **Dependency Resolution** - Broken reference parsing
2. **HCL Parsing** - No variable interpolation
3. **State Management** - Race conditions, fuzzy matching
4. **Resource IDs** - Inconsistent generation, collisions

## Architecture Issues (Fix Week 2)

5. **Provisioning vs Execution** - No clear separation
6. **Protocol Bloat** - Too many stub methods

## Observability Issues (Fix Week 3)

7. **Execution History** - No tracking
8. **Validation** - No schema checking
9. **Error Handling** - Inconsistent
10. **Testing Security** - Uses eval()

## File Structure

```
docs/design/
├── README.md                          # This overview
├── state-model/
│   ├── core-concept.md               # DNA analogy
│   ├── git-backend.md                # Using git
│   ├── structure.md                  # State format
│   └── lifecycle.md                  # State phases
├── architecture/
│   ├── three-layers.md               # Infra/Services/Pipelines
│   ├── resource-vs-pipeline.md       # Clear separation
│   ├── provider-protocol.md          # Apply vs Execute
│   └── use-cases.md                  # Common patterns
└── issues/
    ├── 01-dependency-resolution.md
    ├── 02-hcl-parsing.md
    ├── 03-state-management.md
    ├── 04-resource-ids.md
    ├── 05-provisioning-execution.md
    ├── 06-protocol-bloat.md
    ├── 07-execution-history.md
    ├── 08-validation.md
    ├── 09-error-handling.md
    └── 10-testing-security.md
```

## Next Steps

1. Review this design with team
2. Create Redmine issues for each item
3. Fix critical issues (1-4) before any new features
4. Implement architecture improvements (5-6)
5. Add observability (7-10)

## Benefits of This Approach

- **Reproducibility:** Git history = experiment history
- **Comparison:** `git diff` to compare experiments
- **Simplicity:** No separate state backend needed
- **Collaboration:** PRs for infrastructure changes
- **Clarity:** Clear separation of concerns

## Questions for Discussion

1. Pipeline syntax preferences?
2. Remote state needed for any use cases?
3. State file size limits?
4. Testing strategy for fixes?
