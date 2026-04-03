# Advanced Features Guide

This guide explains how to use tools and human-in-the-loop feedback across different orchestration patterns.

## Architecture Overview

### Feature Placement

| Feature | Location | Applies To | Rationale |
|---------|----------|------------|-----------|
| **Tools** | `AgentTemplate` | Individual agents | Tools are agent-level capabilities |
| **Human Feedback** | Orchestrator classes | Workflows | Feedback pauses workflow execution |

## 1. Tools (Agent-Level Feature)

Tools are functions that agents can call during execution. They are configured at the **agent level** in `AgentTemplate`.

### Adding Tools to Agents

```python
from agent_framework import tool
from pydantic import Field
from typing import Annotated

# Define a tool using the @tool decorator
@tool
def search_database(
    query: Annotated[str, Field(description="Search query")],
    limit: Annotated[int, Field(description="Max results")] = 10
) -> str:
    """Search the product database."""
    # Implementation here
    return f"Found {limit} results for: {query}"

# Create agent with tools
agent = AgentTemplate(
    name="SalesAgent",
    instructions="You help customers find products.",
    tools=[search_database]  # Pass tools here
)
```

### Tools Work With ALL Orchestrations

Since tools are defined at the agent level, they automatically work with any orchestration pattern.

## 2. Human-in-the-Loop Feedback (Orchestration-Level Feature)

Human feedback pauses workflow execution to allow human intervention, approval, or input. This is configured at the **orchestration level**.

All three orchestrators support the same simple API:

```python
result = await orchestrator.run_with_human_feedback(
    initial_message="Your task",
    feedback_agent_names=["Agent1", "Agent2"]  # Optional: pause after these agents
)
```

### Sequential Orchestration with Feedback

```python
from src.sequential_template import SequentialOrchestrator

orchestrator = SequentialOrchestrator(
    agents=[researcher, coder, reviewer]
)

# Pause after specific agents for feedback
result = await orchestrator.run_with_human_feedback(
    initial_message="Create a user login API",
    feedback_agent_names=["Researcher", "Coder"]
)

# Or pause after every agent
result = await orchestrator.run_with_human_feedback(
    initial_message="Create a user login API",
    feedback_agent_names=None
)
```

### Concurrent Orchestration with Feedback

```python
from src.concurrent_template import ConcurrentOrchestrator

orchestrator = ConcurrentOrchestrator(
    agents=[market_researcher, legal_reviewer, tech_analyst]
)

result = await orchestrator.run_with_human_feedback(
    initial_message="Should we launch in EU market?",
    feedback_agent_names=["legal_reviewer"]
)
```

### Group Chat Orchestration with Feedback

```python
from src.groupchat_template import GroupChatOrchestrator

orchestrator = GroupChatOrchestrator(
    agents=[product_manager, tech_lead, designer]
)

result = await orchestrator.run_with_human_feedback(
    initial_message="Add real-time collaboration feature?",
    feedback_agent_names=["ProductManager", "TechLead"],
    verbose=True,
    limit=12
)
```

### Implementation Pattern

All feedback implementations follow the same simple pattern:

1. Build workflow with `.with_request_info(agents=...)` 
2. Process event stream handling both `request_info` and `output` events
3. Loop until no more pending responses
4. Return formatted output

The current implementation auto-approves all feedback requests. To customize:

```python
# Modify the process_event_stream helper in any orchestrator:
if event.type == "request_info":
    # Get user input
    user_input = input(f"Approve {event.request_id}? (y/n): ")
    if user_input.lower() == 'y':
        responses[event.request_id] = AgentRequestInfoResponse.approve()
    else:
        responses[event.request_id] = AgentRequestInfoResponse.reject("User rejected")
```

## 3. Available Methods Summary

### AgentTemplate
- `__init__(name, instructions, tools=None, ...)` - Create agent with optional tools
- `run(message, stream=False)` - Execute agent

### SequentialOrchestrator
- `run(initial_message)` - Basic execution
- `run_with_human_feedback(initial_message, feedback_agent_names=None)` - With pauses

### ConcurrentOrchestrator
- `run(initial_message)` - Basic execution
- `run_with_human_feedback(initial_message, feedback_agent_names=None)` - With pauses

### GroupChatOrchestrator
- `run(initial_message, verbose=False, limit=4)` - Basic execution
- `run_with_human_feedback(initial_message, feedback_agent_names=None, verbose=False, limit=4)` - With pauses

---

For more examples, see:
- [Tool Template](../src/tool_template.py) - Tool definition examples
- [Examples](../examples.py) - Complete orchestration examples
