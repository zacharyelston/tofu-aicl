# Implementation Guide

## Language-Agnostic Implementation

This guide provides implementation patterns that can be adapted to any language.

---

## Phase 1: Core Engine (MVP)

### Step 1: HCL Parser

**Objective**: Parse .aicl files into AST

**Implementation**:
```
1. Choose HCL library for your language:
   - Python: python-hcl2
   - Go: hashicorp/hcl
   - JavaScript: js-hcl-parser
   - Rust: hcl-rs
   
2. Create Parser class:
   - parse(file_path) → AST
   - validate_syntax(ast) → bool
   - extract_blocks(ast, type) → Block[]

3. Define AST data structures:
   - Block: type, name, attributes, children
   - Variable, Provider, Resource, Data, Output blocks

4. Add error handling:
   - Syntax errors with line numbers
   - Missing required fields
   - Invalid block types
```

**Test Cases**:
- Valid HCL file parses successfully
- Syntax errors are caught
- All block types extracted correctly

---

### Step 2: Variable Evaluator

**Objective**: Resolve variable references and interpolations

**Implementation**:
```
1. Create evaluation context:
   - variables: Map<string, any>
   - resources: Map<string, Resource>
   - providers: Map<string, Provider>

2. Implement interpolation resolver:
   - Pattern: ${type.name.attribute}
   - Variable: ${var.model_name}
   - Resource: ${resource.llm.answer.content}
   - Function: ${env("API_KEY")}

3. Add built-in functions:
   - env(name): Read environment variable
   - file(path): Read file content
   - join(sep, list): Join strings
   
4. Recursive evaluation:
   - Handle nested references
   - Detect circular dependencies
```

**Test Cases**:
- Variable references resolve correctly
- Resource references work
- Functions execute properly
- Circular dependencies detected

---

### Step 3: Dependency Planner

**Objective**: Build execution plan with correct ordering

**Implementation**:
```
1. Build dependency graph:
   - Node = Resource
   - Edge = Dependency (explicit or implicit)

2. Extract dependencies:
   - Explicit: depends_on attribute
   - Implicit: References in attributes
   
3. Topological sort:
   - Use Kahn's algorithm or DFS
   - Detect cycles
   - Group independent resources

4. Create execution plan:
   - Ordered list of operations
   - Parallel stages identified
   - Operation types: CREATE, READ, UPDATE, DELETE
```

**Test Cases**:
- Correct dependency order
- Parallel opportunities identified
- Circular dependencies rejected

---

### Step 4: Provider System

**Objective**: Implement provider abstraction and gRPC communication

**Implementation**:
```
1. Define gRPC service (provider.proto):
   - CreateResource(request) → response
   - ReadResource(id) → response
   - UpdateResource(request) → response
   - DeleteResource(id) → response

2. Generate code from proto:
   - Python: grpcio-tools
   - Go: protoc-gen-go
   - JavaScript: grpc-tools
   
3. Create ProviderClient wrapper:
   - Start provider subprocess
   - Establish gRPC channel
   - Send requests
   - Handle errors

4. Implement ProviderServer base class:
   - Service registration
   - Graceful shutdown
   - Error handling
```

**Test Cases**:
- Provider starts successfully
- gRPC communication works
- Errors handled gracefully
- Shutdown cleans up properly

---

### Step 5: Executor

**Objective**: Execute plan and manage state

**Implementation**:
```
1. Create Executor class:
   - execute(plan, state) → new_state
   - For each resource in plan:
     - Get provider
     - Invoke operation
     - Update state

2. Resource operations:
   - CREATE: Call provider.CreateResource()
   - READ: Call provider.ReadResource()
   - UPDATE: Call provider.UpdateResource()
   - DELETE: Call provider.DeleteResource()

3. State management:
   - Track resource metadata
   - Store attributes
   - Record dependencies

4. Error handling:
   - Retry transient errors
   - Mark failed resources
   - Continue or abort based on severity
```

**Test Cases**:
- Resources created successfully
- State updated correctly
- Errors handled appropriately

---

## Phase 2: Provider Implementations

### OpenAI Provider

**Implementation**:
```
1. Create provider directory:
   providers/openai/
   ├── config.yaml
   └── server.py (or .go, .js, etc)

2. Implement gRPC service:
   - CreateResource for llm_completion
   - CreateResource for text_embedding
   
3. OpenAI API integration:
   - Install SDK (openai, openai-go, etc)
   - Call chat.completions.create()
   - Call embeddings.create()

4. Resource attributes:
   - Input: model, prompt, temperature, max_tokens
   - Output: content, usage, cost

5. Error handling:
   - API errors (rate limit, invalid key)
   - Timeout
   - Network errors
```

### Pinecone Provider

