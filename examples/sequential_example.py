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
    outputs = await orchestrator.run(
        "Create a REST API endpoint for user registration with email validation"
    )
    
    # Print the final conversation
    if outputs:
        print("===== Final Conversation =====")
        messages = outputs[-1]
        for i, msg in enumerate(messages, start=1):
            name = msg.author_name or ("assistant" if msg.role == "assistant" else "user")
            print(f"{'-' * 60}\n{i:02d} [{name}]\n{msg.text}")

async def example_human_feedback():
    """Example: Sequential workflow with human-in-the-loop feedback."""
    print("=== Human Feedback Example ===")
    
    # Create specialized agents
    planner = AgentTemplate(
        name="Planner",
        instructions="You are a planning expert. Create a detailed plan for the given task. Keep it concise."
    )
    
    implementer = AgentTemplate(
        name="Implementer",
        instructions="You are an implementation specialist. Execute the plan provided and deliver the solution."
    )
    
    validator = AgentTemplate(
        name="Validator",
        instructions="You are a quality assurance expert. Validate the implementation against the plan."
    )
    
    # Create orchestrator
    orchestrator = SequentialOrchestrator(
        agents=[planner, implementer, validator]
    )
    
    # Execute with human feedback checkpoints
    print(f"\nPipeline: {orchestrator}\n")
    outputs, feedback_requests = await orchestrator.run_with_human_feedback(
        "Design a simple caching system",
        feedback_agent_names=["Planner", "Implementer"]  # Request feedback after these agents
    )
    
    # Print feedback checkpoints
    if feedback_requests:
        print(f"\n===== Feedback Checkpoints =====")
        for i, request_id in enumerate(feedback_requests, start=1):
            print(f"{i}. Feedback requested at: {request_id}")
    
    # Print the final conversation
    if outputs:
        print("\n===== Final Conversation =====")
        messages = outputs[-1]
        for i, msg in enumerate(messages, start=1):
            name = msg.author_name or ("assistant" if msg.role == "assistant" else "user")
            print(f"{'-' * 60}\n{i:02d} [{name}]\n{msg.text}")


async def main():
    """Run all examples."""
    # await example_single_agent()
    # await example_streaming()
    # await example_specialized_agents()
    await example_human_feedback()

if __name__ == "__main__":
    asyncio.run(main())