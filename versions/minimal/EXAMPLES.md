# Example Outputs - Minimal AICL

This document shows real execution output from the minimal AICL experiments.

## Example 1: Self-Build Experiment

**What it does**: AI generates its own provider code, then grades the quality

**Run it:**
```bash
cd versions/minimal
export NAGA_API_KEY='your-key'
python run.py self-build
```

**Output:**

```
======================================================================
  Running self-build
======================================================================

============================================================
MINIMAL AICL ENGINE - APPLY
============================================================

Starting naga provider on port 50052...
✓ naga provider ready

📋 Execution Plan: 2 resources

→ Creating naga_chat.generate_provider
  ✓ ready
→ Creating naga_chat.grade
  ✓ ready

💾 State saved to terraform.tfstate.d/default-minimal.tfstate

============================================================
✅ APPLY COMPLETE
============================================================

🧹 Cleaning up...
  ✓ Stopped naga provider
✅ Cleanup complete

======================================================================
  EXPERIMENT RESULTS
======================================================================

📊 naga_chat-grade
----------------------------------------------------------------------
{
  "score": 85,
  "grade": "ACCEPT",
  "strengths": [
    "Implements the required gRPC functionality correctly",
    "Code is clean, readable, and follows standard patterns"
  ],
  "issues": [
    "Error handling could be improved by validating the presence of 'config.text' before accessing it"
  ]
}

💰 Tokens: 401

======================================================================

✅ Experiment complete!

📁 Full state saved to: terraform.tfstate.d/default-minimal.tfstate
💡 View JSON: cat terraform.tfstate.d/default-minimal.tfstate | jq
```

**What happened:**
1. ✅ AI generated a complete Echo provider in Python
2. ✅ Another AI graded the code quality: **85/100 (ACCEPT)**
3. ✅ Identified strengths: correct gRPC implementation, clean code
4. ✅ Suggested improvement: better error handling
5. ✅ Total cost: 401 tokens (~$0.00006 with Naga)

---

## Example 2: Matrix Test Experiment

**What it does**: Compare 4 AI model variations (different temperature/token settings), then judge which is best

**Run it:**
```bash
cd versions/minimal
export NAGA_API_KEY='your-key'
python run.py matrix-test
```

**Output:**

```
======================================================================
  Running matrix-test
======================================================================

============================================================
MINIMAL AICL ENGINE - APPLY
============================================================

Starting naga provider on port 50052...
✓ naga provider ready

📋 Execution Plan: 5 resources

→ Creating naga_chat.test_low_temp
  ✓ ready
→ Creating naga_chat.test_mid_temp
  ✓ ready
→ Creating naga_chat.test_high_temp
  ✓ ready
→ Creating naga_chat.test_long
  ✓ ready
→ Creating naga_chat.compare
  ✓ ready

💾 State saved to terraform.tfstate.d/default-minimal.tfstate

============================================================
✅ APPLY COMPLETE
============================================================

🧹 Cleaning up...
  ✓ Stopped naga provider
✅ Cleanup complete

======================================================================
  EXPERIMENT RESULTS
======================================================================

📊 naga_chat-test_low_temp
----------------------------------------------------------------------
Recursion in programming can be understood through a simple real-world 
analogy: the process of nesting dolls, also known as Matryoshka dolls.

Imagine you have a set of Russian nesting dolls, where each doll contains 
a smaller doll inside it, and this continues until you reach the smallest 
doll, which is solid and contains nothing inside.

[Temperature: 0.2 - Very deterministic, precise]
💰 Tokens: 366

📊 naga_chat-test_mid_temp
----------------------------------------------------------------------
Recursion in programming can be understood through the analogy of a set 
of nesting dolls, often referred to as Matryoshka dolls.

Imagine you have a large, hollow doll that contains a smaller doll inside 
it. When you want to see the smaller doll, you open the larger one, and 
inside, you find another doll...

[Temperature: 0.7 - Balanced creativity and accuracy]
💰 Tokens: 345

📊 naga_chat-test_high_temp
----------------------------------------------------------------------
Recursion in programming is like a set of Russian dolls, where each doll 
contains a smaller doll inside it, and so on. The concept involves a 
function calling itself to solve smaller instances of the same problem 
until a base condition is met.

Imagine you are tasked with cleaning up a stack of books on a shelf...

[Temperature: 1.2 - More creative, less predictable]
💰 Tokens: 378

📊 naga_chat-test_long
----------------------------------------------------------------------
Recursion in programming can be compared to the process of nesting dolls, 
specifically the Russian Matryoshka dolls. Here's how the analogy works:

Imagine you have a large Russian doll that contains smaller dolls inside 
it. When you want to see all the dolls, you start by opening the largest 
doll, which reveals a smaller one inside it...

[Max Tokens: 300 - More detailed explanation]
💰 Tokens: 458

📊 naga_chat-compare (LLM-as-Judge Evaluation)
----------------------------------------------------------------------
{
  "winner": "B",
  "rankings": [
    {"response": "B", "score": 88, "best_for": "balance"},
    {"response": "D", "score": 86, "best_for": "depth"},
    {"response": "A", "score": 85, "best_for": "precision"},
    {"response": "C", "score": 82, "best_for": "creativity"}
  ],
  "insights": "Response B provides a well-balanced explanation that is 
  clear, accurate, and concise, making it the strongest overall. Response D 
  offers depth but is slightly longer, while A is precise but less engaging."
}

💰 Tokens: 1,864

======================================================================

✅ Experiment complete!

📁 Full state saved to: terraform.tfstate.d/default-minimal.tfstate
💡 View JSON: cat terraform.tfstate.d/default-minimal.tfstate | jq
```

