"""
Handoff Orchestration Patterns
Source: https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/handoff?pivots=programming-language-python

Key Patterns Implemented:
1. Simple triage handoff (default all-to-all routing)
2. Custom handoff rules (controlled routing paths)
3. Bi-directional handoffs
4. Autonomous mode (full, partial, and custom)
5. Tool approval (Human-in-the-Loop for sensitive operations)
6. Checkpointing (durable workflows)
"""

import os
from typing import List, Annotated, Callable, Optional, Dict
from src.handoff_template import HandOffOrchestrator
from src.agent_template import AgentTemplate
from agent_framework import Agent, Message, Content, tool
from agent_framework.orchestrations import HandoffBuilder, HandoffAgentUserRequest

# ============================================================================
# TOOLS - Customer Support Domain
# ============================================================================

@tool
def process_refund(order_number: Annotated[str, "Order number to process refund for"]) -> str:
    """Simulated function to process a refund for a given order number."""
    return f"Refund processed successfully for order {order_number}."


@tool
def check_order_status(order_number: Annotated[str, "Order number to check status for"]) -> str:
    """Simulated function to check the status of a given order number."""
    return f"Order {order_number} is currently being processed and will ship in 2 business days."


@tool
def process_return(order_number: Annotated[str, "Order number to process return for"]) -> str:
    """Simulated function to process a return for a given order number."""
    return f"Return initiated successfully for order {order_number}. You will receive return instructions via email."


@tool(approval_mode="always_require")
def process_refund_with_approval(order_number: Annotated[str, "Order number to process refund for"]) -> str:
    """Process refund with required approval - for sensitive operations."""
    return f"Refund processed successfully for order {order_number}."


# ============================================================================
# AGENT BUILDERS - Domain-Specific Agents
# ============================================================================

def create_customer_support_agents(
    require_approval: bool = False
) -> Dict[str, AgentTemplate]:
    """
    Create a set of specialized customer support agents.
    
    Args:
        require_approval: If True, use tools that require approval
        
    Returns:
        Dictionary of agent templates by role
    """
    refund_tool = process_refund_with_approval if require_approval else process_refund
    
    triage_agent = AgentTemplate(
        name="triage_agent",
        instructions="Route customer issues to specialists. Be brief and direct."
    )
    
    refund_agent = AgentTemplate(
        name="refund_agent",
        instructions="Process refunds. Keep responses short.",
        tools=[refund_tool],
    )
    
    order_agent = AgentTemplate(
        name="order_agent",
        instructions="Handle order inquiries. Be concise.",
        tools=[check_order_status],
    )
    
    return_agent = AgentTemplate(
        name="return_agent",
        instructions="Process returns. Keep responses brief.",
        tools=[process_return],
    )
    
    return {
        "triage": triage_agent,
        "refund": refund_agent,
        "order": order_agent,
        "return": return_agent,
    }


# ============================================================================
# WORKFLOW BUILDERS - Reusable Handoff Configurations
# ============================================================================

def simple_triage_workflow(
    agents: List[Agent],
    termination_condition: Optional[Callable[[List[Message]], bool]] = None
) -> HandoffBuilder:
    """
    Simple triage workflow with default all-to-all handoff routing.
    
    Any agent can handoff to any other agent. This is the simplest configuration.
    Autonomous mode is enabled for non-interactive use with the orchestrator template.
    
    Args:
        agents: List of Agent objects [triage, refund, order, return]
        termination_condition: Optional function to determine when to stop
        
    Returns:
        Configured HandoffBuilder workflow
    """
    return (
        HandoffBuilder(
            name="simple_triage",
            participants=agents,
            termination_condition=termination_condition,
        )
        .with_start_agent(agents[0])  # Triage receives initial input
        .with_autonomous_mode()  # Enable autonomous mode for non-interactive execution
        .build()
    )


def controlled_routing_workflow(
    agents: List[Agent],
    termination_condition: Optional[Callable[[List[Message]], bool]] = None
) -> HandoffBuilder:
    """
    Workflow with custom handoff rules for controlled routing.
    
    Routing rules:
    - Triage cannot route directly to refund agent (must go through return first)
    - Only return agent can handoff to refund (for post-return refunds)
    - All specialists can handoff back to triage for re-routing
    
    Autonomous mode is enabled for non-interactive use with the orchestrator template.
    
    Args:
        agents: List of Agent objects [triage, refund, order, return]
        termination_condition: Optional function to determine when to stop
        
    Returns:
        Configured HandoffBuilder workflow
    """
    triage, refund, order, return_ag = agents
    
    return (
        HandoffBuilder(
            name="controlled_routing",
            participants=agents,
            termination_condition=termination_condition,
        )
        .with_start_agent(triage)
        # Triage routes to order or return, but NOT directly to refund
        .add_handoff(triage, [order, return_ag])
        # Only return agent can handoff to refund (for damaged/defective items)
        .add_handoff(return_ag, [refund])
        # All specialists can handoff back to triage for further routing
        .add_handoff(order, [triage])
        .add_handoff(return_ag, [triage])
        .add_handoff(refund, [triage])
        .with_autonomous_mode()  # Enable autonomous mode for non-interactive execution
        .build()
    )


