"""
Magentic Orchestration Patterns

Source: https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/magentic?pivots=programming-language-python

Key Patterns:
1. Autonomous coordination - Manager orchestrates without human intervention
2. Plan review - Human-in-the-loop plan approval before execution
3. Research + Analysis - Combining specialized agents for complex tasks
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import src
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import asyncio
from src.magentic_template import MagenticOrchestrator
from src.agent_template import AgentTemplate
from agent_framework import AgentResponseUpdate, Message


# ============================================================================
# Event Handlers for Printing Workflow Events
# ============================================================================

class MagenticEventPrinter:
    """Handler for printing Magentic workflow events."""
    
    def __init__(self):
        self.last_executor: str | None = None
        self.last_message_id: str | None = None
    
    def __call__(self, event, manager_name: str):
        """Handle a workflow event and print appropriate output."""
        
        if event.type == "output" and isinstance(event.data, AgentResponseUpdate):
            self._handle_agent_output(event)
        
        elif event.type == "magentic_orchestrator":
            self._handle_orchestrator_event(event, manager_name)
    
    def _handle_agent_output(self, event):
        """Handle streaming agent output."""
        message_id = event.data.message_id
        executor_id = getattr(event, 'executor_id', None)
        
        # Print agent header when switching to a new agent
        if executor_id and executor_id != self.last_executor:
            if self.last_executor is not None:
                print("\n")
            print(f"\n{'-'*20}[{executor_id.upper()}]{'-'*20}")
            self.last_executor = executor_id
        
        print(event.data.text, end="", flush=True)
        self.last_message_id = message_id
    
    def _handle_orchestrator_event(self, event, manager_name: str):
        """Handle orchestrator-specific events."""
        event_type = event.data.event_type.name
        
        if event_type == "PLAN_CREATED":
            self._print_plan(event)
        
        elif event_type == "PROGRESS_LEDGER_UPDATED":
            self._print_progress_update(event, manager_name)
        
        elif event_type == "REPLANNED":
            self._print_replan(event)
    
    def _print_plan(self, event):
        """Print the manager's plan."""
        print(f"\n{'*'*60}")
        print(f"[MANAGER PLAN]")
        print(f"{'*'*60}")
        if isinstance(event.data.content, Message):
            print(f"\n{event.data.content.text}\n")
    
    def _print_progress_update(self, event, manager_name: str):
        """Print agent progress updates."""
        if isinstance(event.data.content, Message):
            message = event.data.content
            
            # Try to get agent name from multiple sources
            agent_name = None
            if hasattr(message, 'author_name') and message.author_name:
                agent_name = message.author_name
            elif hasattr(event, 'executor_id') and event.executor_id:
                agent_name = event.executor_id
            elif hasattr(message, 'role'):
                agent_name = message.role
            
            # Format output with agent header
            if agent_name:
                agent_display = agent_name.upper()
                if agent_name == manager_name:
                    print(f"\n{'-'*20}[MANAGER: {agent_display}]{'-'*20}")
                else:
                    print(f"\n{'-'*20}[AGENT: {agent_display}]{'-'*20}")
            else:
                print(f"\n{'-'*20}[RESPONSE]{'-'*20}")
            
            print(f"{message.text}\n")
    
    def _print_replan(self, event):
        """Print replanning notification."""
        print(f"\n{'!'*60}")
        print(f"[MANAGER REPLANNING]")
        print(f"{'!'*60}")
        if isinstance(event.data.content, Message):
            print(f"\n{event.data.content.text}\n")


async def default_plan_review_handler(event_data):
    """Default handler for plan review requests."""
    print("\n\n[Magentic Plan Review Request]")
    print("=" * 60)
    
    if event_data.current_progress is not None:
        print("\nCurrent Progress Ledger:")
        print(json.dumps(event_data.current_progress.to_dict(), indent=2))
        print()
    
    print(f"Proposed Plan:\n{event_data.plan.text}\n")
    print("=" * 60)
    print("Options:")
    print("  - Press Enter to APPROVE the plan")
    print("  - Type feedback to REVISE the plan")
    print()
    
    reply = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
    
    if reply.strip() == "":
        print("Plan approved. Proceeding with execution...\n")
    else:
        print(f"Plan revised with feedback: {reply}\n")
    
    return reply


