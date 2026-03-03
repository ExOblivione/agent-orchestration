# Getting Started

## Prerequisites

- Python 3.10 or higher
- Azure OpenAI or OpenAI API access
- Basic understanding of async Python

## Installation

### 1. Install Microsoft Agent Framework

```bash
pip install agent-framework --pre
```

### 2. Set Up Environment Variables

Create a `.env` file in your project root:

```bash
# Azure OpenAI (recommended)
AZURE_AI_PROJECT_ENDPOINT=https://your-project.openai.azure.com
AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME=gpt-4
```

**Note**: Agent Framework doesn't auto-load `.env` files. Use `python-dotenv`:

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
load_dotenv()
```

## Your First Agent

Create a simple agent using Microsoft Agent Framework: URL for Readme file to the agent template

## Choose Your Orchestration Pattern

Depending on your use case, select the appropriate pattern:

| Pattern | When to Use | Template |
|---------|-------------|-------------|
| **Sequential** | Linear pipeline, each step depends on previous | URL for template |
| **Concurrent** | Independent tasks that can run in parallel | URL for template |
| **Group Chat** | Collaborative discussion, multiple perspectives | URL for template |
| **Hand-off** | Route to specialists based on task type | URL for template |
| **Magnetic** | Self-organizing, agents claim relevant tasks | URL for template |


## Running Examples

```bash
# Run the examples file
python examples.py
```

## Troubleshooting

### Common Issues

**Issue**: "No module named 'agent_framework'"
```bash
pip install agent-framework --pre
```

**Issue**: Authentication errors with Azure
```bash
az login
az account set --subscription <your-subscription-id>
```

## Resources

- [Architecture Guide](architecture.md)
- [Microsoft Agent Framework Documentation](https://learn.microsoft.com/en-us/agent-framework/)
- [Pattern Examples](patterns/)