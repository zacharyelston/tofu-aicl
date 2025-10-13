# Matrix Experiment System Specification

## Overview

The matrix experiment system enables systematic testing of AI configurations by:
1. Defining test variables and ranges
2. Auto-generating AICL configurations
3. Executing experiments in parallel
4. Collecting comprehensive metrics
5. Grading results with LLM-as-Judge
6. Comparing performance

---

## Test Variables Definition

### YAML Structure: test-variables.yaml

```yaml
# Metadata
experiment:
  name: string
  description: string
  tags: [string]

# Chat model testing
chat_models:
  models:
    - name: string              # Model catalog ID
  
  # Parameters
  temperature:
    min: float
    max: float
    step: float
  
  max_tokens:
    values: [int]
  
  top_p:
    values: [float]
  
  frequency_penalty:
    values: [float]
  
  presence_penalty:
    values: [float]

# Embedding model testing
embedding_models:
  models:
    - name: string              # Model catalog ID

# RAG parameters
rag:
  retrieval:
    top_k:
      values: [int]
    rerank: [bool]
    namespaces: [string]
  
  chunking:
    chunk_size:
      values: [int]
    overlap:
      values: [int]
    separators:
      values: [[string]]

# Prompts/queries
prompts:
  - string
  - string

# Expected answers (for grading)
expected_answers:
  - string
  - string

# Grading configuration
grading:
  judge_model: string           # Model catalog ID for LLM-as-Judge
  criteria:
    - relevance
    - accuracy
    - completeness
```

---

## Template System

### AICL Template with Placeholders

```hcl
# template_rag.aicl
variable "model_name" {
  default = "{{ model_name }}"
}

variable "temperature" {
  default = {{ temperature }}
}

variable "top_k" {
  default = {{ top_k }}
}

provider "openai" {
  api_key = env("OPENAI_API_KEY")
}

resource "llm_completion" "answer" {
  provider    = provider.openai
  model       = var.model_name
  temperature = var.temperature
  
  prompt = "{{ prompt }}"
}

output "response" {
  value = resource.llm_completion.answer.content
}
```

### Template Expansion

```python
def expand_template(template: str, variables: dict) -> str:
    """Expand Jinja2-style placeholders"""
    from jinja2 import Template
    
    t = Template(template)
    return t.render(**variables)

# Example
template = 'model = "{{ model_name }}"'
variables = {"model_name": "gpt-4o-mini"}
result = expand_template(template, variables)
# result: 'model = "gpt-4o-mini"'
```

---

## Experiment Generation

### Generation Algorithm

```python
def generate_experiments(template_path: str, variables_path: str) -> List[str]:
    """Generate AICL configurations from template and variables"""
    
    # Load template
    with open(template_path) as f:
        template = f.read()
    
    # Load variables
    with open(variables_path) as f:
        variables = yaml.safe_load(f)
    
    # Generate combinations
    combinations = generate_variable_combinations(variables)
    
    # Expand template for each combination
    configs = []
    for combo in combinations:
        config = expand_template(template, combo)
        configs.append(config)
    
    return configs

def generate_variable_combinations(variables: dict) -> List[dict]:
    """Generate all combinations of variable values"""
    from itertools import product
    
    # Extract variable ranges
    var_lists = {}
    
    # Chat models
    if 'chat_models' in variables:
        models = [m['name'] for m in variables['chat_models']['models']]
        var_lists['model_name'] = models
        
        # Temperature range
        if 'temperature' in variables['chat_models']:
            temp_config = variables['chat_models']['temperature']
            temps = generate_range(
                temp_config['min'],
                temp_config['max'],
                temp_config.get('step', 0.1)
            )
            var_lists['temperature'] = temps
    
    # RAG parameters
    if 'rag' in variables:
        top_k_values = variables['rag']['retrieval']['top_k']['values']
        var_lists['top_k'] = top_k_values
    
    # Prompts
    if 'prompts' in variables:
        var_lists['prompt'] = variables['prompts']
    
    # Generate Cartesian product
    keys = list(var_lists.keys())
    value_lists = [var_lists[k] for k in keys]
    
    combinations = []
    for values in product(*value_lists):
        combo = dict(zip(keys, values))
        combinations.append(combo)
    
    return combinations
```

