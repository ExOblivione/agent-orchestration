# Multi-Agent Orchestration Framework

A comprehensive template framework for building multi-agent systems with various orchestration patterns, supporting sequential, concurrent, group chat, hand-off, and magentic architectures.

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

5. **Magentic Orchestration**
   - Agents are "attracted" to tasks based on their capabilities
   - Self-organizing system where agents claim relevant work
   - Use case: Load balancing, skill-based routing, autonomous task distribution

### 🛠️ Technology Stack

- **Language**: Python 3.10+
- **Agent Framework**: Microsoft Agent Framework (Python)
- **Azure Services**: Azure OpenAI, Azure AI Projects
- **Async Support**: asyncio for concurrent operations
- **Type Checking**: Pydantic for data validation
- **Testing**: pytest for comprehensive testing

## 🚀 Ready to get started?

[Getting Started](docs/getting-started.md)