def autonomous_workflow(
    agents: List[Agent],
    mode: str = "full",
    termination_condition: Optional[Callable[[List[Message]], bool]] = None,
    turn_limit: Optional[int] = None,
    custom_prompt: Optional[str] = None
) -> HandoffBuilder:
    """
    Workflow with autonomous mode configurations.
    
    Autonomous mode allows agents to continue without human input when they
    don't handoff. Useful for automated workflows.
    
    Args:
        agents: List of Agent objects [triage, refund, order, return]
        mode: "full" (all agents), "partial" (triage only), or "none"
        termination_condition: Optional function to determine when to stop
        turn_limit: Max autonomous turns per agent before requiring human input
        custom_prompt: Custom message for autonomous continuation
        
    Returns:
        Configured HandoffBuilder workflow
    """
    builder = (
        HandoffBuilder(
            name="autonomous_support",
            participants=agents,
            termination_condition=termination_condition,
        )
        .with_start_agent(agents[0])
    )
    
    if mode == "full":
        # All agents run autonomously
        kwargs = {}
        if turn_limit:
            kwargs["turn_limits"] = {agent.name: turn_limit for agent in agents}
        if custom_prompt:
            kwargs["prompts"] = {agent.name: custom_prompt for agent in agents}
        builder = builder.with_autonomous_mode(**kwargs)
        
    elif mode == "partial":
        # Only triage agent runs autonomously
        kwargs = {"agents": [agents[0]]}
        if turn_limit:
            kwargs["turn_limits"] = {agents[0].name: turn_limit}
        if custom_prompt:
            kwargs["prompts"] = {agents[0].name: custom_prompt}
        builder = builder.with_autonomous_mode(**kwargs)
    
    return builder.build()


# ============================================================================
# EXAMPLE USAGE FUNCTIONS
# ============================================================================

async def basic_handoff_example():
    """
    Example 1: Basic triage handoff with default routing.
    
    Demonstrates:
    - Simple all-to-all agent handoff
    - Using HandOffOrchestrator template
    - Custom termination condition
    """
    print("\n=== Basic Handoff Example ===\n")
    
    # Create agents
    agents_dict = create_customer_support_agents()
    agents = [
        agents_dict["triage"],
        agents_dict["refund"],
        agents_dict["order"],
        agents_dict["return"],
    ]
    
    # Create orchestrator with simple termination (max 3 messages for quick testing)
    orchestrator = HandOffOrchestrator(
        agents=agents,
        workflow_builder=simple_triage_workflow,
        termination_condition=lambda c: len(c) >= 2
    )
    
    # Run the workflow
    result = await orchestrator.run("I need help with my order #12345")
    print(result)


async def controlled_routing_example():
    """
    Example 2: Controlled routing with custom handoff rules.
    
    Demonstrates:
    - Custom handoff paths between agents
    - Bi-directional routing (specialists back to triage)
    - Workflow builder with add_handoff() configuration
    """
    print("\n=== Controlled Routing Example ===\n")
    
    agents_dict = create_customer_support_agents()
    agents = [
        agents_dict["triage"],
        agents_dict["refund"],
        agents_dict["order"],
        agents_dict["return"],
    ]
    
    # Use controlled routing workflow with very short termination for quick testing
    orchestrator = HandOffOrchestrator(
        agents=agents,
        workflow_builder=controlled_routing_workflow,
        termination_condition=lambda c: len(c) >= 2  # Stop after just 2 messages 
    )
    
    result = await orchestrator.run("My order arrived damaged, I need a refund")
    print(result)


