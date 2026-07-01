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
    # Set to None to see only individual responses without aggregation
    aggregator = AgentTemplate(
        name="summarizer",
        instructions="You are a helpful assistant that consolidates multiple domain expert outputs into one cohesive, concise summary with clear takeaways. Keep it under 200 words."
    )
    # aggregator = None  # Uncomment to disable aggregation
    
    # Create concurrent orchestrator
    orchestrator = ConcurrentOrchestrator(
        agents=agents,
        aggregator=aggregator
    )
    
    # Execute in parallel
    question = "We are launching a new budget-friendly electric bike for urban commuters."
    
    print(f"\nOrchestrator: {orchestrator}\n")
    messages, aggregated_summary = await orchestrator.run(question)
    
    # Print the results
    if messages:
        print("===== Full Concurrent Conversation =====")
        for i, msg in enumerate(messages, start=1):
            name = msg.author_name if msg.author_name else msg.role
            separator = "-" * 60
            print(f"{separator}\n{i:02d} [{name}]:\n{msg.text}")
        
        # Print aggregator's consolidated output if available
        if aggregated_summary:
            print("\n" + "=" * 60)
            print("===== Aggregator's Consolidated Summary =====")
            print("=" * 60)
            print(aggregated_summary)
    else:
        print("No response generated")

async def main():
    await example_concurrent_agents()

if __name__ == "__main__":
    asyncio.run(main())