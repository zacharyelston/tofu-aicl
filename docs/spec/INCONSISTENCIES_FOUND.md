# Specification Inconsistencies Found

## Critical Issues

### 1. ❌ Point Total Mismatch

**Files Affected:** `00-architecture.md`, `README.md`, `TEST_CRITERIA.md`

**Problem:**
- `00-architecture.md` says **100 points total** (rubric)
- `README.md` says **165 points total** (sum of components)
- `TEST_CRITERIA.md` says **140 points** for automated tests

**Math:**
```
Config:        30
Logging:       20
Docker:        30
Local:         20
Run:           15
Output:        20
Entry:         30
--------------
Total:        165 points (matches README)
```

**Fix Required:** Update architecture to reflect 165 total, not 100.

---

### 2. ❌ File Size Limits Inconsistent

**Files Affected:** Multiple specs

**Problem:**
| File | Header Says | Success Criteria Says | Architecture Says |
|------|-------------|----------------------|-------------------|
| `config.py` | ~50 lines | < 60 lines | 50 lines |
| `logging_setup.py` | ~30 lines | < 35 lines | 30 lines |
| `docker.py` | ~70 lines | < 90 lines | 70 lines |
| `entry_point` | ~80 lines | < 120 lines | 80-100 lines |

**Fix Required:** Standardize limits in success criteria.

---

### 3. ❌ Missing `validate.py` Spec

**Files Affected:** `00-architecture.md`, Directory structure

**Problem:**
- Architecture shows `validate.py` (35 lines) in structure
- No `05-validate-command.md` spec file exists
- `05-run-command.md` only covers `run.py`
- Missing from grading (no points allocated)

**Fix Required:** Either:
1. Create `08-validate-command.md` spec, OR
2. Remove from architecture if not needed

---

### 4. ❌ Missing `state.py` Spec

**Files Affected:** `00-architecture.md`, Directory structure

**Problem:**
- Architecture shows `state.py` (60 lines) in structure
- No `state-commands.md` spec file exists
- Referenced in entry point spec but no detailed spec
- Missing from grading (no points allocated)

**Fix Required:** Create `09-state-commands.md` spec.

---

### 5. ⚠️ Docker Volume Mounts Inconsistency

**File:** `03-docker-runner.md`

**Problem:**
Spec mentions TWO automatic mounts:
1. State directory ✅ (implemented)
2. Experiments directory ❌ (mentioned but NOT in implementation)

```python
# Mentioned in spec (line 116-119)
2. **Experiments Directory** (read-write)
   - Host: `{settings.paths.experiments_dir}`
   - Container: `/app/experiments`

# But NOT in example implementation (line 278-280)
# Only state_dir is mounted
```

**Fix Required:** Either:
1. Add experiments_dir mount to implementation, OR
2. Remove from automatic mounts section

---

### 6. ⚠️ Test Point Math Wrong

**File:** `TEST_CRITERIA.md`

**Problem:**
```python
# Says:
Automated Tests (140 points * 0.7 = 98 points)

# But components add up to:
Config: 30 + Logging: 20 + Docker: 30 + Local: 20 + 
Commands: 15 + Output: 20 + Entry: 30 = 165 points

# Should be:
Automated Tests (165 points * 0.7 = 115.5 points)
```

**Fix Required:** Update formula to use 165, not 140.

---

### 7. ⚠️ Commands Point Allocation

**File:** `TEST_CRITERIA.md`

**Problem:**
```python
# Says:
Commands: 15  # Only for run.py

# But missing:
validate.py: ? points
state.py: ? points
```

If we have validate and state commands, need points allocated.

**Fix Required:** Either:
1. Allocate 15 points just for `run.py` (current), OR
2. Split points: run (15), validate (10), state (15) = 40 total

---

## Minor Issues

### 8. ℹ️ Typo in README

**File:** `README.md` line 14

**Current:** `05-run-command.md`  
**Issue:** Missing validate and state specs in table

**Fix:** Add missing rows or note they're combined.

---

### 9. ℹ️ Architecture vs Implementation

**File:** `00-architecture.md` line 103

**Problem:**
```
See: `/Users/zacelston/code/tofu-aicl/cli/`
```

This is a **local absolute path** - won't work for others.

**Fix:** Use relative path: `See: ../../cli/`

---

## Recommended Fixes

### Priority 1: Point Totals
```markdown
# 00-architecture.md (line 90)
- **Total:** 100 points
+ **Total:** 165 points

# TEST_CRITERIA.md (line 81)
- Automated Tests (140 points * 0.7 = 98 points)
+ Automated Tests (165 points * 0.7 = 115.5 points)
```

### Priority 2: File Size Limits
Standardize to "~X lines" in header matching max in success criteria.

### Priority 3: Missing Specs
Create or document:
- `08-validate-command.md` (if needed)
- `09-state-commands.md` (if needed)

### Priority 4: Docker Mounts
Either add experiments mount or remove from docs.

---

## Summary

| Issue | Severity | Impact | Fix Time |
|-------|----------|--------|----------|
| Point total mismatch | High | Grading wrong | 5 min |
| File size inconsistency | Medium | Confusion | 10 min |
| Missing validate spec | High | Incomplete | 20 min |
| Missing state spec | High | Incomplete | 20 min |
| Docker mounts | Low | Feature gap | 5 min |
| Test math | Medium | Grading wrong | 5 min |
| Commands points | Medium | Grading incomplete | 10 min |

**Total Fix Time:** ~75 minutes

---

## Action Plan

1. ✅ Document all inconsistencies (this file)
2. 🔄 Fix point totals (00-architecture, TEST_CRITERIA)
3. 🔄 Standardize file size limits
4. 🔄 Create missing specs (validate, state)
5. 🔄 Fix Docker mounts documentation
6. 🔄 Update test point math
7. ✅ Review and verify all fixes
