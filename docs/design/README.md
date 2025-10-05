# Design Review: State-as-DNA Architecture

**Branch:** `design/state-as-dna`  
**Date:** 2025-10-05  
**Status:** Proposed

## Overview

This design review proposes a fundamental shift in how tofu-aicl handles state management, treating state as a comprehensive "DNA" - a flattened, complete record of the entire system lifecycle.

## Key Concepts

1. **State as DNA**: State is not just current inventory, but a complete lineage of what happened
2. **Git-based State**: Primary state backend uses git for versioning, collaboration, and comparison
3. **Clear Separation**: Distinct models for provisioning, services, and execution
4. **Modular Architecture**: Small, focused components with clear responsibilities

## Navigation

### State Model
- [Core Concept](./state-model/core-concept.md) - The DNA analogy
- [Git Backend](./state-model/git-backend.md) - Using git for state
- [State Structure](./state-model/structure.md) - State file format
- [Lifecycle](./state-model/lifecycle.md) - State through different phases

### Architecture
- [Three Layers](./architecture/three-layers.md) - Infrastructure, Services, Execution
- [Resource vs Pipeline](./architecture/resource-vs-pipeline.md) - Clear separation
- [Provider Protocol](./architecture/provider-protocol.md) - Apply vs Execute
- [Use Cases](./architecture/use-cases.md) - Common patterns

### Critical Issues
- [01 - Dependency Resolution](./issues/01-dependency-resolution.md)
- [02 - HCL Parsing](./issues/02-hcl-parsing.md)
- [03 - State Management](./issues/03-state-management.md)
- [04 - Resource IDs](./issues/04-resource-ids.md)
- [05 - Provisioning vs Execution](./issues/05-provisioning-execution.md)
- [06 - Protocol Bloat](./issues/06-protocol-bloat.md)
- [07 - Execution History](./issues/07-execution-history.md)
- [08 - Validation](./issues/08-validation.md)
- [09 - Error Handling](./issues/09-error-handling.md)
- [10 - Testing Security](./issues/10-testing-security.md)

## Priority

**Week 1:** Fix issues 1-4 (critical path)  
**Week 2:** Address issues 5-6 (architecture)  
**Week 3:** Implement issues 7-10 (observability)
