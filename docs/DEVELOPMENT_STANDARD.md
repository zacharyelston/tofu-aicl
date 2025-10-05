# tofu-aicl Development Standard
## Operationalized AI-Assisted Development Process

**Version**: 1.0
**Last Updated**: October 5, 2025
**Based On**: `/Users/zacelston/code/memories/ai_development_ruleset.md`

---

## Quick Start

Before starting ANY new feature or provider:
1. Create project wiki page in `docs/` with research
2. Create issues in `docs/issues.yaml` or project management tool
3. **Write complete design specification** (see template below)
4. Get design spec approved
5. Only then begin coding

---

## Project-Specific Configuration

```yaml
# Configuration for tofu-aicl project
PROJECT_WIKI_TOOL: docs/ directory in repository
ISSUE_TRACKER: docs/issues.yaml + GitHub Issues
DIAGRAM_TOOL: Mermaid (embedded in markdown)
AI_CONTEXT_SYSTEM: MCP + Claude Desktop
CODE_LOCATION: /Users/zacelston/code/tofu-aicl
DESIGN_SPECS_LOCATION: /Users/zacelston/code/tofu-aicl/docs/designs/
```

---

## Example: Replit Provider Implementation

### Phase 1: Research (Status: IN PROGRESS)

**Location**: `/Users/zacelston/code/tofu-aicl/APIDocs/`

**Research Completed**:
- ✅ Init API documented (`01-init-api.md`)
- ✅ Auth API documented (`02-auth-api.md`)
- ✅ Data API documented (`03-data-api.md`)

**Research Pending**:
- [ ] UI Extension API
- [ ] Commands API
- [ ] File System API
- [ ] Themes API

**Decision**: Build Replit provider for tofu-aicl to enable:
- Workspace context awareness
- Authentication and user management
- File access and manipulation
- Integration with Replit workspace

### Phase 2: Skeletal Planning

**Issues to Create** (in `docs/issues.yaml`):

```yaml
- id: REPL-001
  title: "Implement Replit Provider - Init API"
  type: provider
  status: planned
  acceptance_criteria:
    - Provider registers with engine
    - Handshake with Replit workspace successful
    - Cleanup/dispose function works
    - Resource type: replit_extension
  dependencies: []

- id: REPL-002
  title: "Implement Replit Provider - Auth API"
  type: provider
  status: planned
  acceptance_criteria:
    - JWT token generation works
    - Token verification works
    - Resource type: replit_authenticated_session
  dependencies: [REPL-001]

- id: REPL-003
  title: "Implement Replit Provider - Data API"
  type: provider
  status: planned
  acceptance_criteria:
    - Can fetch current user data
    - Can fetch current repl data
    - Data sources for workspace context
  dependencies: [REPL-001]

- id: REPL-004
  title: "Integration Tests - Replit Provider"
  type: test
  status: planned
  acceptance_criteria:
    - End-to-end test with real Replit workspace
    - All resource types validated
  dependencies: [REPL-001, REPL-002, REPL-003]
```

### Phase 3: Design Specification (CRITICAL GATE)

**File**: `/Users/zacelston/code/tofu-aicl/docs/designs/replit-provider-spec.md`

This MUST be created using the design specification template before ANY code is written.

**Required Sections for Replit Provider**:

1. **Design Statements**
   - The Replit provider SHALL implement gRPC provider interface
   - The provider SHALL support three resource types: extension, auth_session, workspace_data
   - The provider SHALL handle Replit API communication via JavaScript bridge
   - etc.

2. **API Specifications**
   - Complete function signatures for all provider methods
   - Resource schemas (extension config, auth tokens, workspace data)
   - Error conditions and handling

3. **Data Models**
   ```python
   # Example from design spec
   class ReplitExtension:
       id: str
       name: str
       handshake_status: HandshakeStatus
       dispose_function: Callable
   ```

4. **Architecture Diagrams**
   - Provider architecture (Python provider ↔ JavaScript Replit API)
   - Resource lifecycle
   - Data flow diagrams

