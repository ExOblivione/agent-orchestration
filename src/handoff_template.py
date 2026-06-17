from typing import List, Callable, Optional
from src.agent_template import AgentTemplate
from agent_framework.orchestrations import HandoffBuilder
from agent_framework import Message


class HandOffOrchestrator:
    """
    Handoff workflow orchestrator for agent routing and delegation.
    
    This orchestrator allows agents to transfer conversations to other agents
    based on expertise and routing rules. Runs in autonomous mode by default.
    
    For interactive workflows with user input and tool approvals, use HandoffBuilder
    directly instead of this template (see examples/handoff_patterns.py).
    
    Source: https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/handoff?pivots=programming-language-python
    """
    
    def __init__(
        self, 
        agents: List[AgentTemplate],
        termination_condition: Optional[Callable[[List[Message]], bool]] = None,
        workflow_name: str = "handoff"
    ):
        """
        Initialize the handoff orchestrator for autonomous execution.
        
        Args:
            agents: List of agents to participate in handoffs
            termination_condition: Optional function that determines when to stop the workflow.
                                 Takes conversation (list of Messages) and returns True to terminate.
                                 If None, workflow runs without automatic termination.
            workflow_name: Name for the workflow (default: "handoff")
        """
        self.agents = agents
        self.termination_condition = termination_condition
        self.workflow_name = workflow_name
    
    async def run(self, initial_message: str, on_event = None) -> list[Message]:
        """
        Execute the handoff workflow autonomously with an initial message.
        
        The workflow runs in autonomous mode, allowing agents to continue without
        human input. Use termination_condition to control when the workflow stops.
        
        Args:
            initial_message: The starting message/prompt for the workflow
            on_event: Optional callback function to handle workflow events (default: None)
            
        Returns:
            List of messages from the handoff conversation
        """
        # Build workflow with autonomous mode
        participants = [agent.agent for agent in self.agents]
        workflow = (
            HandoffBuilder(
                name=self.workflow_name,
                participants=participants,
                termination_condition=self.termination_condition,
            )
            .with_start_agent(participants[0])  # Start with first agent
            .with_autonomous_mode()
            .build()
        )
        
        # Stream events and collect final conversation
        final_messages: list[Message] = []
        async for event in workflow.run(initial_message, stream=True):
            # Call event callback if provided
            if on_event:
                on_event(event)
            
            if event.type == "output":
                # Check if this is the final output (list of Messages) vs streaming updates
                if isinstance(event.data, list):
                    final_messages = event.data
        
        return final_messages
    
    def __repr__(self) -> str:
        """String representation of the orchestrator."""
        agent_names = ", ".join([agent.name for agent in self.agents])
        return f"HandOffOrchestrator([{agent_names}])"