---

## Execution Engine

### Parallel Execution

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def execute_experiments(
    configs: List[str],
    max_parallel: int = 5,
    storage: StorageBackend = None
) -> List[ExperimentResult]:
    """Execute experiments in parallel"""
    
    results = []
    
    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        # Submit all experiments
        futures = {
            executor.submit(execute_single, cfg, storage): cfg 
            for cfg in configs
        }
        
        # Collect results as they complete
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                
                # Log progress
                print(f"[{len(results)}/{len(configs)}] "
                      f"{result.model} @ temp={result.temperature} "
                      f"✓ ({result.duration_ms}ms, ${result.cost:.4f})")
                
            except Exception as e:
                print(f"Experiment failed: {e}")
    
    return results

def execute_single(
    config: str,
    storage: StorageBackend
) -> ExperimentResult:
    """Execute a single experiment"""
    
    # Parse and run AICL config
    engine = AICLEngine()
    state = engine.run(config)
    
    # Extract metrics
    result = ExperimentResult(
        configuration=config,
        output=state.outputs,
        duration_ms=state.duration_ms,
        total_tokens=state.total_tokens,
        cost=state.total_cost,
        timestamp=datetime.now()
    )
    
    # Store result
    if storage:
        storage.store_result(result)
    
    return result
```

---

## LLM-as-Judge Grading

### Grading Prompt Template

```python
JUDGE_PROMPT_TEMPLATE = """
You are an expert judge evaluating AI system responses.

QUESTION: {question}

EXPECTED ANSWER: {expected_answer}

ACTUAL ANSWER: {actual_answer}

Evaluate the actual answer on these criteria:
1. Relevance (0-10): Does it address the question?
2. Accuracy (0-10): Is the information correct?
3. Completeness (0-10): Does it fully answer the question?

Provide your evaluation in JSON format:
{{
  "relevance": <score>,
  "accuracy": <score>,
  "completeness": <score>,
  "overall": <average>,
  "reasoning": "<brief explanation>"
}}
"""
```

### Grading Implementation

```python
def grade_result(
    result: ExperimentResult,
    question: str,
    expected_answer: str,
    judge_model: str = "openrouter-mistral-large"
) -> QualityScore:
    """Grade experiment result with LLM-as-Judge"""
    
    # Build grading prompt
    prompt = JUDGE_PROMPT_TEMPLATE.format(
        question=question,
        expected_answer=expected_answer,
        actual_answer=result.output
    )
    
    # Call judge model
    judge_response = call_llm(
        model=judge_model,
        prompt=prompt,
        temperature=0.0  # Deterministic grading
    )
    
    # Parse scores
    scores = json.loads(judge_response)
    
    # Create quality score object
    quality_score = QualityScore(
        result_id=result.id,
        judge_model=judge_model,
        overall_score=scores['overall'],
        relevance_score=scores['relevance'],
        accuracy_score=scores['accuracy'],
        completeness_score=scores['completeness'],
        judge_reasoning=scores['reasoning'],
        judge_raw_output=judge_response
    )
    
    return quality_score
```

---

## Test Suites

### Pre-Configured Suites

#### 1. Smoke Test (Quick Validation)

```yaml
# suites/smoke_test.yaml
experiment:
  name: Smoke Test
  description: Quick validation (2-5 minutes)

chat_models:
  models:
    - name: "gpt-4o-mini"
  temperature:
    values: [0.0, 0.7]

prompts:
  - "What is machine learning?"
```

**Result**: 1 model × 2 temps × 1 prompt = 2 experiments

---

#### 2. Comprehensive Test (Full Evaluation)

```yaml
# suites/comprehensive_test.yaml
experiment:
  name: Comprehensive Test
  description: Full evaluation (30-60 minutes)

