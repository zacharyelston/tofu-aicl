# AICL MCP Server for Windsurf

This guide shows you how to connect the AICL RAG system to Windsurf using the Model Context Protocol (MCP).

## What This Enables

Once configured, you can use these AI-powered tools directly in Windsurf:

- **`query_codebase`** - Ask questions about AICL architecture and get AI-generated answers
- **`run_aicl_config`** - Execute AICL configuration files from Windsurf
- **`list_aicl_examples`** - Browse available example configurations
- **`get_provider_info`** - Get documentation on available providers

## Prerequisites

- Windsurf editor installed
- This AICL project cloned locally
- Python 3.11+ with `mcp` package installed (already done via `uv`)

## Setup Steps

### 1. Find Windsurf MCP Configuration

Windsurf stores MCP server configurations in:

**macOS:**
```
~/Library/Application Support/Windsurf/mcp_config.json
```

**Windows:**
```
%APPDATA%\Windsurf\mcp_config.json
```

**Linux:**
```
~/.config/Windsurf/mcp_config.json
```

### 2. Add AICL MCP Server

Edit the `mcp_config.json` file and add the AICL server:

```json
{
  "mcpServers": {
    "aicl-rag": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/your/aicl/project",
        "run",
        "mcp_server.py"
      ],
      "env": {
        "OPENROUTER_API_KEY": "your-openrouter-key-here",
        "PINECONE_API_KEY": "your-pinecone-key-here",
        "PINECONE_HOST_URL": "your-pinecone-url-here"
      }
    }
  }
}
```

**Important:** Replace `/absolute/path/to/your/aicl/project` with the actual absolute path to this project directory.

### 3. Configure Environment Variables

You have two options for API keys:

#### Option A: Inline in config (shown above)
Add them directly to the `env` section of the config.

#### Option B: Use existing environment
Remove the `env` section and ensure your shell has these variables:
```bash
export OPENROUTER_API_KEY="your-key"
export PINECONE_API_KEY="your-key"
export PINECONE_HOST_URL="your-url"
```

### 4. Restart Windsurf

Close and reopen Windsurf completely for the changes to take effect.

## Using AICL Tools in Windsurf

### Query the Codebase

Ask Cascade (Windsurf AI) questions like:
```
Use the query_codebase tool to ask: "What are the main components of AICL?"
```

### Run a Configuration

```
Use the run_aicl_config tool to execute demo_simple.aicl
```

### List Examples

```
Use the list_aicl_examples tool to see what configurations are available
```

### Get Provider Documentation

```
Use the get_provider_info tool to learn about available providers
```

## Example Workflow

1. **Explore**: `list_aicl_examples` → See available configs
2. **Learn**: `get_provider_info` → Understand what each provider does
3. **Query**: `query_codebase("How does the executor work?")` → Get AI answers
4. **Execute**: `run_aicl_config("demo_simple.aicl")` → Run a configuration
5. **Build**: Create your own `.aicl` files and run them via Windsurf!

## Troubleshooting

### Server Not Appearing in Windsurf

1. Check the config file syntax (valid JSON)
2. Verify the absolute path is correct
3. Ensure `uv` is in your system PATH
4. Check Windsurf logs: Help → Toggle Developer Tools → Console

### Tool Execution Fails

1. Verify environment variables are set correctly
2. Check that `mcp` package is installed: `uv pip list | grep mcp`
3. Test the server directly: `uv run mcp_server.py`

### API Key Issues

Ensure your Replit Secrets or environment variables include:
- `OPENROUTER_API_KEY` - For AI model access
- `PINECONE_API_KEY` - For vector database (if using RAG)
- `PINECONE_HOST_URL` - Pinecone endpoint (if using RAG)

## Advanced Usage

### Custom AICL Configurations

You can create your own `.aicl` files and run them via the MCP server:

```hcl
# my_custom.aicl
terraform {
  required_providers {
    openrouter = {
      source = "aicl/openrouter"
    }
  }
}

resource "chat" "code_review" {
  model = "anthropic/claude-3.5-sonnet"
  messages = [
    {
      role = "user"
      content = "Review this code for security issues: ${file('main.py')}"
    }
  ]
  max_tokens = 1000
}
```

Then in Windsurf:
```
Use run_aicl_config to execute my_custom.aicl
```

### Extending the MCP Server

The `mcp_server.py` file is fully customizable. Add new tools by:

1. Opening `mcp_server.py`
2. Adding a new function with `@mcp.tool()` decorator
3. Restart Windsurf to load the new tool

Example:
```python
@mcp.tool()
async def analyze_code(file_path: str) -> str:
    """Analyze a code file using AICL AI providers."""
    # Your implementation
    return result
```

## Architecture

```
┌─────────────┐
│  Windsurf   │
│   (Editor)  │
└──────┬──────┘
       │ MCP Protocol
       ↓
┌─────────────┐
│ mcp_server  │
│   (Python)  │
└──────┬──────┘
       │ subprocess
       ↓
┌─────────────┐
│ AICL Engine │
│  (run.py)   │
└──────┬──────┘
       │
       ↓
┌──────────────────┐
│ Providers (gRPC) │
│ - openrouter     │
│ - file_loader    │
│ - pinecone       │
└──────────────────┘
```

## Resources

- **MCP Documentation**: https://modelcontextprotocol.io
- **Windsurf**: https://codeium.com/windsurf
- **AICL Project**: See README.md in this repository

## Support

For issues with:
- **AICL Engine**: Check logs in `/tmp/logs/`
- **MCP Server**: Run `uv run mcp_server.py` to test
- **Windsurf**: Check Developer Tools → Console for MCP errors
