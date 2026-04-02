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

@tool
def calculate_price(
    base_price: Annotated[float, Field(description="Base price")],
    discount: Annotated[float, Field(description="Discount percentage")] = 0
) -> float:
    """Calculate final price with discount."""
    return base_price * (1 - discount / 100)

# Create agent with tools
agent = AgentTemplate(
    name="SalesAgent",
    instructions="You help customers find products and calculate prices.",
    tools=[search_database, calculate_price]  # Pass tools here
)
```

### Tools Work With ALL Orchestrations

Since tools are defined at the agent level, they automatically work with any orchestration:

```python
# Sequential orchestration with tools
researcher = AgentTemplate(
    name="Researcher",
    instructions="Research products",
    tools=[search_database]
)

analyst = AgentTemplate(
    name="Analyst", 
    instructions="Analyze pricing",
    tools=[calculate_price]
)

sequential = SequentialOrchestrator(agents=[researcher, analyst])
await sequential.run("Find best laptop under $1000")

# Concurrent orchestration with tools
concurrent = ConcurrentOrchestrator(agents=[researcher, analyst])
await concurrent.run("Compare product options")

# Group chat orchestration with tools
group_chat = GroupChatOrchestrator(agents=[researcher, analyst])
await group_chat.run("Discuss pricing strategy")
```

Each agent uses their own tools independently, regardless of the orchestration pattern.

## 2. Human-in-the-Loop Feedback (Orchestration-Level Feature)

Human feedback pauses workflow execution to allow human intervention, approval, or input. This is configured at the **orchestration level**.

### How It Works

1. Workflow runs normally
2. When a specified agent completes, workflow pauses
3. `request_info` event is triggered
4. You can review the agent's output and:
   - **Approve**: Continue to next agent
   - **Reject**: Stop execution
   - **Modify**: Provide custom feedback

5. Workflow continues based on your response

### Sequential Orchestration with Feedback

```python
from src.sequential_template import SequentialOrchestrator

orchestrator = SequentialOrchestrator(
    agents=[researcher, coder, reviewer]
)

# Pause after researcher and coder for feedback
result = await orchestrator.run_with_human_feedback(
    initial_message="Create a user login API",
    feedback_agent_names=["Researcher", "Coder"]  # Only pause after these agents
)

# Or pause after every agent
result = await orchestrator.run_with_human_feedback(
    initial_message="Create a user login API",
    feedback_agent_names=None  # Pause after all agents
)
```

### Concurrent Orchestration with Feedback

```python
from src.concurrent_template import ConcurrentOrchestrator

orchestrator = ConcurrentOrchestrator(
    agents=[market_researcher, legal_reviewer, tech_analyst]
)

# Pause after specific agents complete
result = await orchestrator.run_with_human_feedback(
    initial_message="Should we launch in EU market?",
    feedback_agent_names=["legal_reviewer"]  # Review legal before proceeding
)
```

### Group Chat Orchestration with Feedback

```python
from src.groupchat_template import GroupChatOrchestrator

orchestrator = GroupChatOrchestrator(
    agents=[product_manager, tech_lead, designer]
)

# Pause after specific participants speak
result = await orchestrator.run_with_human_feedback(
    initial_message="Add real-time collaboration feature?",
    feedback_agent_names=["ProductManager", "TechLead"],
    verbose=True,
    limit=12
)
```

### Customizing Feedback Responses

The current implementation auto-approves all feedback requests. To add custom logic:

```python
# In the orchestrator's process_event_stream function:
if event.type == "request_info":
    # Get agent output for review
    print(f"Agent {event.request_id} completed. Review output:")
    
    # Option 1: Auto-approve
    responses[event.request_id] = AgentRequestInfoResponse.approve()
    
    # Option 2: Get user input
    user_input = input("Approve? (y/n): ")
    if user_input.lower() == 'y':
        responses[event.request_id] = AgentRequestInfoResponse.approve()
    else:
        responses[event.request_id] = AgentRequestInfoResponse.reject("User rejected")
    
    # Option 3: Provide custom feedback
    feedback = input("Feedback (or press Enter to approve): ")
    if feedback:
        responses[event.request_id] = AgentRequestInfoResponse.approve(
            feedback=feedback
        )
    else:
        responses[event.request_id] = AgentRequestInfoResponse.approve()
```

## 3. Combining Tools and Feedback

You can use both features together:

```python
# Create agents with tools
researcher = AgentTemplate(
    name="Researcher",
    instructions="Research using the database",
    tools=[search_database, get_product_specs]
)

coder = AgentTemplate(
    name="Coder",
    instructions="Write code based on research",
    tools=[generate_code, run_tests]
)

# Use in orchestration with human feedback
orchestrator = SequentialOrchestrator(agents=[researcher, coder])

result = await orchestrator.run_with_human_feedback(
    initial_message="Create product recommendation API",
    feedback_agent_names=["Researcher"]  # Review research before coding
)
```

## 4. Available Methods Summary

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

## 5. Best Practices

### Tools
✅ **DO:**
- Define tools as simple, focused functions
- Use type hints and Pydantic Field descriptions
- Keep tool implementations stateless when possible
- Test tools independently before adding to agents

❌ **DON'T:**
- Create tools that modify global state unexpectedly
- Use tools for long-running operations without timeout handling
- Pass sensitive credentials directly in tool parameters

### Human Feedback
✅ **DO:**
- Use feedback for critical decision points
- Pause after agents that need verification (legal, security, compliance)
- Provide clear context when requesting feedback
- Consider async workflows for better UX

❌ **DON'T:**
- Request feedback after every agent (creates friction)
- Block on feedback indefinitely without timeout
- Use for simple validations that could be automated

## 6. Example: Complete Workflow

```python
from src.agent_template import AgentTemplate
from src.sequential_template import SequentialOrchestrator
from agent_framework import tool
from pydantic import Field
from typing import Annotated

# Define tools
@tool
def search_requirements(query: Annotated[str, Field(description="Search query")]) -> str:
    """Search requirements database."""
    return f"Requirements for {query}: secure auth, input validation, rate limiting"

@tool
def generate_code(spec: Annotated[str, Field(description="Code specification")]) -> str:
    """Generate code from specification."""
    return f"def api_endpoint():\\n    # Implementation based on: {spec}\\n    pass"

# Create agents with tools
analyst = AgentTemplate(
    name="Analyst",
    instructions="Analyze requirements using search_requirements tool",
    tools=[search_requirements]
)

developer = AgentTemplate(
    name="Developer",
    instructions="Generate code using generate_code tool based on analyst's findings",
    tools=[generate_code]
)

reviewer = AgentTemplate(
    name="Reviewer",
    instructions="Review the code for security and best practices"
)

# Create orchestration with feedback
pipeline = SequentialOrchestrator(agents=[analyst, developer, reviewer])

# Execute with human review after analysis and development
result = await pipeline.run_with_human_feedback(
    initial_message="Create a new user registration API endpoint",
    feedback_agent_names=["Analyst", "Developer"]  # Review after these agents
)

print(result)
```

---

For more examples, see:
- [Tool Template](../src/tool_template.py) - Tool definition examples
- [Examples](../examples.py) - Complete orchestration examples