5. **Wireframes** (N/A for backend provider)

6. **Workflow Examples**
   - Initialize extension workflow
   - Authenticate user workflow
   - Fetch workspace data workflow

7. **POC Validation Results**
   - POC: Can Python subprocess communicate with Replit JavaScript API?
   - POC: Can we extract user/workspace data reliably?
   - Results and implications

8. **Amendments Log** (starts empty)

**Status**: ⛔ NOT CREATED - BLOCKING ALL IMPLEMENTATION

---

## Daily Development Workflow

### Morning Standup (5 min)
```bash
# Review yesterday's work
git log --oneline --since="yesterday" --author="$(git config user.name)"

# Check design compliance
ls docs/designs/  # Verify design specs exist

# Review deviation log
cat docs/deviations/$(date +%Y-%m-%d).md 2>/dev/null || echo "No deviations logged"
```

### During Development

**Before writing ANY function**:
1. Open relevant design specification
2. Find the function signature in the spec
3. Implement EXACTLY as specified
4. If deviation needed → document immediately

**AI Usage Pattern**:
```bash
# Load design spec into AI context
cat docs/designs/replit-provider-spec.md

# Ask AI to validate implementation against spec
"Does this implementation match the design specification for
the init_extension() function? Highlight any deviations."
```

### End of Day Review (15 min)

Create daily compliance report:

```bash
# File: docs/compliance/2025-10-05.md
# Implementation Compliance - 2025-10-05

## Metrics
- Functions implemented: 3/12 (25%)
- API contracts honored: 3/3 (100%)
- Deviations discovered: 1

## Deviations
1. Added `timeout` parameter to init_extension()
   - **Reason**: Replit handshake can be slow, needed timeout control
   - **Status**: Amendment proposed in REPL-001-amendment-001.md
   - **Decision**: Pending review

## Tomorrow's Target
- Implement authenticate_user() per spec section 2.2
- Review and approve timeout amendment
```

---

## Project Structure for Design Docs

```
/Users/zacelston/code/tofu-aicl/
├── docs/
│   ├── designs/               # Design specifications (Phase 3 artifacts)
│   │   ├── replit-provider-spec.md
│   │   ├── improved-rag-pipeline-spec.md
│   │   └── template.md        # Copy of design spec template
│   ├── compliance/            # Daily compliance reports
│   │   ├── 2025-10-05.md
│   │   └── 2025-10-06.md
│   ├── deviations/            # Deviation logs
│   │   └── REPL-001-amendment-001.md
│   ├── pocs/                  # POC test results
│   │   ├── replit-js-bridge-poc.py
│   │   └── replit-js-bridge-results.md
│   └── issues.yaml            # Issue tracking
├── APIDocs/                   # Research phase artifacts
└── providers/                 # Implementation (only after design approved)
    └── replit/
        ├── __init__.py
        ├── provider.py        # Implements design spec
        └── test_provider.py   # Validates against spec
```

---

## Amendment Process for tofu-aicl

When implementation reveals design issues:

```markdown
# File: docs/deviations/REPL-001-amendment-001.md

## Amendment Request

**Issue**: REPL-001
**Date**: 2025-10-05
**Proposed By**: Zac Elston

### Deviation Discovered
The `init_extension()` function in the design spec does not include a timeout parameter.

### Reason for Deviation
During POC testing, we discovered that the Replit handshake can take 5-10 seconds
on slow connections. Without a timeout, the function can hang indefinitely.

### Proposed Amendment
Add optional `timeout` parameter to `init_extension()`:

**Current Spec**:
```python
def init_extension(name: str, version: str) -> ReplitExtension:
```

**Proposed Spec**:
```python
def init_extension(
    name: str,
    version: str,
    timeout: int = 5000  # milliseconds
) -> ReplitExtension:
```

### Impact Analysis
- **Breaking Change**: No (optional parameter with default)
- **Test Updates**: Add timeout test cases
- **Documentation**: Update API reference

### Review Status
- [ ] Technical Lead Review
- [ ] Team Discussion
- [ ] Approved / Rejected

### Decision
[To be filled after review]

---
If APPROVED:
1. Update docs/designs/replit-provider-spec.md
2. Log in amendments section
3. Proceed with implementation
```

