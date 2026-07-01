# Getting Started

## � Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Azure subscription with Azure OpenAI access
- Azure AI Projects setup

### Installation

1. **Clone the repository** (if you haven't already)
   ```bash
   git clone <your-repo-url>
   cd agent-orchestration
   ```

2. **Create a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
    Create a `.env` file in your project root:

    ```bash
    # Azure OpenAI (recommended)
    AZURE_AI_PROJECT_ENDPOINT=https://your-project.openai.azure.com
    AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME=gpt-4
    ```

## Your First Agent

Use the [simple agent example](../examples/agent_examples.py) for creating an agent using Microsoft Agent Framework.

## Choose Your Orchestration Pattern

Depending on your use case, select the appropriate pattern:

| Pattern | When to Use | Template |
|---------|-------------|-------------|
| **Sequential** | Linear pipeline, each step depends on previous | [Template](../src/sequential_example.py) |
| **Concurrent** | Independent tasks that can run in parallel | [Template](../src/concurrent_template.py) |
| **Group Chat** | Collaborative discussion, multiple perspectives | [Template](../src/groupchat_template.py)|
| **Hand-off** | Route to specialists based on task type | [Template](../src/handoff_template.py) |
| **Magentic** | Self-organizing, agents claim relevant tasks | [Template](../src/magentic_template.py) |


## Running Examples

```bash
# Run the examples file
python examples.py
```

## Troubleshooting

### Common Issues

**Issue:** PowerShell Execution Policy Error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue**: "No module named 'agent_framework'"
```bash
pip install agent-framework --pre
```

**Issue**: Experimental warnings from agent_framework
These warnings are suppressed by default in the framework templates. If you see them in your own code, add this to the top of your script:
```python
import warnings
warnings.filterwarnings('ignore', message='.*experimental.*')
```

**Issue**: Authentication errors with Azure
```bash
az login
az account set --subscription <your-subscription-id>
```

## Resources

- [Architecture Guide](architecture.md)
- [Microsoft Agent Framework Documentation](https://learn.microsoft.com/en-us/agent-framework/)
- [Pattern Documentations](patterns/)