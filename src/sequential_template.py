from typing import List, cast
from src.agent_template import AgentTemplate
from agent_framework.orchestrations import SequentialBuilder, AgentRequestInfoResponse
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
    
    async def run(self, initial_message: str) -> list[list[Message]]:
        """
        Execute the sequential workflow with an initial message.
        
        Args:
            initial_message: The starting message/prompt for the workflow
            
        Returns:
            List of message lists representing the conversation at each step
        """
        # Build the sequential workflow with actual agents
        seq_agents = [agent.agent for agent in self.agents]
        workflow = SequentialBuilder(participants=seq_agents).build()
        
        # Run the workflow and collect outputs
        outputs: list[list[Message]] = []
        async for event in workflow.run(initial_message, stream=True):
            if event.type == "output":
                outputs.append(cast(list[Message], event.data))
        
        return outputs
    
    async def run_with_human_feedback(
        self, 
        initial_message: str, 
        feedback_agent_names: List[str] | None = None
    ) -> str:
        """
        Execute the sequential workflow with human-in-the-loop feedback.
        
        This method pauses after specified agents respond, allowing for
        external input or review before continuing to the next agent.
        
        Args:
            initial_message: The starting message/prompt for the workflow
            feedback_agent_names: List of agent names to pause after for feedback.
                                 If None, pauses after all agents.
            
        Returns:
            List of message lists representing the conversation at each step,
            along with a list of request IDs where feedback was requested
        """
        # Build the sequential workflow with actual agents
        seq_agents = [agent.agent for agent in self.agents]
        
        # Build workflow with request_info enabled for specified agents
        builder = SequentialBuilder(participants=seq_agents)
        if feedback_agent_names:
            workflow = builder.with_request_info(agents=feedback_agent_names).build()
        else:
            workflow = builder.with_request_info().build()
        
        feedback_requests = []
        
        async def process_event_stream(stream):
            """Process events and collect request_info responses."""
            responses = {}
            outputs = []
            
            async for event in stream:
                if event.type == "request_info":
                    # Auto-approve for this template
                    # In production, this is where you'd gather actual human feedback
                    feedback_requests.append(event.request_id)
                    responses[event.request_id] = AgentRequestInfoResponse.approve()
                elif event.type == "output":
                    outputs.append(cast(list[Message], event.data))
            
            return responses if responses else None, outputs
        
        # Initial run
        stream = workflow.run(initial_message, stream=True)
        pending_responses, outputs = await process_event_stream(stream)
        
        # Continue processing until no more feedback requests
        while pending_responses is not None:
            stream = workflow.run(stream=True, responses=pending_responses)
            pending_responses, new_outputs = await process_event_stream(stream)
            if new_outputs:
                outputs = new_outputs
        
        return outputs, feedback_requests
    
    def __repr__(self) -> str:
        """String representation of the orchestrator."""
        agent_names = " -> ".join([agent.name for agent in self.agents])
        return f"SequentialOrchestrator({agent_names})"