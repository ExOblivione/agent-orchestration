# Group Chat Orchestration Pattern

## Overview

Group chat orchestration enables multiple agents to communicate in a shared conversation space, with dynamic turn-taking based on relevance and expertise. Agents collaborate, debate, and build on each other's contributions to solve complex problems.

## Pattern Structure

```
       ┌──────────────────────────────┐
       │   Shared Conversation        │
       │                              │
Agent1 ←→ Agent2 ←→ Agent3 ←→ Agent4 ←→ User
       │                              │
       │   Turn Management System     │
       └──────────────────────────────┘
```

Key elements:
1. **Shared Context**: All agents see the full conversation
2. **Speaker Selection**: System determines who speaks next
3. **Dynamic Flow**: Conversation evolves based on contributions
4. **Termination**: Ends when goal is reached or conditions met

## When to Use

- **Complex Problem Solving**: Requires multiple expertise areas
- **Brainstorming**: Need diverse perspectives and creative solutions
- **Collaborative Design**: Multiple stakeholders need input
- **Decision Making**: Requires weighing different viewpoints
- **Peer Review**: Multiple reviewers provide feedback

## Real-Life Example: Product Design Review

**Scenario**: Design a new mobile app feature with input from multiple experts ensuring technical feasibility, user experience, security, and business alignment.

### Agents in Group Chat

1. **Product Manager**: Defines requirements and business goals
2. **UX Designer**: Focuses on user experience and interface design
3. **Backend Engineer**: Addresses technical implementation and scalability
4. **Security Expert**: Identifies security concerns and compliance
5. **Facilitator Agent**: Manages conversation flow and synthesizes decisions

### Execution Flow

```
[Facilitator]: "Let's review: Add biometric authentication with fallback to PIN"
   ↓
[Product Manager]: "This addresses user feedback. 78% want faster login. 
                    Expected to improve retention by 15%."
   ↓
[UX Designer]: "Biometric should be primary flow. PIN as backup. 
                Need smooth error states if biometric fails."
   ↓
[Backend Engineer]: "We'll need secure enclave for biometric data. 
                     API rate limiting for PIN attempts. ~2 weeks work."
   ↓
[Security Expert]: "CRITICAL: Biometric data must stay on device. 
                    Implement exponential backoff on PIN. GDPR considerations."
   ↓
[Product Manager]: "Good point on GDPR. Can we get consent flow designed?"
   ↓
[UX Designer]: "Yes, I'll add consent screen with clear privacy explanation."
   ↓
[Backend Engineer]: "For API, I suggest 5 attempts then 15-min lockout."
   ↓
[Security Expert]: "Agreed. Also log failed attempts for security monitoring."
   ↓
[Facilitator]: "Summary: Approved with conditions:
                 1. Device-only biometric storage
                 2. Consent flow with privacy details
                 3. 5 PIN attempts with lockout
                 4. Security logging
                 Timeline: 2 weeks. Any concerns?"
   ↓
[All]: "Agreed." / "Looks good." / "No concerns."
```

## Speaker Selection Strategies

 1. Expertise-Based: Facilitator chooses based on topic relevance
 2. Round Robin: Each agent gets turn in order
 3. Autonomous: Agents self-select when they have relevant input
 
## Advantages

- **Collaborative**: Multiple perspectives lead to better decisions
- **Dynamic**: Conversation adapts to emerging issues
- **Comprehensive**: All aspects covered by specialists
- **Realistic**: Mimics real team discussions
- **Quality**: Peer review catches issues early

## Disadvantages

- **Unpredictable Length**: Hard to estimate completion time
- **Complex Management**: Requires sophisticated turn-taking logic
- **Costly**: Many LLM calls for extended conversations
- **Potential Loops**: Agents might debate indefinitely without facilitator
- **Context Window**: Long conversations may exceed token limits

## Best Practices

1. **Clear Roles**: Define each agent's expertise and responsibilities
2. **Facilitator**: Use facilitator for complex discussions
3. **Turn Limits**: Set maximum consecutive turns per agent
4. **Summarization**: Periodically summarize to manage context
5. **Termination**: Define clear completion criteria
6. **Context Pruning**: Remove irrelevant history to save tokens

## Implementation

```python
from src import AgentTemplate, GroupChatOrchestrator

# Define discussion participants
agents = [
    AgentTemplate(name="ProductManager", instructions="..."),
    AgentTemplate(name="UXDesigner", instructions="..."),
    AgentTemplate(name="Engineer", instructions="..."),
    AgentTemplate(name="SecurityExpert", instructions="...")
]

# Optional: Define facilitator
facilitator = AgentTemplate(
    name="Facilitator",
    instructions="Guide discussion and synthesize decisions..."
)

# Create orchestrator
orchestrator = GroupChatOrchestrator(
    agents=agents,
    facilitator=facilitator,  # Optional
    max_rounds=10,            # Max conversation rounds
    selector_prompt="Select next speaker based on expertise..."  # Optional
)

# Run discussion
result = await orchestrator.run("Review: Biometric authentication feature")
```

**Key Features:**
- Dynamic speaker selection based on context
- Optional facilitator for coordination
- Configurable termination conditions
- Full conversation context maintained

## Further Reading

- [Microsoft Agent Framework - Group Chat Orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/group-chat?pivots=programming-language-python)
- [Architecture Guide](../architecture.md)
- [Example Implementation](../../examples/groupchat_example.py)

