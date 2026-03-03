# Sequential Orchestration Pattern

## Overview

Sequential orchestration executes agents in a linear, predefined order where each agent's output becomes the next agent's input. This pattern is ideal for pipeline workflows where steps must occur in sequence.

## Pattern Structure

```
Input → Agent 1 → Agent 2 → Agent 3 → ... → Agent N → Output
```

Each agent:
1. Receives the output from the previous agent
2. Processes the input according to its role
3. Produces output for the next agent
4. Final agent returns the result to the user

## When to Use

- **Pipeline Processing**: Multi-stage transformations where order matters
- **Sequential Dependencies**: Each step requires the previous step's output
- **Predictable Workflows**: Well-defined process with clear stages
- **Quality Gates**: Each agent validates/improves the previous step's work

## Real-Life Example: Content Creation Pipeline

**Scenario**: Create a technical blog post with proper research, writing, and review stages.

### Agents in Sequence

1. **Research Agent**: Gathers information on the topic
2. **Writing Agent**: Creates initial draft based on research
3. **Editing Agent**: Improves clarity and grammar
4. **SEO Agent**: Optimizes for search engines
5. **Publishing Agent**: Formats and prepares for publication


### Execution Flow

```
Input: "Create a blog post about: The Future of Quantum Computing"
   ↓
[Research Agent]
Output: "Key facts: quantum superposition, current applications, 
         major players (IBM, Google), challenges..."
   ↓
[Writing Agent]
Output: "# The Future of Quantum Computing\n\nQuantum computing 
         represents a paradigm shift... [1000 word article]"
   ↓
[Editing Agent]
Output: "[Improved version with better flow and grammar]"
   ↓
[SEO Agent]
Output: "[Article with meta tags, optimized headings, keywords]"
   ↓
[Publishing Agent]
Output: "[Final HTML with proper formatting and images]"
```

## Advantages

- **Predictable**: Clear execution order, easy to debug
- **Quality Control**: Each stage can improve/validate previous work
- **Specialization**: Each agent focuses on its expertise
- **Error Isolation**: Easy to identify which stage failed

## Disadvantages

- **Serial Execution**: Can be slower than parallel approaches
- **Bottlenecks**: One slow agent delays the entire pipeline
- **Rigid**: Difficult to skip or reorder steps dynamically

## Best Practices

1. **Clear Interfaces**: Define clear input/output contracts between agents
2. **Validation**: Each agent should validate its input before processing
3. **Idempotency**: Design agents to be safely re-runnable
4. **Logging**: Log each stage's input and output for debugging
5. **Timeouts**: Set reasonable timeouts for each agent

## Related Patterns

- **Concurrent**: Use when stages can run independently
- **Hand-off**: Use when routing logic is needed between stages
- **Group Chat**: Use when stages need to collaborate rather than strictly follow order

## Further Reading

- [Microsoft Agent Framework Workflows](https://learn.microsoft.com/en-us/agent-framework/workflows/)
- [Architecture Guide](../architecture.md)
- [Example Implementation](../../examples/sequential_pipeline.py)
