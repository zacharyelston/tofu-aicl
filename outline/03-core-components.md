# Core Components Specification

## 1. Parser

### Responsibilities
- Parse HCL configuration files (.aicl extension)
- Validate syntax
- Extract blocks: variable, provider, resource, data, output
- Generate Abstract Syntax Tree (AST)

### Input
- File path to .aicl configuration
- Optional: variable overrides (CLI flags)

### Output
- AST structure with typed nodes
- Syntax error messages (if invalid)

### Key Operations
```
parse(file_path: string) -> AST | Error
validate_syntax(content: string) -> bool
extract_blocks(ast: AST, block_type: string) -> Block[]
```

### Dependencies
- HCL parser library (python-hcl2, hclparse, or native)

---

## 2. Evaluator

### Responsibilities
- Resolve variable interpolations: `${var.name}`
- Resolve resource references: `${resource.type.name.attr}`
- Evaluate functions: `env("VAR")`, `file("path")`
- Template expansion for experiments: `{{ variable }}`

### Input
- AST from parser
- Variable definitions
- Environment context

### Output
- Fully resolved configuration (no interpolations)
- Evaluation errors (undefined variables, etc)

### Key Operations
```
evaluate(ast: AST, context: Context) -> ResolvedConfig | Error
resolve_variable(ref: string, context: Context) -> any
resolve_resource_ref(ref: string, state: State) -> any
expand_template(template: string, vars: dict) -> string
```

### Expression Types
- **Variable**: `${var.temperature}`
- **Resource**: `${resource.llm_completion.answer.content}`
- **Provider**: `${provider.openai}`
- **Function**: `${env("API_KEY")}`, `${file("prompt.txt")}`

### Template Expansion
- Jinja2-style: `{{ model_name }}`, `{{ temperature }}`
- Used in matrix experiments
- Multi-variable expansion creates combinations

---

## 3. Planner

### Responsibilities
- Build dependency graph from resources
- Topological sort for execution order
- Detect circular dependencies
- Determine parallel execution opportunities

### Input
- Resolved configuration from evaluator
- Current state (for updates)

### Output
- Execution plan (ordered list of operations)
- Dependency graph visualization (optional)
- Plan errors (cycles, missing dependencies)

### Key Operations
```
plan(config: ResolvedConfig, state: State) -> ExecutionPlan | Error
build_dependency_graph(resources: Resource[]) -> Graph
topological_sort(graph: Graph) -> Resource[]
detect_cycles(graph: Graph) -> Cycle[] | null
optimize_for_parallelism(sorted: Resource[]) -> Stage[]
```

### Resource Lifecycle Operations
- **CREATE**: Resource doesn't exist in state
- **READ**: Resource exists, no changes needed
- **UPDATE**: Resource exists, configuration changed
- **DELETE**: Resource in state, not in config
- **REPLACE**: Resource exists, immutable fields changed

### Dependency Types
- **Explicit**: `depends_on = [resource.foo.bar]`
- **Implicit**: References in attributes (e.g., `model = resource.x.y.id`)

---

## 4. Executor

### Responsibilities
- Execute the plan from planner
- Manage provider lifecycle (start/stop)
- Invoke provider operations via gRPC
- Handle errors and retries
- Update state after each operation

### Input
- Execution plan from planner
- Provider configurations
- Current state

### Output
- Updated state
- Execution logs
- Operation results (success/failure)

### Key Operations
```
execute(plan: ExecutionPlan, state: State) -> ExecutionResult | Error
start_provider(provider_name: string) -> ProviderClient
stop_provider(provider_name: string) -> void
invoke_operation(provider: ProviderClient, op: Operation) -> Result
retry_on_failure(operation: Operation, max_retries: int) -> Result
```

### Provider Communication (gRPC)
```
CreateResource(request: ResourceRequest) -> ResourceResponse
ReadResource(request: ResourceID) -> ResourceResponse
UpdateResource(request: ResourceRequest) -> ResourceResponse
DeleteResource(request: ResourceID) -> DeleteResponse
```

### Error Handling
- Transient errors: Retry with exponential backoff
- Permanent errors: Mark resource as failed, continue if non-critical
- Critical errors: Abort execution, rollback if possible

---

## 5. State Manager

### Responsibilities
- Persist resource state to storage
- Load previous state
- State locking for concurrent operations
- State comparison (drift detection)

### Input
- Resource metadata (ID, type, attributes)
- Operation results from executor

### Output
- State file (JSON format)
- State lock acquisition/release

### Key Operations
```
save_state(state: State, path: string) -> void | Error
load_state(path: string) -> State | Error
acquire_lock(state_path: string, timeout: int) -> Lock | Error
release_lock(lock: Lock) -> void
compare_states(current: State, desired: State) -> Diff
```

### State File Format (JSON)
```json
{
  "version": 1,
  "timestamp": "2025-10-11T12:00:00Z",
  "resources": [
    {
      "id": "resource.llm_completion.answer",
      "type": "llm_completion",
      "provider": "openai",
      "attributes": {
        "model": "gpt-4o-mini",
        "prompt": "...",
        "content": "..."
      },
      "dependencies": ["provider.openai"],
      "metadata": {
        "created_at": "2025-10-11T12:00:00Z",
        "updated_at": "2025-10-11T12:00:00Z"
      }
    }
  ]
}
```

### State Locking
- Lock file: `{state_path}.lock`
- Contains: PID, hostname, timestamp
- Timeout: 60 seconds (configurable)
- Stale lock cleanup

---

## 6. Provider Registry

### Responsibilities
- Auto-discover providers from file system
- Load provider configurations
- Validate provider schemas
- Provide provider lookup

### Input
- Providers directory path (default: `./providers/`)

### Output
- Registry of available providers
- Provider metadata (capabilities, models, ports)

### Key Operations
```
discover_providers(directory: string) -> ProviderConfig[]
load_provider_config(path: string) -> ProviderConfig | Error
validate_config(config: ProviderConfig) -> bool | Error
get_provider(name: string) -> ProviderConfig | null
list_all() -> ProviderConfig[]
```

### Provider Config Schema (YAML)
```yaml
provider:
  name: openai
  display_name: OpenAI
  version: 1.0.0
  description: OpenAI API provider
  
  runtime:
    entrypoint: server.py
    default_port: 50051
    mode: subprocess  # or: docker, both
  
  environment:
    required_vars: [OPENAI_API_KEY]
    optional_vars: []
  
  capabilities:
    types: [llm, embeddings]
    operations: [chat_completion, text_embedding]
  
  model_ids:  # References to model catalog
    - gpt-4o
    - gpt-4o-mini
    - text-embedding-3-small
```

### Auto-Discovery Algorithm
1. Scan `providers/` directory
2. For each subdirectory:
   - Look for `config.yaml`
   - Parse and validate
   - Add to registry
3. Skip invalid configs (log warning)
4. Return sorted list by name
