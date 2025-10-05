# Complete Development Lifecycle

## The Full Picture

This is how a single feature moves from idea to production, following the disciplined DevOpsZealot principles.

## Week 1: Design → Implementation → Demo

### Monday: Planning

```bash
# 1. Review design spec
cat docs/designs/replit-provider/README.md

# 2. Create task branch
git checkout main
git pull origin main
git checkout -b feature/repl-123-js-bridge

# 3. Define success criteria
echo "## Success Criteria
- [ ] JSBridge executes JavaScript via Node.js
- [ ] Returns parsed JSON
- [ ] Handles errors and timeouts
- [ ] Tests pass (>80% coverage)
- [ ] Demo-able on Friday" > task.md
```

### Tuesday-Wednesday: Build

```bash
# Write code for ONE thing
touch providers/replit/js_bridge.py

# Write test IMMEDIATELY
touch tests/providers/replit/test_js_bridge.py

# Test locally (GATE)
python -m pytest tests/providers/replit/test_js_bridge.py -v
# ✅ ALL PASS → commit
# ❌ ANY FAIL → fix now

# Commit when ONE thing works
git add providers/replit/js_bridge.py tests/providers/replit/test_js_bridge.py
git commit -m "feat(replit): add JSBridge.execute() method

- Executes JavaScript via Node.js subprocess
- Parses JSON output
- Basic error handling
- Test: test_execute_simple_code PASSING"

# Repeat for next method
```

### Thursday: Polish & Review

```bash
# Self-review checklist
# - [ ] Code is readable
# - [ ] All tests pass
# - [ ] Coverage >80%
# - [ ] Documentation updated
# - [ ] No commented code
# - [ ] No debug prints

# Improve if needed
git add .
git commit -m "refactor(replit): improve error messages in JSBridge"

# Push when satisfied
git push origin feature/repl-123-js-bridge

# Create PR
gh pr create \
  --title "feat(replit): implement JavaScript bridge" \
  --body "Implements: docs/designs/replit-provider/implementation/js-bridge.md

## What
JavaScript bridge to execute Node.js code from Python

## Why
Enables Replit provider to call Extension APIs

## Tests
- 12 unit tests ✅
- 3 integration tests ✅
- Coverage: 89%

## Demo
Ready for Friday demo"
```

### Friday: Demo & Release

```bash
# 1. Merge PR after review
gh pr merge --squash

# 2. Update version
# Edit pyproject.toml: version = "1.2.0"
# Edit __init__.py: __version__ = "1.2.0"

# 3. Update changelog
cat >> CHANGELOG.md << 'EOF'

## [1.2.0] - 2025-10-05

### Added
- JavaScript bridge for Replit provider (#123)
EOF

# 4. Commit version bump
git add pyproject.toml __init__.py CHANGELOG.md
git commit -m "chore: bump version to 1.2.0"
git push origin main

# 5. Tag release
git tag -a v1.2.0 -m "Release v1.2.0: Replit JavaScript Bridge"
git push origin v1.2.0

# 6. Demo (3pm)
python demo/js_bridge_demo.py
```

## The Lifecycle Diagram

```
Monday          Tuesday         Wednesday       Thursday        Friday
───────────────────────────────────────────────────────────────────────

Design Spec  →  Code + Test  →  Code + Test  →  Review      →  Demo
                    ↓               ↓             ↓             ↓
                 Commit          Commit        Improve       Merge
                    ↓               ↓             ↓             ↓
                Test Local      Test Local     Push PR      Tag Release
                    ↓               ↓             ↓             ↓
                ✅ PASS         ✅ PASS        CI ✅         Present
```

## Anti-Pattern Timeline (Don't Do This)

```
Monday          Tuesday         Wednesday       Thursday        Friday
───────────────────────────────────────────────────────────────────────

Write Code  →  Keep Writing  →  More Code  →  Fix Tests  →  "Almost Done"
  ↓               ↓               ↓             ↓             ↓
Many Files    Many Files      Push          CI Fails      Push Again
  ↓               ↓               ↓             ↓             ↓
No Tests      No Tests        Create PR     Fix More      CI Fails
  ↓               ↓               ↓             ↓             ↓
❌ Sprawl     ❌ Sprawl       ❌ Review     ❌ Panic      ❌ No Demo
```

## Daily Workflow

### Morning Checklist
```bash
# Pull latest
git checkout main
git pull origin main

# Check your branch status
git checkout feature/your-branch
git rebase main  # Keep up to date

# Review today's goal
cat task.md
```

### Development Loop
```bash
# 1. Write code for ONE thing
vim providers/replit/js_bridge.py

# 2. Write test IMMEDIATELY
vim tests/providers/replit/test_js_bridge.py

# 3. Run test locally
python -m pytest tests/providers/replit/test_js_bridge.py::test_execute -v

# 4. If PASS → commit, if FAIL → fix
# Repeat steps 1-4 until feature complete
```

