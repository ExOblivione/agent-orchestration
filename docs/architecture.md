# Architecture Guide

## Overview

This framework is built on top of **Microsoft Agent Framework**, providing pre-configured templates and patterns for common multi-agent orchestration scenarios. Rather than reimplementing core functionality, we leverage the enterprise-grade features of Microsoft's solution while adding opinionated templates for rapid development.

## Architecture Layers

```
┌─────────────────────────────────────────┐
│     Templates & Examples Layer          │  ← Your Implementation
│  (Pre-configured agents, workflows)     │
├─────────────────────────────────────────┤
│   Microsoft Agent Framework Layer       │  ← Enterprise Foundation
│  (Workflows, Agents, State, Tools)      │
├─────────────────────────────────────────┤
│         LLM Provider Layer              │
│           (Azure OpenAI)                │
└─────────────────────────────────────────┘
```

## Core Components

### 1. Workflows (Microsoft Agent Framework)
Workflows provide graph-based orchestration with:
- **Executors**: Individual processing units (agents or functions)
- **Edges**: Connections defining message flow between executors
- **Events**: Observability into workflow execution
- **Checkpointing**: State persistence for long-running processes

### 2. LLM Agents (Microsoft Agent Framework)
Individual agents that:
- Process inputs using LLMs
- Call tools and MCP servers
- Maintain conversation context
- Generate responses

### 3. Templates (This Framework)
Pre-built components for common scenarios:
- **Workflow Templates**: Ready-to-use orchestration patterns
- **Agent Templates**: Domain-specific agents (research, coding, review)
- **Tool Templates**: Common tool integrations
- **Configuration Templates**: Best-practice configurations


## State Management

Microsoft Agent Framework provides session-based state management:

- **Agent Session**: Conversation context and history
- **Workflow State**: Execution checkpoints and intermediate results
- **Tool State**: Tool execution results and caching
- **Custom State**: Application-specific data storage


## Next Steps

- [Getting Started Guide](getting-started.md)
- [Pattern Documentation](patterns/)
- [Microsoft Agent Framework Docs](https://learn.microsoft.com/en-us/agent-framework/)
