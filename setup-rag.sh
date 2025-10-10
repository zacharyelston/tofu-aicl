#!/bin/bash
set -e

echo "=========================================="
echo "RAG Testing Setup for tofu-aicl"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file template..."
    cat > .env << 'EOF'
# OpenAI API Key for embeddings
OPENAI_API_KEY=sk-...

# Anthropic API Key for Claude models
ANTHROPIC_API_KEY=sk-ant-...

# Pinecone Configuration
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-east-1
EOF
    echo "✅ Created .env file - Please add your API keys"
    echo ""
else
    echo "✅ .env file exists"
    echo ""
fi

# Check if questions.txt exists
if [ ! -f questions.txt ]; then
    echo "Creating sample questions.txt..."
    cat > questions.txt << 'EOF'
# RAG Test Questions
# One question per line, lines starting with # are ignored

How does the HCL evaluator resolve interpolations?
What is the role of the StateManager?
Explain the parsing flow from HCL input to executable plan.
EOF
    echo "✅ Created questions.txt with sample questions"
    echo ""
else
    echo "✅ questions.txt exists"
    echo ""
fi

# Create experiments directory
mkdir -p experiments
echo "✅ Created experiments/ directory"
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Edit .env and add your API keys:"
echo "   - OPENAI_API_KEY"
echo "   - ANTHROPIC_API_KEY"
echo "   - PINECONE_API_KEY"
echo ""
echo "2. Choose your preferred method:"
echo ""
echo "   Docker (Recommended - Portable):"
echo "   $ docker compose -f docker-compose.rag.yml build"
echo "   $ docker compose -f docker-compose.rag.yml run --rm rag-test"
echo ""
echo "   Local Python:"
echo "   $ uv sync"
echo "   $ python scripts/test_rag_query.py questions.txt"
echo ""
echo "3. View results in experiments/ directory"
echo ""
