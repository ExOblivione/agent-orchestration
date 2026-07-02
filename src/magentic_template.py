import json
import asyncio
from typing import List, cast
from src.agent_template import AgentTemplate
from agent_framework.orchestrations import MagenticBuilder, MagenticPlanReviewRequest

from agent_framework import (
    AgentResponseUpdate,
    Message,
    WorkflowEvent,
)

class MagenticOrchestrator:
    """
    Magentic workflow orchestrator for dynamic multi-agent collaboration.
    
    This orchestrator uses a manager agent to coordinate specialized agents,
    dynamically selecting which agent should act next based on task progress
    and agent capabilities. Supports complex, open-ended tasks requiring
    iterative refinement.

    Based on Magentic-One from AutoGen: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html
    Source: https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/magentic?pivots=programming-language-python
    """
    
    def __init__(self, agents: List[AgentTemplate], manager_agent: AgentTemplate):
        """
        Initialize the Magentic orchestrator.
        
        Args:
            agents: List of specialized agents for the manager to coordinate
            manager_agent: The manager agent responsible for orchestrating the workflow
        """
        self.agents = agents
        self.manager_agent = manager_agent
    
    async def run(
        self, 
        initial_message: str, 
        max_rounds: int = 10, 
        max_stalls: int = 3, 
        max_resets: int = 2,
        on_event = None
    ) -> str:
        """
        Execute the Magentic workflow without plan review.
        
        The manager will coordinate agents autonomously based on the task.
        
        Args:
            initial_message: The task or question for the workflow
            max_rounds: Maximum number of orchestration rounds (default: 10)
            max_stalls: Maximum stall count before replanning (default: 3)
            max_resets: Maximum number of replans allowed (default: 2)
            on_event: Optional callback function to handle workflow events (default: None)
            
        Returns:
            The final synthesized output from the manager
        """
        participants = [agent.agent for agent in self.agents]
        workflow = MagenticBuilder(
            participants=participants,
            enable_plan_review=False,
            manager_agent=self.manager_agent.agent,
            max_round_count=max_rounds,
            max_stall_count=max_stalls,
            max_reset_count=max_resets,
        ).build()        
        
        outputs = []
        async for event in workflow.run(initial_message, stream=True):
            # Call event callback if provided
            if on_event:
                on_event(event, self.manager_agent.name)
            
            if event.type == "output":
                outputs.append(event.data)

        # Extract final text from outputs
        if outputs:
            last_output = outputs[-1]
            # Handle both AgentResponseUpdate and list[Message] cases
            if isinstance(last_output, AgentResponseUpdate):
                return last_output.text
            elif isinstance(last_output, list):
                messages = cast(list[Message], last_output)
                return messages[-1].text if messages else "No response generated"

        return "No response generated"
    
    def __repr__(self) -> str:
        """String representation of the orchestrator."""
        agent_names = ", ".join([agent.name for agent in self.agents])
        return f"MagenticOrchestrator(manager={self.manager_agent.name}, agents=[{agent_names}])"