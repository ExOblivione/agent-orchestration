import asyncio
from typing import List, Optional, Callable
from src.agent_template import AgentTemplate


class ConcurrentOrchestrator:
    """
    Concurrent workflow orchestrator for parallel agent execution.
    
    This orchestrator runs multiple agents in parallel with the same input,
    then aggregates their results using an aggregator agent.
    
    """
    def __init__(
        self, 
        agents: Optional[List[AgentTemplate]] = None,
        aggregator: Optional[AgentTemplate] = None,
        verbose: bool = False
    ):
        """
        Initialize the concurrent orchestrator.
        
        Args:
            agents: List of agents to execute in parallel
            aggregator: Agent that combines results from all parallel agents
            verbose: Whether to print execution progress
        """
        self.agents = agents or []
        self.aggregator = aggregator
        self.verbose = verbose
    
    def add_agent(self, agent: AgentTemplate) -> None:
        """
        Add an agent to the parallel execution pool.
        
        Args:
            agent: Agent to add to the pool
        """
        self.agents.append(agent)
    
    def add_agents(self, agents: List[AgentTemplate]) -> None:
        """
        Add multiple agents to the parallel execution pool.
        
        Args:
            agents: List of agents to add to the pool
        """
        self.agents.extend(agents)
    
    def set_aggregator(self, aggregator: AgentTemplate) -> None:
        """
        Set the aggregator agent that combines results.
        
        Args:
            aggregator: Agent to aggregate results from parallel agents
        """
        self.aggregator = aggregator
    
    async def execute(self, input_message: str) -> str:
        """
        Execute all agents in parallel and aggregate results.
        
        All agents receive the same input_message simultaneously.
        Results are aggregated by the aggregator agent.
        
        Args:
            input_message: The input message for all agents
        
        Returns:
            Aggregated output from the aggregator agent
        
        Raises:
            ValueError: If no agents are registered or no aggregator is set
        """
        if not self.agents:
            raise ValueError("No agents registered. Add agents before executing.")
        
        if not self.aggregator:
            raise ValueError("No aggregator set. Set an aggregator before executing.")
        
        if self.verbose:
            print(f"\n[Concurrent Execution] Running {len(self.agents)} agents in parallel...")
            print(f"Input: {input_message[:100]}{'...' if len(input_message) > 100 else ''}\n")
        
        # Execute all agents concurrently
        tasks = [agent.run(input_message) for agent in self.agents]
        results = await asyncio.gather(*tasks)
        
        # Display individual results if verbose
        if self.verbose:
            for agent, result in zip(self.agents, results):
                print(f"[{agent.name}] Output: {result[:100]}{'...' if len(result) > 100 else ''}\n")
        
        # Aggregate results
        aggregation_input = self._format_results_for_aggregation(input_message, results)
        
        if self.verbose:
            print(f"[Aggregating] Combining results...\n")
        
        final_result = await self.aggregator.run(aggregation_input)
        
        return final_result
    
    async def execute_with_details(self, input_message: str) -> dict:
        """
        Execute all agents in parallel and return detailed results.
        
        Args:
            input_message: The input message for all agents
        
        Returns:
            Dictionary containing individual results and final aggregated result
        """
        if not self.agents:
            raise ValueError("No agents registered. Add agents before executing.")
        
        if not self.aggregator:
            raise ValueError("No aggregator set. Set an aggregator before executing.")
        
        # Execute all agents concurrently
        tasks = [agent.run(input_message) for agent in self.agents]
        results = await asyncio.gather(*tasks)
        
        # Store individual results
        individual_results = [
            {
                "agent_name": agent.name,
                "output": result
            }
            for agent, result in zip(self.agents, results)
        ]
        
        # Aggregate results
        aggregation_input = self._format_results_for_aggregation(input_message, results)
        final_result = await self.aggregator.run(aggregation_input)
        
        return {
            "input": input_message,
            "individual_results": individual_results,
            "final_result": final_result,
            "total_agents": len(self.agents)
        }
    
    def _format_results_for_aggregation(self, original_input: str, results: List[str]) -> str:
        """
        Format individual agent results for the aggregator.
        
        Args:
            original_input: The original input message
            results: List of results from parallel agents
        
        Returns:
            Formatted string for aggregator input
        """
        formatted = f"Original Question: {original_input}\n\n"
        formatted += "Results from parallel agents:\n\n"
        
        for i, (agent, result) in enumerate(zip(self.agents, results), 1):
            formatted += f"Agent {i} ({agent.name}):\n{result}\n\n"
        
        formatted += "Please synthesize these results into a comprehensive response."
        
        return formatted
    
    def clear_agents(self) -> None:
        """Clear all agents from the pool."""
        self.agents = []
    
    def __len__(self) -> int:
        """Return the number of agents in the pool."""
        return len(self.agents)
    
    def __repr__(self) -> str:
        """String representation of the orchestrator."""
        agent_names = [agent.name for agent in self.agents]
        return f"ConcurrentOrchestrator(agents={agent_names}, aggregator={self.aggregator.name if self.aggregator else None})"
