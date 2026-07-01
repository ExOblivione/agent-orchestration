from typing import List, cast
from src.agent_template import AgentTemplate
from agent_framework.orchestrations import SequentialBuilder
from agent_framework import Message


class SequentialOrchestrator:
    """
    Sequential workflow orchestrator for agent pipeline execution.
    
    This orchestrator runs agents in sequence, passing the output of each
    agent as input to the next agent in the pipeline.

    Source: https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/sequential?pivots=programming-language-python
    """
    
    def __init__(self, agents: List[AgentTemplate]):
        """
        Initialize the sequential orchestrator.
        
        Args:
            agents: List of agents to execute in sequence
        """
        self.agents = agents
    
    def _build_workflow(self, include_request_info: bool = False, feedback_agent_names: List[str] | None = None):
        """
        Build the sequential workflow with optional request_info enabled.
        
        Args:
            include_request_info: Whether to enable human-in-the-loop feedback
            feedback_agent_names: List of agent names to pause after for feedback
            
        Returns:
            Built workflow ready to run
        """
        seq_agents = [agent.agent for agent in self.agents]
        builder = SequentialBuilder(participants=seq_agents)
        
        if include_request_info:
            if feedback_agent_names:
                return builder.with_request_info(agents=feedback_agent_names).build()
            else:
                return builder.with_request_info().build()
        
        return builder.build()
    
    async def run(self, initial_message: str) -> list[list[Message]]:
        """
        Execute the sequential workflow with an initial message.
        
        Args:
            initial_message: The starting message/prompt for the workflow
            
        Returns:
            List of message lists representing the conversation at each step
        """
        workflow = self._build_workflow()
        
        # Run the workflow and collect outputs
        outputs: list[list[Message]] = []
        async for event in workflow.run(initial_message, stream=True):
            if event.type == "output":
                outputs.append(cast(list[Message], event.data))
        
        return outputs
    
    def __repr__(self) -> str:
        """String representation of the orchestrator."""
        agent_names = " -> ".join([agent.name for agent in self.agents])
        return f"SequentialOrchestrator({agent_names})"