---

## Provider Development Checklist

Use this for every new provider (Replit, improved RAG, etc.):

### Phase 1: Research
- [ ] Create research wiki page in `docs/`
- [ ] Document API capabilities
- [ ] Identify alternatives considered
- [ ] List assumptions and constraints
- [ ] Define success criteria

### Phase 2: Skeleton
- [ ] Create issues in `docs/issues.yaml`
- [ ] Add acceptance criteria to each issue
- [ ] Identify dependencies
- [ ] Link issues to research wiki

### Phase 3: Design (THE GATE)
- [ ] Create design spec from template in `docs/designs/`
- [ ] Write complete API specifications
- [ ] Create data models
- [ ] Draw architecture diagrams (Mermaid)
- [ ] Document workflow examples
- [ ] Build POC tests for risky assumptions
- [ ] Get design spec reviewed and approved
- [ ] ⛔ **DO NOT PROCEED UNTIL APPROVED**

### Phase 4: Standards
- [ ] Review project coding standards (`CONTRIBUTING.md`)
- [ ] Configure linters for Python (black, ruff)
- [ ] Generate test cases from spec
- [ ] Set up AI validation

### Phase 5: Implementation
- [ ] Daily: Load design spec into AI context
- [ ] Daily: Implement per spec
- [ ] Daily: Log deviations
- [ ] Daily: Generate compliance report
- [ ] Weekly: Demo working features
- [ ] Weekly: Update wiki with progress

---

## Replit Provider: Next Actions

Based on where we are now:

### Immediate (This Week)
1. **Complete Research Phase**
   - [ ] Document remaining Replit APIs (UI, Commands, FS, Themes)
   - [ ] Create decision document on which APIs to implement first

2. **Create Design Specification**
   - [ ] Copy template to `docs/designs/replit-provider-spec.md`
   - [ ] Fill in complete API specifications
   - [ ] Create architecture diagrams
   - [ ] Write POC tests for JavaScript bridge communication
   - [ ] Get design spec approved

3. **POC Validation** (parallel with design)
   - [ ] Test: Can Python subprocess call Replit JavaScript APIs?
   - [ ] Test: Can we reliably get workspace context?
   - [ ] Test: Does authentication work in Replit environment?
   - [ ] Document results in `docs/pocs/`

### Following Week (After Design Approved)
4. **Implementation**
   - [ ] Implement init API per spec
   - [ ] Daily compliance reviews
   - [ ] Track deviations

5. **Demo & Release**
   - [ ] Working Replit provider demo
   - [ ] Updated documentation
   - [ ] Release notes

---

## Integration with Existing tofu-aicl Patterns

### Provider Registry
When implementing Replit provider, add to `provider_registry.py`:

```python
PROVIDER_REGISTRY = {
    # ... existing providers ...
    "replit": {
        "image": None,  # No container in subprocess mode
        "version": "1.0.0",
        "source": "providers/replit/provider.py",
        "description": "Replit workspace integration",
        "resource_types": [
            "replit_extension",
            "replit_authenticated_session",
            "replit_workspace_data"
        ]
    }
}
```

### Example .aicl Usage

After provider is built, usage should look like:

```hcl
# File: replit_integration.aicl

# Get current workspace context
data "replit_workspace_data" "current" {
  include_files = true
  include_user = true
}

# Authenticate user
resource "replit_authenticated_session" "user" {
  required_permissions = ["read", "write"]
}

# Use context in AI workflow
resource "openrouter_chat" "code_review" {
  model = "anthropic/claude-3.5-sonnet"

  messages = [
    {
      role = "user"
      content = "Review the code in workspace '${data.replit_workspace_data.current.title}'"
    }
  ]

  context = {
    workspace_language = data.replit_workspace_data.current.language
    file_count = data.replit_workspace_data.current.file_count
    authenticated_user = resource.replit_authenticated_session.user.username
  }
}
```

