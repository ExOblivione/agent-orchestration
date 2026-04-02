"""
Tool Template - Define custom tools for agents using the Microsoft Agent Framework

This template demonstrates how to:
1. Define tools with the @tool decorator
2. Add parameter descriptions using Annotated and Field
3. Configure tool approval modes
4. Wire tools into an agent
5. Run the agent with tool capabilities

Source: https://github.com/microsoft/agent-framework/blob/main/python/samples/01-get-started/02_add_tools.py
"""

import asyncio
from typing import Annotated

from agent_framework import tool
from pydantic import Field


# ============================================================================
# Tool Definitions
# ============================================================================

# NOTE: Use approval_mode="never_require" for tools that can be executed without user confirmation.
# Use "always_require" in production for user confirmation before tool execution.
@tool(approval_mode="never_require")
def example_tool(
    parameter_name: Annotated[str, Field(description="Description of what this parameter is for.")],
) -> str:
    """
    Brief description of what this tool does.
    
    This docstring will be used by the LLM to understand when to call this tool.
    Be clear and specific about the tool's purpose and behavior.
    """
    # Implement your tool logic here
    result = f"Processing '{parameter_name}'"
    return result


# ============================================================================
# Async Tool Example
# ============================================================================

@tool(approval_mode="never_require")
async def async_tool(
    query: Annotated[str, Field(description="The query to process.")],
) -> str:
    """
    Example of an async tool for I/O-bound operations.
    
    Use async tools for:
    - API calls
    - Database queries
    - File operations
    - Any I/O-bound work
    """
    await asyncio.sleep(0.1)  # Simulate async operation
    return f"Async result for: {query}"
