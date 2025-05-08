"""Test suite for the Python SAMLib implementation."""
import asyncio
import pytest
from typing import List
from samlib import Agent, AgentRef, Environment, Channel

@pytest.mark.asyncio
async def test_basic_messaging():
    """Test basic message passing between agents."""
    env = Environment()
    received_messages: List[int] = []
    
    async def consumer(agent: Agent[int]) -> None:
        while msg := await agent.try_receive():
            received_messages.append(msg)
            
    consumer_ref = env.make_agent(int, consumer)
    await consumer_ref.send(1)
    await consumer_ref.send(2)
    await asyncio.sleep(0.1)  # Allow messages to be processed
    
    assert received_messages == [1, 2]
    env.stop_agents()

@pytest.mark.asyncio
async def test_ping_pong():
    """Test ping-pong message pattern from C++ example."""
    env = Environment()
    ping_count = 0
    pong_count = 0
    
    async def ping(val: float) -> float:
        nonlocal ping_count
        ping_count += 1
        return val + 1.0
        
    async def pong(val: float) -> float:
        nonlocal pong_count
        pong_count += 1
        return val + 1.0
        
    async def ping_agent(agent: Agent[float], out: AgentRef[float]) -> None:
        while msg := await agent.try_receive():
            result = await ping(msg)
            await out.send(result)
            
    async def pong_agent(agent: Agent[float], out: AgentRef[float]) -> None:
        while msg := await agent.try_receive():
            result = await pong(msg)
            await out.send(result)
    
    p1_ref = env.make_agent(float, lambda a: ping_agent(a, p2_ref))
    p2_ref = env.make_agent(float, lambda a: pong_agent(a, p1_ref))
    
    await p2_ref.send(1.0)
    await asyncio.sleep(0.2)  # Allow messages to be processed
    
    assert ping_count > 0
    assert pong_count > 0
    env.stop_agents()

@pytest.mark.asyncio
async def test_channel_operations():
    """Test channel operations including close behavior."""
    channel = Channel[int]()
    
    # Test send/receive
    await channel.send(42)
    result = await channel.receive()
    assert result == 42
    
    # Test try_receive on empty channel
    result = await channel.try_receive()
    assert result is None
    
    # Test close behavior
    channel.close()
    assert not await channel.send(42)
    assert await channel.receive() is None

@pytest.mark.asyncio
async def test_agent_lifecycle():
    """Test agent lifecycle including start, stop, and cleanup."""
    env = Environment(auto_start=False)
    started = False
    stopped = False
    
    async def lifecycle_test(agent: Agent[int]) -> None:
        nonlocal started, stopped
        started = True
        while msg := await agent.try_receive():
            pass
        stopped = True
        
    agent_ref = env.make_agent(int, lifecycle_test)
    agent_ref.start()
    await asyncio.sleep(0.1)
    
    assert started
    agent_ref.stop()
    await asyncio.sleep(0.1)
    assert stopped
    env.stop_agents()
