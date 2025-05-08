"""Post office implementation for Python SAMLib.

This module provides the PostOffice class which manages channels between agents.
"""
from __future__ import annotations

from typing import Dict, Generic, TypeVar
from samlib.channel import Channel

T = TypeVar('T')

class PostOffice:
    """Manages channels between agents."""
    
    def __init__(self):
        self._channels: Dict[str, Channel] = {}
        
    def make_channel(self, channel_type: type[T]) -> Channel[T]:
        """Create a new channel of the specified type."""
        channel = Channel[channel_type]()
        self._channels[str(id(channel))] = channel
        return channel
        
    def total_to_deliver(self) -> int:
        """Get the total number of messages waiting to be delivered."""
        return sum(channel.size() for channel in self._channels.values())
        
    def close(self) -> None:
        """Close all channels."""
        for channel in self._channels.values():
            channel.close()
