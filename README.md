# Multi-Agent Orchestration Framework

A comprehensive template framework for building multi-agent systems with various orchestration patterns, supporting sequential, concurrent, group chat, hand-off, and magnetic architectures.

## 🎯 Project Overview

This framework provides reusable templates and patterns for orchestrating multiple AI agents to solve complex tasks. It implements five core orchestration architectures as defined in Microsoft's Agent Orchestration documentation.

## 🏗️ Architecture Overview

### Core Orchestration Patterns

1. **Sequential Orchestration**
   - Agents execute in a predefined linear order
   - Output from one agent becomes input to the next
   - Use case: Pipeline workflows, step-by-step processing

2. **Concurrent Orchestration**
   - Multiple agents execute in parallel, one collector agent
   - Results are aggregated once all agents complete, the collector agent is able to respond to user
   - Use case: Parallel processing, independent tasks, performance optimization

3. **Group Chat Orchestration**
   - Agents communicate in a shared conversation space
   - Dynamic turn-taking based on relevance and expertise
   - Use case: Collaborative problem-solving, brainstorming, multi-perspective analysis

4. **Hand-off Orchestration**
   - Agents pass control to specialized agents based on context
   - Dynamic routing based on task requirements
   - Use case: Task specialization, escalation workflows, domain-specific routing

5. **Magnetic Orchestration**
   - Agents are "attracted" to tasks based on their capabilities
   - Self-organizing system where agents claim relevant work
   - Use case: Load balancing, skill-based routing, autonomous task distribution


## 🔑 Key Components

### 1. Base Orchestrator
The foundation for all orchestration patterns with common functionality:
- Agent registration and lifecycle management
- Message routing and coordination
- State management across agents
- Error handling and recovery
- Logging and monitoring hooks

### 2. Agent Template
Standard agent interface with:
- **Capabilities declaration**: What the agent can do
- **Message handling**: Receive and process messages
- **Tool invocation**: Execute actions via tools
- **State access**: Read/write shared context
- **Response generation**: Format and send responses

### 3. Tool/Action Framework
Extensible tool system featuring:
- **Tool interface**: Standard contract for all tools
- **Tool registry**: Central tool discovery and management
- **Input validation**: Parameter checking and sanitization
- **Output formatting**: Standardized response structures
- **Error handling**: Graceful failure management

### 4. Message System
Robust messaging infrastructure:
- **Message types**: Request, response, broadcast, etc.
- **Routing logic**: Pattern-specific message delivery
- **Priority queuing**: Handle urgent messages first
- **Message history**: Audit trail and context preservation

### 5. State Management
Centralized state handling:
- **Shared context**: Cross-agent data sharing
- **Session state**: Conversation-specific data
- **Agent state**: Individual agent memory
- **Persistence**: Optional state storage


## 🛠️ Technology Stack

- **Language**: Python 3.10+
- **Async Support**: asyncio for concurrent operations
- **Configuration**: YAML/JSON for declarative setup
- **Type Checking**: Pydantic for data validation
- **Testing**: pytest for comprehensive testing
- **Logging**: structlog for structured logging

## 🎨 Usage Example Preview

```python
from agent_orchestration import SequentialOrchestrator
from agent_orchestration.templates import ResearchAgent, CodingAgent, ReviewAgent

# Create orchestrator
orchestrator = SequentialOrchestrator()

# Register agents
orchestrator.register_agent(ResearchAgent(name="researcher"))
orchestrator.register_agent(CodingAgent(name="coder"))
orchestrator.register_agent(ReviewAgent(name="reviewer"))

# Execute workflow
result = await orchestrator.execute(
    input="Build a REST API for user management",
    context={"language": "Python", "framework": "FastAPI"}
)

print(result.output)
```