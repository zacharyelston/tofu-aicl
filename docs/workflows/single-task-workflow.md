# Single Task Workflow

## Principle

**One branch = One task = One testable change**

Never mix multiple features, fixes, or refactors in a single branch. AI wants to "help" by updating everything at once. Resist this. Stay focused.

## The Workflow

### 1. Start from Clean Main

```bash
# Always start from latest main
git checkout main
git pull origin main

# Verify you're up to date
git log --oneline -5
```

### 2. Create Focused Branch

```bash
# Branch naming: type/ticket-short-description
git checkout -b feature/repl-123-js-bridge
git checkout -b fix/repl-124-timeout-handling
git checkout -b docs/repl-125-api-specification
git checkout -b refactor/repl-126-error-handling

# Types:
# - feature/  : New functionality
# - fix/      : Bug fix
# - docs/     : Documentation only
# - refactor/ : Code improvement, no behavior change
# - test/     : Test additions/improvements
# - chore/    : Maintenance (dependencies, config)
```

### 3. Define Success Criteria FIRST

Before writing any code, write down what "done" looks like:

```markdown
# Branch: feature/repl-123-js-bridge

## Goal
Implement JavaScript bridge to execute Node.js code from Python.

## Success Criteria
- [ ] JSBridge class can execute JavaScript code
- [ ] Returns parsed JSON results
- [ ] Handles errors gracefully
- [ ] Has timeout protection
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration test with simple init() call works
- [ ] Documentation in implementation/js-bridge.md

## Out of Scope (NOT in this branch)
- Extension resource implementation
- Authentication
- Retry logic (separate branch)
- Performance optimization
```

### 4. Work in Small Increments

```bash
# Create the file
touch providers/replit/js_bridge.py

# Write minimal implementation
# Add ONE method at a time
# Test that method

# Commit when ONE thing works
git add providers/replit/js_bridge.py
git commit -m "feat(replit): add JSBridge.execute() method

- Executes JavaScript via Node.js subprocess
- Parses JSON output
- Basic error handling
- Test: test_execute_simple_code PASSING"

# Continue with next method
# Commit when it works
# Repeat
```

### 5. Test Locally (MANDATORY GATE)

```bash
# Run tests for your specific feature
python -m pytest tests/providers/replit/test_js_bridge.py -v

# Expected output:
# test_execute_simple_code PASSED
# test_execute_with_error PASSED
# test_timeout_handling PASSED
# ===================== 3 passed in 0.52s =====================

# If ANY test fails:
# - Fix it NOW
# - Do NOT commit
# - Do NOT move forward
```

### 6. Self-Review Checklist

Before pushing, review your own code:

```markdown
## Code Quality
- [ ] Code is readable and well-commented
- [ ] No commented-out code left behind
- [ ] No debug print() statements
- [ ] No hardcoded values (use constants)
- [ ] Error messages are clear and helpful

## Testing
- [ ] All new code has tests
- [ ] All tests pass locally
- [ ] Edge cases covered
- [ ] Error conditions tested

## Documentation
- [ ] Docstrings on all public methods
- [ ] README or design doc updated
- [ ] Example usage provided if needed

## Integration
- [ ] No changes to unrelated files
- [ ] Imports are correct
- [ ] No new warnings or errors
```

### 7. Push Only When Satisfied

```bash
# Push your branch
git push origin feature/repl-123-js-bridge

# Create PR with clear description
# Use PR template (see code-review-process.md)
```

## What If AI Wants to Update Other Files?

### Scenario: AI Suggests Changes to 5 Files

```
AI: "I should update:
- providers/replit/provider.py (use new bridge)
- providers/replit/extension.py (use new bridge)
- tests/test_provider.py (test new bridge)
- README.md (document new bridge)
- provider_registry.py (register new bridge)"
```

### Your Response: STOP

```bash
# Current branch: feature/repl-123-js-bridge
# ONLY touch: providers/replit/js_bridge.py
#             tests/providers/replit/test_js_bridge.py
#             docs/designs/replit-provider/implementation/js-bridge.md

# For other changes, create NEW branches:
# - feature/repl-124-use-bridge-in-provider
# - feature/repl-125-update-docs
# - feature/repl-126-register-provider
```

**Why?**
1. Each change is testable independently
2. Reviews are focused
3. Rollback is surgical
4. CI failures are clear
5. Merge conflicts are minimal

## Commit Message Format

```
type(scope): short description

- Detailed point 1
- Detailed point 2
- Test status: ALL PASSING

[optional: link to design spec]
[optional: link to ticket]
```

**Examples:**

```
feat(replit): implement JavaScript bridge

- Add JSBridge class with execute() method
- Parse JSON from Node.js subprocess
- Handle timeouts and errors
- Test coverage: 85%
- Tests: 8/8 PASSING

Implements: docs/designs/replit-provider/implementation/js-bridge.md
```

```
fix(replit): handle JSON parse errors in bridge

- Catch JSONDecodeError from malformed output
- Return clear error message
- Add test case for invalid JSON
- Tests: 9/9 PASSING
```

```
test(replit): add edge cases for JS bridge

- Test empty output
- Test very large output (>1MB)
- Test concurrent executions
- Tests: 12/12 PASSING
```

## Branch Lifecycle

```
main
 │
 ├─ feature/repl-123-js-bridge (created)
 │   │
 │   ├─ Work → Test → Commit (small increment 1)
 │   ├─ Work → Test → Commit (small increment 2)
 │   ├─ Work → Test → Commit (small increment 3)
 │   │
 │   ├─ Self-review and improve
 │   │
 │   └─ Push → PR → Review → Merge
 │
 ├─ main (updated with js-bridge)
 │
 └─ feature/repl-124-use-bridge (new branch, new task)
```

## Red Flags

🚩 Branch has >10 changed files
🚩 Commit message says "and" multiple times
🚩 Tests weren't run before commit
🚩 PR description says "various fixes"
🚩 Can't explain what the branch does in one sentence
🚩 Branch open for >1 week

## Recovery from AI Sprawl

If AI already updated many files:

```bash
# 1. Assess damage
git status
git diff

# 2. Stash unrelated changes
git stash

# 3. Create separate branches
git checkout -b feature/repl-123-js-bridge
git stash pop
# Carefully add ONLY js_bridge.py changes
git add providers/replit/js_bridge.py tests/providers/replit/test_js_bridge.py
git stash  # Re-stash everything else

# 4. Commit focused change
git commit -m "feat(replit): implement JavaScript bridge"

# 5. Repeat for other changes
git checkout main
git checkout -b feature/repl-124-update-provider
git stash pop
# Add ONLY provider.py changes
# etc.
```

## Success Metrics

- Branch lifespan: <3 days
- Files changed: <5 files
- Lines changed: <300 lines
- Commits: 1-5 commits
- Test coverage: >80%
- Time to review: <30 minutes