chat_models:
  models:
    - name: "gpt-4o"
    - name: "gpt-4o-mini"
    - name: "openrouter-claude-sonnet"
  
  temperature:
    min: 0.0
    max: 1.0
    step: 0.5

prompts:
  - "What is machine learning?"
  - "Explain neural networks."
  - "What are transformers?"
```

**Result**: 3 models × 3 temps × 3 prompts = 27 experiments

---

#### 3. Cost Optimization Test

```yaml
# suites/cost_optimization.yaml
experiment:
  name: Cost Optimization
  description: Find best value (quality ≥7, lowest cost)

chat_models:
  models:
    # Only models with quality ≥7
    - name: "gpt-4o-mini"          # $0.15/1M
    - name: "openrouter-claude-haiku"  # $0.25/1M
  
  temperature:
    values: [0.3, 0.7]

prompts:
  - "Summarize: [text]"
```

---

#### 4. Quality Optimization Test

```yaml
# suites/quality_optimization.yaml
experiment:
  name: Quality Optimization
  description: Maximize quality (30-45 minutes)

chat_models:
  models:
    # Top quality models only
    - name: "gpt-4o"               # Quality: 9.5/10
    - name: "openrouter-claude-sonnet"  # Quality: 9.7/10
  
  temperature:
    min: 0.0
    max: 0.5
    step: 0.25

prompts:
  - "Complex reasoning task..."
```

---

## Metrics Collection

### Per-Experiment Metrics

```python
class ExperimentMetrics:
    # Execution
    duration_ms: int
    started_at: datetime
    completed_at: datetime
    
    # Usage
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    # Cost
    input_cost: float
    output_cost: float
    total_cost: float
    
    # Quality
    quality_score: float
    relevance: float
    accuracy: float
    completeness: float
    
    # Configuration
    model: str
    temperature: float
    max_tokens: int
    # ... other parameters
```

---

## Comparative Analysis

### Analysis Functions

```python
def compare_by_cost(results: List[ExperimentResult]) -> List:
    """Sort by cost (ascending)"""
    return sorted(results, key=lambda r: r.cost)

def compare_by_quality(results: List[ExperimentResult]) -> List:
    """Sort by quality score (descending)"""
    return sorted(results, key=lambda r: r.quality_score, reverse=True)

def get_pareto_frontier(results: List[ExperimentResult]) -> List:
    """Get Pareto-optimal results (quality vs cost)"""
    frontier = []
    
    for r in sorted(results, key=lambda x: x.cost):
        # Add if no existing result has better quality at lower cost
        dominated = any(
            f.quality_score >= r.quality_score and f.cost <= r.cost
            for f in frontier
        )
        if not dominated:
            frontier.append(r)
    
    return frontier
```

### Summary Report

```python
def generate_summary(results: List[ExperimentResult]) -> str:
    """Generate experiment summary report"""
    
    total = len(results)
    total_cost = sum(r.cost for r in results)
    avg_quality = sum(r.quality_score for r in results) / total
    avg_latency = sum(r.duration_ms for r in results) / total
    
    best_quality = max(results, key=lambda r: r.quality_score)
    best_value = max(results, key=lambda r: r.quality_score / r.cost)
    cheapest = min(results, key=lambda r: r.cost)
    
    return f"""
Experiment Summary
==================
Total Experiments: {total}
Total Cost: ${total_cost:.4f}
Avg Quality: {avg_quality:.2f}/10
Avg Latency: {avg_latency:.0f}ms

Best Quality: {best_quality.model} @ temp={best_quality.temperature}
  Score: {best_quality.quality_score:.2f}/10
  Cost: ${best_quality.cost:.4f}

Best Value: {best_value.model} @ temp={best_value.temperature}
  Quality/Cost Ratio: {best_value.quality_score / best_value.cost:.2f}

Cheapest: {cheapest.model} @ temp={cheapest.temperature}
  Cost: ${cheapest.cost:.4f}
  Quality: {cheapest.quality_score:.2f}/10
"""
```
