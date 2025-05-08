"""Example demonstrating stateful agents in Python SAMLib.

This example shows how to use state in agents, similar to example4c.cc from the C++ version.
It maintains counters in the agent state and demonstrates state isolation between agents.
"""
import asyncio
from dataclasses import dataclass
from samlib import Environment, Agent, AgentRef
from samlib.tasks import transform

@dataclass
class AgentState:
    """State for ping/pong agents."""
    value: int = 0

async def ping(state: AgentState, val: int) -> int:
    """Stateful ping function that updates counter."""
    print(f"Ping -> {val}")
    val += 1
    state.value += 1
    return val

async def pong(state: AgentState, val: int) -> int:
    """Stateful pong function that updates counter."""
    print(f"{val} <- Pong")
    val += 1
    state.value += 1
    return val

async def stateful_transform(fn, out: AgentRef, state: AgentState):
    """Create a transform task that maintains state."""
    async def task(agent: Agent[int]) -> None:
        while agent.environment.active():
            if data := await agent.try_receive():
                result = await fn(state, data)
                await out.send(result)
    return task

async def main():
    # Create environment
    env = Environment()
    
    # Create states for agents
    ping_state = AgentState()
    pong_state = AgentState()
    
    # Create agent references
    p1_ref = env.make_agent(int, None, state=ping_state)
    p2_ref = env.make_agent(int, None, state=pong_state)
    
    # Set up the tasks with state
    ping_task = await stateful_transform(ping, p2_ref, ping_state)
    pong_task = await stateful_transform(pong, p1_ref, pong_state)
    
    # Update agent tasks
    p1_ref._agent.task = ping_task
    p2_ref._agent.task = pong_task
    
    # Send initial message
    await p2_ref.send(1)
    
    # Let the system run for a while
    await asyncio.sleep(1)
    
    print("------------ Time's up ---------------")
    env.stop_agents()
    
    # Print final state values
    print(f"P1 value: {ping_state.value}")
    print(f"P2 value: {pong_state.value}")

if __name__ == "__main__":
    asyncio.run(main())
