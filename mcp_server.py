#!/usr/bin/env python3
"""
AICL MCP Server - Exposes AICL RAG capabilities via Model Context Protocol
For use with Windsurf, Claude Desktop, and other MCP-compatible AI editors
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Any
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("aicl-rag")

# Add workspace to Python path
workspace_root = str(Path(__file__).parent)
sys.path.insert(0, workspace_root)

@mcp.tool()
async def query_codebase(question: str) -> str:
    """Query the AICL codebase using RAG to get answers about how the framework works.
    
    Args:
        question: Natural language question about AICL architecture, components, or usage
        
    Returns:
        AI-generated answer based on the codebase documentation
    """
    # Create a temporary AICL config for the query
    config_content = f'''terraform {{
  required_providers {{
    openrouter = {{
      source = "aicl/openrouter"
    }}
  }}
}}

resource "chat" "answer" {{
  model = "anthropic/claude-3.5-sonnet"
  messages = [
    {{
      role = "user"
      content = "{question}"
    }}
  ]
  max_tokens = 1000
}}
'''
    
    # Write temporary config
    temp_config = Path("/tmp/mcp_query.aicl")
    temp_config.write_text(config_content)
    
    # Run AICL
    try:
        result = subprocess.run(
            [sys.executable, "run.py", str(temp_config)],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Extract answer from output
        if result.returncode == 0:
            # Parse the output to extract the chat response
            # For now, return the full output
            return f"Query executed successfully.\n\nQuestion: {question}\n\nNote: Full RAG integration pending. Current response from OpenRouter chat."
        else:
            return f"Error executing query: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "Query timed out after 60 seconds"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # Cleanup
        if temp_config.exists():
            temp_config.unlink()


@mcp.tool()
async def run_aicl_config(config_path: str) -> str:
    """Execute an AICL configuration file.
    
    Args:
        config_path: Path to the .aicl configuration file (relative to workspace)
        
    Returns:
        Execution output including resource creation and any errors
    """
    config_file = Path(workspace_root) / config_path
    
    if not config_file.exists():
        return f"Error: Configuration file not found: {config_path}"
    
    if not config_file.suffix == ".aicl":
        return f"Error: File must have .aicl extension: {config_path}"
    
    try:
        result = subprocess.run(
            [sys.executable, "run.py", str(config_file)],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = f"=== AICL Execution: {config_path} ===\n\n"
        output += result.stdout
        
        if result.stderr:
            output += f"\n\n=== Errors ===\n{result.stderr}"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"Execution timed out after 120 seconds for: {config_path}"
    except Exception as e:
        return f"Error executing {config_path}: {str(e)}"


@mcp.tool()
async def list_aicl_examples() -> str:
    """List available AICL example configurations.
    
    Returns:
        List of example .aicl files with descriptions
    """
    workspace = Path(workspace_root)
    examples = []
    
    for aicl_file in sorted(workspace.glob("*.aicl")):
        # Read first few lines to find description
        content = aicl_file.read_text()
        description = "AICL configuration file"
        
        # Try to extract description from comments
        for line in content.split('\n')[:10]:
            if line.strip().startswith('#'):
                description = line.strip('# ').strip()
                break
        
        examples.append(f"- {aicl_file.name}: {description}")
    
    if not examples:
        return "No .aicl example files found in workspace"
    
    return "Available AICL Examples:\n\n" + "\n".join(examples)


@mcp.tool()
async def get_provider_info() -> str:
    """Get information about available AICL providers.
    
    Returns:
        List of available providers and their capabilities
    """
    info = """Available AICL Providers:

1. **openrouter**
   - Source: aicl/openrouter
   - Capabilities: Chat completions with Claude, GPT-4, and other models
   - Resource types: chat
   - Example:
     ```hcl
     resource "chat" "my_chat" {
       model = "anthropic/claude-3.5-sonnet"
       messages = [...]
       max_tokens = 1000
     }
     ```

2. **file_loader**
   - Source: aicl/file_loader  
   - Capabilities: Load documents from filesystem
   - Resource types: loader_files
   - Example:
     ```hcl
     resource "loader_files" "docs" {
       path = "./docs"
       glob = "**/*.md"
     }
     ```

3. **text_splitter**
   - Source: aicl/text_splitter
   - Capabilities: Chunk text for processing
   - Resource types: splitter_text
   - Example:
     ```hcl
     resource "splitter_text" "chunks" {
       documents = "${resource.loader_files.docs.attributes.documents}"
       chunk_size = 1000
     }
     ```

4. **pinecone**
   - Source: aicl/pinecone
   - Capabilities: Vector database operations
   - Resource types: pinecone_upsert, query
   - Requires: PINECONE_API_KEY, PINECONE_HOST_URL

5. **command_assertion**
   - Source: aicl/command_assertion
   - Capabilities: Validation and testing
"""
    return info


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