# ============================================================================
# Agent Creation Functions
# ============================================================================
def create_research_analysis_agents() -> dict[str, AgentTemplate]:
    """
    Create specialized agents for research and analysis tasks.
    
    Returns:
        Dictionary of agent templates by role
    """
    
    researcher = AgentTemplate(
        name="ResearcherAgent",
        instructions=(
            "You gather facts and data. "
            "When assigned: provide new information each time. "
            "When you see analysis or opinions from others, provide additional facts to support or challenge them. "
            "Build on previous contributions - don't just repeat what you've already said. "
            "Keep responses brief but substantive."
        ),
    )
    
    analyst = AgentTemplate(
        name="AnalystAgent",
        instructions=(
            "You analyze information critically. "
            "When assigned: provide deeper analysis each time. "
            "When you see facts from the researcher, analyze their implications and identify patterns. "
            "Challenge assumptions and provide counterpoints. "
            "Build on your previous analysis - go deeper with each round. "
            "Keep responses concise but insightful."
        ),
    )
    
    writer = AgentTemplate(
        name="WriterAgent",
        instructions=(
            "You organize and synthesize ideas. "
            "When assigned: structure the discussion and identify what's missing. "
            "When you see research and analysis, identify gaps, conflicts, or areas needing clarification. "
            "Ask for specific information to fill gaps. "
            "In later rounds, help organize the emerging consensus. "
            "Keep responses brief but actionable."
        ),
    )
    
    return {
        "researcher": researcher,
        "analyst": analyst,
        "writer": writer,
    }


def create_manager_agent() -> AgentTemplate:
    """
    Create a manager agent for Magentic orchestration.
    
    Returns:
        Manager agent template
    """
    return AgentTemplate(
        name="ManagerAgent",
        instructions=(
            "You coordinate a team of researcher, analyst, and writer. "
            "Your goal is to facilitate MULTIPLE ROUNDS of discussion before concluding. "
            "\n\nProcess:"
            "\n1. Have researcher provide initial facts"
            "\n2. Have analyst critique and analyze those facts"
            "\n3. Have writer identify gaps or conflicts"
            "\n4. Go back to researcher for additional data based on gaps"
            "\n5. Have analyst provide deeper analysis"
            "\n6. Continue iterating until you have comprehensive coverage"
            "\n7. Only conclude when all perspectives have been thoroughly explored"
            "\n\nEncourage debate and challenge assumptions. Don't rush to conclusions. "
            "Keep individual plans brief but run multiple rounds."
        ),
    )


async def basic_magentic_example():
    """
    Example 1: Basic Magentic orchestration without plan review.
    
    Demonstrates:
    - Autonomous manager coordination
    - Dynamic agent selection
    - Complex task breakdown
    """
    print("\n=== Basic Magentic Example ===\n")
    
    # Create agents
    agents_dict = create_research_analysis_agents()
    manager = create_manager_agent()
    
    agents = [
        agents_dict["researcher"],
        agents_dict["analyst"],
        agents_dict["writer"],
    ]
    
    # Create orchestrator with reduced limits for context window
    orchestrator = MagenticOrchestrator(
        agents=agents,
        manager_agent=manager
    )
    
    # Task designed to spark debate and require multiple perspectives
    task = (
        "Should companies adopt AI code assistants like GitHub Copilot? "
        "I need research on adoption rates, analysis of pros/cons, and a structured recommendation. "
        "Get input from all team members before concluding."
    )
    
    # Create event printer to handle all console output
    event_printer = MagenticEventPrinter()
    
    result = await orchestrator.run(
        task,
        max_rounds=10,  # More rounds for conversation
        max_stalls=2,
        max_resets=2,
        intermediate_outputs=True,  # Stream intermediate outputs for visibility
        on_event=event_printer  # Pass the event handler
    )
    
    print(result)

async def main():
    await basic_magentic_example()
    

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())