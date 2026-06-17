import json
import asyncio
from typing import List, cast
from src.agent_template import AgentTemplate
from agent_framework.orchestrations import MagenticBuilder, MagenticPlanReviewRequest

from agent_framework import (
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
        intermediate_outputs: bool = True,
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
            intermediate_outputs: Whether to stream intermediate agent outputs (default: True)
            on_event: Optional callback function to handle workflow events (default: None)
            
        Returns:
            The final synthesized output from the manager
        """
        participants = [agent.agent for agent in self.agents]
        workflow = MagenticBuilder(
            participants=participants,
            intermediate_outputs=intermediate_outputs,
            enable_plan_review=False,
            manager_agent=self.manager_agent.agent,
            max_round_count=max_rounds,
            max_stall_count=max_stalls,
            max_reset_count=max_resets,
        ).build()        
        
        output_event: WorkflowEvent | None = None
        async for event in workflow.run(initial_message, stream=True):
            # Call event callback if provided
            if on_event:
                on_event(event, self.manager_agent.name)
            
            if event.type == "output":
                output_event = event

        if output_event:
            output_messages = cast(list[Message], output_event.data)
            return output_messages[-1].text

        return "No response generated"
    
    async def run_with_plan_review(
        self,
        initial_message: str,
        max_rounds: int = 10,
        max_stalls: int = 3,
        max_resets: int = 2,
        intermediate_outputs: bool = True,
        on_event = None,
        on_plan_review = None
    ) -> str:
        """
        Execute the Magentic workflow with human-in-the-loop plan review.
        
        The manager will propose plans before execution, allowing you to:
        - Press Enter to approve the plan as-is
        - Provide feedback to revise the plan
        
        This is useful for ensuring plans align with your expectations before
        agents execute subtasks.
        
        Args:
            initial_message: The task or question for the workflow
            max_rounds: Maximum number of orchestration rounds (default: 10)
            max_stalls: Maximum stall count before replanning (default: 3)
            max_resets: Maximum number of replans allowed (default: 2)
            intermediate_outputs: Whether to stream intermediate agent outputs (default: True)
            on_event: Optional callback function to handle workflow events (default: None)
            on_plan_review: Optional callback function to handle plan review (default: None)
            
        Returns:
            The final synthesized output from the manager
        """
        participants = [agent.agent for agent in self.agents]
        workflow = MagenticBuilder(
            participants=participants,
            intermediate_outputs=intermediate_outputs,
            enable_plan_review=True,  # Enable plan review
            manager_agent=self.manager_agent.agent,
            max_round_count=max_rounds,
            max_stall_count=max_stalls,
            max_reset_count=max_resets,
        ).build()
        
        pending_request: WorkflowEvent | None = None
        pending_responses: dict[str, object] | None = None
        output_event: WorkflowEvent | None = None
        
        while not output_event:
            # Run workflow with or without responses
            if pending_responses is not None:
                stream = workflow.run(stream=True, responses=pending_responses)
            else:
                stream = workflow.run(initial_message, stream=True)
            
            # Process events
            async for event in stream:
                # Call event callback if provided
                if on_event:
                    on_event(event, self.manager_agent.name)
                
                if event.type == "request_info" and event.request_type is MagenticPlanReviewRequest:
                    pending_request = event
                
                elif event.type == "output":
                    output_event = event
            
            pending_responses = None
            
            # Handle plan review request if any
            if pending_request is not None:
                event_data = cast(MagenticPlanReviewRequest, pending_request.data)
                
                # Use callback if provided, otherwise use default behavior
                if on_plan_review:
                    reply = await on_plan_review(event_data)
                else:
                    # Default plan review handler
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
                    pending_responses = {pending_request.request_id: event_data.approve()}
                else:
                    pending_responses = {pending_request.request_id: event_data.revise(reply)}
                
                pending_request = None
        
        if output_event:
            output_messages = cast(list[Message], output_event.data)
            return output_messages[-1].text
        
        return "No response generated"
    
    def __repr__(self) -> str:
        """String representation of the orchestrator."""
        agent_names = ", ".join([agent.name for agent in self.agents])
        return f"MagenticOrchestrator(manager={self.manager_agent.name}, agents=[{agent_names}])"