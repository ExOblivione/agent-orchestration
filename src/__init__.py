"""
Agent Orchestration Framework

A collection of templates and patterns for building multi-agent workflows
using the Microsoft Agent Framework.
"""
import warnings

# Suppress experimental warnings from agent_framework
warnings.filterwarnings('ignore', message='.*experimental.*')
warnings.filterwarnings('ignore', message='.*SKILLS.*')
warnings.filterwarnings('ignore', message='.*HARNESS.*')

from .agent_template import AgentTemplate
from .sequential_template import SequentialOrchestrator
from .concurrent_template import ConcurrentOrchestrator
from .groupchat_template import GroupChatOrchestrator
from .handoff_template import HandOffOrchestrator
from .magentic_template import MagenticOrchestrator

__all__ = [
    "AgentTemplate",
    "SequentialOrchestrator",
    "ConcurrentOrchestrator",
    "GroupChatOrchestrator",
    "HandOffOrchestrator",
    "MagenticOrchestrator",
]