**Implementation**:
```
1. Implement vector operations:
   - create_index
   - upsert_vectors
   - query_vectors
   
2. Pinecone API integration:
   - Install SDK
   - Initialize client with API key
   - Handle index management

3. Resource types:
   - vector_index
   - vector_upsert
   - vector_query
```

---

## Phase 3: Storage Layer

### In-Memory Storage

**Implementation**:
```
1. Create MemoryStorage class:
   - experiments: Map<id, Experiment>
   - results: Map<id, Result>
   
2. Implement interface methods:
   - store_experiment()
   - get_experiment()
   - list_experiments()
   
3. No persistence (data lost on exit)
```

### SQLite Storage

**Implementation**:
```
1. Create database schema:
   - experiments table
   - configurations table
   - results table
   - quality_scores table

2. Use SQL library for your language:
   - Python: sqlite3
   - Go: database/sql + mattn/go-sqlite3
   - JavaScript: better-sqlite3

3. Implement CRUD operations:
   - INSERT for store methods
   - SELECT for get methods
   - UPDATE for modifications
```

---

## Phase 4: Matrix Experiments

### Template Generator

**Implementation**:
```
1. Template engine:
   - Python: Jinja2
   - Go: text/template
   - JavaScript: Handlebars

2. Variable expansion:
   - Parse test-variables.yaml
   - Generate combinations (Cartesian product)
   - Expand template for each combination

3. Generate AICL configs:
   - Replace {{ placeholder }} with values
   - Save to files or execute directly
```

### Parallel Executor

**Implementation**:
```
1. Concurrency library:
   - Python: concurrent.futures.ThreadPoolExecutor
   - Go: goroutines + sync.WaitGroup
   - JavaScript: Promise.all()

2. Execute experiments:
   - Submit all to executor
   - Collect results as they complete
   - Update progress

3. Result aggregation:
   - Store all results
   - Calculate statistics
   - Identify best performers
```

---

## Phase 5: LLM-as-Judge

### Grading System

**Implementation**:
```
1. Grading prompt:
   - Template with question, expected, actual
   - Request JSON output with scores

2. Judge execution:
   - Call LLM with grading prompt
   - Parse JSON response
   - Extract scores

3. Quality score storage:
   - Link to experiment result
   - Store all dimensions (relevance, accuracy, etc)
   - Store judge reasoning
```

---

## Phase 6: CLI Interface

### Command Structure

**Implementation**:
```
1. CLI framework:
   - Python: argparse (stdlib) or Click/Typer
   - Go: Cobra
   - JavaScript: Commander.js

2. Commands to implement:
   aicl run <config>
   aicl plan <config>
   aicl validate <config>
   aicl experiment run <suite>
   aicl providers list
   aicl models list

3. Core flags:
   - --var key=value
   - --state <path>
   - --auto-approve
   - --parallelism <n>

4. Output control (v0.2.0+):
   - --output-file (JSON state files)
   - --output-docdb (PostgreSQL DocDB)
   - --output-stdout (console output)
   - --no-stdout (disable console)
   - --quiet (errors only)

5. Experiment metadata (v0.2.0+):
   - --experiment-id <id>
   - --tags <comma-separated>

6. Output formatting:
   - Colored output (success/error)
   - Progress indicators
   - Tables for results
```

### Output Destination Routing (v0.2.0+)

**Architecture**:
```python
class OutputManager:
    """Routes outputs to multiple destinations"""
    
    def __init__(self, args):
        self.destinations = []
        
        # Determine if any output flags were explicitly set
        has_explicit_output = (
            args.output_file or 
            args.output_docdb or 
            args.output_stdout or
            args.no_output_file or
            args.no_stdout
        )
        
        # File output (default: enabled if no explicit outputs)
        enable_file = (
            args.output_file or 
            (not has_explicit_output and not args.no_output_file)
        ) and not args.no_output_file
        
        if enable_file:
            self.destinations.append(
                FileOutputHandler(args.state)
            )
        
        # DocDB output
        if args.output_docdb:
            if os.getenv('DATABASE_URL'):
                self.destinations.append(
                    DocDBOutputHandler(
                        os.getenv('DATABASE_URL'),
                        args.experiment_id,
                        args.tags
                    )
                )
            else:
                logging.warning("DATABASE_URL not set, DocDB disabled")
        
        # Stdout output (default: enabled if no explicit outputs)
        enable_stdout = (
            args.output_stdout or
            (not has_explicit_output and not args.no_stdout)
        ) and not args.no_stdout and not args.quiet
        
        if enable_stdout:
            self.destinations.append(
                StdoutOutputHandler()
            )
    
    def write_outputs(self, outputs: Dict):
        """Write to all configured destinations"""
        for dest in self.destinations:
            dest.write(outputs)
```

