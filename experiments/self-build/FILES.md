# Self-Building Experiment Files

Complete list of files for AICL's self-modification capability.

---

## Specification Document

### outline/13-self-modification-experiments.md
**Lines**: 780  
**Purpose**: Complete technical specification for self-building experiments

**Contents**:
- Architecture overview
- Resource types (`code_generator`, `test_runner`, `code_judge`)
- Complete workflow examples
- 6-level progression path
- Safety mechanisms
- Grading rubric
- Success criteria

---

## Experiment Files

### 1. add-echo-provider.aicl
**Lines**: 268  
**Type**: Complete self-build experiment  
**Purpose**: Generate an echo provider from scratch

**What it does**:
- Queries RAG for provider patterns
- Generates provider code (server.py)
- Generates provider config (config.yaml)
- Generates comprehensive tests (test_echo.py)
- Evaluates code quality (0-100 score)
- Provides application recommendation

**Resources used**:
- `vector_query` - Find implementation patterns
- `llm_completion` - Generate code (4x)
- Output quality evaluation and files

**Run**:
```bash
python run.py experiments/self-build/add-echo-provider.aicl
```

---

### 2. test-self-build-variables.yaml
**Lines**: 201  
**Type**: Test variable definitions  
**Purpose**: Define parameter space for self-building experiments

**Contains**:
- **Code generation models**: gpt-4o, gpt-4o-mini, claude-sonnet
- **Judge models**: gpt-4o, claude-sonnet
- **Feature types**: provider, resource, utility, bug_fix, optimization, feature
- **Quality thresholds**: minimum 80, excellent 90
- **Test suites**: 
  - simple_provider (2 experiments)
  - resource_extension (1 experiment)
  - bug_fix (1 experiment)
  - quality_comparison (3 experiments)
- **Grading criteria**: correctness (40%), quality (30%), practices (20%), maintainability (10%)

**Use with**:
```bash
python generate_experiments.py suite simple_provider
```

---

## Documentation Files

### 3. README.md
**Lines**: 368  
**Purpose**: Complete guide to self-building capability

**Sections**:
- Vision and philosophy
- 6-level progression path
- Quick start guide
- Experiment structure
- Quality evaluation (100-point scale)
- Safety mechanisms
- Test suites
- Usage examples
- Metrics & success criteria
- Roadmap

---

### 4. QUICKSTART.md
**Lines**: 356  
**Purpose**: 5-minute getting started guide

**Covers**:
- Prerequisites setup
- Running first experiment
- Reviewing output
- Applying generated code
- Testing new provider
- Verifying auto-discovery
- Troubleshooting
- Best practices

**Perfect for**: First-time users

---

### 5. PROGRESSION.md
**Lines**: 355  
**Purpose**: Detailed progression path from simple to self-optimization

**Levels**:
1. **Simple Provider** (Current) - Echo provider generation
2. **Resource Extension** - Add resources to providers
3. **Utility Functions** - Generate helpers
4. **Bug Fixes** - Automated test fixing
5. **NL to Features** - Natural language to code
6. **Self-Optimization** - Performance improvements

**Each level includes**:
- Capability description
- Complexity rating
- Implementation timeline
- Example code
- Success criteria

---

## File Statistics

```
Specification:      780 lines (outline/13)
Experiments:        268 lines (add-echo-provider.aicl)
Test Variables:     201 lines (test-self-build-variables.yaml)
Documentation:    1,079 lines (README + QUICKSTART + PROGRESSION)
────────────────────────────────────────────────
Total:           2,328 lines (self-build specific)

Combined with outline specs: 6,610 lines total
```

---

## Directory Structure

```
experiments/self-build/
├── add-echo-provider.aicl          # Main experiment
├── test-self-build-variables.yaml  # Test parameters
├── README.md                        # Complete guide
├── QUICKSTART.md                    # Getting started
├── PROGRESSION.md                   # Progression path
└── FILES.md                         # This file

outline/
└── 13-self-modification-experiments.md  # Technical spec

Generated output (after running):
providers/echo/
├── server.py         # Generated provider code
├── config.yaml       # Generated config
└── test_echo.py      # Generated tests
```

---

## Quick Reference

### Run Experiment
```bash
python run.py experiments/self-build/add-echo-provider.aicl
```

### Generate Test Suite
```bash
python generate_experiments.py suite simple_provider
```

### Apply Generated Code
```bash
# Review output first, then copy files shown in output
mkdir -p providers/echo
# Copy generated code from experiment output
```

### Test New Provider
```bash
pytest providers/echo/test_echo.py -v
```

---

## Next Steps

1. **Run the example**: Start with add-echo-provider.aicl
2. **Review the docs**: Read QUICKSTART.md
3. **Understand progression**: Read PROGRESSION.md
4. **Explore specs**: Study outline/13
5. **Create your own**: Write custom specifications
6. **Contribute**: Share successful patterns

---

*These files represent the foundation for AICL's self-building capability - enabling AI systems that improve themselves.*
