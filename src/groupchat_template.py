from typing import List, Optional
from src.agent_template import AgentTemplate
from agent_framework import AgentResponseUpdate, Message
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
    
    async def run(self, initial_message: str, verbose: bool = False, limit: int = 4) -> str:
        """
        Execute the group chat workflow with an initial message.
        
        Args:
            initial_message: The starting message/prompt for the group chat
            verbose: If True, prints the conversation as it happens. If False, only returns final result.
            limit: The maximum number of assistant messages before terminating the chat.
        
        Returns:
            Formatted final conversation from all agents
        """
        # Unwrap the agents from AgentTemplate to get actual agent objects
        agents = [agent.agent for agent in self.agents]

        # Build the group chat workflow
        # To use content_based_selector or a custom selector, change selection_func parameter
        if self.orchestrator_agent:
            # Use agent-based orchestrator for intelligent speaker selection
            workflow = GroupChatBuilder(
                participants=agents,
                termination_condition=lambda messages: sum(1 for msg in messages if msg.role == "assistant") >= limit,
                orchestrator_agent=self.orchestrator_agent.agent
            ).build()
        else:
            # Use round-robin selector by default
            workflow = GroupChatBuilder(
                participants=agents,
                termination_condition=lambda messages: sum(1 for msg in messages if msg.role == "assistant") >= limit,
                selection_func=GroupChatOrchestrator.round_robin_selector
            ).build()
        
        final_conversation: list[Message] = []
        last_author: str | None = None

        # Run the workflow with streaming enabled
        async for event in workflow.run(initial_message, stream=True):
            if event.type == "output" and isinstance(event.data, AgentResponseUpdate):
                # Print streaming agent updates only if verbose mode is enabled
                if verbose:
                    author = event.data.author_name
                    if author != last_author:
                        if last_author is not None:
                            print()
                        print(f"[{author}]:", end=" ", flush=True)
                        last_author = author
                    print(event.data.text, end="", flush=True)
            elif event.type == "output" and isinstance(event.data, list):
                # Workflow completed - data is a list of Message
                final_conversation = event.data

        # Format and return final conversation
        if final_conversation:
            if verbose:
                print("\n\n" + "=" * 80)
                print("Final Conversation:")
            result_parts = []
            for msg in final_conversation:
                author = msg.author_name or msg.role
                result_parts.append(f"\n[{author}]\n{msg.text}")
                if verbose:
                    print(f"\n[{author}]\n{msg.text}")
                    print("-" * 80)
            return "\n".join(result_parts)
        
        return "No response generated"
    
    async def run_with_human_feedback(
        self,
        initial_message: str,
        feedback_agent_names: List[str] | None = None,
        verbose: bool = False,
        limit: int = 4
    ) -> str:
        """
        Execute the group chat workflow with human-in-the-loop feedback.
        
        This method pauses after specified agents respond, allowing for
        external input or review before continuing.
        
        Args:
            initial_message: The starting message/prompt for the group chat
            feedback_agent_names: List of agent names to pause after for feedback.
                                 If None, pauses after all agents.
            verbose: If True, prints the conversation as it happens
            limit: The maximum number of assistant messages before terminating
            
        Returns:
            Formatted final conversation from all agents
        """
        # Unwrap the agents from AgentTemplate to get actual agent objects
        agents = [agent.agent for agent in self.agents]

        # Build the group chat workflow
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
        
        # Build workflow with request_info enabled for specified agents
        if feedback_agent_names:
            workflow = builder.with_request_info(agents=feedback_agent_names).build()
        else:
            workflow = builder.with_request_info().build()
        
        async def process_event_stream(stream):
            """Process events and collect request_info responses."""
            responses = {}
            final_conversation: list[Message] = []
            last_author: str | None = None
            
            async for event in stream:
                if event.type == "request_info":
                    # Auto-approve for this template
                    # In production, this is where you'd gather actual human feedback
                    print(f"Request for feedback at: {event.request_id}")
                    responses[event.request_id] = AgentRequestInfoResponse.approve()
                elif event.type == "output" and isinstance(event.data, AgentResponseUpdate):
                    # Print streaming agent updates only if verbose mode is enabled
                    if verbose:
                        author = event.data.author_name
                        if author != last_author:
                            if last_author is not None:
                                print()
                            print(f"[{author}]:", end=" ", flush=True)
                            last_author = author
                        print(event.data.text, end="", flush=True)
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
        
        # Format and return final conversation
        if final_conversation:
            if verbose:
                print("\n\n" + "=" * 80)
                print("Final Conversation:")
            result_parts = []
            for msg in final_conversation:
                author = msg.author_name or msg.role
                result_parts.append(f"\n[{author}]\n{msg.text}")
                if verbose:
                    print(f"\n[{author}]\n{msg.text}")
                    print("-" * 80)
            return "\n".join(result_parts)
        
        return "No response generated"

    def __repr__(self) -> str:
        """String representation of the orchestrator."""
        agent_names = ", ".join([agent.name for agent in self.agents])
        if self.orchestrator_agent:
            return f"GroupChatOrchestrator([{agent_names}], orchestrator={self.orchestrator_agent.name})"
        return f"GroupChatOrchestrator([{agent_names}])"