"""
Examples of using the AgentTemplate in different scenarios.

This demonstrates how the simple agent template can be used
for various roles and orchestration patterns.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import src
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from src.agent_template import AgentTemplate
from src.groupchat_template import GroupChatOrchestrator


async def group_chat_example():
    """Example: Multiple agents collaborating in a group chat using round-robin."""
    print("\n=== Group Chat Orchestration Example ===")
    
    # Create specialized agents for collaborative discussion
    researcher = AgentTemplate(
        name="Researcher",
        instructions="""You are a research specialist in a collaborative discussion. 
        Your role: Provide concise, factual information to help answer the user's question.
        Keep responses brief (2-3 sentences). After sharing key facts, indicate you're done by saying 
        something like 'That covers the main points from my research.' or 'I'll let the Writer synthesize this.'"""
    )
    
    writer = AgentTemplate(
        name="Writer",
        instructions="""You are a technical writer in a collaborative discussion.
        Your role: Build upon the Researcher's findings to create a clear, comprehensive answer.
        - Review what the Researcher shared
        - Synthesize it into a well-structured response
        - Add clarity and context
        - Keep it concise (3-4 sentences)
        Signal completion by saying 'This synthesis is complete.' or 'I believe this covers the question well.'"""
    )
    
    # Create group chat orchestrator with round-robin selection (no orchestrator agent)
    orchestrator = GroupChatOrchestrator(
        agents=[researcher, writer],
    )
    
    # Execute the group chat
    task = "What are the key benefits of async/await in Python?"
    
    print(f"\nOrchestrator: {orchestrator}")
    print(f"Task: {task}\n")
    print("=" * 80 + "\n")
    
    final_result = await orchestrator.run(task, verbose=False, limit=4)
    print("\n=== Final Result ===")
    print(final_result)
    print("\n" + "=" * 80)
    print("Group chat completed!")
    print("=" * 80)


async def group_chat_with_orchestrator_example():
    """Example: Group chat with intelligent agent-based orchestrator."""
    print("\n=== Group Chat with Agent-Based Orchestrator Example ===")
    
    # Create specialized agents with clear descriptions for the orchestrator
    product_manager = AgentTemplate(
        name="ProductManager",
        instructions="""You are a product manager in a collaborative team discussion.
        
        In your responses:
        - Build on what TechLead and Designer have said
        - Address concerns or questions raised by the team
        - Add new product/business perspectives each time you speak
        - Focus on: user needs, product requirements, business value, priorities
        
        Keep responses concise (2-3 sentences max)."""
    )
    
    tech_lead = AgentTemplate(
        name="TechLead",
        instructions="""You are a technical lead in a collaborative team discussion.
        
        In your responses:
        - Build on what ProductManager and Designer have said
        - Address concerns or questions raised by the team
        - Add new technical perspectives each time you speak
        - Focus on: technical feasibility, architecture, implementation, scalability, risks
        
        Keep responses concise (2-3 sentences max)."""
    )
    
    designer = AgentTemplate(
        name="Designer",
        instructions="""You are a UX designer in a collaborative team discussion.
        
        In your responses:
        - Build on what ProductManager and TechLead have said
        - Address concerns or questions raised by the team
        - Add new UX perspectives each time you speak
        - Focus on: user experience, design patterns, usability, accessibility
        
        Keep responses concise (2-3 sentences max)."""
    )
    
    # Create the orchestrator agent that intelligently manages the conversation
    coordinator = AgentTemplate(
        name="Coordinator",
        instructions="""You coordinate a team discussion to thoroughly evaluate the user's question through MULTIPLE ROUNDS of discussion.

            Your team members and their expertise:
            - ProductManager: Analyzes product requirements and user needs
            - TechLead: Evaluates technical feasibility and suggests architecture  
            - Designer: Focuses on user experience and design quality

            Discussion process - RUN AT LEAST 3 ROUNDS OF DISCUSSION:
            
            ROUND 1 - Initial perspectives:
            1. ProductManager shares initial requirements
            2. TechLead provides technical assessment
            3. Designer gives UX perspective
            
            ROUND 2 - Build on previous points:
            4. ProductManager responds to tech/design concerns, adds business considerations
            5. TechLead addresses product needs with specific technical solutions
            6. Designer refines UX based on product and technical constraints
            
            ROUND 3 - Deep dive and consensus:
            7. ProductManager prioritizes features and timeline
            8. TechLead proposes implementation phases
            9. Designer suggests incremental UX improvements
            
            Continue additional rounds as needed to explore trade-offs, risks, and decisions.
            
            CRITICAL: Your response must be ONLY the name of the next speaker (e.g., "ProductManager" or "TechLead" or "Designer").
            DO NOT provide summaries or conclusions - just select speakers to keep the discussion going.
            Let the conversation naturally build with each agent responding to others."""
    )
    
    # Create group chat with agent-based orchestrator
    orchestrator = GroupChatOrchestrator(
        agents=[product_manager, tech_lead, designer],
        orchestrator_agent=coordinator
    )
    
    # Execute the group chat with a product planning task
    task = "Should we add real-time collaborative editing to our document app?"
    
    print(f"\nOrchestrator: {orchestrator}")
    print(f"Task: {task}\n")
    print("=" * 80 + "\n")
    
    print("Running with agent-based orchestrator (intelligent speaker selection):\n")
    final_result = await orchestrator.run(task, verbose=True, limit=12)
    
    print("=" * 80)
    print("\n=== Final Result ===")
    print(final_result)


async def main():
    """Run all examples."""
    # await group_chat_example()
    await group_chat_with_orchestrator_example()

if __name__ == "__main__":
    asyncio.run(main())