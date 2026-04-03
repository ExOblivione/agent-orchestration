"""
Magentic Orchestration Patterns

This module provides examples for implementing Magentic orchestrations with
the Microsoft Agent Framework.

Source: https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/magentic?pivots=programming-language-python

Key Patterns Implemented:
1. Autonomous coordination - Manager orchestrates without human intervention
2. Plan review - Human-in-the-loop plan approval before execution
3. Research + Analysis - Combining specialized agents for complex tasks
"""

import os
from typing import Dict
from src.magentic_template import MagenticOrchestrator
from src.agent_template import AgentTemplate


def create_research_analysis_agents() -> Dict[str, AgentTemplate]:
    """
    Create specialized agents for research and analysis tasks.
    
    Returns:
        Dictionary of agent templates by role
    """
    
    researcher = AgentTemplate(
        name="ResearcherAgent",
        instructions=(
            "You gather facts and data. When you see analysis or opinions from others, "
            "provide additional facts to support or challenge them. Keep responses brief but substantive."
        ),
    )
    
    analyst = AgentTemplate(
        name="AnalystAgent",
        instructions=(
            "You analyze information critically. When you see facts from the researcher, "
            "analyze their implications. Challenge assumptions and provide counterpoints. "
            "Keep responses concise but insightful."
        ),
    )
    
    writer = AgentTemplate(
        name="WriterAgent",
        instructions=(
            "You organize and synthesize ideas. When you see research and analysis, "
            "identify gaps or conflicts and ask for clarification. Structure the discussion. "
            "Keep responses brief."
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
            "Assign tasks to get different perspectives and encourage debate. "
            "Make multiple agents respond before synthesizing. Keep plans brief."
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
    
    result = await orchestrator.run(
        task,
        max_rounds=10,  # More rounds for conversation
        max_stalls=2,
        max_resets=2,
        intermediate_outputs=True  # Stream intermediate outputs for visibility
    )
    
    print(result)



# ============================================================================
# MAIN - Run Examples
# ============================================================================

async def main():
    """Run examples (uncomment the ones you want to test)."""
        
    await basic_magentic_example()
    
    print("\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
