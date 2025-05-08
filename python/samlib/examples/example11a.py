"""Complex example demonstrating the Python SAMLib task system.

This example shows multiple agents working together using various task types:
- Generator task producing vectors of random numbers
- Splitter task sending data to multiple processing agents
- Transform tasks finding min/max values
- Sink task for output
"""
import asyncio
import random
from dataclasses import dataclass
from typing import List, Tuple
from samlib import Environment, Agent, AgentRef
from samlib.tasks import generator, splitter, transform, sink

Vector = List[int]
Output = Tuple[str, int]

def generate(size: int) -> Vector:
    """Generate a vector of random numbers."""
    data = [random.randint(1, 100) for _ in range(10)]
    print("Generated:", ",".join(map(str, data)))
    return data

def min_value(data: Vector) -> Output:
    """Find the minimum value in a vector."""
    if data:
        return ("Min", min(data))
    return ("Done", 0)

def max_value(data: Vector) -> Output:
    """Find the maximum value in a vector."""
    if data:
        return ("Max", max(data))
    return ("Done", 0)

def output(val: Output) -> None:
    """Output sink function."""
    name, value = val
    print(f"{name}: {value}")

async def main():
    # Create environment
    env = Environment()
    
    # Create agent references
    p_gen = env.make_agent(int, None)  # Will be set up with generator task
    p_split = env.make_agent(Vector, None)  # Will be set up with splitter task
    p_min = env.make_agent(Vector, None)  # Will be set up with transform task
    p_max = env.make_agent(Vector, None)  # Will be set up with transform task
    p_out = env.make_agent(Output, sink(output))
    
    # Set up the task chain
    gen_task = await generator(generate, p_split)
    split_task = await splitter(p_min, p_max)
    min_task = await transform(min_value, p_out)
    max_task = await transform(max_value, p_out)
    
    # Update agent tasks
    p_gen._agent.task = gen_task
    p_split._agent.task = split_task
    p_min._agent.task = min_task
    p_max._agent.task = max_task
    
    print("------------ First version ---------------")
    
    # Send initial message to generate 2 sets of numbers
    await p_gen.send(2)
    
    # Let the system run for a while
    await asyncio.sleep(1)
    
    print("------------ Time's up ---------------")
    env.stop_agents()

if __name__ == "__main__":
    asyncio.run(main())
