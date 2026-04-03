"""
Examples of using the AgentTemplate in different scenarios.

Patterns demonstrated:
- Single agent usage
- Streaming responses
- Sequential orchestration with specialized agents
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import src
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from src import AgentTemplate, SequentialOrchestrator

async def example_single_agent():
    """Example: Using a single agent."""
    print("=== Single Agent Example ===")
    
    agent = AgentTemplate(
        name="Assistant",
        instructions="You are a helpful assistant. Keep responses concise."
    )
    
    response = await agent.run("What is Python?")
    print(f"{agent.name}: {response}\n")


async def example_streaming():
    """Example: Using streaming responses."""
    print("=== Streaming Response Example ===")
    
    agent = AgentTemplate(
        name="Storyteller",
        instructions="You are a creative storyteller. Keep stories brief and engaging."
    )
    
    print(f"{agent.name}: ", end="", flush=True)
    async for chunk in await agent.run("Tell a one-sentence story about a robot.", stream=True):
        print(chunk, end="", flush=True)
    print("\n")


async def example_specialized_agents():
    """Example: Creating specialized agents using Sequential Orchestrator."""
    print("=== Sequential Orchestration Example ===")
    
    # Create specialized agents
    researcher = AgentTemplate(
        name="Researcher",
        instructions="You are a research specialist. Provide factual, well-researched information about the topic. Keep it concise."
    )
    
    coder = AgentTemplate(
        name="Coder",
        instructions="You are a Python coding expert. Based on the research provided, write clean, efficient code with comments."
    )
    
    reviewer = AgentTemplate(
        name="Reviewer",
        instructions="You are a code reviewer. Review the code provided and give constructive feedback and improvements."
    )
    
    # Create sequential orchestrator
    orchestrator = SequentialOrchestrator(
        agents=[researcher, coder, reviewer]
    )
    
    # Execute the pipeline
    print(f"\nPipeline: {orchestrator}\n")
    await orchestrator.run(
        "Create a REST API endpoint for user registration with email validation"
    )

async def main():
    """Run all examples."""
    # await example_single_agent()
    # await example_streaming()
    await example_specialized_agents()

if __name__ == "__main__":
    asyncio.run(main())