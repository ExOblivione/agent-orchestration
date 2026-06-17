"""
Handoff Orchestration Patterns
Source: https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/handoff

Simple examples:
1. AUTONOMOUS: Agents handoff tasks automatically
2. INTERACTIVE: Human approval for sensitive operations (using HandoffBuilder directly)

"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Annotated, Dict
from src.handoff_template import HandOffOrchestrator
from src.agent_template import AgentTemplate
from agent_framework import Message, Content, AgentResponseUpdate, tool
from agent_framework.orchestrations import HandoffBuilder

# ============================================================================
# Event Handlers for Printing Workflow Events
# ============================================================================

class HandoffEventPrinter:
    """Handler for printing handoff workflow events."""
    
    def __init__(self):
        self.current_agent: str | None = None
        self.message_count = 0
    
    def __call__(self, event):
        """Handle a workflow event and print appropriate output."""
        
        if event.type == "started":
            print("[WORKFLOW STARTED]\n")
        
        elif event.type == "output":
            if isinstance(event.data, AgentResponseUpdate):
                # Streaming output
                print(event.data.text, end="", flush=True)
            elif isinstance(event.data, list):
                # Final messages - print new ones
                self._print_new_messages(event.data)
    
    def _print_new_messages(self, messages: List[Message]):
        """Print new messages from the conversation."""
        if len(messages) > self.message_count:
            new_messages = messages[self.message_count:]
            for msg in new_messages:
                msg_author = msg.author_name or msg.role
                
                # Detect handoff
                if msg_author and msg_author != "user" and msg_author != self.current_agent:
                    if self.current_agent and self.current_agent != "user":
                        print(f"\n>>> HANDOFF: {self.current_agent} -> {msg_author} <<<\n")
                    elif msg_author not in ["user", "system"]:
                        print(f">>> AGENT: {msg_author} <<<\n")
                    self.current_agent = msg_author
                
                # Print message
                if msg.text and msg.text.strip():
                    print(f"[{msg_author}]: {msg.text}\n")
            
            self.message_count = len(messages)

# ============================================================================
# TOOLS
# ============================================================================

@tool
def check_order_status(order_number: Annotated[str, "Order number to check"]) -> str:
    """Check the status of an order."""
    return f"Order {order_number} shipped yesterday and arrives tomorrow!"


@tool
def process_return(order_number: Annotated[str, "Order number to return"]) -> str:
    """Process a product return."""
    return f"Return initiated for order {order_number}. Return label sent to your email!"


@tool(approval_mode="always_require")
def process_refund(order_number: Annotated[str, "Order number to refund"]) -> str:
    """Process a refund (requires approval)."""
    return f"Refund of $49.99 processed for order {order_number}!"

# ============================================================================
# EXAMPLE 1: AUTONOMOUS HANDOFF
# ============================================================================

async def autonomous_handoff_example():
    """
    AUTONOMOUS EXAMPLE: Multi-agent handoff with visible conversation.
    
    Shows agents handing off tasks with clear conversation flow.
    Customer Support -> Order Specialist -> Shipping Specialist
    """
    print("\n" + "="*70)
    print("AUTONOMOUS HANDOFF EXAMPLE")
    print("="*70)
    # print("Customer: 'My order #12345 hasn't arrived yet, what's going on?'\n")
    
    # Create agents with distinct roles
    customer_support = AgentTemplate(
        name="Customer_Support",
        instructions=(
            "You are a friendly customer support agent. "
            "When customers ask about orders, acknowledge their concern briefly, "
            "then transfer to Order_Specialist."
        )
    )
    
    order_specialist = AgentTemplate(
        name="Order_Specialist",
        instructions=(
            "You handle order inquiries. Use check_order_status to get info. "
            "After checking, if shipped, transfer to Shipping_Specialist."
        ),
        tools=[check_order_status],
    )
    
    shipping_specialist = AgentTemplate(
        name="Shipping_Specialist",
        instructions=(
            "You're the shipping expert. Review conversation history for order status, "
            "then provide final delivery information with tracking details. "
            "Do NOT transfer to anyone else - you provide the final answer."
        )
    )
    
    # Termination: stop after shipping specialist provides a response
    def stop_after_shipping(conversation: List[Message]) -> bool:
        # Stop after we get a text response from Shipping_Specialist
        for msg in reversed(conversation):
            if msg.author_name == "Shipping_Specialist" and msg.text and msg.text.strip():
                return True
        return False
    
    # Create orchestrator
    orchestrator = HandOffOrchestrator(
        agents=[customer_support, order_specialist, shipping_specialist],
        termination_condition=stop_after_shipping,
        workflow_name="support_handoff"
    )
    
    # Run with event printer
    event_printer = HandoffEventPrinter()
    messages = await orchestrator.run(
        "My order #12345 hasn't arrived yet, what's going on?",
        on_event=event_printer
    )
    
    # Show final result
    # print("\n" + "="*70)
    # print(f"FINAL RESULT: {len(messages)} messages in conversation")
    # print("="*70)
    # if messages:
    #     last_message = messages[-1]
    #     print(f"\nFinal response from {last_message.author_name}:")
    #     print(f"{last_message.text}\n")

# ============================================================================
# EXAMPLE 2: INTERACTIVE HANDOFF (Human Approval Required)
# ============================================================================

async def interactive_handoff_example():
    """
    INTERACTIVE EXAMPLE: Human approval required for refunds.
    
    Shows how to handle approval-required tools in a handoff workflow.
    You'll be asked to approve the refund before it's processed.
    
    Note: Uses HandoffBuilder directly (not the template) for interactive control.
    """
    print("\n" + "="*70)
    print("INTERACTIVE HANDOFF EXAMPLE (Human-in-the-Loop)")
    print("="*70)
    print("Customer: 'My order #67890 is defective, I need a refund'\n")
    
    # Create agents
    triage = AgentTemplate(
        name="Triage",
        instructions="Route refund requests to Refund_Specialist."
    )
    
    refund_specialist = AgentTemplate(
        name="Refund_Specialist",
        instructions="Use process_refund tool to issue refunds.",
        tools=[process_refund],  # Requires approval!
    )
    
    # Build workflow (using HandoffBuilder directly for interactive mode)
    agents = [triage.agent, refund_specialist.agent]
    workflow = (
        HandoffBuilder(
            name="approval_workflow",
            participants=agents,
        )
        .with_start_agent(agents[0])
        .build()
    )
    
    # Start workflow
    print("Starting workflow...\n")
    pending_requests = []
    event_printer = HandoffEventPrinter()
    
    async for event in workflow.run("My order #67890 is defective, I need a refund", stream=True):
        # Print events
        event_printer(event)
        
        # Collect approval requests
        if event.type == "request_info":
            pending_requests.append(event)
    
    # Handle approval requests
    if pending_requests:
        print("\n" + "="*70)
        responses: Dict[str, object] = {}
        
        for request in pending_requests:
            if isinstance(request.data, Content) and request.data.type == "function_approval_request":
                func_call = request.data.function_call
                args = func_call.parse_arguments() or {}
                
                print("APPROVAL REQUIRED:")
                print(f"  Tool: {func_call.name}")
                print(f"  Order: {args.get('order_number', 'N/A')}")
                
                approval = input("\n  Approve refund? (y/n): ").strip().lower() == "y"
                
                if approval:
                    print("  Approved!\n")
                else:
                    print("  Denied.\n")
                
                responses[request.request_id] = request.data.to_function_approval_response(approved=approval)
        
        # Continue with approval response
        print("="*70)
        print("Continuing workflow with your decision...\n")
        
        async for event in workflow.run(responses=responses, stream=True):
            if event.type == "output" and isinstance(event.data, list):
                if event.data:
                    last_msg = event.data[-1]
                    if last_msg.text:
                        print(f"\n[FINAL RESULT]")
                        print(f"[{last_msg.author_name}]: {last_msg.text}\n")

async def main():
    """Run the examples."""
    
    # Example 1: Autonomous handoff
    await autonomous_handoff_example()
    
    # Example 2: Interactive handoff
    # await interactive_handoff_example()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())