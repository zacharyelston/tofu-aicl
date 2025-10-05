# Contributing to tofu-aicl

## Commit Messages

All commit messages **MUST** follow the [Conventional Commits 1.0.0](https://conventionalcommits.org/) specification.

**Format:**
```
type[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

The commit type **MUST** be one of the following:

| Type | Description |
|------|-------------|
| **feat** | A new feature |
| **fix** | A bug fix |
| **docs** | Documentation only changes |
| **style** | Changes that do not affect the meaning of the code |
| **refactor** | A code change that neither fixes a bug nor adds a feature |
| **test** | Adding missing tests or correcting existing tests |
| **chore** | Changes to the build process or auxiliary tools |
| **ci** | Changes to our CI configuration files and scripts |
| **build** | Changes that affect the build system |
| **perf** | A code change that improves performance |
| **revert** | Reverts a previous commit |

### Examples

**Simple commits:**
```
feat: add dependency resolution for HCL interpolations
fix: correct executor import for ResourceState
docs: update bootstrap instructions
```

**With scope:**
```
feat(executor): add HCL interpolation parsing
fix(planner): strip ${} wrapper from dependencies
refactor(state): use exact type+name matching
```

**With breaking change:**
```
feat!: change service connection naming convention
feat(api)!: update provider protocol to v2

BREAKING CHANGE: service connections now use project-specific names
```

## Git Hooks

This repository includes git hooks that automatically validate commit message format:

- **`commit-msg` hook**: Validates commit message format (Conventional Commits 1.0.0)
- **`pre-commit` hook**: Checks Python syntax and trailing whitespace

### Setup Git Hooks

```bash
# Configure git to use .githooks directory
git config core.hooksPath .githooks

# Make hooks executable
chmod +x .githooks/*
```

### Skip Validation

**To skip validation for a specific commit:**
Add `skip validation` anywhere in your commit message.

**To bypass hooks temporarily:**
```bash
git commit --no-verify -m "your message"
```

## Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Test locally:**
   ```bash
   # Build provider containers
   ./scripts/build_providers.sh

   # Run tests
   PYTHONPATH=./src python3 run.py file_loader_test.aicl
   ```

4. **Commit with conventional commits:**
   ```bash
   git add .
   git commit -m "feat(provider): add new provider functionality"
   ```

5. **Push and create PR:**
   ```bash
   git push -u origin feature/your-feature-name
   ```

## Code Quality

- Follow PEP 8 for Python code
- Add type hints where appropriate
- Write docstrings for public functions
- Keep functions focused and small
- Avoid duplicate code

## Testing

- Test provider containers independently
- Verify dependency resolution works
- Check state management
- Validate HCL parsing

## Documentation

- Update README.md for user-facing changes
- Add ADRs for architectural decisions
- Document new providers in `docs/providers/`
- Keep CHANGELOG.md updated

## Pull Request Process

1. Ensure all tests pass locally
2. Update documentation as needed
3. Follow conventional commit format
4. Link to relevant Redmine issues
5. Request review from team members
6. Address review feedback
7. Squash commits if needed
8. Merge after approval

---

**Questions?** Check the [Design Review](docs/DESIGN_REVIEW_2025-10-04.md) or ask in the team channel.