**What happened:**
1. ✅ Asked same question to 4 different model configurations
2. ✅ **Response B (temp=0.7, 150 tokens) won: 88/100** - Best balance
3. ✅ Response D (temp=0.7, 300 tokens): 86/100 - Best for depth
4. ✅ Response A (temp=0.2, 150 tokens): 85/100 - Best for precision  
5. ✅ Response C (temp=1.2, 150 tokens): 82/100 - Best for creativity
6. ✅ Total cost: 3,411 tokens (~$0.00051 with Naga)

**Key Insight**: Temperature 0.7 with 150 tokens gives the best balance of clarity, accuracy, and engagement for this type of explanation.

---

## Understanding the Results

### Temperature Settings
- **0.2** (Low): Deterministic, precise, consistent
- **0.7** (Medium): Balanced creativity and accuracy ✅ **Winner**
- **1.2** (High): More creative, less predictable

### Token Limits
- **150 tokens**: Concise, focused answers
- **300 tokens**: More detailed, comprehensive explanations

### LLM-as-Judge
The final resource uses a separate AI to:
1. Compare all responses objectively
2. Score each on clarity, accuracy, creativity, conciseness
3. Identify which setting works best for which use case
4. Provide insights on tradeoffs

### Cost Analysis
With Naga.ai (50% cheaper than OpenAI):
- Self-build experiment: ~$0.00006 (401 tokens)
- Matrix test experiment: ~$0.00051 (3,411 tokens)
- **Total for both: ~$0.00057** (less than a tenth of a penny!)

---

## View Detailed Results

All results are saved as JSON:

```bash
cd versions/minimal
cat terraform.tfstate.d/default-minimal.tfstate | jq
```

**Example state structure:**
```json
{
  "version": 1,
  "resources": {
    "naga_chat-generate_provider": {
      "id": "naga_chat-generate_provider",
      "type": "naga_chat",
      "attributes": {
        "content": "#!/usr/bin/env python3\nimport grpc...",
        "usage": {
          "total_tokens": 401,
          "prompt_tokens": 120,
          "completion_tokens": 281
        }
      },
      "status": "ready"
    },
    "naga_chat-grade": {
      "id": "naga_chat-grade",
      "type": "naga_chat",
      "attributes": {
        "content": "{\"score\": 85, \"grade\": \"ACCEPT\", ...}",
        "usage": {"total_tokens": 401}
      },
      "status": "ready"
    }
  }
}
```

---

## Next Steps

### Modify the Experiments

**Change the question** (matrix-test.aicl):
```hcl
variable "test_question" {
  type    = string
  default = "Your custom question here"
}
```

**Add more variations**:
```hcl
resource "naga_chat" "test_very_creative" {
  model = "gpt-4o-mini"
  temperature = 1.5  # Even more creative!
  max_tokens = 200
  
  messages = [...]
  aiclResourceName = "test_very_creative"
}
```

**Use different models**:
```hcl
resource "naga_chat" "test_gpt4" {
  model = "gpt-4o"  # Higher quality, more expensive
  temperature = 0.7
  max_tokens = 150
  
  messages = [...]
  aiclResourceName = "test_gpt4"
}
```

### Create Your Own Experiment

1. Copy an existing `.aicl` file
2. Modify the resources and variables
3. Run: `python run.py <your-experiment-name>`

### Extend the Minimal Version

See `ARCHITECTURE.md` for:
- Adding new providers
- Integrating databases
- Adding metrics/observability
- Scaling to production

---

**Total Execution Time**: ~15-30 seconds per experiment  
**Total Cost**: Less than $0.001 for both experiments  
**Value**: Automated quality comparison and code generation
