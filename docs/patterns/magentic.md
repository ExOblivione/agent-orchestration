# Magentic Orchestration Pattern

## Overview

Magentic orchestration is a flexible, general-purpose multi-agent pattern designed for complex, open-ended tasks that require dynamic collaboration. Based on the [Magentic-One](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html) system from AutoGen, this pattern uses a dedicated **Magentic manager** to coordinate a team of specialized agents, dynamically selecting which agent should act next based on the evolving context, task progress, and agent capabilities.

The Magentic manager maintains a shared context, tracks progress, and adapts the workflow in real time. This enables the system to break down complex problems, delegate subtasks, and iteratively refine solutions through agent collaboration.

## Pattern Structure

```
User Task → Manager Agent → Plan Creation
                ↓
        [Context & Progress Tracking]
                ↓
    Manager selects next agent dynamically
                ↓
    ResearcherAgent / CoderAgent / AnalystAgent
                ↓
        Agent executes subtask
                ↓
    Manager evaluates progress & updates plan
                ↓
    [Repeat until complete or stalled]
                ↓
        Manager synthesizes final result
```

**Key Components:**
1. **Manager Agent**: Coordinates the team, creates plans, selects agents, tracks progress
2. **Specialized Agents**: Execute specific tasks (research, coding, analysis, etc.)
3. **Shared Context**: Manager maintains conversation history and progress ledger
4. **Dynamic Selection**: Manager decides which agent acts next based on current state
5. **Iterative Refinement**: Multiple rounds of agent collaboration to refine solutions

## When to Use

- **Complex, Open-Ended Tasks**: Solution path not known in advance
- **Multi-Step Reasoning**: Tasks requiring research → analysis → synthesis
- **Dynamic Workflows**: Need to adapt based on intermediate results
- **Mixed Capabilities**: Tasks requiring different types of expertise
- **Iterative Refinement**: Solutions that need multiple rounds of improvement
- **Uncertain Requirements**: Tasks where the approach emerges during execution

## Advantages

- **Dynamic Coordination**: Manager adapts to evolving task requirements
- **Flexible Collaboration**: Agents can be called multiple times in any order
- **Complex Problem Solving**: Breaks down intricate tasks into manageable subtasks
- **Progress Tracking**: Built-in mechanisms to detect stalls and replan
- **Human Oversight**: Optional plan review for critical decisions
- **Context Awareness**: Manager maintains shared understanding across all agents
- **Iterative Improvement**: Supports refinement through multiple rounds

## Disadvantages

- **Manager Complexity**: Requires sophisticated planning and coordination logic
- **Higher Latency**: Planning overhead adds to execution time
- **Token Usage**: Manager sees all agent interactions (high context consumption)
- **Coordination Overhead**: More LLM calls for manager decisions
- **Unpredictable Paths**: Execution flow varies based on manager decisions
- **Debugging Complexity**: Harder to trace through dynamic agent selection

## Workflow Execution Flow

The Magentic orchestration follows this execution pattern:

1. **Planning Phase**: Manager analyzes task and creates initial plan
2. **Optional Plan Review** (if enabled): Human reviews and approves/modifies plan
3. **Agent Selection**: Manager selects most appropriate agent for next subtask
4. **Execution**: Selected agent executes their portion of the task
5. **Progress Assessment**: Manager evaluates progress and updates the plan
6. **Stall Detection**: If progress stalls, auto-replan (with optional human review)
7. **Iteration**: Steps 3-6 repeat until task complete or limits reached
8. **Final Synthesis**: Manager synthesizes all agent outputs into final result

## Configuration Parameters

```python
MagenticBuilder(
    participants=[agent1, agent2, agent3],    # Specialized agents
    manager_agent=manager,                     # Coordination agent
    intermediate_outputs=True,                 # Stream agent responses
    enable_plan_review=False,                  # Human-in-the-loop planning
    max_round_count=10,                        # Max orchestration rounds
    max_stall_count=3,                         # Stalls before replanning
    max_reset_count=2,                         # Max replans allowed
)
```

**Parameter Guidelines:**
- `max_round_count`: Higher for complex tasks (10-20), lower for simple (3-5)
- `max_stall_count`: How many rounds without progress before replan (2-3)
- `max_reset_count`: How many times to replan before giving up (1-2)
- `enable_plan_review`: Use for critical tasks requiring human oversight

## Best Practices

1. **Specialized Agents**: Define clear, non-overlapping roles (researcher, coder, analyst)
2. **Manager Instructions**: Train manager to delegate effectively and track progress
3. **Monitor Context**: Watch token usage - manager sees all agent interactions
4. **Limit Rounds**: Set appropriate max_round_count to prevent runaway execution
5. **Plan Review**: Enable for complex/critical tasks to ensure proper delegation
6. **Stall Handling**: Configure stall detection to catch stuck workflows
7. **Agent Descriptions**: Provide clear descriptions so manager knows when to use each agent

## Comparison with Group Chat

Magentic orchestration has the **same architecture** as Group Chat but with a more powerful manager:

| Aspect | Magentic | Group Chat |
|--------|----------|------------|
| Manager Role | Complex planning & coordination | Simple speaker selection |
| Planning | Explicit plan creation | Implicit in selection |
| Progress Tracking | Built-in progress ledger | Manual |
| Replanning | Automatic stall detection | Manual |
| Complexity | Higher | Lower |
| Use Case | Complex, multi-step tasks | Discussions, debates |

**When to choose Magentic over Group Chat:**
- Need explicit planning and progress tracking
- Tasks require breaking into clear subtasks
- Want automatic stall detection and replanning
- Need human-in-the-loop plan approval

**When to choose Group Chat instead:**
- Simpler coordination (just speaker selection)
- Discussion/debate scenarios
- Lower token budget
- More predictable execution flow

## Implementation

```python
from src import AgentTemplate, MagenticOrchestrator

# Define specialized agents
agents = [
    AgentTemplate(name="ResearcherAgent", instructions="Research and gather information..."),
    AgentTemplate(name="CoderAgent", instructions="Write and execute code..."),
    AgentTemplate(name="AnalystAgent", instructions="Analyze data and provide insights...")
]

# Define manager agent
manager = AgentTemplate(
    name="MagenticManager",
    instructions="Coordinate the team to complete complex tasks efficiently..."
)

# Create orchestrator
orchestrator = MagenticOrchestrator(
    agents=agents,
    manager_agent=manager
)

# Run autonomous workflow
result = await orchestrator.run(
    "Analyze energy efficiency of ML model architectures",
    max_rounds=10,
    max_stalls=3,
    max_resets=2,
    intermediate_outputs=True
)

# Run with human-in-the-loop plan review
result = await orchestrator.run_with_plan_review(
    "Compare Python vs JavaScript for web development",
    max_rounds=10,
    max_stalls=3,
    max_resets=2,
    intermediate_outputs=True
)
```

**Key Features:**
- Manager creates explicit plans and tracks progress
- Dynamic agent selection based on task evolution
- Automatic stall detection and replanning
- Optional human plan review and approval
- Progress ledger for monitoring collaboration
- Clear output formatting showing manager plans and agent responses

## Further Reading

- [Microsoft Agent Framework - Magentic Orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/magentic?pivots=programming-language-python)
- [Magentic-One Paper (AutoGen)](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html)
- [Architecture Guide](../architecture.md)
- [Example Implementation](../../examples/magentic_patterns.py)