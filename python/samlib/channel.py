"""Channel implementation for Python SAMLib.

This module provides the Channel class which implements a multi-producer multi-consumer queue
with asynchronous operations.
"""
from __future__ import annotations

import asyncio
from typing import Generic, Optional, TypeVar

T = TypeVar('T')

class Channel(Generic[T]):
    """A multi-producer multi-consumer queue implementation."""
    
    def __init__(self, capacity: int = 64):
        self._queue = asyncio.Queue[T](maxsize=capacity)
        self._closed = False
        
    async def send(self, value: T) -> bool:
        """Send a value to the channel."""
        if self._closed:
            return False
        await self._queue.put(value)
        return True
        
    async def receive(self) -> Optional[T]:
        """Receive a value from the channel, waiting if none is available."""
        if self._closed and self._queue.empty():
            return None
        try:
            return await self._queue.get()
        except asyncio.CancelledError:
            return None
            
    async def try_receive(self) -> Optional[T]:
        """Try to receive a value without waiting."""
        if self._closed and self._queue.empty():
            return None
        try:
            return self._queue.get_nowait()
        except asyncio.QueueEmpty:
            return None
            
    def close(self) -> None:
        """Close the channel."""
        self._closed = True
        
    def size(self) -> int:
        """Get the current size of the channel."""
        return self._queue.qsize()
