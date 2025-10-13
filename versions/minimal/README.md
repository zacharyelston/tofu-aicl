# AICL Minimal - Getting Started

This is a **spartan version** of tofu-aicl with just the essentials. Perfect for understanding the core concepts or starting your own AICL-based project.

## What's Included

### Core Components (~200 lines total)
- **engine.py** - Orchestrates the workflow
- **core/parser.py** - Parses HCL configuration
- **core/evaluator.py** - Resolves variables and interpolations
- **core/planner.py** - Builds dependency graph
- **core/executor.py** - Executes resources
- **core/state_manager.py** - Tracks resource state

### Provider
- **Naga Provider** - Chat and embeddings via Naga.ai API
  - Cost-effective alternative to OpenAI
  - Same API format, 50% cheaper

### Experiments
1. **self-build.aicl** - AI generates its own provider code
2. **matrix-test.aicl** - Compare model variations (temperature, tokens)

## Quick Start

### 1. Install Dependencies

```bash
cd versions/minimal
pip install python-hcl2 grpcio grpcio-tools protobuf requests python-dotenv
```

### 2. Set API Key

You need a Naga.ai API key (get one at https://naga.ac):

```bash
export NAGA_API_KEY='your-api-key-here'
```

### 3. Run Experiments

**Self-Build** (AI generates code):
```bash
python run.py self-build
```

**Matrix Test** (Compare variations):
```bash
python run.py matrix-test
```

## How It Works

### 1. Define Infrastructure (HCL)

```hcl
terraform {
  required_providers {
    naga = { source = "aicl/naga" }
  }
}

resource "naga_chat" "example" {
  model = "gpt-4o-mini"
  temperature = 0.7
  max_tokens = 500
  
  messages = [
    {
      role = "user"
      content = "Explain quantum computing"
    }
  ]
  
  aiclResourceName = "example"
}
```

### 2. Engine Processes It

1. **Parse** - Load HCL config
2. **Plan** - Build dependency graph
3. **Execute** - Run resources in order
4. **Save** - Store state in JSON

### 3. View Results

Results saved to: `terraform.tfstate.d/default-minimal.tfstate`

```bash
cat terraform.tfstate.d/default-minimal.tfstate | jq
```

## Understanding the Experiments

### Self-Build Experiment

Demonstrates **self-modification** - AI writing code that extends itself:

1. **Generate**: AI creates a new provider (Echo)
2. **Grade**: AI evaluates the code quality (0-100)
3. **Result**: Shows if generated code meets standards

**Key Learning**: AICL can improve itself through structured prompts

### Matrix Test Experiment

Demonstrates **systematic testing** - comparing variations:

1. **Test A**: Low temp (0.2) - Deterministic, precise
2. **Test B**: Mid temp (0.7) - Balanced creativity
3. **Test C**: High temp (1.2) - More creative, less predictable
4. **Test D**: Longer output (300 tokens) - More depth
5. **Compare**: AI ranks all responses

**Key Learning**: Find optimal settings for your use case

## Architecture

```
versions/minimal/
├── engine.py              # Main orchestrator (~150 lines)
├── core/                  # Core components
│   ├── parser.py         # HCL parsing
│   ├── evaluator.py      # Variable resolution
│   ├── planner.py        # Dependency graph
│   ├── executor.py       # Resource execution
│   └── state_manager.py  # State tracking
├── providers/
│   └── naga/
│       └── server.py     # Naga provider (~130 lines)
├── experiments/
│   ├── self-build.aicl   # Self-modification example
│   └── matrix-test.aicl  # Matrix testing example
└── proto/                # gRPC definitions (copied from main)
```

## Next Steps

### Extend the Minimal Version

1. **Add Provider**: Create `providers/myservice/server.py`
2. **Add Experiment**: Create `experiments/mytest.aicl`
3. **Run**: `python run.py mytest`

### Example: Add a Simple Provider

```python
# providers/hello/server.py
class HelloProvider(provider_pb2_grpc.ProviderServicer):
    def ApplyResourceChange(self, request, context):
        config = MessageToDict(request.config)
        name = config.get('name', 'World')
        
        output = {'greeting': f'Hello, {name}!'}
        output_struct = Struct()
        ParseDict(output, output_struct)
        
        return provider_pb2.ApplyResourceChangeResponse(
            new_state=provider_pb2.ResourceState(
                id=f"hello-{name}",
                type=request.type_name,
                attributes=output_struct,
                status='ready'
            )
        )
```

Update `engine.py` to start it on port 50054.

## Differences from Full Version

**Minimal Version** (this):
- ✅ Simple, easy to understand (~300 lines total)
- ✅ 1 provider (Naga)
- ✅ 2 experiments
- ✅ Basic features only
- ✅ No database, no metrics, no complex features

**Full Version** (../..):
- 📦 Complete production system (10,000+ lines)
- 📦 9 providers (OpenAI, Naga, Ragie, Pinecone, etc.)
- 📦 Advanced features (RAG, grading, experiments)
- 📦 SQLite/PostgreSQL storage
- 📦 OpenTelemetry observability
- 📦 v2 architecture with storage abstraction

## Why Naga?

- **Cost**: 50% cheaper than OpenAI
- **Quality**: Same models, same API format
- **Simple**: Drop-in replacement, just change API key
- **Perfect for learning**: Low cost for experimentation

## Troubleshooting

**Provider won't start**:
- Check NAGA_API_KEY is set: `echo $NAGA_API_KEY`
- Verify port 50052 is free: `lsof -i:50052`

**Import errors**:
- Make sure you're running from `/home/runner/tofu-aicl` directory
- Proto files should be in `proto/` directory

**State not saved**:
- Check `terraform.tfstate.d/` directory exists
- Look for error messages in console output

## Learn More

- 📖 **Full Specs**: See `../../outline/` for complete technical specs
- 🔬 **More Experiments**: See `../../experiments/` for advanced examples
- 🏗️ **Full Version**: See `../../` for production-ready system

---

**Total Code**: ~300 lines  
**Time to Understand**: ~30 minutes  
**Perfect For**: Learning, prototyping, extending
