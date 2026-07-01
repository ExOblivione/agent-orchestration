"""
Examples of using the AgentTemplate in different scenarios.

Patterns demonstrated:
- Sequential orchestration with specialized agents
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import src
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from src import AgentTemplate, SequentialOrchestrator

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
        "Write a simple hello world function in Python"
    )
    
    # Print the responses
    if outputs:
        print("===== Agent Responses =====\n")
        
        current_author = None
        for msg in outputs:
            if msg.text:  # Only print messages with actual text content
                author = msg.author_name or msg.role
                
                # Print author name only when it changes
                if author != current_author:
                    if current_author is not None:
                        print()  # New line before switching to next agent
                    print(f"\n[{author.upper()}]: ", end="", flush=True)
                    current_author = author
                
                print(msg.text, end="", flush=True)
        print("\n")

async def main():
    await example_specialized_agents()

if __name__ == "__main__":
    asyncio.run(main())