async def autonomous_mode_example(mode: str = "full"):
    """
    Example 3: Autonomous mode variations.
    
    Demonstrates:
    - Full autonomous mode (all agents)
    - Partial autonomous mode (triage only)
    - Custom autonomous prompts and turn limits
    
    Args:
        mode: "full" or "partial"
    """
    print(f"\n=== Autonomous Mode Example ({mode}) ===\n")
    
    agents_dict = create_customer_support_agents()
    agents = [
        agents_dict["triage"],
        agents_dict["refund"],
        agents_dict["order"],
        agents_dict["return"],
    ]
    
    # Custom workflow builder with autonomous mode
    def autonomous_builder(agent_list: List[Agent]) -> HandoffBuilder:
        return autonomous_workflow(
            agent_list,
            mode=mode,
            termination_condition=lambda c: len(c) > 12,
            turn_limit=3,
            custom_prompt="Continue assisting the user autonomously. Make your best judgment."
        )
    
    orchestrator = HandOffOrchestrator(
        agents=agents,
        workflow_builder=autonomous_builder
    )
    
    result = await orchestrator.run("Where is my order #67890?")
    print(result)


async def interactive_handoff_example():
    """
    Example 4: Interactive handoff with user input handling.
    
    Demonstrates:
    - Manual event processing
    - Handling HandoffAgentUserRequest for user input
    - Interactive conversation loop
    - Direct workflow.run() usage without orchestrator template
    """
    print("\n=== Interactive Handoff Example ===\n")
    
    agents_dict = create_customer_support_agents()
    
    # Build workflow directly (not using orchestrator template)
    workflow = simple_triage_workflow(
        agents=[
            agents_dict["triage"].agent,
            agents_dict["refund"].agent,
            agents_dict["order"].agent,
            agents_dict["return"].agent,
        ],
        termination_condition=lambda c: len(c) > 0 and "goodbye" in c[-1].text.lower()
    )
    
    # Start workflow
    pending_requests = []
    async for event in workflow.run_stream("I need help with my order"):
        if event.type == "request_info" and isinstance(event.data, HandoffAgentUserRequest):
            pending_requests.append(event)
    
    # Interactive loop
    while pending_requests:
        for req in pending_requests:
            print(f"\nAgent {req.executor_id} says:")
            for msg in req.data.agent_response.messages[-2:]:
                print(f"  {msg.author_name}: {msg.text}")
        
        # Get user input
        user_input = input("\nYou: ")
        
        # Send responses
        responses = {
            req.request_id: HandoffAgentUserRequest.create_response(user_input)
            for req in pending_requests
        }
        
        # Continue workflow
        pending_requests = []
        async for event in workflow.run(responses=responses):
            if event.type == "request_info" and isinstance(event.data, HandoffAgentUserRequest):
                pending_requests.append(event)
            elif event.type == "output":
                print("\nWorkflow completed!")


async def tool_approval_example():
    """
    Example 5: Tool approval workflow (Human-in-the-Loop).
    
    Demonstrates:
    - Tools with approval_mode="always_require"
    - Handling function_approval_request events
    - Processing both user input AND tool approval requests
    - Content.to_function_approval_response() usage
    """
    print("\n=== Tool Approval Example ===\n")
    
    # Create agents with approval-required tools
    agents_dict = create_customer_support_agents(require_approval=True)
    
    workflow = simple_triage_workflow(
        agents=[
            agents_dict["triage"].agent,
            agents_dict["refund"].agent,
            agents_dict["order"].agent,
        ]
    )
    
    # Start workflow
    pending_requests = []
    async for event in workflow.run_stream("My order 12345 arrived damaged. I need a refund."):
        if event.type == "request_info":
            pending_requests.append(event)
    
    # Process pending requests - could be user input OR tool approval
    while pending_requests:
        responses: Dict[str, object] = {}
        
        for request in pending_requests:
            if isinstance(request.data, HandoffAgentUserRequest):
                # Agent needs user input
                print(f"\nAgent {request.executor_id} asks:")
                for msg in request.data.agent_response.messages[-2:]:
                    print(f"  {msg.author_name}: {msg.text}")
                
                user_input = input("You: ")
                responses[request.request_id] = HandoffAgentUserRequest.create_response(user_input)
                
            elif isinstance(request.data, Content) and request.data.type == "function_approval_request":
                # Agent wants to call a tool that requires approval
                func_call = request.data.function_call
                args = func_call.parse_arguments() or {}
                
                print(f"\n⚠️  Tool approval requested: {func_call.name}")
                print(f"Arguments: {args}")
                
                approval = input("Approve? (y/n): ").strip().lower() == "y"
                responses[request.request_id] = request.data.to_function_approval_response(approved=approval)
        
        # Send all responses and collect new requests
        pending_requests = []
        async for event in workflow.run(responses=responses):
            if event.type == "request_info":
                pending_requests.append(event)
            elif event.type == "output":
                print("\n✓ Workflow completed!")


