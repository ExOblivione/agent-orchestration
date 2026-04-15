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
from agent_framework.orchestrations import MagenticProgressLedger

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
        intermediate_outputs: bool = True
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
        
        # Keep track of the last executor to format output nicely in streaming mode
        last_message_id: str | None = None
        last_executor: str | None = None
        output_event: WorkflowEvent | None = None
        async for event in workflow.run(initial_message, stream=True):
            # Debug: print event type to understand what we're receiving
            # print(f"\n[DEBUG] Event type: {event.type}, executor_id: {getattr(event, 'executor_id', 'N/A')}")
            
            if event.type == "output" and isinstance(event.data, AgentResponseUpdate):
                message_id = event.data.message_id
                executor_id = getattr(event, 'executor_id', None)
                
                # Print agent header when switching to a new agent
                if executor_id and executor_id != last_executor:
                    if last_executor is not None:
                        print("\n")
                    print(f"\n{'-'*20}[{executor_id.upper()}]{'-'*20}")
                    last_executor = executor_id
                    
                print(event.data.text, end="", flush=True)
                last_message_id = message_id

            elif event.type == "magentic_orchestrator":
                event_type = event.data.event_type.name
                
                if event_type == "PLAN_CREATED":
                    # Show manager's plan with clear formatting
                    print(f"\n{'*'*60}")
                    print(f"📊 [MANAGER PLAN]")
                    print(f"{'*'*60}")
                    if isinstance(event.data.content, Message):
                        print(f"\n{event.data.content.text}\n")
                
                elif event_type == "PROGRESS_LEDGER_UPDATED":
                    # Show agent response with agent name (when not streaming)
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
                            if agent_name == self.manager_agent.name:
                                print(f"\n{'-'*20}[MANAGER: {agent_display}]{'-'*20}")
                            else:
                                print(f"\n{'-'*20}[AGENT: {agent_display}]{'-'*20}")
                        else:
                            print(f"\n{'-'*20}[RESPONSE]{'-'*20}")
                        
                        print(f"{message.text}\n")
                
                elif event_type == "REPLANNED":
                    # Show replanning with clear formatting
                    print(f"\n{'!'*60}")
                    print(f"⚠️  [MANAGER REPLANNING]")
                    print(f"{'!'*60}")
                    if isinstance(event.data.content, Message):
                        print(f"\n{event.data.content.text}\n")
                
                # Commented out - enable if needed for debugging
                # elif isinstance(event.data.content, MagenticProgressLedger):
                #     print(f"Progress ledger:\n{json.dumps(event.data.content.to_dict(), indent=2)}")

            elif event.type == "output":
                output_event = event

        # The output of the Magentic workflow is a list of ChatMessages with only one final message
        # generated by the orchestrator.
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
        intermediate_outputs: bool = True
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
            last_message_id: str | None = None
            async for event in stream:
                if event.type == "output" and isinstance(event.data, AgentResponseUpdate):
                    message_id = event.data.message_id
                    if message_id != last_message_id:
                        if last_message_id is not None:
                            print("\n")
                        # Get agent name from event executor_id
                        agent_name = event.executor_id if hasattr(event, 'executor_id') and event.executor_id else "UNKNOWN"
                        print(f"\n{'-'*20}[{agent_name.upper()}]{'-'*20}")
                        last_message_id = message_id
                    print(event.data.text, end="", flush=True)
                
                elif event.type == "magentic_orchestrator":
                    event_type = event.data.event_type.name
                    
                    if event_type == "PLAN_CREATED":
                        # Show manager's plan with clear formatting
                        print(f"\n{'*'*60}")
                        print(f"📊 [MANAGER PLAN]")
                        print(f"{'*'*60}")
                        if isinstance(event.data.content, Message):
                            print(f"\n{event.data.content.text}\n")
                    
                    elif event_type == "PROGRESS_LEDGER_UPDATED":
                        # Show agent response with agent name (when not streaming)
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
                                if agent_name == self.manager_agent.name:
                                    print(f"\n{'-'*20}[MANAGER: {agent_display}]{'-'*20}")
                                else:
                                    print(f"\n{'-'*20}[AGENT: {agent_display}]{'-'*20}")
                            else:
                                print(f"\n{'-'*20}[RESPONSE]{'-'*20}")
                            
                            print(f"{message.text}\n")
                    
                    elif event_type == "REPLANNED":
                        # Show replanning with clear formatting
                        print(f"\n{'!'*60}")
                        print(f"⚠️  [MANAGER REPLANNING]")
                        print(f"{'!'*60}")
                        if isinstance(event.data.content, Message):
                            print(f"\n{event.data.content.text}\n")
                
                elif event.type == "request_info" and event.request_type is MagenticPlanReviewRequest:
                    pending_request = event
                
                elif event.type == "output":
                    output_event = event
            
            pending_responses = None
            
            # Handle plan review request if any
            if pending_request is not None:
                event_data = cast(MagenticPlanReviewRequest, pending_request.data)
                
                print("\n\n[🔍 Magentic Plan Review Request]")
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
                    print("✓ Plan approved. Proceeding with execution...\n")
                    pending_responses = {pending_request.request_id: event_data.approve()}
                else:
                    print(f"📝 Plan revised with feedback: {reply}\n")
                    pending_responses = {pending_request.request_id: event_data.revise(reply)}
                
                pending_request = None
        
        # Extract final output
        if output_event:
            output_messages = cast(list[Message], output_event.data)
            return output_messages[-1].text
        
        return "No response generated"
    
    def __repr__(self) -> str:
        """String representation of the orchestrator."""
        agent_names = ", ".join([agent.name for agent in self.agents])
        return f"MagenticOrchestrator(manager={self.manager_agent.name}, agents=[{agent_names}])"