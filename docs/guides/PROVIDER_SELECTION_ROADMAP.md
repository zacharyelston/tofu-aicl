# Provider Selection Architecture Roadmap

## Current State (October 11, 2025)

### Problem
The executor uses a hardcoded `resource_to_provider` mapping that ignores the Terraform `required_providers` block:

```python
self.resource_to_provider = {
    'embedding': 'openai',
    'chat': 'openrouter',  # <-- Hardcoded!
    'query': 'pinecone',
}
```

This prevents multiple providers from handling the same resource types (e.g., both OpenRouter and Naga.ai for chat).

### Current Workaround
Use provider-prefixed resource types:
- `naga_chat` → routes to naga provider
- `chat` → routes to openrouter provider

## Architect Analysis (October 11, 2025)

### Root Cause
Provider selection is hardcoded in executor, ignoring which providers are actually declared in the configuration's `terraform.required_providers` block.

### Recommended Solution

**1. Configuration-Driven Provider Selection**
- Parse `required_providers` block to determine available providers
- Support explicit provider assignment per resource (like Terraform's `provider = aws.west`)
- Fall back to smart inference only when not explicitly specified

**2. Implementation Plan**

#### Phase 1: Parser Enhancement
- Update HCL parser to capture `required_providers` declarations
- Extract provider aliases and mappings
- Pass provider metadata to planner

#### Phase 2: Planner Enhancement
```python
# Attach provider to each resource during planning
resource_plan = {
    'type': 'chat',
    'name': 'answer',
    'provider': 'naga',  # <-- Resolved from config
    'config': {...}
}
```

#### Phase 3: Executor Refactoring
```python
# Use resolved provider from plan
provider_name = resource_plan.get('provider')
if not provider_name:
    # Fallback to legacy mapping
    provider_name = self.resource_to_provider.get(res_type)
```

#### Phase 4: Validation
- Validate provider supports requested resource type (via schema)
- Surface misconfigurations during planning (before execution)
- Use provider registry metadata for capability checks

### Benefits
✅ **Multi-provider support**: OpenRouter and Naga can both handle chat  
✅ **Config-driven**: Respects Terraform semantics  
✅ **Backward compatible**: Falls back to legacy mapping  
✅ **Early validation**: Catches errors before execution  

## Example: Future Syntax

```hcl
terraform {
  required_providers {
    openrouter = {
      source = "aicl/openrouter"
    }
    naga = {
      source = "aicl/naga"
    }
  }
}

# Explicit provider assignment (Terraform-style)
resource "chat" "expensive_query" {
  provider = openrouter  # <-- Explicit
  model = "anthropic/claude-3.5-sonnet"
  ...
}

resource "chat" "cheap_query" {
  provider = naga  # <-- Explicit
  model = "openai/gpt-4o-mini"
  ...
}

# Or implicit (uses first matching provider from required_providers)
resource "chat" "auto" {
  model = "openai/gpt-4o"
  # Will use 'openrouter' or 'naga' based on declaration order
  ...
}
```

## Implementation Tasks

### High Priority
- [ ] Update parser to extract `required_providers` and provider assignments
- [ ] Modify planner to resolve provider for each resource
- [ ] Refactor executor to use resolved provider (with fallback)

### Medium Priority  
- [ ] Add provider capability validation (via schema/registry)
- [ ] Support provider aliases (`naga = { source = "aicl/naga", alias = "fast" }`)
- [ ] Improve error messages for provider mismatches

### Low Priority
- [ ] Provider dependency resolution (if provider A needs provider B)
- [ ] Dynamic provider selection based on cost/performance policies

## Timeline
- **Phase 1-2**: 2-3 days (Parser + Planner)
- **Phase 3**: 1 day (Executor refactoring)
- **Phase 4**: 1 day (Validation + testing)
- **Total**: ~1 week for complete implementation

## Related Files
- `src/aicl/parser.py` - HCL parsing
- `src/aicl/planner.py` - Resource planning and dependencies
- `src/aicl/executor.py` - Resource execution (needs provider resolution)
- `src/aicl/core/engine.py` - Provider lifecycle management
- `src/aicl/provider_registry.py` - Provider metadata

---
*Architecture analysis provided by Architect Agent - October 11, 2025*
