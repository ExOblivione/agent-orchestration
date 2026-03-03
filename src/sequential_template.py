from typing import List, Optional
from src.agent_template import AgentTemplate


class SequentialOrchestrator:
    """
    Sequential workflow orchestrator for agent pipeline execution.
    
    This orchestrator runs agents in sequence, passing the output of each
    agent as input to the next agent in the pipeline.
    
    """
    def __init__(self, agents: Optional[List[AgentTemplate]] = None, verbose: bool = False):
        """
        Initialize the sequential orchestrator.
        
        Args:
            agents: List of agents to execute in sequence (can be added later)
            verbose: Whether to print execution progress
        """
        self.agents = agents or []
        self.verbose = verbose
    
    def add_agent(self, agent: AgentTemplate) -> None:
        """
        Add an agent to the end of the pipeline.
        
        Args:
            agent: Agent to add to the pipeline
        """
        self.agents.append(agent)
    
    def add_agents(self, agents: List[AgentTemplate]) -> None:
        """
        Add multiple agents to the pipeline.
        
        Args:
            agents: List of agents to add to the pipeline
        """
        self.agents.extend(agents)
    
    async def execute(self, initial_input: str) -> str:
        """
        Execute the agent pipeline sequentially.
        
        Each agent receives the output from the previous agent as input.
        The first agent receives the initial_input.
        
        Args:
            initial_input: The initial message/input for the first agent
        
        Returns:
            The final output from the last agent in the pipeline
        
        Raises:
            ValueError: If no agents are registered
        """
        if not self.agents:
            raise ValueError("No agents registered in the pipeline. Add agents before executing.")
        
        current_input = initial_input
        
        for i, agent in enumerate(self.agents, 1):
            if self.verbose:
                print(f"\n[Step {i}/{len(self.agents)}] Executing {agent.name}...")
                print(f"Input: {current_input[:100]}{'...' if len(current_input) > 100 else ''}")
            
            # Run the agent and get output
            current_input = await agent.run(current_input)
            
            if self.verbose:
                print(f"Output: {current_input[:100]}{'...' if len(current_input) > 100 else ''}")
        
        return current_input
    
    async def execute_with_history(self, initial_input: str) -> dict:
        """
        Execute the pipeline and return detailed history of each step.
        
        Args:
            initial_input: The initial message/input for the first agent
        
        Returns:
            Dictionary containing final result and execution history
        """
        if not self.agents:
            raise ValueError("No agents registered in the pipeline. Add agents before executing.")
        
        history = []
        current_input = initial_input
        
        for i, agent in enumerate(self.agents, 1):
            step_info = {
                "step": i,
                "agent_name": agent.name,
                "input": current_input
            }
            
            # Run the agent
            current_input = await agent.run(current_input)
            step_info["output"] = current_input
            
            history.append(step_info)
        
        return {
            "final_result": current_input,
            "history": history,
            "total_steps": len(self.agents)
        }
    
    def clear_agents(self) -> None:
        """Clear all agents from the pipeline."""
        self.agents = []
    
    def __len__(self) -> int:
        """Return the number of agents in the pipeline."""
        return len(self.agents)
    
    def __repr__(self) -> str:
        """String representation of the orchestrator."""
        agent_names = [agent.name for agent in self.agents]
        return f"SequentialOrchestrator(agents={agent_names})"