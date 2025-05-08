"""Environment implementation for Python SAMLib.

This module provides the Environment class which manages agents and their communications.
"""
from __future__ import annotations

from typing import Any, TypeVar
from samlib.agent import Agent, AgentRef
from samlib.postoffice import PostOffice

T = TypeVar('T')

class Environment:
    """Manages agents and their communications in an actor system."""
    
    def __init__(self, auto_start: bool = True):
        self._msg_sys = PostOffice()
        self._agents: dict[str, AgentRef] = {}
        self._agent_counter = 0
        self._auto_start = auto_start
        self._active = False
        
    def make_agent(self, msg_type: type[T], task: callable, name: str = "") -> AgentRef[T]:
        """Create a new agent with the given task."""
        if not name:
            self._agent_counter += 1
            name = f"_{self._agent_counter}"
            
        agent = Agent[msg_type](self, task)
        ref = AgentRef[msg_type](agent)
        self._agents[name] = ref
        
        if self._auto_start:
            self._active = True
            ref.start()
            
        return ref
        
    def get_agent_ref(self, name: str) -> AgentRef | None:
        """Get an agent reference by name."""
        return self._agents.get(name)
    
    def make_channel(self, channel_type: type[T]) -> Any:
        """Create a new channel of the specified type."""
        return self._msg_sys.make_channel(channel_type)
    
    def active(self) -> bool:
        """Check if the environment is active."""
        return self._active
    
    def activate(self) -> None:
        """Activate the environment."""
        self._active = True
    
    def start_agents(self) -> None:
        """Start all agents."""
        self._active = True
        for agent_ref in self._agents.values():
            agent_ref.start()
    
    def stop_agents(self) -> None:
        """Stop all agents."""
        self._active = False
        self._msg_sys.close()
        for agent_ref in self._agents.values():
            agent_ref.stop()
    
    def wait_for_agents(self) -> None:
        """Wait for all agents to finish."""
        for agent_ref in self._agents.values():
            agent_ref.wait()