---

## Quality Gates for tofu-aicl

### Phase 1 → 2
```bash
# Check: Research complete?
[ -f docs/APIDocs/01-init-api.md ] &&
[ -f docs/APIDocs/02-auth-api.md ] &&
[ -f docs/APIDocs/03-data-api.md ]
```

### Phase 2 → 3
```bash
# Check: Issues created with acceptance criteria?
grep -q "acceptance_criteria" docs/issues.yaml
```

### Phase 3 → 4 (CRITICAL)
```bash
# Check: Design spec exists and is complete?
[ -f docs/designs/replit-provider-spec.md ] &&
grep -q "## 1. Design Statements" docs/designs/replit-provider-spec.md &&
grep -q "## 2. API Specifications" docs/designs/replit-provider-spec.md &&
grep -q "## 7. POC Validation Results" docs/designs/replit-provider-spec.md &&
grep -q "Status: APPROVED" docs/designs/replit-provider-spec.md
```

### Phase 4 → 5
```bash
# Check: Standards configured?
[ -f .ruff.toml ] &&
[ -f pyproject.toml ]
```

### Week → Week
```bash
# Check: Compliance reports current?
[ -f docs/compliance/$(date +%Y-%m-%d).md ]
```

---

## Red Flags for tofu-aicl 🚩

Watch for these in code reviews:

- **Provider implementation without design spec** ❌
- **New resource types not documented in design** ❌
- **Deviations from spec not logged** ❌
- **POC tests skipped because "it should work"** ❌
- **Direct implementation of Replit APIs without researching alternatives** ❌
- **More than 20% deviation rate from design spec** ❌

---

## Success Metrics

Track these in weekly retrospectives:

```yaml
# File: docs/retrospectives/2025-W41.md

week: 41
project: tofu-aicl
feature: Replit Provider

metrics:
  spec_completeness: 100%  # Design spec complete before coding
  poc_success_rate: 2/3    # 2 out of 3 POC tests validated assumptions
  deviation_rate: 5%       # Only 1 deviation in 20 functions
  amendments_approved: 1/1 # All justified deviations approved

lessons_learned:
  - JavaScript bridge POC saved us from bad architecture
  - Design spec caught missing error conditions early
  - Amendment process worked well for timeout parameter

improvements:
  - Need more detailed POC tests for edge cases
  - Should validate design spec with actual Replit docs earlier
```

---

## Getting Started: Your First Provider

Follow this exact sequence:

1. **Create Research Wiki** (30 min)
   ```bash
   cp docs/BOOTSTRAP_INSTRUCTIONS.md docs/my-provider-research.md
   # Edit with your research
   ```

2. **Create Issues** (15 min)
   ```bash
   # Add to docs/issues.yaml
   ```

3. **Write Design Spec** (2-4 hours)
   ```bash
   cp docs/designs/template.md docs/designs/my-provider-spec.md
   # Fill in COMPLETELY
   ```

4. **Build POC Tests** (1-2 hours)
   ```bash
   mkdir -p docs/pocs/
   # Create minimal tests
   ```

5. **Get Approval** (async)
   ```bash
   # Share design spec for review
   # Do NOT proceed until approved
   ```

6. **Implement** (days/weeks)
   ```bash
   # Now you can code
   # Follow design spec EXACTLY
   # Log deviations immediately
   ```

---

## Remember

> "The design specification IS the contract"

- Complete specs = Fewer surprises
- POC tests = Validated assumptions
- Daily reviews = Course correction
- Amendments = Learning captured
- AI validation = Mechanical compliance

**The goal**: Build the Replit provider (and all future providers) with zero architectural surprises because we researched, designed, and validated before writing a single line of implementation code.

---

**Next Step for Replit Provider**: Create `docs/designs/replit-provider-spec.md` using the template from `/Users/zacelston/code/memories/design_specification_template.md`