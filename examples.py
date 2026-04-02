"""
Examples of using the AgentTemplate in different scenarios.

This demonstrates how the simple agent template can be used
for various roles and orchestration patterns.
"""
import asyncio
from src.agent_template import AgentTemplate
from src.sequential_template import SequentialOrchestrator
from src.concurrent_template import ConcurrentOrchestrator


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
    """Example: Multiple agents working concurrently with optional aggregation."""
    print("\n=== Concurrent Orchestration Example ===")
    
    # Create specialized agents that will work in parallel
    agents = [
        AgentTemplate(
            name="researcher",
            instructions="You're an expert market and product researcher. Given a prompt, provide concise, factual insights, opportunities, and risks."
        ),
        AgentTemplate(
            name="marketer",
            instructions="You're a creative marketing strategist. Craft compelling value propositions and target messaging aligned to the prompt."
        ),
        AgentTemplate(
            name="legal",
            instructions="You're a cautious legal/compliance reviewer. Highlight constraints, disclaimers, and policy concerns based on the prompt."
        )
    ]
    
    # Optional: Create aggregator agent to consolidate responses
    # PLACEHOLDER: Set to None to see all agent responses, or provide an aggregator to consolidate
    aggregator = AgentTemplate(
        name="summarizer",
        instructions="You are a helpful assistant that consolidates multiple domain expert outputs into one cohesive, concise summary with clear takeaways. Keep it under 200 words."
    )
    aggregator = None  # Uncomment to see individual agent responses without aggregation
    
    # Create concurrent orchestrator
    orchestrator = ConcurrentOrchestrator(
        agents=agents,
        aggregator=aggregator
    )
    
    # Execute in parallel
    question = "We are launching a new budget-friendly electric bike for urban commuters."
    
    print(f"\nOrchestrator: {orchestrator}\n")
    final_result = await orchestrator.run(question)
    
    print(final_result)


async def main():
    """Run all examples."""
    # await example_single_agent()
    # await example_streaming()
    # await example_specialized_agents()
    await example_concurrent_agents()

if __name__ == "__main__":
    asyncio.run(main())