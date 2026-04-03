# Magentic Orchestration Pattern

## Overview

Magentic orchestration creates a self-organizing system where agents autonomously "claim" tasks from a shared pool based on their capabilities and current workload. Tasks act like magnets, attracting the most suitable available agents.

## Pattern Structure

```
Task Pool: [Task1] [Task2] [Task3] [Task4] [Task5]
              ↓       ↓       ↓       ↓       ↓
           [Agents evaluate and claim tasks]
              ↓       ↓       ↓       ↓       ↓
           Agent1  Agent2  Agent3  Agent4  Agent1
          (Python) (JS)    (DB)    (Deploy) (Python)
```

Key mechanics:
1. **Task Broadcasting**: Tasks published to shared pool
2. **Agent Evaluation**: Agents assess task fit based on capabilities
3. **Claiming**: Agent with best fit claims the task
4. **Execution**: Agent completes task independently
5. **Load Balancing**: Busy agents are less likely to claim new tasks

## When to Use

- **Dynamic Workloads**: Unpredictable task arrival patterns
- **Load Balancing**: Distribute work across available agents
- **Skill-Based Routing**: Match tasks to specialized agents
- **Autonomous Systems**: Minimal central coordination needed
- **Scalable Systems**: Add/remove agents without reconfiguration

## Real-Life Example: Development Task Assignment

**Scenario**: A development team has various tasks (coding, code review, testing, deployment) that need to be completed. Agents specialize in different areas and autonomously pick tasks they're best suited for.

### Agents with Capabilities

1. **Python Developer Agent**: Capabilities: [python, backend, api, testing]
2. **JavaScript Developer Agent**: Capabilities: [javascript, frontend, react, ui]
3. **Database Agent**: Capabilities: [sql, database, optimization, migration]
4. **DevOps Agent**: Capabilities: [deployment, ci-cd, docker, kubernetes]
5. **QA Agent**: Capabilities: [testing, qa, automation, integration-tests]


### Execution Flow

```
Task Pool Published:
- TASK-101: Auth API [python, api, backend] - HIGH
- TASK-102: Login Form [javascript, react, frontend] - HIGH
- TASK-103: DB Optimization [sql, database] - MEDIUM
- TASK-104: CI/CD Setup [ci-cd, deployment] - HIGH
- TASK-105: Integration Tests [testing, python] - MEDIUM

┌─────────────────────────────────────────────────────┐
│ Agent Evaluation Phase (all agents evaluate)        │
└─────────────────────────────────────────────────────┘

[Python Dev 1]: 
  - TASK-101: Match 100% (all caps match), Load: 0/3 → BID: 0.95
  - TASK-105: Match 66% (testing+python), Load: 0/3 → BID: 0.60

[JS Dev 1]:
  - TASK-102: Match 100% (all caps match), Load: 0/2 → BID: 0.95
  
[DB Specialist]:
  - TASK-103: Match 100% (all caps match), Load: 0/2 → BID: 0.95

[DevOps 1]:
  - TASK-104: Match 100% (all caps match), Load: 0/4 → BID: 0.95

[QA 1]:
  - TASK-105: Match 100% (testing perfect match), Load: 0/3 → BID: 0.95

┌─────────────────────────────────────────────────────┐
│ Task Assignment (highest bids win)                  │
└─────────────────────────────────────────────────────┘

✓ TASK-101 → Python Dev 1 (bid: 0.95, perfect match)
✓ TASK-102 → JS Dev 1 (bid: 0.95, perfect match)
✓ TASK-103 → DB Specialist (bid: 0.95, perfect match)
✓ TASK-104 → DevOps 1 (bid: 0.95, perfect match)
✓ TASK-105 → QA 1 (bid: 0.95, testing specialist)

All tasks claimed and in progress...

┌─────────────────────────────────────────────────────┐
│ New Task Arrives                                     │
└─────────────────────────────────────────────────────┘

New Task: TASK-106: Fix Python API bug [python, backend, api]

[Python Dev 1]: Load 1/3 (working on TASK-101) → BID: 0.60 (reduced)
[QA 1]: Has python capability, Load 1/3 → BID: 0.40

✓ TASK-106 → Python Dev 1 (still best match despite load)
```

