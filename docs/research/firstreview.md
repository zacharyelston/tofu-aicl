I'll carefully review the codebase at /Users/zacelston/code/tofu-aicl to understand the design and identify potential issues for better planning.

Let me start by exploring the directory structure to understand what we're working with.Good! Now let me read the key documentation files to understand the architecture and design principles:Let me continue reading the architecture and design documents:Now let me look at the ADR about dependency management and the core implementation files:Now let me look at the executor and example files to understand how resources are being executed:Let me look at one of the provider implementations to understand the protocol better:Now let me look at the state manager to understand state handling:Now let me check the parser to understand HCL handling:Let me also check the text_splitter provider to understand how dependencies should work:Perfect! Now I have a comprehensive understanding of the codebase. Let me create a thoughtful analysis document. Before I proceed with making recommendations, let me verify my understanding is complete by checking if there are any other critical files:Now I have a complete picture. Let me provide you with a comprehensive design review and recommendations:

---

# Design Review & Planning Recommendations for tofu-aicl

## Executive Summary

I've reviewed the tofu-aicl codebase - a declarative AI infrastructure framework that aims to be the "Terraform for AI workflows." The core architecture is **sound and well-designed**, but there are several **critical issues** that need addressing now before development continues. The good news: these are solvable with careful planning rather than major rewrites.

## Critical Issues to Address Immediately

### 1. **Dependency Resolution is Fundamentally Broken** ⚠️ **HIGHEST PRIORITY**

**Current Problem:**
```python
# In executor.py - lines attempting to resolve dependencies
ref_type, ref_name, ref_attr, ref_key = parts[1], parts[2], parts[3], parts[4]
# This expects: resource.loader_files.docs.attributes.documents
# But actual reference is: resource.loader_files.docs.attributes.documents
```

The dependency resolution makes **several dangerous assumptions**:
- Assumes reference format always has exactly 5 parts (splits on `.`)
- Hardcodes `attributes` as part[3] and expects a specific key as part[4]
- Uses `get_resource_by_name()` which does fuzzy matching with `if name in res.id`
- No validation that the referenced resource actually exists or has executed

**Why This Will Fail:**
1. Reference `resource.loader_files.docs.attributes.documents` has 5 parts, but what if you reference `resource.loader_files.docs.id`? (4 parts)
2. The `get_resource_by_name()` uses substring matching - if you have `docs` and `docs_v2`, it might match the wrong one
3. No error handling when a referenced attribute doesn't exist

**Solution Approach:**
```python
# Need a proper reference parser that handles:
# - resource.{type}.{name}.{attribute_path...}
# - Validation that resource exists in state
# - Proper error messages when resolution fails
# - Support for nested attribute access (attributes.documents[0].content)
```

### 2. **HCL Parsing is Too Simplistic**

**Current Problem:**
```python
class HCLParser:
    def parse(self):
        with open(self.file_path, 'r') as f:
            return hcl2.load(f)
```

The `hcl2` library returns raw Python dicts with **no evaluation context**. This means:
- Variable interpolation doesn't work properly
- Function calls in HCL won't work
- Complex expressions will fail

**Example That Will Break:**
```hcl
variable "base_path" {
  default = "./data"
}

resource "loader_files" "docs" {
  path = "${var.base_path}/documents"  # This won't interpolate!
}
```

**Solution:** Need to build an evaluation context or use a library that supports HCL evaluation (like `python-hcl2` with variable evaluation).

### 3. **State Management Has Race Conditions**

**Current Problem:**
```python
# In state/manager.py
def get_resource_by_name(self, name: str) -> Optional[ResourceState]:
    for res in self.current_state.resources.values():
        if name in res.id:  # Substring match - dangerous!
            return res
    return None
```

Issues:
- Substring matching is fragile (mentioned above)
- No locking mechanism for concurrent access
- State is loaded once at start, but resources are added during execution
- If execution fails mid-way, partial state is saved (no transactions)

**Solution:** 
- Use exact lookups with a resource registry: `{(type, name) -> resource_id}`
- Implement state locking or make operations atomic
- Consider transaction-like semantics (rollback on failure)

### 4. **Resource ID Generation is Inconsistent**

Different providers generate IDs differently:
```python
# file_loader: id=f"loader-{Path(path).name}"
# text_splitter: id="text-splitter"
```

This creates collisions if you have two `text_splitter` resources. The state manager uses IDs as dict keys - **collisions will silently overwrite resources**.

**Solution:** Standardize ID generation: `{provider}_{type}_{unique_name}` or use UUIDs.

## Architectural Design Issues

### 5. **No Clear Separation Between "Provisioning" and "Execution"**

The framework conflates two different concepts:

**Provisioning** (Terraform-style): Creating infrastructure resources
- Example: Creating a Pinecone index, configuring an LLM model
- Should be idempotent
- Should have state

**Execution** (DAG/workflow-style): Running computations through a pipeline
- Example: Loading files → splitting text → generating embeddings
- Should be deterministic but not necessarily idempotent
- State is about "results" not "infrastructure"

**Current Confusion:**
The `file_loader` provider treats "loading files" as a resource to "provision," but it's really an **execution step**. This creates semantic confusion:
- What does it mean to "destroy" a file loader resource?
- Should the loaded files be part of state?
- How do you re-run a pipeline without recreating everything?

**Recommendation:**
Clearly distinguish:
1. **Resource blocks** → Provisioning (create index, configure model)
2. **Data blocks** or **Execution blocks** → Runtime computations
3. Maybe introduce a `pipeline` or `workflow` construct for multi-step processing

### 6. **The gRPC Protocol Tries to Do Too Much**

