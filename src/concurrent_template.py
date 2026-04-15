from typing import List, cast
from src.agent_template import AgentTemplate
from agent_framework.orchestrations import ConcurrentBuilder, AgentRequestInfoResponse
from agent_framework import Message
from agent_framework import AgentExecutorResponse

class ConcurrentOrchestrator:
    """
    Concurrent workflow orchestrator for parallel agent execution.
    
    This orchestrator runs multiple agents in parallel with the same input,
    collecting all their responses together. Optionally, an aggregator agent
    can consolidate the diverse perspectives into a single coherent response.
    
    When an aggregator is provided, the output includes:
    1. The complete conversation from all parallel agents (for transparency)
    2. The aggregator's consolidated summary (for synthesis)
    
    Source: https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/concurrent?pivots=programming-language-python
    """
    
    def __init__(self, agents: List[AgentTemplate], aggregator: AgentTemplate | None = None):
        """
        Initialize the concurrent orchestrator.
        
        Args:
            agents: List of agents to execute in parallel
            aggregator: Optional agent to aggregate the results
        """
        self.agents = agents
        self.aggregator = aggregator
        # Store messages before aggregation for transparency
        self._raw_messages: list[Message] = []
        self._aggregated_summary: str | None = None
    
    async def run(self, initial_message: str) -> str:
        """
        Execute the concurrent workflow with an initial message.
        
        All agents process the same input simultaneously and independently.
        Their responses are collected and returned together. If an aggregator
        is configured, its consolidated summary is appended after all individual
        agent responses, providing both transparency and synthesis.
        
        Args:
            initial_message: The starting message/prompt for the workflow
            
        Returns:
            Formatted output containing all agent responses, with optional
            aggregator summary appended at the end
        """
        # Reset state for this run
        self._raw_messages = []
        self._aggregated_summary = None
        
        # Build the concurrent workflow with actual agents
        con_agents = [agent.agent for agent in self.agents]
        builder = ConcurrentBuilder(participants=con_agents)
        
        # Add custom aggregator if provided
        if self.aggregator:
            workflow = builder.with_aggregator(self._summarize_results).build()
        else:
            workflow = builder.build()
        
        # Execute workflow and collect outputs
        output_data = None
        
        async for event in workflow.run(initial_message, stream=True):
            if event.type == "output":
                output_data = event.data
        
        # Handle output - always show full conversation
        if self.aggregator:
            # With aggregator: use stored raw messages + aggregated summary
            if self._raw_messages:
                result_parts = ["===== Full Concurrent Conversation ====="]
                
                for i, msg in enumerate(self._raw_messages, start=1):
                    name = msg.author_name if msg.author_name else msg.role
                    separator = "-" * 60
                    result_parts.append(f"{separator}\n{i:02d} [{name}]:\n{msg.text}")
                
                # Append aggregator's consolidated output
                if self._aggregated_summary:
                    result_parts.append("\n" + "=" * 60)
                    result_parts.append("===== Aggregator's Consolidated Summary =====")
                    result_parts.append("=" * 60)
                    result_parts.append(self._aggregated_summary)
                
                return "\n".join(result_parts)
        else:
            # Without aggregator: output is list of messages
            if output_data and isinstance(output_data, list):
                messages: list[Message] = cast(list[Message], output_data)
                result_parts = ["===== Full Concurrent Conversation ====="]
                
                for i, msg in enumerate(messages, start=1):
                    name = msg.author_name if msg.author_name else msg.role
                    separator = "-" * 60
                    result_parts.append(f"{separator}\n{i:02d} [{name}]:\n{msg.text}")
                
                return "\n".join(result_parts)
        
        return "No response generated"
    
    async def _summarize_results(self, results: list[AgentExecutorResponse]) -> str:
        """
        Custom aggregator callback that consolidates multiple agent outputs.
        
        This method is invoked by the workflow when an aggregator is configured.
        
        Args:
            results: List of executor responses from all parallel agents
            
        Returns:
            Consolidated summary from the aggregator agent
        """
        # Extract and store all messages before aggregation for transparency
        self._raw_messages = []
        expert_sections: list[str] = []
        
        for r in results:
            try:
                messages = getattr(r.agent_response, "messages", [])
                # Store all messages for display
                self._raw_messages.extend(messages)
                # Extract final message for aggregation
                final_text = messages[-1].text if messages and hasattr(messages[-1], "text") else "(no content)"
                expert_sections.append(f"{r.executor_id}:\n{final_text}")
            except Exception as e:
                expert_sections.append(f"{r.executor_id}: (error: {type(e).__name__}: {e})")

        # Ask the aggregator agent to synthesize a concise summary
        prompt = "\n\n".join(expert_sections)
        response = await self.aggregator.run(prompt)
        # AgentTemplate.run() returns a string directly
        self._aggregated_summary = response
        return response
    
    async def run_with_human_feedback(
        self,
        initial_message: str,
        feedback_agent_names: List[str] | None = None
    ) -> str:
        """
        Execute the concurrent workflow with human-in-the-loop feedback.
        
        This method pauses after specified agents respond, allowing for
        external input or review before continuing. If an aggregator is
        configured, its consolidated summary is appended after all individual
        agent responses.
        
        Args:
            initial_message: The starting message/prompt for the workflow
            feedback_agent_names: List of agent names to pause after for feedback.
                                 If None, pauses after all agents.
            
        Returns:
            Formatted output containing all agent responses, with optional
            aggregator summary appended at the end
        """
        # Reset state for this run
        self._raw_messages = []
        self._aggregated_summary = None
        
        # Build the concurrent workflow with actual agents
        con_agents = [agent.agent for agent in self.agents]
        builder = ConcurrentBuilder(participants=con_agents)
        
        # Build workflow with request_info enabled for specified agents
        if feedback_agent_names:
            builder = builder.with_request_info(agents=feedback_agent_names)
        else:
            builder = builder.with_request_info()
        
        # Add custom aggregator if provided
        if self.aggregator:
            workflow = builder.with_aggregator(self._summarize_results).build()
        else:
            workflow = builder.build()
        
        async def process_event_stream(stream):
            """Process events and collect request_info responses."""
            responses = {}
            output_data = None
            
            async for event in stream:
                if event.type == "request_info":
                    # Auto-approve for this template
                    # In production, this is where you'd gather actual human feedback
                    print(f"Request for feedback at: {event.request_id}")
                    responses[event.request_id] = AgentRequestInfoResponse.approve()
                elif event.type == "output":
                    output_data = event.data
            
            return responses if responses else None, output_data
        
        # Initial run
        stream = workflow.run(initial_message, stream=True)
        pending_responses, output_data = await process_event_stream(stream)
        
        # Continue processing until no more feedback requests
        while pending_responses is not None:
            stream = workflow.run(stream=True, responses=pending_responses)
            pending_responses, new_output = await process_event_stream(stream)
            if new_output is not None:
                output_data = new_output
        
        # Handle output - always show full conversation
        if self.aggregator:
            # With aggregator: use stored raw messages + aggregated summary
            if self._raw_messages:
                result_parts = ["===== Full Concurrent Conversation ====="]
                
                for i, msg in enumerate(self._raw_messages, start=1):
                    name = msg.author_name if msg.author_name else msg.role
                    separator = "-" * 60
                    result_parts.append(f"{separator}\n{i:02d} [{name}]:\n{msg.text}")
                
                # Append aggregator's consolidated output
                if self._aggregated_summary:
                    result_parts.append("\n" + "=" * 60)
                    result_parts.append("===== Aggregator's Consolidated Summary =====")
                    result_parts.append("=" * 60)
                    result_parts.append(self._aggregated_summary)
                
                return "\n".join(result_parts)
        else:
            # Without aggregator: output is list of messages
            if output_data and isinstance(output_data, list):
                messages: list[Message] = cast(list[Message], output_data)
                result_parts = ["===== Full Concurrent Conversation ====="]
                
                for i, msg in enumerate(messages, start=1):
                    name = msg.author_name if msg.author_name else msg.role
                    separator = "-" * 60
                    result_parts.append(f"{separator}\n{i:02d} [{name}]:\n{msg.text}")
                
                return "\n".join(result_parts)
        
        return "No response generated"

    def __repr__(self) -> str:
        """String representation of the orchestrator."""
        agent_names = ", ".join([agent.name for agent in self.agents])
        if self.aggregator:
            return f"ConcurrentOrchestrator([{agent_names}] -> {self.aggregator.name})"
        return f"ConcurrentOrchestrator([{agent_names}])"