async def checkpointing_example():
    """
    Example 6: Durable workflows with checkpointing.
    
    Demonstrates:
    - FileCheckpointStorage for persistence
    - Pausing and resuming workflows
    - Long-running approval processes
    - Checkpoint restoration and continuation
    """
    print("\n=== Checkpointing Example ===\n")
    
    from agent_framework import FileCheckpointStorage
    
    agents_dict = create_customer_support_agents(require_approval=True)
    storage = FileCheckpointStorage(storage_path="./checkpoints")
    
    # Build workflow with checkpointing
    workflow = (
        HandoffBuilder(
            name="durable_support",
            participants=[
                agents_dict["triage"].agent,
                agents_dict["refund"].agent,
                agents_dict["order"].agent,
            ],
            checkpoint_storage=storage,
        )
        .with_start_agent(agents_dict["triage"].agent)
        .build()
    )
    
    # Initial run - workflow pauses when approval is needed
    print("Starting workflow... (will pause at approval)")
    pending_requests = []
    async for event in workflow.run_stream("I need a refund for order 12345"):
        if event.type == "request_info":
            pending_requests.append(event)
    
    print(f"Workflow paused with {len(pending_requests)} pending request(s)")
    print("Process can exit here - checkpoint is saved automatically\n")
    
    # Simulate process restart...
    print("--- Simulating process restart ---\n")
    
    # Later: Resume from checkpoint
    checkpoints = await storage.list_checkpoints(workflow_name="durable_support")
    if not checkpoints:
        print("No checkpoints found!")
        return
    
    latest = sorted(checkpoints, key=lambda c: c.timestamp, reverse=True)[0]
    print(f"Resuming from checkpoint: {latest.checkpoint_id}\n")
    
    # Step 1: Restore checkpoint to reload pending requests
    restored_requests = []
    async for event in workflow.run_stream(checkpoint_id=latest.checkpoint_id):
        if event.type == "request_info":
            restored_requests.append(event)
    
    # Step 2: Send responses
    responses = {}
    for req in restored_requests:
        if isinstance(req.data, Content) and req.data.type == "function_approval_request":
            print(f"Approving tool: {req.data.function_call.name}")
            responses[req.request_id] = req.data.to_function_approval_response(approved=True)
        elif isinstance(req.data, HandoffAgentUserRequest):
            responses[req.request_id] = HandoffAgentUserRequest.create_response("Yes, please process the refund.")
    
    # Complete the workflow
    async for event in workflow.run(responses=responses):
        if event.type == "output":
            print("✓ Refund workflow completed from checkpoint!")


# ============================================================================
# CUSTOM WORKFLOW EXAMPLES
# ============================================================================

async def custom_handoff_builder_example():
    """
    Example 7: Fully customized handoff workflow builder.
    
    Demonstrates:
    - Building custom workflow configurations
    - Combining multiple features (routing + autonomous + termination)
    - Creating domain-specific workflow templates
    """
    print("\n=== Custom Workflow Builder Example ===\n")
    
    agents_dict = create_customer_support_agents()
    
    # Custom workflow builder combining multiple features
    def my_custom_workflow(agents: List[Agent]) -> HandoffBuilder:
        triage, refund, order, return_ag = agents
        
        return (
            HandoffBuilder(
                name="custom_support_workflow",
                participants=agents,
                termination_condition=lambda c: (
                    len(c) > 20 or 
                    (len(c) > 0 and any(word in c[-1].text.lower() for word in ["goodbye", "thank you", "resolved"]))
                ),
            )
            .with_start_agent(triage)
            # Custom routing
            .add_handoff(triage, [order, return_ag])
            .add_handoff(return_ag, [refund, triage])
            # Partial autonomous mode for triage
            .with_autonomous_mode(
                agents=[triage],
                prompts={triage.name: "Continue helping the user. Route to specialists when needed."},
                turn_limits={triage.name: 5}
            )
            .build()
        )
    
    orchestrator = HandOffOrchestrator(
        agents=[
            agents_dict["triage"],
            agents_dict["refund"],
            agents_dict["order"],
            agents_dict["return"],
        ],
        workflow_builder=my_custom_workflow
    )
    
    result = await orchestrator.run("I have multiple issues with my recent orders")
    print(result)


# ============================================================================
# MAIN - Run Examples
# ============================================================================

async def main():
    """Run all examples (uncomment the ones you want to test)."""
    
    # Choose which examples to run:
    
    # await basic_handoff_example()
    await controlled_routing_example()
    # await autonomous_mode_example(mode="full")
    # await autonomous_mode_example(mode="partial")
    # await interactive_handoff_example()
    # await tool_approval_example()
    # await checkpointing_example()
    # await custom_handoff_builder_example()
    
    print("\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
