"""Task system implementation for Python SAMLib.

This module provides task factories similar to the C++ implementation,
but using async/await patterns for better Python integration.
"""
from __future__ import annotations

import asyncio
from typing import Any, Callable, Generic, TypeVar
from .agent import Agent, AgentRef

T = TypeVar('T')
U = TypeVar('U')

async def transform(fn: Callable[[T], U], out: AgentRef[U]) -> Callable:
    """Create a transform task that processes messages through a function.
    
    Similar to the C++ transform task but using async/await.
    """
    async def task(agent: Agent[T]) -> None:
        while agent.environment.active():
            if data := await agent.try_receive():
                result = await fn(data) if asyncio.iscoroutinefunction(fn) else fn(data)
                await out.send(result)
    return task

async def generator(fn: Callable[[T], T], out: AgentRef[T]) -> Callable:
    """Create a generator task that produces multiple messages.
    
    Similar to the C++ generator task but using async/await.
    """
    async def task(agent: Agent[T]) -> None:
        while agent.environment.active():
            if data := await agent.try_receive():
                n = data
                while n > 0 and agent.environment.active():
                    result = await fn(n) if asyncio.iscoroutinefunction(fn) else fn(n)
                    await out.send(result)
                    n -= 1
    return task

def sink(fn: Callable[[T], None]) -> Callable:
    """Create a sink task that consumes messages.
    
    Similar to the C++ sink task but using async/await.
    """
    async def task(agent: Agent[T]) -> None:
        while agent.environment.active():
            if data := await agent.try_receive():
                if asyncio.iscoroutinefunction(fn):
                    await fn(data)
                else:
                    fn(data)
    return task

async def splitter(*outputs: AgentRef[T]) -> Callable:
    """Create a splitter task that sends each message to multiple outputs.
    
    Similar to the C++ splitter task but using async/await.
    """
    async def task(agent: Agent[T]) -> None:
        while agent.environment.active():
            if data := await agent.try_receive():
                await asyncio.gather(*(out.send(data) for out in outputs))
    return task

class TaskGroup:
    """Context manager for managing groups of tasks.
    
    Provides a way to run multiple tasks together and handle cleanup.
    """
    def __init__(self):
        self.tasks: list[asyncio.Task] = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.tasks:
            for task in self.tasks:
                task.cancel()
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
    def create_task(self, coro):
        """Create and track a new task."""
        task = asyncio.create_task(coro)
        self.tasks.append(task)
        return task
        
    async def gather(self, *coros):
        """Run multiple coroutines together."""
        tasks = [self.create_task(coro) for coro in coros]
        await asyncio.gather(*tasks)
