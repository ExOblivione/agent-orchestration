from typing import List, cast, Callable, Optional
from src.agent_template import AgentTemplate
from agent_framework.orchestrations import HandoffBuilder
from agent_framework import Message, Agent


class HandOffOrchestrator:
    """
    Handoff workflow orchestrator for agent routing and delegation.
    
    This orchestrator allows agents to transfer conversations to other agents
    based on expertise and routing rules.
    
    Source: https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/handoff?pivots=programming-language-python
    """
    
    def __init__(
        self, 
        agents: List[AgentTemplate],
        workflow_builder: Optional[Callable[[List[Agent]], HandoffBuilder]] = None,
        termination_condition: Optional[Callable[[List[Message]], bool]] = None
    ):
        """
        Initialize the handoff orchestrator for non-interactive execution.
        
        This orchestrator enables autonomous mode by default, allowing agents to continue
        without human input. For interactive workflows that handle user input and tool
        approvals, use HandoffBuilder directly (see examples/handoff_patterns.py).
        
        Args:
            agents: List of agents to participate in handoffs
            workflow_builder: Optional function that takes a list of Agent objects and returns
                            a configured HandoffBuilder with .with_autonomous_mode() enabled.
                            If None, uses default configuration with autonomous mode.
            termination_condition: Optional function that determines when to stop the workflow.
                                 Takes conversation (list of Messages) and returns True to terminate.
                                 If None, workflow runs without automatic termination.
                                 
        Note:
            For interactive workflows with user input and tool approvals, use HandoffBuilder
            directly instead of this template. See examples/handoff_patterns.py for interactive
            patterns like tool_approval_example() and interactive_handoff_example().
        """
        self.agents = agents
        self.workflow_builder = workflow_builder
        self.termination_condition = termination_condition
    
    def _default_workflow_builder(self, agents: List[Agent]) -> HandoffBuilder:
        """
        Default workflow configuration with autonomous mode enabled.
        
        Override this method or pass a custom workflow_builder to __init__.
        
        Default configuration:
        - Starts with first agent (typically triage/coordinator)
        - Uses termination_condition from __init__ (None if not provided)
        - Autonomous mode enabled for non-interactive execution
        
        Note:
            Custom workflow builders should also enable autonomous mode if they
            want to work with the orchestrator's simple run() method. For interactive
            workflows that handle user input, use the workflow directly (see examples).
        """
        return (
            HandoffBuilder(
                name="default_handoff",
                participants=agents,
                termination_condition=self.termination_condition,
            )
            .with_autonomous_mode()  # Enable autonomous mode for non-interactive use
            .build()
        )
    
    async def run(self, initial_message: str) -> str:
        """
        Execute the handoff workflow autonomously with an initial message.
        
        The workflow runs in autonomous mode, allowing agents to continue without
        human input. Use termination_condition to control when the workflow stops.
        
        Args:
            initial_message: The starting message/prompt for the workflow
            
        Returns:
            The final conversation history from all agents
        """
        # Unwrap agents from AgentTemplate
        agents = [agent.agent for agent in self.agents]
        
        # Build the workflow using custom or default builder
        if self.workflow_builder:
            workflow = self.workflow_builder(agents)
        else:
            workflow = self._default_workflow_builder(agents)
        
        # Stream events and collect outputs
        outputs = []
        async for event in workflow.run(stream=True, message=initial_message):
            if event.type == "output":
                outputs.append(cast(list[Message], event.data))
        
        # Format and return conversation
        if outputs:
            messages: list[Message] = outputs[-1]
            result_parts = []
            for msg in messages:
                author = msg.author_name or msg.role
                result_parts.append(f"\n[{author}]\n{msg.text}")
            return "\n".join(result_parts)
        
        return "No response generated"
    
    def __repr__(self) -> str:
        """String representation of the orchestrator."""
        agent_names = ", ".join([agent.name for agent in self.agents])
        return f"HandOffOrchestrator([{agent_names}])"