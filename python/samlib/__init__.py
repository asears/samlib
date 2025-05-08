"""SAMLib - Simple Agent/Actor Model Library for Python.

This library provides an implementation of the actor/agent based computation model in Python.
"""

from .agent import Agent, BaseAgent, AgentRef
from .channel import Channel
from .environment import Environment
from .executor import Executor
from .postoffice import PostOffice

__version__ = "0.1.0"
__all__ = ["Agent", "BaseAgent", "AgentRef", "Channel", "Environment", "Executor", "PostOffice"]
