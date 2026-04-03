# Hand-off Orchestration Pattern

## Overview

Hand-off orchestration routes requests to specialized agents based on context, requirements, or expertise needed. An entry agent (triage) analyzes the request and dynamically transfers control to the most appropriate specialist agent.

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
1. **Entry Agent** receives initial request
2. **Analysis** determines which specialist is needed
3. **Hand-off** transfers control with full context
4. **Specialist** handles the request
5. **Optional**: Specialist can hand-off to another if needed

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
2. **Transfer Limits**: Set maximum hand-offs to prevent loops
3. **Context Preservation**: Always pass full context on transfer
4. **Fallback Agent**: Define default when routing is uncertain
5. **Transfer Reasons**: Log why transfers happen for improvement
6. **Customer Experience**: Minimize visible hand-offs to user

## Further Reading

- [Microsoft Agent Framework Workflows](https://learn.microsoft.com/en-us/agent-framework/workflows/)
- [Architecture Guide](../architecture.md)
- [Example Implementation](../../examples/hand_off_support.py)