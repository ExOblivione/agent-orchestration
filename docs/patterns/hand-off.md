# Handoff Orchestration Pattern

## Overview

Handoff orchestration enables dynamic routing of conversations between specialized agents based on context, requirements, or expertise needed. Agents can transfer control to each other, allowing complex tasks to be handled by the most appropriate specialist at each stage.

This pattern implements intelligent agent-to-agent transfers with full context preservation, supporting both simple triage workflows and complex multi-agent collaboration.

## Pattern Structure

```
                        ┌─→ Specialist Agent A (Billing)
                        │
Entry/Triage Agent ─────┼─→ Specialist Agent B (Technical)
                        │
                        ├─→ Specialist Agent C (Sales)
                        │
                        └─→ Specialist Agent D (Account)
```

Flow:
1. **Entry/Triage Agent** receives initial request
2. **Analysis** determines which specialist is needed
3. **Handoff** transfers control with full context
4. **Specialist** handles the request
5. **Optional**: Specialist can handoff to another if needed

## When to Use

- **Domain Specialization**: Different agents for different domains
- **Customer Support**: Route to appropriate support specialist
- **Escalation**: Transfer to higher expertise when needed
- **Task Routing**: Direct work to qualified agents
- **Dynamic Expertise**: Requirements vary per request

## Real-Life Example: Customer Support System

**Scenario**: A customer support system that intelligently routes inquiries to the right specialist, escalating complex issues and transferring between departments as needed.

### Agents in Hand-off Flow

1. **Triage Agent**: Analyzes customer inquiry and routes appropriately
2. **Billing Specialist**: Handles payment, subscription, refund issues
3. **Technical Support**: Resolves technical problems and bugs
4. **Account Management**: Handles account changes, security, data
5. **Sales Agent**: Answers product questions and upgrades
6. **Escalation Agent**: Handles complex or sensitive issues


### Execution Flow

```
Customer: "I was charged twice this month and I'm very upset!"
   ↓
[Triage Agent]
Analysis: "Billing issue + customer upset = route to billing first"
Decision: HAND-OFF → Billing Agent
   ↓
[Billing Agent]
Action: Checks account, confirms duplicate charge
Response: "I see the duplicate charge. I'm processing a refund now."
Detection: Customer still upset, issue complex
Decision: HAND-OFF → Escalation Agent (with context)
   ↓
[Escalation Agent]
Context received: duplicate charge, refund processing, upset customer
Action: "I sincerely apologize. I've expedited your refund and added 
        a month free to your account. It will arrive in 2-3 business days."
Result: Issue resolved, customer satisfied
```

### Complex Multi-Transfer Example

```
Customer: "I can't log in and I think I was hacked!"
   ↓
[Triage] → [Account Management] 
   ↓ (detects suspicious activity)
[Account Management] → [Technical Support]
   ↓ (confirms security breach)
[Technical Support] → [Escalation]
   ↓
[Escalation]: Coordinates secure account reset + security review
```

## Advantages

- **Specialization**: Each agent focuses on their expertise
- **Efficiency**: Direct routing to right expert first time
- **Scalability**: Easy to add new specialists
- **Flexibility**: Dynamic routing based on actual needs
- **Context Preservation**: Full history passed between agents

## Disadvantages

- **Complex Routing**: Requires intelligent triage logic
- **Transfer Overhead**: Each hand-off adds latency
- **Context Management**: Must preserve context across transfers
- **Potential Loops**: Without limits, could transfer infinitely
- **Training**: Triage agent needs good classification

## Best Practices

1. **Clear Specialties**: Define non-overlapping domains when possible
2. **Transfer Limits**: Set maximum handoffs to prevent loops
3. **Context Preservation**: Always pass full context on transfer
4. **Fallback Agent**: Define default when routing is uncertain
5. **Transfer Reasons**: Log why transfers happen for improvement
6. **Customer Experience**: Minimize visible handoffs to user

## Implementation

```python
from src import AgentTemplate, HandOffOrchestrator
from agent_framework.orchestrations import HandoffBuilder

# Define specialized agents
agents = [
    AgentTemplate(name="TriageAgent", instructions="..."),
    AgentTemplate(name="BillingAgent", instructions="..."),
    AgentTemplate(name="TechSupportAgent", instructions="...")
]

# Define custom routing (optional)
def custom_workflow_builder(agents_list):
    builder = HandoffBuilder(participants=agents_list)
    # Triage can handoff to anyone
    builder.add_handoff(source="TriageAgent", target="*")
    # Billing can handoff to TechSupport or back to Triage
    builder.add_handoff(source="BillingAgent", target=["TechSupportAgent", "TriageAgent"])
    return builder.with_autonomous_mode()  # Enable non-interactive execution

# Create orchestrator
orchestrator = HandOffOrchestrator(
    agents=agents,
    workflow_builder=custom_workflow_builder,  # Optional custom routing
    termination_condition=lambda msgs: len(msgs) >= 10  # Optional
)

# Run handoff workflow
result = await orchestrator.run("I was charged twice this month!")
```

**Key Features:**
- Flexible routing: default all-to-all or custom rules
- Autonomous mode for non-interactive execution
- Custom termination conditions
- Full context preservation across handoffs

## Further Reading

- [Microsoft Agent Framework - Handoff Orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/handoff?pivots=programming-language-python)
- [Architecture Guide](../architecture.md)
- [Example Implementation](../../examples/handoff_patterns.py)