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
from agent_framework.orchestrations import GroupChatBuilder
from agent_framework import AgentResponseUpdate


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
    
    final_conversation = await orchestrator.run(task, limit=4)
    
    # Print the final result
    print("\n=== Final Result ===")
    if final_conversation:
        for msg in final_conversation:
            author = msg.author_name or msg.role
            print(f"\n[{author}]\n{msg.text}")
    else:
        print("No response generated")
    
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
    
    # Stream the conversation in real-time
    final_conversation = []
    last_author = None
    
    agents = [pm.agent for pm in [product_manager, tech_lead, designer]]
    
    if orchestrator.orchestrator_agent:
        workflow_builder = GroupChatBuilder(
            participants=agents,
            termination_condition=lambda messages: sum(1 for msg in messages if msg.role == "assistant") >= 12,
            orchestrator_agent=coordinator.agent
        )
    else:
        workflow_builder = GroupChatBuilder(
            participants=agents,
            termination_condition=lambda messages: sum(1 for msg in messages if msg.role == "assistant") >= 12,
            selection_func=GroupChatOrchestrator.round_robin_selector
        )
    
    workflow = workflow_builder.build()
    
    async for event in workflow.run(task, stream=True):
        if event.type == "output" and isinstance(event.data, AgentResponseUpdate):
            author = event.data.author_name
            if author != last_author:
                if last_author is not None:
                    print()
                print(f"[{author}]:", end=" ", flush=True)
                last_author = author
            print(event.data.text, end="", flush=True)
        elif event.type == "output" and isinstance(event.data, list):
            final_conversation = event.data
    
    print("\n\n" + "=" * 80)
    print("\n=== Final Result ===")
    if final_conversation:
        for msg in final_conversation:
            author = msg.author_name or msg.role
            print(f"\n[{author}]\n{msg.text}")
    else:
        print("No response generated")


async def group_chat_with_human_feedback():
    """Example: Group chat with human-in-the-loop feedback."""
    print("\n=== Group Chat with Human Feedback Example ===")
    
    # Create specialized agents
    analyst = AgentTemplate(
        name="Analyst",
        instructions="You are a data analyst. Provide data-driven insights and recommendations. Keep responses brief."
    )
    
    engineer = AgentTemplate(
        name="Engineer",
        instructions="You are a software engineer. Provide technical implementation details. Keep responses brief."
    )
    
    manager = AgentTemplate(
        name="Manager",
        instructions="You are a project manager. Synthesize inputs and provide actionable decisions. Keep responses brief."
    )
    
    # Create orchestrator
    orchestrator = GroupChatOrchestrator(
        agents=[analyst, engineer, manager]
    )
    
    # Execute with human feedback checkpoints
    task = "Should we migrate our monolith to microservices?"
    
    print(f"\nOrchestrator: {orchestrator}")
    print(f"Task: {task}\n")
    print("=" * 80 + "\n")
    
    final_conversation, feedback_requests = await orchestrator.run_with_human_feedback(
        task,
        feedback_agent_names=["Analyst", "Engineer"],  # Request feedback after these agents
        limit=6
    )
    
    # Print feedback checkpoints
    if feedback_requests:
        print(f"\n\n===== Feedback Checkpoints =====")
        for i, request_id in enumerate(feedback_requests, start=1):
            print(f"{i}. Feedback requested at: {request_id}")
    
    # Print the final conversation
    print("\n" + "=" * 80)
    print("\n=== Final Conversation ===")
    if final_conversation:
        for msg in final_conversation:
            author = msg.author_name or msg.role
            print(f"\n[{author}]\n{msg.text}")
            print("-" * 80)
    else:
        print("No response generated")


async def main():
    """Run all examples."""
    # await group_chat_example()
    await group_chat_with_orchestrator_example()
    # await group_chat_with_human_feedback()

if __name__ == "__main__":
    asyncio.run(main())