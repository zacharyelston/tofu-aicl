#!/bin/bash
# Naga Embedding Comparison - 3 embeddings x 2 questions = 6 experiments
# Run sequentially with delays to avoid provider conflicts

set -e

EMBEDDINGS=("text-embedding-3-small:1536" "text-embedding-3-large:3072" "gemini-embedding-001:3072")
QUESTIONS=(
  "What is the role of the Evaluator component in the AICL framework?"
  "How does the Planner handle resource dependencies?"
)

CHAT_MODEL="gpt-4o-2024-08-06"
JUDGE_MODEL="mistralai/mistral-large"

mkdir -p experiments/naga_embedding_results
RESULTS_FILE="experiments/naga_embedding_results/results_$(date +%Y%m%d_%H%M%S).json"

echo "[" > "$RESULTS_FILE"
FIRST=true

echo ""
echo "🚀 Naga Embedding Comparison"
echo "   Embeddings: ${#EMBEDDINGS[@]}"
echo "   Questions: ${#QUESTIONS[@]}"
echo "   Chat Model: $CHAT_MODEL (via Naga)"
echo "   Judge: $JUDGE_MODEL (via OpenRouter)"
echo ""

for EMB_INFO in "${EMBEDDINGS[@]}"; do
  IFS=':' read -r EMB_MODEL EMB_DIMS <<< "$EMB_INFO"
  
  for Q_IDX in "${!QUESTIONS[@]}"; do
    QUESTION="${QUESTIONS[$Q_IDX]}"
    EXP_ID="${EMB_MODEL//./-}-q$((Q_IDX+1))"
    
    echo "🔄 [$EXP_ID] $EMB_MODEL (${EMB_DIMS}d)..."
    
    # Create AICL config
    cat << EOF > "experiments/naga_embedding_results/${EXP_ID}.aicl"
terraform {
  required_providers {
    naga = { source = "aicl/naga" }
    pinecone = { source = "aicl/pinecone" }
  }
}

resource "naga_embedding" "question_vector" {
  model = "$EMB_MODEL"
  text = "$(echo "$QUESTION" | sed 's/"/\\"/g')"
  aiclResourceName = "question_vector"
}

resource "query" "results" {
  index_name = "tofu-aicl"
  namespace = "tofu-aicl-codebase"
  top_k = 5
  vector = "\${resource.naga_embedding.question_vector.attributes.embeddings[0].values}"
  aiclResourceName = "results"
}