## Claiming Strategies

### 1. Best Fit (Default)
```python
workflow.set_claiming_strategy("best_fit")
# Agent with highest capability match claims task
# Formula: (matched_caps / required_caps) * (1 - current_load)
```

### 2. Load Balanced
```python
workflow.set_claiming_strategy("load_balanced")
# Prioritizes agents with lower current workload
# Even distribution across agents
```

### 3. Priority-Based
```python
workflow.set_claiming_strategy("priority_based")
# High-priority tasks attract stronger bids
# Agents may defer low-priority tasks
```

### 4. Capability Threshold
```python
workflow.set_claiming_strategy(
    "capability_threshold",
    min_match_percentage=0.75  # Must match 75%+ of required capabilities
)
```

## Bid Calculation

```python
# Example bid calculation algorithm
def calculate_bid(task, agent):
    # Capability match score
    matched_caps = len(set(task.capabilities) & set(agent.capabilities))
    required_caps = len(task.capabilities)
    capability_score = matched_caps / required_caps
    
    # Workload factor
    current_load = agent.current_tasks / agent.capacity
    availability_score = 1 - current_load
    
    # Priority multiplier
    priority_multiplier = {
        "high": 1.5,
        "medium": 1.0,
        "low": 0.7
    }[task.priority]
    
    # Final bid
    bid = capability_score * availability_score * priority_multiplier
    
    return bid if bid >= 0.5 else None  # Don't bid if too low
```

## Advantages

- **Self-Organizing**: No central dispatcher needed
- **Load Balancing**: Automatically distributes work
- **Fault Tolerant**: If agent fails, task returns to pool
- **Scalable**: Add agents without reconfiguration
- **Adaptive**: Responds to changing workloads dynamically
- **Skill Matching**: Tasks go to best-qualified agents

## Disadvantages

- **Coordination Overhead**: Bid evaluation for each task
- **Potential Conflicts**: Multiple agents might want same task
- **Starvation**: Low-capability agents might not get tasks
- **Complexity**: Bid algorithms can be complex
- **Monitoring**: Harder to predict exact agent assignments

## Advanced Features

### Task Priority Adjustment
```python
# High-priority tasks increase bid attractiveness
workflow.set_priority_multipliers({
    "critical": 2.0,
    "high": 1.5,
    "medium": 1.0,
    "low": 0.5
})
```

### Capability Learning
```python
# Agents improve capability scores based on success
workflow.enable_learning(
    track_success_rate=True,
    adjust_bids_by_history=True
)
```

### Task Reassignment
```python
# If agent fails, return task to pool
workflow.enable_reassignment(
    max_attempts=3,
    backoff_factor=1.5
)
```

## Best Practices

1. **Clear Capabilities**: Define specific, non-overlapping capabilities
2. **Realistic Capacity**: Set agent capacity based on actual performance
3. **Priority System**: Use priority levels effectively
4. **Monitoring**: Track assignment patterns and adjust
5. **Fallback**: Have backup plan if no agent bids on task
6. **Timeout**: Set task timeouts to prevent indefinite waiting

## Use Case Variations

### Customer Service Routing
```python
# Route support tickets based on agent expertise and availability
agents = [
    TechnicalSupportAgent(capabilities=["technical", "api", "bugs"]),
    BillingSupportAgent(capabilities=["billing", "refunds", "invoices"]),
    AccountSupportAgent(capabilities=["account", "security", "access"])
]
```

### Content Moderation
```python
# Distribute moderation tasks to available moderators
agents = [
    ModeratorAgent(capabilities=["text", "english"], capacity=10),
    ModeratorAgent(capabilities=["image", "nsfw"], capacity=8),
    ModeratorAgent(capabilities=["video", "copyright"], capacity=5)
]
```

## Related Patterns

- **Hand-off**: Use when routing logic should be centralized
- **Concurrent**: Use when all tasks should start simultaneously
- **Sequential**: Use when task order matters

## Further Reading

- [Microsoft Agent Framework Workflows](https://learn.microsoft.com/en-us/agent-framework/workflows/)
- [Architecture Guide](../architecture.md)
- [Example Implementation](../../examples/magentic_task_distribution.py)
