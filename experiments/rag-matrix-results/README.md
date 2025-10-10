# RAG Testing with Docker

This directory contains portable Docker-based RAG testing setup for tofu-aicl.

## Quick Start

### Prerequisites
- Docker installed
- API keys for OpenAI, Anthropic, and Pinecone

### Setup Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-east-1
```

### Run RAG Tests

```bash
# Build the Docker image
docker compose -f docker-compose.rag.yml build

# Run tests with your questions
docker compose -f docker-compose.rag.yml run --rm rag-test

# Or run directly with Docker
docker build -f Dockerfile.rag -t tofu-aicl-rag .
docker run --rm \
  --env-file .env \
  -v $(pwd)/experiments:/app/experiments \
  -v $(pwd)/questions.txt:/app/questions.txt \
  tofu-aicl-rag python scripts/test_rag_query.py questions.txt
```

## Configuration

Edit `rag-config.yaml` to customize:
- Pinecone index settings
- Models to compare (Claude, GPT-4, etc.)
- Number of retrieved chunks
- Embedding model

## Output

Results are saved to `experiments/` directory:
- `rag_test_results.json` - Latest results in JSON
- `rag_test_results.md` - Latest results in Markdown
- `rag_test_<id>.json` - Individual test runs
- `rag_test_<id>.md` - Individual test runs in Markdown

## Questions File Format

Create `questions.txt` with one question per line:

```
What is the role of the StateManager?
How does the parsing flow work?
Explain the provider protocol.
```

## Example Results

The system will:
1. Embed your question
2. Search Pinecone for relevant code chunks
3. Query multiple LLMs with RAG context
4. Compare responses with an LLM judge
5. Save detailed comparison results

## Troubleshooting

### Missing API Keys
Ensure all required environment variables are set in `.env`

### Empty Results
Check Pinecone index has been populated:
```bash
python scripts/load_codebase_to_pinecone.py
```

### Permission Errors
Ensure experiments directory is writable:
```bash
chmod -R 755 experiments
```
