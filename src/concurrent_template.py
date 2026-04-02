from typing import List, cast
from src.agent_template import AgentTemplate
from agent_framework.orchestrations import ConcurrentBuilder
from agent_framework import Message
from agent_framework import AgentExecutorResponse


class ConcurrentOrchestrator:
    """
    Concurrent workflow orchestrator for parallel agent execution.
    
    This orchestrator runs multiple agents in parallel with the same input,
    collecting all their responses together. Optionally, an aggregator agent
    can consolidate the diverse perspectives into a single coherent response.
    
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
    
    async def run(self, initial_message: str) -> str:
        """
        Execute the concurrent workflow with an initial message.
        
        All agents process the same input simultaneously and independently.
        Their responses are collected and returned together, optionally
        aggregated by a custom aggregator agent.
        
        Args:
            initial_message: The starting message/prompt for the workflow
            
        Returns:
            Formatted output containing all agent responses, or aggregated summary
        """
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
        
        # Handle output based on whether aggregator was used
        if output_data:
            if self.aggregator:
                # With aggregator: output is a consolidated string
                return f"===== Final Consolidated Output =====\n{output_data}"
            else:
                # Without aggregator: output is list of messages
                messages: list[Message] = cast(list[Message], output_data)
                result_parts = ["===== Final Aggregated Conversation ====="]
                
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
        # Extract one final assistant message per agent
        expert_sections: list[str] = []
        for r in results:
            try:
                messages = getattr(r.agent_response, "messages", [])
                final_text = messages[-1].text if messages and hasattr(messages[-1], "text") else "(no content)"
                expert_sections.append(f"{r.executor_id}:\n{final_text}")
            except Exception as e:
                expert_sections.append(f"{r.executor_id}: (error: {type(e).__name__}: {e})")

        # Ask the aggregator agent to synthesize a concise summary
        prompt = "\n\n".join(expert_sections)
        response = await self.aggregator.run(prompt)
        # AgentTemplate.run() returns a string directly
        return response

    def __repr__(self) -> str:
        """String representation of the orchestrator."""
        agent_names = ", ".join([agent.name for agent in self.agents])
        if self.aggregator:
            return f"ConcurrentOrchestrator([{agent_names}] -> {self.aggregator.name})"
        return f"ConcurrentOrchestrator([{agent_names}])"