The `provider.proto` combines:
- Terraform-like lifecycle (Plan/Apply/Read/Delete)
- AI execution (Execute streaming)
- Testing (Validate)
- All in one service

This creates **interface bloat** where every provider must implement 10+ RPC methods, most of which are stubs:

```python
# Every provider has this boilerplate:
def ReadResource(self, request, context):
    return provider_pb2.ReadResourceResponse()  # Empty stub
```

**Recommendation:**
Consider splitting into multiple services:
- `LifecycleProvider` - For provisioning resources
- `ExecutionProvider` - For DAG/pipeline steps
- `ValidationProvider` - For testing

Or use **optional methods** with feature flags so providers only implement what they need.

### 7. **No Execution History or Observability**

Once a resource is applied, there's no trace of:
- What input was provided
- What output was produced
- When it was executed
- How long it took
- Any errors or warnings

The state file only stores final attributes, losing all execution context.

**Recommendation:**
Add execution logging/history:
```python
@dataclass
class ExecutionRecord:
    timestamp: str
    resource_id: str
    input: Dict[str, Any]
    output: Dict[str, Any]
    duration_ms: int
    diagnostics: List[Diagnostic]
```

## Design Patterns & Best Practices Missing

### 8. **No Validation Layer**

There's no validation of:
- Resource configuration before sending to providers
- Provider schemas (GetSchema is defined but never called)
- Dependency types (can't check if `documents` attribute exists before referencing it)

**Recommendation:**
Implement schema validation:
1. Call `GetSchema()` when provider starts
2. Validate resource configs against schema before `ApplyResourceChange()`
3. Validate references exist before dependency resolution

### 9. **Error Handling is Inconsistent**

Some providers return diagnostics, others raise exceptions. The engine sometimes catches, sometimes doesn't.

```python
# In engine.py - sometimes does this:
try:
    response = provider.stub.DeleteResource(req)
except grpc.RpcError as e:
    print(f"Error deleting resource {res_id}: {e.details()}")

# Other times - no error handling at all
```

**Recommendation:**
Standardize error handling:
- Providers ALWAYS return diagnostics (never raise)
- Engine converts gRPC errors to diagnostics
- Fail fast on ERROR diagnostics, continue on WARNING

### 10. **Testing Framework is Incomplete**

The `test-cl` framework has conceptual issues:

```python
# In engine.py test() method
eval_context = {'self': {'output': dict(response.output)}}
result = eval(condition, {}, eval_context)  # SECURITY RISK!
```

Using `eval()` on user input is **extremely dangerous**. Even if you trust `.test-cl` files, this is bad practice.

**Recommendation:**
- Build a safe expression evaluator
- Or use a sandboxed environment
- Or define assertion operators (equals, contains, matches_regex)

## What's Working Well ✅

Before I focus only on problems, here's what you've done RIGHT:

1. **Clean separation of concerns** - Engine, Parser, Planner, Executor, State Manager
2. **Container isolation** - Each provider is truly isolated
3. **gRPC for provider communication** - Good choice for cross-language support
4. **Topological sort for dependencies** - The planner correctly handles DAG ordering
5. **State file design** - JSON format, versioned, experiment-scoped
6. **Documentation structure** - Good use of ADRs and architecture docs

## Recommended Action Plan (Priority Order)

### Week 1: Fix Critical Path Issues
1. ✅ **Fix dependency resolution** (executor.py)
   - Build proper reference parser
   - Add validation that resources exist
   - Handle nested attribute access

2. ✅ **Fix resource ID generation** (all providers)
   - Standardize to: `{provider}_{type}_{resource_name}`
   - Update state manager to use composite keys

3. ✅ **Add basic validation** (engine.py)
   - Call GetSchema on provider startup
   - Validate configs before Apply

### Week 2: Architectural Clarity
4. ✅ **Separate provisioning from execution semantics**
   - Define which resources are "infrastructure" vs "data processing"
   - Consider adding `data` blocks for execution-only steps

5. ✅ **Improve HCL evaluation**
   - Add variable interpolation
   - Build evaluation context for expressions

6. ✅ **Standardize error handling**
   - All providers use diagnostics
   - Engine has consistent error handling paths

### Week 3: Observability & Testing
7. ✅ **Add execution history**
   - Track inputs, outputs, timing
   - Enable debugging and replay

8. ✅ **Fix test framework security**
   - Remove `eval()` usage
   - Build safe assertion language

9. ✅ **Add basic logging/tracing**
   - Structured logging for all operations
   - Consider OpenTelemetry for distributed tracing

## Questions to Consider

Before moving forward, the development team should decide:

1. **Is this a provisioning tool or an execution engine?** 
   - If both, how do you clearly separate the two modes?

2. **Should pipelines be first-class citizens?**
   - Maybe a `pipeline` block that orchestrates `resource` blocks?

3. **How should state work for data transformations?**
   - Should intermediate results be cached?
   - How do you invalidate/recompute?

4. **What's the deployment model?**
   - Single-user local experimentation?
   - Multi-user shared infrastructure?
   - This affects state management and locking

5. **What's the testing philosophy?**
   - Unit tests on individual steps?
   - Integration tests on full pipelines?
   - Property-based testing on outputs?

---

## Final Recommendation

**Do NOT write more code until you fix issues #1, #2, #3, and #4.** These are foundational - building on top of broken dependency resolution and resource IDs will create technical debt that becomes exponentially harder to fix.

The good news: the architecture is sound. This is a **planning and implementation quality** issue, not a fundamental design flaw. With careful attention to these issues now, you'll have a solid foundation for the advanced features.