**CLI Argument Parsing**:
```python
import argparse

parser = argparse.ArgumentParser(description='AICL Engine')
parser.add_argument('config_path', help='Path to .aicl config file')

# Output control
output_group = parser.add_argument_group('Output Control')
output_group.add_argument('--output-file', action='store_true',
                         help='Save to JSON state files (default if no outputs specified)')
output_group.add_argument('--no-output-file', action='store_true',
                         help='Disable JSON state file output')
output_group.add_argument('--output-docdb', action='store_true',
                         help='Save to PostgreSQL DocDB')
output_group.add_argument('--output-stdout', action='store_true',
                         help='Print to console (default if no outputs specified)')
output_group.add_argument('--no-stdout', action='store_true',
                         help='Disable console output')
output_group.add_argument('--quiet', action='store_true',
                         help='Minimal output (errors only)')

# Experiment metadata
meta_group = parser.add_argument_group('Experiment Metadata')
meta_group.add_argument('--experiment-id', type=str,
                       help='Custom experiment identifier')
meta_group.add_argument('--tags', type=str,
                       help='Comma-separated tags')

# Execution
exec_group = parser.add_argument_group('Execution')
exec_group.add_argument('--parallel', action='store_true',
                       help='Enable parallel execution')

args = parser.parse_args()
```

**Integration Example**:
```python
def main():
    args = parser.parse_args()
    
    # Initialize output manager
    output_mgr = OutputManager(args)
    
    # Run engine
    engine = AICLEngine(
        config_path=args.config_path,
        experiment_id=args.experiment_id,
        tags=args.tags.split(',') if args.tags else None
    )
    
    outputs = engine.run()
    
    # Write to all destinations
    output_mgr.write_outputs(outputs)
```

---

## Phase 7: Observability

### OpenTelemetry Integration

**Implementation**:
```
1. Install OpenTelemetry SDK:
   - Python: opentelemetry-api, opentelemetry-sdk
   - Go: go.opentelemetry.io/otel
   - JavaScript: @opentelemetry/api

2. Instrument engine:
   - Span per resource operation
   - Span attributes (model, tokens, cost)
   - Trace context propagation

3. Export traces:
   - OTLP exporter to collector
   - Or Jaeger, Zipkin, etc.

4. Metrics:
   - Counter: total_experiments
   - Histogram: execution_duration
   - Gauge: active_providers
```

---

## Testing Strategy

### Unit Tests

```
1. Parser tests:
   - Valid/invalid HCL
   - Block extraction
   - Error handling

2. Evaluator tests:
   - Variable resolution
   - Function execution
   - Circular dependency detection

3. Planner tests:
   - Dependency ordering
   - Parallel stages
   - Cycle detection

4. Provider tests:
   - Mock gRPC responses
   - Error handling
   - Resource operations
```

### Integration Tests

```
1. End-to-end tests:
   - Complete AICL execution
   - State management
   - Multi-resource workflows

2. Provider tests:
   - Real API calls (optional)
   - Mock external services
   - Error scenarios

3. Storage tests:
   - CRUD operations
   - Concurrent access
   - Data integrity
```

---

## Performance Optimization

### Key Areas

```
1. Parallel execution:
   - Execute independent resources concurrently
   - Optimize thread/goroutine count

2. Caching:
   - Cache provider connections
   - Cache model metadata
   - Cache evaluation results

3. Database queries:
   - Index frequently queried columns
   - Batch inserts
   - Connection pooling

4. Provider startup:
   - Reuse provider processes
   - Lazy initialization
   - Health checks
```

---

## Deployment Checklist

### CLI Release

```
☐ Compile binaries for all platforms
☐ Create installer scripts
☐ Publish to package managers (PyPI, Homebrew, etc)
☐ Generate documentation
☐ Create example AICL configs
☐ Write migration guide (if upgrading)
```

### Web Release

```
☐ Set up CI/CD pipeline
☐ Configure production database
☐ Set up monitoring (Prometheus, Grafana)
☐ Configure error tracking (Sentry)
☐ Load balancing setup
☐ SSL certificates
☐ Backup strategy
☐ Disaster recovery plan
```

---

## Common Pitfalls to Avoid

### 1. Hardcoded Provider Logic
❌ Don't: Hardcode provider details in engine
✅ Do: Use configuration files and auto-discovery

### 2. Blocking I/O
❌ Don't: Execute providers sequentially when independent
✅ Do: Use parallel execution for independent resources

### 3. Missing Error Handling
❌ Don't: Assume API calls always succeed
✅ Do: Handle all error cases with retries

### 4. Security Issues
❌ Don't: Log API keys or secrets
✅ Do: Use environment variables and encryption

### 5. Poor State Management
❌ Don't: Store state in memory only
✅ Do: Use persistent storage with locking
