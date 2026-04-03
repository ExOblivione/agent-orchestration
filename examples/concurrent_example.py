"""
Examples of using the AgentTemplate in the Concurrent Orchestrator pattern.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import src
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from src import AgentTemplate, ConcurrentOrchestrator


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
    await example_concurrent_agents()

if __name__ == "__main__":
    asyncio.run(main())