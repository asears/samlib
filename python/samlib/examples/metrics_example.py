"""Example demonstrating the metrics system with SAMLib.

This example shows how to use metrics to monitor agent performance,
building on the ping-pong pattern while collecting performance data.
"""
import asyncio
from samlib import Environment, Agent, AgentRef
from samlib.metrics import collector, with_metrics

async def ping(val: int) -> int:
    """Ping function with simulated work."""
    await asyncio.sleep(0.1)  # Simulate processing time
    print(f"Ping -> {val}")
    return val + 1

async def pong(val: int) -> int:
    """Pong function with simulated work."""
    await asyncio.sleep(0.2)  # Simulate processing time
    print(f"{val} <- Pong")
    return val + 1

async def main():
    # Create environment
    env = Environment()
    
    # Define agent tasks with metrics
    async def ping_task(agent: Agent[int], out: AgentRef[int]):
        while env.active():
            if msg := await agent.try_receive():
                result = await with_metrics("ping", ping(msg))
                await out.send(result)
                collector.record_sent("ping")
                
    async def pong_task(agent: Agent[int], out: AgentRef[int]):
        while env.active():
            if msg := await agent.try_receive():
                result = await with_metrics("pong", pong(msg))
                await out.send(result)
                collector.record_sent("pong")
    
    # Create agents
    p1_ref = env.make_agent(int, lambda a: ping_task(a, p2_ref), "ping")
    p2_ref = env.make_agent(int, lambda a: pong_task(a, p1_ref), "pong")
    
    # Send several messages to generate metrics
    for i in range(5):
        await p2_ref.send(i)
    
    # Let the system run for a while
    await asyncio.sleep(2)
    
    print("\n------------ Metrics Report ---------------")
    print(collector.report())
    
    print("\n------------ Time's up ---------------")
    env.stop_agents()

if __name__ == "__main__":
    asyncio.run(main())
