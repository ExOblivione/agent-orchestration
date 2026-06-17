from typing import List, Optional
from src.agent_template import AgentTemplate
from agent_framework import Message
from agent_framework.orchestrations import GroupChatBuilder, GroupChatState, AgentRequestInfoResponse


class GroupChatOrchestrator:
    """
    Group chat workflow orchestrator for multi-agent collaboration.
    
    This orchestrator coordinates a conversation among multiple agents using
    either a simple selector function or an intelligent agent-based orchestrator.
    
    Source: https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/group-chat?pivots=programming-language-python
    """
    
    def __init__(self, agents: List[AgentTemplate], orchestrator_agent: Optional[AgentTemplate] = None):
        """
        Initialize the group chat orchestrator.
        
        Args:
            agents: List of agents to execute in the group chat
            orchestrator_agent: Optional agent-based orchestrator for intelligent speaker selection.
                              If None, uses round-robin selector by default.
        
        Note:
            For custom selection logic, you can modify the run() method to accept a
            selection_func parameter, or subclass this orchestrator. See the static
            selector methods (round_robin_selector, content_based_selector) for examples.
        """
        self.agents = agents
        self.orchestrator_agent = orchestrator_agent

    @staticmethod
    def round_robin_selector(state: GroupChatState) -> str:
        """
        Round-robin selector that picks speakers in sequence.
        
        This is the simplest selection strategy - each agent speaks in turn.
        Good for ensuring equal participation.
        """
        participant_names = list(state.participants.keys())
        return participant_names[state.current_round % len(participant_names)]
    
    def _build_workflow(
        self, 
        limit: int = 4,
        include_request_info: bool = False,
        feedback_agent_names: List[str] | None = None
    ):
        """
        Build the group chat workflow with optional request_info enabled.
        
        Args:
            limit: Maximum number of assistant messages before terminating
            include_request_info: Whether to enable human-in-the-loop feedback
            feedback_agent_names: List of agent names to pause after for feedback
            
        Returns:
            Built workflow ready to run
        """
        # Unwrap the agents from AgentTemplate to get actual agent objects
        agents = [agent.agent for agent in self.agents]

        # Build the base workflow
        if self.orchestrator_agent:
            builder = GroupChatBuilder(
                participants=agents,
                termination_condition=lambda messages: sum(1 for msg in messages if msg.role == "assistant") >= limit,
                orchestrator_agent=self.orchestrator_agent.agent
            )
        else:
            builder = GroupChatBuilder(
                participants=agents,
                termination_condition=lambda messages: sum(1 for msg in messages if msg.role == "assistant") >= limit,
                selection_func=GroupChatOrchestrator.round_robin_selector
            )
        
        # Add request_info if needed
        if include_request_info:
            if feedback_agent_names:
                builder = builder.with_request_info(agents=feedback_agent_names)
            else:
                builder = builder.with_request_info()
        
        return builder.build()
    
    async def run(self, initial_message: str, limit: int = 4) -> list[Message]:
        """
        Execute the group chat workflow with an initial message.
        
        Args:
            initial_message: The starting message/prompt for the group chat
            limit: The maximum number of assistant messages before terminating the chat.
        
        Returns:
            List of messages from the group chat conversation
        """
        workflow = self._build_workflow(limit=limit)
        final_conversation: list[Message] = []

        # Run the workflow with streaming enabled
        async for event in workflow.run(initial_message, stream=True):
            if event.type == "output" and isinstance(event.data, list):
                final_conversation = event.data

        return final_conversation
    
    async def run_with_human_feedback(
        self,
        initial_message: str,
        feedback_agent_names: List[str] | None = None,
        limit: int = 4
    ) -> tuple[list[Message], list[str]]:
        """
        Execute the group chat workflow with human-in-the-loop feedback.
        
        This method pauses after specified agents respond, allowing for
        external input or review before continuing.
        
        Args:
            initial_message: The starting message/prompt for the group chat
            feedback_agent_names: List of agent names to pause after for feedback.
                                 If None, pauses after all agents.
            limit: The maximum number of assistant messages before terminating
            
        Returns:
            Tuple of (messages, feedback_requests):
            - messages: List of all messages from the group chat
            - feedback_requests: List of request IDs where feedback was requested
        """
        workflow = self._build_workflow(
            limit=limit,
            include_request_info=True,
            feedback_agent_names=feedback_agent_names
        )
        feedback_requests = []
        
        async def process_event_stream(stream):
            """Process events and collect request_info responses."""
            responses = {}
            final_conversation: list[Message] = []
            
            async for event in stream:
                if event.type == "request_info":
                    # This is where you gather actual human feedback
                    feedback_requests.append(event.request_id)
                    
                    # Request human approval before proceeding
                    user_input = input("\nProceed with this agent's response? (yes/no): ").strip().lower()
                    
                    if user_input in ["yes", "y"]:
                        responses[event.request_id] = AgentRequestInfoResponse.approve()
                    else:
                        responses[event.request_id] = AgentRequestInfoResponse.reject()
                elif event.type == "output" and isinstance(event.data, list):
                    # Workflow completed - data is a list of Message
                    final_conversation = event.data
            
            return responses if responses else None, final_conversation
        
        # Initial run
        stream = workflow.run(initial_message, stream=True)
        pending_responses, final_conversation = await process_event_stream(stream)
        
        # Continue processing until no more feedback requests
        while pending_responses is not None:
            stream = workflow.run(stream=True, responses=pending_responses)
            pending_responses, new_conversation = await process_event_stream(stream)
            if new_conversation:
                final_conversation = new_conversation
        
        return (final_conversation, feedback_requests)

    def __repr__(self) -> str:
        """String representation of the orchestrator."""
        agent_names = ", ".join([agent.name for agent in self.agents])
        if self.orchestrator_agent:
            return f"GroupChatOrchestrator([{agent_names}], orchestrator={self.orchestrator_agent.name})"
        return f"GroupChatOrchestrator([{agent_names}])"