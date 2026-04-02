"""
Examples of using the AgentTemplate in different scenarios.

This demonstrates how the simple agent template can be used
for various roles and orchestration patterns.
"""
import asyncio
from src.agent_template import AgentTemplate
from src.sequential_template import SequentialOrchestrator
# from src.concurrent_template import ConcurrentOrchestrator


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
    final_result = await orchestrator.run(
        "Create a REST API endpoint for user registration with email validation"
    )
    
    print("\n" + "="*60)
    print("FINAL RESULT:")
    print("="*60)
    print(final_result)


async def example_concurrent_agents():
    """Example: Multiple agents working concurrently with aggregation."""
    print("\n=== Concurrent Orchestration Example ===")
    
    # Create specialized agents that will work in parallel
    agents = [
        AgentTemplate(
            name="DataAnalyst",
            instructions="You are a data analysis expert. Analyze the question from a metrics and data perspective. Keep it concise."
        ),
        AgentTemplate(
            name="UXDesigner",
            instructions="You are a UX/UI expert. Analyze the question from a user experience and design perspective. Keep it concise."
        ),
        AgentTemplate(
            name="TechArchitect",
            instructions="You are a technical architect. Analyze the question from a technical implementation perspective. Keep it concise."
        )
    ]
    
    # Create aggregator agent
    aggregator = AgentTemplate(
        name="Synthesizer",
        instructions="You are a synthesis expert. Combine the different perspectives into a comprehensive, well-rounded answer."
    )
    
    # Create concurrent orchestrator
    orchestrator = ConcurrentOrchestrator(
        agents=agents,
        aggregator=aggregator
    )
    
    # Execute in parallel
    question = "What makes a good dashboard for monitoring system performance?"
    
    print(f"\nOrchestrator: {orchestrator}\n")
    final_result = await orchestrator.run(question)
    
    print("="*60)
    print("FINAL SYNTHESIZED RESULT:")
    print("="*60)
    print(final_result)


async def main():
    """Run all examples."""
    # await example_single_agent()
    # await example_streaming()
    await example_specialized_agents()
    # await example_concurrent_agents()

if __name__ == "__main__":
    asyncio.run(main())