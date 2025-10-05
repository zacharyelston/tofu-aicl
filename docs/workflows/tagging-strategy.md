# Tagging Strategy

## Principle

**Tags are not decoration. They are immutable markers of software lifecycle.**

Every release gets a semantic version tag. Every tag represents a tested, reviewable, deployable artifact.

## Semantic Versioning

Format: `vMAJOR.MINOR.PATCH`

```
v1.0.0 → v1.0.1 → v1.1.0 → v2.0.0
```

### Version Increments

**MAJOR (v1.0.0 → v2.0.0)**
- Breaking API changes
- Incompatible with previous version
- Requires user migration

**MINOR (v1.0.0 → v1.1.0)**
- New features
- Backward compatible
- No breaking changes

**PATCH (v1.0.0 → v1.0.1)**
- Bug fixes
- Security patches
- No new features

## Tagging Workflow

### 1. Prepare Release

```bash
# Ensure you're on main with latest changes
git checkout main
git pull origin main

# Verify all tests pass
python -m pytest tests/ -v

# Verify code quality
# All PRs merged
# All issues closed
# Changelog updated
```

### 2. Update Version Numbers

```python
# pyproject.toml or setup.py
version = "1.2.0"

# __init__.py
__version__ = "1.2.0"
```

### 3. Update Changelog

```markdown
# CHANGELOG.md

## [1.2.0] - 2025-10-05

### Added
- Replit provider with JavaScript bridge (#123)
- Workspace data source (#124)
- Authentication session resource (#125)

### Changed
- Improved error handling in provider base (#126)

### Fixed
- Timeout handling in gRPC server (#127)

### Security
- Token hashing for secure logging (#128)
```

### 4. Commit Version Bump

```bash
git add pyproject.toml __init__.py CHANGELOG.md
git commit -m "chore: bump version to 1.2.0

- Update version in pyproject.toml
- Update __init__.__version__
- Update CHANGELOG.md with release notes"

git push origin main
```

### 5. Create Tag

```bash
# Create annotated tag (preferred)
git tag -a v1.2.0 -m "Release v1.2.0: Replit Provider

Major features:
- Replit provider implementation
- JavaScript bridge for Node.js integration
- Workspace data access
- User authentication

See CHANGELOG.md for full details."

# Push tag to remote
git push origin v1.2.0
```

### 6. Verify Tag

```bash
# List tags
git tag -l

# Show tag details
git show v1.2.0

# Verify on GitHub
# Tags should appear in:
# - https://github.com/{org}/{repo}/tags
# - https://github.com/{org}/{repo}/releases
```

## Tag Naming Conventions

### Release Tags
```
v1.0.0          # Official release
v1.1.0-alpha    # Alpha release
v1.1.0-beta     # Beta release
v1.1.0-rc.1     # Release candidate
```

### Provider-Specific Tags
```
v1.0.0-replit           # Replit provider release
v1.0.0-openrouter       # OpenRouter provider release
v2.0.0-breaking-api     # Breaking change release
```

### Hotfix Tags
```
v1.0.1-hotfix.1         # Emergency hotfix
v1.0.1-security         # Security patch
```

## Automated Tagging (GitHub Actions)

```yaml
# .github/workflows/tag-release.yml
name: Tag Release

on:
  push:
    branches:
      - main
    paths:
      - 'pyproject.toml'

jobs:
  tag:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Extract version
        id: version
        run: |
          VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
          echo "version=v$VERSION" >> $GITHUB_OUTPUT

      - name: Create tag
        run: |
          git tag -a ${{ steps.version.outputs.version }} -m "Release ${{ steps.version.outputs.version }}"
          git push origin ${{ steps.version.outputs.version }}
```

## Tag Lifecycle

```
Development → Testing → Release Candidate → Release → Tag
                                                        ↓
                                                    v1.2.0
                                                        ↓
                                              Immutable Artifact
```

## GitHub Release from Tag

After tagging, create GitHub release:

```bash
# Using GitHub CLI
gh release create v1.2.0 \
  --title "Release v1.2.0: Replit Provider" \
  --notes-file RELEASE_NOTES.md \
  --latest

# Or manually via GitHub UI
# 1. Go to Releases
# 2. Draft new release
# 3. Choose tag: v1.2.0
# 4. Add release notes
# 5. Publish release
```

## Release Notes Template

```markdown
# Release v1.2.0: Replit Provider

## 🎉 Highlights

- Complete Replit provider implementation
- JavaScript bridge for seamless Node.js integration
- Workspace data access for AI context

## ✨ New Features

- **Replit Extension Resource** (#123)
  - Initialize and manage Replit extensions
  - Automatic handshake and cleanup

- **Authentication Session** (#125)
  - JWT token management
  - Secure token hashing for logs

- **Workspace Data Source** (#124)
  - Read workspace metadata
  - File list access
  - User information

## 🔧 Improvements

- Enhanced error handling across all providers
- Improved retry logic with exponential backoff
- Better logging and observability

## 🐛 Bug Fixes

- Fixed timeout handling in gRPC server (#127)
- Corrected JSON parsing edge cases (#129)

## 🔒 Security

- Token hashing prevents plain text logging (#128)
- Input validation on all configuration parameters

## 📚 Documentation

- Complete design specification in docs/designs/replit-provider/
- POC validation results included
- Implementation guide with examples

## 🧪 Testing

- 47 new tests added
- 92% code coverage
- All tests passing ✅

## 📦 Installation

\`\`\`bash
pip install tofu-aicl==1.2.0
\`\`\`

## 🔗 Links

- [Full Changelog](CHANGELOG.md)
- [Design Spec](docs/designs/replit-provider/)
- [Documentation](docs/)

---

**Full Changelog**: v1.1.0...v1.2.0
```

## Tag Protection

Enable tag protection on GitHub:

1. Settings → Tags → Protected tags
2. Add rule: `v*`
3. Requirements:
   - ✅ Require signed commits
   - ✅ Restrict tag creation to maintainers
   - ✅ No force push
   - ✅ No deletion

## Viewing Release History

```bash
# List all tags chronologically
git tag -l --sort=-version:refname

# Show tags with dates
git log --tags --simplify-by-decoration --pretty="format:%ai %d"

# Compare tags
git diff v1.1.0 v1.2.0

# Checkout specific version
git checkout v1.2.0
```

## Rollback Strategy

If release v1.2.0 is broken:

```bash
# Create hotfix from previous stable tag
git checkout v1.1.0
git checkout -b hotfix/critical-fix

# Fix the issue
# ... code changes ...
# ... tests ...

# Commit and push
git commit -m "fix: critical issue from v1.2.0"
git push origin hotfix/critical-fix

# Merge to main
# Tag new version
git tag -a v1.2.1 -m "Hotfix for v1.2.0 critical issue"
git push origin v1.2.1

# Optionally mark v1.2.0 as yanked in releases
```

## Success Metrics

- ✅ Every release has a tag
- ✅ Tag messages are descriptive
- ✅ Changelog matches tagged version
- ✅ Tags are immutable (never deleted/modified)
- ✅ Release notes are complete
- ✅ All tagged versions are tested
- ✅ Version numbers follow semantic versioning