### Evening Checklist
```bash
# Run full test suite
python -m pytest tests/ -v

# Check coverage
python -m pytest tests/ --cov=providers/replit --cov-report=term-missing

# Self-review today's commits
git log --oneline -5
git diff HEAD~3  # Review last 3 commits

# Update task.md
# Mark completed items
# Note blockers
# Plan tomorrow
```

## CI/CD Pipeline Flow

```yaml
# When you push to feature branch
Push → GitHub Actions:
  1. Checkout code
  2. Setup Python
  3. Install dependencies
  4. Run tests (you already know these pass)
  5. Generate coverage report
  6. Post results to PR

# When PR is merged to main
Merge → GitHub Actions:
  1. Run tests again (validation)
  2. Build package
  3. Run security scan
  4. Update documentation
  5. Ready for tag

# When you create a tag
Tag → GitHub Actions:
  1. Run tests (final validation)
  2. Build release package
  3. Create GitHub release
  4. Publish to PyPI (if configured)
  5. Deploy to staging
  6. Notify team
```

## Branching Strategy

```
main (protected)
 │
 ├── feature/repl-123-js-bridge
 │   └── (your work, tested, ready to merge)
 │
 ├── feature/repl-124-extension-resource
 │   └── (next feature, depends on #123)
 │
 ├── fix/repl-125-timeout-bug
 │   └── (bug fix, can merge independently)
 │
 └── docs/repl-126-api-docs
     └── (documentation, low risk)
```

**Rules:**
- Only merge to main via PR
- PRs require:
  - ✅ All tests passing
  - ✅ Code review approved
  - ✅ Coverage maintained
  - ✅ CI green
- main is always deployable
- Tags only from main

## Version Management

### Development Versions
```
main: 1.2.0-dev
feature branches: no version change
```

### Release Versions
```
1.0.0 → Initial release
1.0.1 → Bug fix
1.1.0 → New feature
2.0.0 → Breaking change
```

### Pre-Release Versions
```
1.2.0-alpha    → Early testing
1.2.0-beta     → Feature complete, testing
1.2.0-rc.1     → Release candidate
1.2.0          → Official release
```

## Quality Gates

### Gate 1: Local Tests (Before Commit)
```bash
python -m pytest tests/ -x  # Fast fail
# ✅ PASS → proceed
# ❌ FAIL → fix now
```

### Gate 2: Self Review (Before Push)
```markdown
- [ ] Code readable
- [ ] Tests comprehensive
- [ ] Documentation updated
- [ ] No debug code
```

### Gate 3: CI (After Push)
```yaml
- Run tests
- Check coverage
- Lint code
- Security scan
```

### Gate 4: Code Review (Before Merge)
```markdown
- [ ] Functionality correct
- [ ] Tests adequate
- [ ] Design patterns followed
- [ ] Documentation clear
```

### Gate 5: Integration (After Merge)
```yaml
- Run full test suite
- Integration tests
- Performance tests
- Build artifact
```

## Emergency Hotfix Process

```bash
# Critical bug in production (v1.2.0)

# 1. Branch from the tag
git checkout v1.2.0
git checkout -b hotfix/critical-auth-bug

# 2. Fix the bug
vim providers/replit/auth.py
vim tests/providers/replit/test_auth.py

# 3. Test locally
python -m pytest tests/providers/replit/test_auth.py -v
# ✅ Must pass

# 4. Commit
git commit -m "fix(replit): critical auth token validation bug

- Validate token format before use
- Add test for malformed tokens
- Security: prevents auth bypass

Fixes: #456"

# 5. Fast-track review
git push origin hotfix/critical-auth-bug
gh pr create --title "HOTFIX: Critical auth bug" --label "priority:critical"

# 6. After merge, tag immediately
git checkout main
git pull
git tag -a v1.2.1 -m "Hotfix v1.2.1: Critical auth bug"
git push origin v1.2.1

# 7. Deploy immediately
# 8. Notify users
```

## Success Metrics Dashboard

Track these weekly:

```markdown
## Week of Oct 1-5, 2025

### Delivery
- Features shipped: 3
- Bugs fixed: 2
- Tags created: 1 (v1.2.0)

### Quality
- Test coverage: 89% (+2%)
- Tests added: 15
- CI failures: 0
- Hotfixes: 0

### Process
- Avg PR size: 4 files
- Avg PR review time: 2 hours
- Friday demos: 100% (3/3)
- Branch lifespan: 2.1 days

### Code Health
- Lines added: 847
- Lines removed: 123
- Net documentation: +234 lines
- TODOs added: 0
```

## The Perfect Week

```
✅ Monday: Design reviewed, branch created, work started
✅ Tuesday: First feature working, tested, committed
✅ Wednesday: Second feature working, tested, committed
✅ Thursday: Polish, review, PR created
✅ Friday: PR merged, tagged v1.2.0, demo delivered

Result: 1 complete feature, tested, tagged, demoed
```

This is the standard. Repeat every week.