resource "naga_chat" "answer" {
  model = "$CHAT_MODEL"
  messages = [
    {
      role = "user"
      content = "Question: $(echo "$QUESTION" | sed 's/"/\\"/g')\n\nContext: \${resource.query.results.attributes.matches}\n\nProvide a detailed answer based on the context."
    }
  ]
  max_tokens = 500
  temperature = 0.7
  aiclResourceName = "answer"
}
EOF
    
    # Run experiment
    START_TIME=$(date +%s)
    if timeout 60 python run.py "experiments/naga_embedding_results/${EXP_ID}.aicl" > /dev/null 2>&1; then
      END_TIME=$(date +%s)
      ELAPSED=$((END_TIME - START_TIME))
      
      # Extract answer from state
      ANSWER=$(cat terraform.tfstate.d/default-exp.tfstate | python3 -c "import sys, json; state=json.load(sys.stdin); print(state['resources'].get('naga_chat-answer', {}).get('attributes', {}).get('response', 'No answer'))" 2>/dev/null || echo "No answer")
      TOKENS=$(cat terraform.tfstate.d/default-exp.tfstate | python3 -c "import sys, json; state=json.load(sys.stdin); print(state['resources'].get('naga_chat-answer', {}).get('attributes', {}).get('usage', {}).get('total_tokens', 0))" 2>/dev/null || echo "0")
      
      echo "   ✅ Complete in ${ELAPSED}s | Tokens: $TOKENS"
      
      # Grade with Mistral Large
      GRADING_PROMPT="Evaluate this AI answer:\n\nQuestion: $QUESTION\nAnswer: $ANSWER\n\nScore 1-10 based on accuracy, completeness, clarity.\n\nFormat:\nScore: [number]\nJustification: [brief]"
      
      JUDGE_RESPONSE=$(curl -s -X POST https://openrouter.ai/api/v1/chat/completions \
        -H "Authorization: Bearer $OPENROUTER_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"$JUDGE_MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"$GRADING_PROMPT\"}]}" | \
        python3 -c "import sys, json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo "Score: 0\nJustification: Grading failed")
      
      SCORE=$(echo "$JUDGE_RESPONSE" | grep -oP 'Score:\s*\K[\d.]+' | head -1 || echo "0")
      
      echo "   📊 Quality Score: $SCORE/10"
      
      # Add to results
      if [ "$FIRST" = false ]; then
        echo "," >> "$RESULTS_FILE"
      fi
      FIRST=false
      
      cat << JSONEOF >> "$RESULTS_FILE"
  {
    "exp_id": "$EXP_ID",
    "embedding": "$EMB_MODEL",
    "dimensions": $EMB_DIMS,
    "question": $(echo "$QUESTION" | python3 -c "import sys, json; print(json.dumps(sys.stdin.read().strip()))"),
    "answer": $(echo "$ANSWER" | python3 -c "import sys, json; print(json.dumps(sys.stdin.read().strip()))"),
    "quality_score": $SCORE,
    "judge_feedback": $(echo "$JUDGE_RESPONSE" | python3 -c "import sys, json; print(json.dumps(sys.stdin.read().strip()))"),
    "tokens": $TOKENS,
    "time": $ELAPSED,
    "success": true
  }
JSONEOF
      
    else
      echo "   ❌ Failed or timed out"
    fi
    
    # Wait before next experiment
    sleep 2
  done
done

echo "]" >> "$RESULTS_FILE"

echo ""
echo "💾 Results saved: $RESULTS_FILE"
echo ""

# Print summary
python3 << 'PYEOF'
import json

with open('$RESULTS_FILE') as f:
    results = json.load(f)

successful = [r for r in results if r.get('success')]

if successful:
    print("="*80)
    print("📊 NAGA EMBEDDING COMPARISON RESULTS")
    print("="*80)
    
    by_emb = {}
    for r in successful:
        emb = r['embedding']
        if emb not in by_emb:
            by_emb[emb] = []
        by_emb[emb].append(r)
    
    stats = []
    for emb, res_list in by_emb.items():
        scores = [r['quality_score'] for r in res_list if r.get('quality_score')]
        if scores:
            stats.append({
                'embedding': emb,
                'dims': res_list[0]['dimensions'],
                'avg_score': sum(scores) / len(scores),
                'min_score': min(scores),
                'max_score': max(scores)
            })
    
    stats.sort(key=lambda x: x['avg_score'], reverse=True)
    
    print("\n🏆 EMBEDDING MODEL RANKINGS\n")
    print(f"{'Rank':<6} {'Embedding':<30} {'Dims':<8} {'Score':<8} {'Range'}")
    print("-" * 70)
    
    for i, stat in enumerate(stats):
        medal = ['🥇', '🥈', '🥉'][i] if i < 3 else f"{i+1}"
        print(f"{medal:<6} {stat['embedding']:<30} {stat['dims']:<8} "
              f"{stat['avg_score']:.1f}/10  {stat['min_score']:.1f}-{stat['max_score']:.1f}")
    
    if stats:
        winner = stats[0]
        print(f"\n🎯 WINNER: {winner['embedding']}")
        print(f"   Dimensions: {winner['dims']}")
        print(f"   Average Quality: {winner['avg_score']:.1f}/10")
    
    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    print("="*80)
PYEOF
