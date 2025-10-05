# Development Workflows - Quick Reference

## The Problem

**AI Code Sprawl**: AI eagerly updates many files with broken references before review. By the time you notice, the damage is done.

## The Solution

Disciplined, single-task workflow with mandatory local testing gates.

---

## Core Rules (Never Break These)

1. ✅ **One branch = One task** - No mixing features
2. ✅ **Test locally before commit** - No exceptions
3. ✅ **Small commits** - <5 files per commit
4. ✅ **Self-review before PR** - Think how to improve
5. ✅ **Tag every release** - Tags are lifecycle, not decoration
6. ✅ **Demo every Friday** - If you can't demo it, it's not done

---

## Daily Workflow (Cheat Sheet)

### Morning
```bash
git checkout main && git pull
git checkout -b feature/task-123-description
```

### Development Loop
```bash
# 1. Code ONE thing
vim file.py

# 2. Test IMMEDIATELY
vim test_file.py
python -m pytest test_file.py -v

# 3. If PASS → commit, if FAIL → fix
git add file.py test_file.py
git commit -m "feat: add specific thing"

# Repeat until feature complete
```

### Before Push
```bash
# Self-review checklist
# ✅ Code readable
# ✅ Tests pass locally
# ✅ Coverage >80%
# ✅ Documentation updated

# Push when satisfied
git push origin feature/task-123
gh pr create
```

---

## Friday Demo (3pm Every Week)

### What to Show (5-7 minutes)
1. **Context**: What you built and why
2. **Before**: The problem that existed
3. **Demo**: Show it working (live!)
4. **Tests**: Prove it's tested
5. **Impact**: What this unlocks
6. **Tag**: Version number

### Not Acceptable
- ❌ "I'm 90% done..."
- ❌ "It works on my machine..."
- ❌ "I was researching..."
- ❌ PowerPoint slides

---

## Tagging Releases

### When to Tag
```bash
# After merge to main
# After tests pass
# After version bumped

git tag -a v1.2.0 -m "Release v1.2.0: Feature name"
git push origin v1.2.0
```

### Version Format
```
v1.0.0 → v1.0.1  # Patch (bug fix)
v1.0.0 → v1.1.0  # Minor (new feature)
v1.0.0 → v2.0.0  # Major (breaking change)
```

---

## Emergency Checklists

### AI Updated Too Many Files?

```bash
# STOP. Assess damage
git status
git diff

# Stash everything
git stash

# Create focused branch
git checkout -b feature/just-one-thing

# Unstash and add ONLY related files
git stash pop
git add specific/file/only.py
git stash  # Re-stash the rest

# Commit focused change
git commit -m "feat: one specific thing"

# Repeat for other changes in separate branches
```

### Tests Failing in CI?

```bash
# Don't fix in CI. Fix locally.

# 1. Pull the branch
git checkout feature/failing-branch

# 2. Run tests locally
python -m pytest tests/ -v

# 3. Fix until ALL pass
# ... fix code ...

# 4. Commit fix
git commit -m "fix: resolve test failures"
git push

# CI will now pass (you already verified locally)
```

### Forgot to Tag Release?

```bash
# Find the commit that was the release
git log --oneline

# Tag it retroactively
git tag -a v1.2.0 <commit-hash> -m "Release v1.2.0"
git push origin v1.2.0
```

---

## File Structure

```
docs/workflows/
├── README.md                      # Overview
├── QUICK_REFERENCE.md            # This file
├── single-task-workflow.md       # One task at a time
├── local-testing-gate.md         # Test before commit
├── tagging-strategy.md           # Version and release tags
├── friday-demo-prep.md           # Weekly demos
└── complete-lifecycle.md         # Full workflow
```

---

## Success Metrics

### You're Doing It Right If:
- ✅ Every commit has passing tests
- ✅ Every PR is <5 files
- ✅ Every Friday has a demo
- ✅ Every release has a tag
- ✅ Zero "oops, broke main"
- ✅ CI never finds bugs (you already tested locally)

### Red Flags:
- 🚩 Committing without running tests
- 🚩 Branch open for >1 week
- 🚩 PR with >10 files changed
- 🚩 Skipping Friday demo
- 🚩 Releasing without tagging
- 🚩 "I'll fix the tests later"

---

## When to Read Full Docs

- **Starting new feature?** → Read [single-task-workflow.md](single-task-workflow.md)
- **About to commit?** → Read [local-testing-gate.md](local-testing-gate.md)
- **Ready to release?** → Read [tagging-strategy.md](tagging-strategy.md)
- **Thursday night?** → Read [friday-demo-prep.md](friday-demo-prep.md)
- **Lost/confused?** → Read [complete-lifecycle.md](complete-lifecycle.md)

---

## Philosophy

From [DevOpsZealot](https://github.com/zacharyelston/DevOpsZealot):

> Tags and releases are the software lifecycle. Not decoration.
>
> Work must be small, modular, simple, tested, and then presented.
>
> Imagine every Friday you have to present the artifacts you delivered.
>
> Before anyone can approve code, AI has anxiously run rampant updating many files with erroneous pointers.
>
> All work must be in a branch, single task, complete with test, run locally to verify, then committed.

---

**Remember**: If you can't demo it on Friday, it's not done.