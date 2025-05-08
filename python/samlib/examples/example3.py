"""Example demonstrating the Python SAMLib implementation.

This example implements a pattern similar to example3.cc from the C++ version,
showing message passing between ping and pong agents.
"""
import asyncio
from samlib import Environment, Agent, AgentRef

async def ping(val: int) -> int:
    """Transform a value in the ping agent."""
    print(f"Ping -> {val}")
    return val + 1

async def pong(val: int) -> int:
    """Transform a value in the pong agent."""
    print(f"{val} <- Pong")
    return val + 1

async def main():
    # Create environment
    env = Environment()
    
    # Define agent tasks
    async def ping_task(agent: Agent[int], out: AgentRef[int]):
        while env.active():
            if msg := await agent.try_receive():
                result = await ping(msg)
                await out.send(result)
                await asyncio.sleep(0.1)  # Simulate work
                
    async def pong_task(agent: Agent[int], out: AgentRef[int]):
        while env.active():
            if msg := await agent.try_receive():
                result = await pong(msg)
                await out.send(result)
                await asyncio.sleep(0.1)  # Simulate work
    
    # Create agents
    p1_ref = env.make_agent(int, lambda a: ping_task(a, p2_ref), "p1")
    p2_ref = env.make_agent(int, lambda a: pong_task(a, p1_ref), "p2")
    
    # Send initial message
    await p2_ref.send(1)
    
    # Let the system run for a while
    await asyncio.sleep(1)
    
    print("------------ Time's up ---------------")
    env.stop_agents()

if __name__ == "__main__":
    asyncio.run(main())
