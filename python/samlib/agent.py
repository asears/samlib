"""
Agent implementation for the Python samlib.

This module provides the core agent abstractions for message passing and
concurrent execution in the samlib framework.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator, Callable, Generic, Protocol, TypeVar, TYPE_CHECKING
import asyncio
from concurrent.futures import ThreadPoolExecutor

if TYPE_CHECKING:
    from .channel import Channel
else:
    try:
        from .channel import Channel
    except ImportError:
        from typing import Protocol, Generic
        T = TypeVar('T')
        class Channel(Protocol, Generic[T]):
            """Protocol for channel interface."""
            async def send(self, value: T) -> bool: ...
            async def receive(self) -> T | None: ...

T = TypeVar('T')
State = TypeVar('State')
Message = TypeVar('Message')

class MessageProtocol(Protocol):
    """Protocol defining the requirements for message objects."""
    pass

@dataclass
class EmptyState:
    """Default empty state for agents that don't need internal state."""
    pass

class AgentRef(Generic[Message]):
    """A reference-counted wrapper around an agent implementation."""
    
    def __init__(self, agent: Agent[Message]) -> None:
        """Initialize an agent reference.
        
        Args:
            agent: The agent instance to wrap
        """
        self._agent = agent
    
    async def send(self, message: Message) -> None:
        """Send a message to this agent.
        
        Args:
            message: The message to send
            
        Raises:
            QueueFullError: If the agent's channel is full
        """
        await self._agent.get_channel().send(message)

class Agent(ABC, Generic[Message]):
    """Base class for all agents in the system."""
    
    @abstractmethod
    def handle_message(self, message: Message) -> None:
        """Handle an incoming message.
        
        Args:
            message: The message to handle
        """
        pass
    
    @abstractmethod
    def get_channel(self) -> Channel[Message]:
        """Get the agent's channel for receiving messages.
        
        Returns:
            The agent's channel
        """
        pass

class BaseAgent(Agent[Message], Generic[Message, State]):
    """A base implementation of an agent with common functionality."""
    
    def __init__(self, channel: Channel[Message], initial_state: State) -> None:
        """Initialize a base agent.
        
        Args:
            channel: The channel for receiving messages
            initial_state: The initial state for the agent
        """
        self._channel = channel
        self._state = initial_state
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._running = False
    
    def get_channel(self) -> Channel[Message]:
        """Get the agent's channel for receiving messages."""
        return self._channel

    def handle_message(self, message: Message) -> None:
        """Default message handler that does nothing."""
        pass

    async def run(self, task: Callable[['BaseAgent[Message, State]'], None]) -> None:
        """Run the agent's task processing loop.
        
        Args:
            task: The task function to run for processing messages
        """
        self._running = True
        try:
            while self._running:
                message = await self._channel.receive()
                if message is None:
                    continue
                # Run task in thread pool to avoid blocking the event loop
                await asyncio.get_event_loop().run_in_executor(
                    self._executor, 
                    task,
                    self
                )
                self.handle_message(message)
        finally:
            self._running = False
            self._executor.shutdown(wait=True)

    def stop(self) -> None:
        """Stop the agent's processing loop."""
        self._running = False

    @property
    def state(self) -> State:
        """Get the agent's current state."""
        return self._state

    @state.setter
    def state(self, new_state: State) -> None:
        """Update the agent's state.
        
        Args:
            new_state: The new state to set
        """
        self._state = new_state