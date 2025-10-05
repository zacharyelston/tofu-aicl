# State as DNA: Git-Based State Backend Design

## Overview

This design document describes the "State as DNA" model for tofu-aicl, where state files serve as comprehensive reports of the complete lineage and current reality of AI infrastructure and pipelines.

## Core Concept

State is the "flattened view" of the entire process - the DNA unrolled. It contains:
- Complete lineage of all actions taken
- Current state of infrastructure
- Execution history and results
- Metadata for reproducibility

## Directory Structure

```
docs/design/state-as-dna/
├── README.md                    # This file
├── 01-core-model.md            # State as DNA core model
├── 02-git-backend.md           # Git-based state backend
├── 03-state-structure.md       # State file structure
├── 04-lifecycle.md             # State lifecycle phases
├── 05-remote-backend.md        # Optional remote backend (S3/DynamoDB)
├── 06-implementation.md        # Implementation approach
└── diagrams/                   # Architecture diagrams
    ├── state-lifecycle.mmd
    ├── state-separation.mmd
    └── git-workflow.mmd
```

## Key Files

- **01-core-model.md** - Explains the DNA metaphor and core concepts
- **02-git-backend.md** - Why git is perfect for tofu-aicl state
- **03-state-structure.md** - JSON structure with lineage + current state
- **04-lifecycle.md** - Recording → Complete → Reading → Destroying
- **05-remote-backend.md** - When to use S3/DynamoDB instead
- **06-implementation.md** - Code changes needed

## Design Principles

1. **State is append-only** - Lineage grows with each action
2. **State is self-describing** - Contains full history
3. **State is diffable** - Compare experiments via git diff
4. **State is reproducible** - Read state → recreate system
5. **Git is the default** - Remote backends are optional

## Next Steps

1. Review each module in order
2. Implement StateManager enhancements
3. Add lineage tracking
4. Test git-based workflows
