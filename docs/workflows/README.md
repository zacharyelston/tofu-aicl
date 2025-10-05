# Development Workflows

## Overview

This directory contains the disciplined development workflows for tofu-aicl. These workflows prevent AI-generated code sprawl and ensure every change is:

- **Small** - Single task, single purpose
- **Modular** - Independent, testable unit
- **Tested** - Verified locally before commit
- **Reviewed** - Improved through reflection
- **Delivered** - Tagged and released properly

## The Problem We're Solving

**AI Code Sprawl**: AI eagerly updates many files with erroneous pointers before anyone can review. By the time you notice the problem, dozens of files reference the broken code.

**The Solution**: Disciplined, single-task workflow with local testing gates.

## Core Principles

From [DevOpsZealot](https://github.com/zacharyelston/DevOpsZealot):

1. **Branch per task** - Isolate work
2. **Test locally first** - Know it works before commit
3. **Small commits** - Single purpose, easy to review
4. **Reflect before PR** - Think how to make it better
5. **CI validates what you already tested** - Immutable artifact proof
6. **Tags and releases matter** - Not decoration, actual lifecycle

## Workflows

### Development
- [Single Task Workflow](single-task-workflow.md) - One feature/fix at a time
- [Local Testing Gate](local-testing-gate.md) - Test before commit
- [Code Review Process](code-review-process.md) - Improve before PR

### Release Management
- [Tagging Strategy](tagging-strategy.md) - Semantic versioning with tags
- [Release Process](release-process.md) - From code to deployment
- [Changelog Management](changelog-management.md) - Track every change

### Quality Gates
- [Pre-Commit Checks](pre-commit-checks.md) - Automated quality gates
- [CI Pipeline](ci-pipeline.md) - Immutable artifact validation
- [Friday Demo Prep](friday-demo-prep.md) - Weekly artifact presentation

## Quick Start

```bash
# Start new task
git checkout main
git pull origin main
git checkout -b feature/task-123-short-description

# Work on single task
# ... code ...
# ... write test ...

# Test locally (REQUIRED)
python -m pytest tests/test_your_feature.py -v
# ALL tests must pass before proceeding

# Commit only when tests pass
git add specific/files/only
git commit -m "feat: add specific feature

- Single focused change
- Tests included and passing
- Documentation updated"

# Reflect and improve
# Review your own code
# Refactor if needed
# Add more tests

# Push and create PR only when satisfied
git push origin feature/task-123-short-description
# Create PR with clear description
# Link to design spec
# Show test results
```

## Weekly Rhythm

### Monday
- Review design specs
- Create task branches
- Start implementation

### Tuesday-Thursday
- Implement features
- Write tests
- Local validation
- Small commits

### Friday
- Demo completed artifacts
- Show working tests
- Discuss improvements
- Tag releases

## Anti-Patterns (Don't Do This)

❌ Commit without local tests passing
❌ Update multiple unrelated files in one commit
❌ Create PR before self-review
❌ Push code that "should work" untested
❌ Fix tests in CI instead of locally
❌ Rush to merge without reflection
❌ Skip tagging and changelog

## File Structure

```
workflows/
├── README.md                      # This file
├── single-task-workflow.md        # One task at a time
├── local-testing-gate.md          # Test before commit
├── code-review-process.md         # Self-review and improvement
├── tagging-strategy.md            # Semantic versioning
├── release-process.md             # Release lifecycle
├── changelog-management.md        # Track changes
├── pre-commit-checks.md           # Quality gates
├── ci-pipeline.md                 # Pipeline validation
└── friday-demo-prep.md            # Weekly presentations
```

## Success Metrics

- ✅ Every commit has passing tests
- ✅ Every PR is small and focused
- ✅ Every release is tagged properly
- ✅ Every Friday has artifacts to demo
- ✅ Zero "oops, broke main" incidents
- ✅ Clear changelog for every version