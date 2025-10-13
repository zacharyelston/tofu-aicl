# Minimal AICL Architecture

## Design Philosophy

This is a **spartan version** of tofu-aicl with only the essentials. Total: ~820 lines (92% reduction from full 10,000+ line codebase).

## Why Things Were Simplified

### 1. Executor - Too Complex for Minimal
**Full Version**: 180+ lines with:
- OpenTelemetry tracing/metrics
- 30+ resource type → provider mappings
- Complex dependencies (observability, evaluator)
- Support for 9 different providers

**Minimal Solution**: **Removed entirely**
- Direct provider calls from engine.py
- Simple Struct conversion
- One provider (Naga) only
- Zero tracing overhead

### 2. StateManager - Too Complex for Minimal
**Full Version**: Requires:
- experiment_id parameter
- Database integration (SQLite/PostgreSQL)
- Complex load/save logic
- Multi-experiment tracking

**Minimal Solution**: **SimpleState class** (12 lines)
```python
class SimpleState:
    def __init__(self):
        self.resources = {}
    
    def add_resource(self, resource_state):
        self.resources[resource_state.id] = resource_state
```

### 3. Provider System - One Provider Only
**Full Version**: 9 providers
- OpenAI, Naga, OpenRouter, Claude
- Ragie, Pinecone, File Loader, Text Splitter, etc.
- Complex configuration, Docker support

**Minimal Solution**: **Naga only** (130 lines)
- Chat completions
- Embeddings  
- Direct API calls
- No Docker, subprocess only

## File Structure

```
versions/minimal/
├── engine.py                 # 210 lines - Main orchestrator
│   ├── SimpleState          # 12 lines - In-memory state
│   ├── ResourceState        # 8 lines - State object
│   ├── MinimalEngine        # 190 lines - Core logic
│   └── Direct provider calls (no Executor!)
│
├── run.py                    # 80 lines - CLI wrapper
│
├── core/                     # ~400 lines total
│   ├── parser.py            # 9 lines - HCL parsing
│   ├── evaluator.py         # 96 lines - Variable resolution
│   └── planner.py           # 116 lines - Dependency graph
│
├── providers/naga/           
│   └── server.py            # 130 lines - Naga provider
│
├── experiments/
│   ├── self-build.aicl      # AI generates provider code
│   └── matrix-test.aicl     # Compare model variations
│
└── README.md                 # Complete getting started guide
```

## How It Works

### 1. Parse Config (HCL)
```python
parser = HCLParser(config_path)
parsed_config = parser.parse()
```

### 2. Plan Execution (Topological Sort)
```python
planner = Planner(parsed_config)
sorted_resources, resource_map = planner.build_graph()
```

### 3. Execute Resources (Direct Provider Calls)
```python
for resource_id in sorted_resources:
    # Resolve variables
    context = evaluator.build_context()
    resolved_config = evaluator.resolve_config(config_attrs, context)
    
    # Call provider directly (no Executor!)
    request = provider_pb2.ApplyResourceChangeRequest(
        type_name=res_type,
        config=config_struct
    )
    response = provider_stub.ApplyResourceChange(request)
    
    # Update state
    state.add_resource(new_state)
```

### 4. Save State (JSON)
```python
state_data = {
    "version": 1,
    "resources": {rid: {...} for rid, rstate in state.resources.items()}
}
json.dump(state_data, file)
```

## What Was Removed

1. ❌ **Executor** - Too complex, direct calls instead
2. ❌ **StateManager** - Custom SimpleState instead
3. ❌ **8 providers** - Only Naga remains
4. ❌ **OpenTelemetry** - No tracing/metrics
5. ❌ **Database** - Simple JSON state only
6. ❌ **Docker support** - Subprocess only
7. ❌ **v2 architecture** - No storage abstraction
8. ❌ **Experiment DB** - No SQLite/PostgreSQL
9. ❌ **Model catalog** - Hardcoded in experiments
10. ❌ **Provider registry** - Hardcoded Naga path

## What Remains (Core Essentials)

1. ✅ **HCL parsing** - Full terraform syntax support
2. ✅ **Variable interpolation** - ${var.x} and ${resource.y.z}
3. ✅ **Dependency resolution** - Topological sort
4. ✅ **Provider protocol** - gRPC communication
5. ✅ **State management** - Resource tracking
6. ✅ **Self-building** - AI generates code
7. ✅ **Matrix testing** - Compare variations

## Test Results

### Self-Build Experiment
```bash
python run.py self-build
```
- ✅ Generated Echo provider code
- ✅ Quality Score: 85/100 (ACCEPT)
- ✅ Tokens: 384

### Matrix Test Experiment
```bash
python run.py matrix-test
```
- ✅ Tested 4 variations (temp: 0.2, 0.7, 1.2; tokens: 150, 300)
- ✅ Winner: Response B (temp=0.7, balanced) - 88/100
- ✅ Total tokens: 3,324

## Extension Points

To add features:

1. **Add Provider**: Create `providers/x/server.py`, update engine provider routing
2. **Add Experiment**: Create `experiments/x.aicl`
3. **Add Storage**: Replace SimpleState with database backend
4. **Add Metrics**: Integrate OpenTelemetry in engine.py

## Comparison

| Feature | Full Version | Minimal Version |
|---------|--------------|-----------------|
| Lines of Code | 10,000+ | 820 |
| Providers | 9 | 1 (Naga) |
| Storage | SQLite/PostgreSQL | JSON |
| Observability | OpenTelemetry | None |
| Dependencies | 15+ packages | 5 packages |
| Complexity | Production-ready | Learning-focused |
| Time to Understand | Days | 30 minutes |

---

**Philosophy**: Remove everything non-essential. Keep only what makes AICL work.
