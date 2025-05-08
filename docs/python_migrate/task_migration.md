# Task System Migration Guide

This document details the migration of the task system from C++ to Python's async/await patterns, focusing on transformers, generators, and sinks.

## Overview

The C++ implementation uses template metaprogramming and function composition for task handling. The Python version leverages coroutines and async/await for more natural task composition.

## Core Task Types

### 1. Transform Tasks

C++ Version:
```cpp
template<typename Fn, typename O>
auto transform(Fn fn, O& out) {
    return [fn, &out](auto& agent) {
        if (auto data = agent.try_receive())
            out.send(fn(std::move(*data)));
    };
}
```

Python Version:
```python
async def transform(fn: Callable[[T], U], out: AgentRef[U]) -> Callable:
    async def task(agent: Agent[T]) -> None:
        if data := await agent.try_receive():
            await out.send(fn(data))
    return task
```

### 2. Generator Tasks

C++ Version:
```cpp
template<typename Fn, typename O>
auto generator(Fn fn, O& out) {
    return [fn, &out](auto& agent) {
        if (auto dat = agent.try_receive()) {
            auto n = *dat;
            while (n > 0) {
                out.send(fn(n));
                --n;
            }
        }
    };
}
```

Python Version:
```python
async def generator(fn: Callable[[T], T], out: AgentRef[T]) -> Callable:
    async def task(agent: Agent[T]) -> None:
        if data := await agent.try_receive():
            n = data
            while n > 0 and agent.environment.active():
                await out.send(fn(n))
                n -= 1
    return task
```

### 3. Sink Tasks

C++ Version:
```cpp
auto sink = [](auto fn) {
    return [fn](auto& agent) {
        if (auto data = agent.try_receive())
            fn(*data);
    };
};
```

Python Version:
```python
def sink(fn: Callable[[T], None]) -> Callable:
    async def task(agent: Agent[T]) -> None:
        if data := await agent.try_receive():
            fn(data)
    return task
```

## Migration Patterns

### 1. Task Composition

C++ Chaining:
```cpp
auto task = transform(fn1, transform(fn2, sink(fn3)));
```

Python Async Composition:
```python
async def composed_task(agent: Agent[T]) -> None:
    async with TaskGroup() as tg:
        task1 = await transform(fn1, agent1)
        task2 = await transform(fn2, agent2)
        task3 = await sink(fn3)
        await tg.gather(task1, task2, task3)
```

### 2. State Management

C++ State Inheritance:
```cpp
struct state {
    int value;
};
size_t task(state& st, size_t val) {
    st.value += 1;
    return val;
}
```

Python State Pattern:
```python
@dataclass
class State:
    value: int = 0

async def task(agent: Agent[int], state: State) -> None:
    state.value += 1
    return await agent.receive()
```

### 3. Splitter Tasks

C++ Version:
```cpp
template<typename... O>
auto splitter(O&... outs) {
    return [&](auto& agent) {
        if (auto data = agent.try_receive())
            for (auto out : {outs...})
                out.send(*data);
    };
}
```

Python Version:
```python
async def splitter(*outputs: AgentRef[T]) -> Callable:
    async def task(agent: Agent[T]) -> None:
        if data := await agent.try_receive():
            await asyncio.gather(*(out.send(data) for out in outputs))
    return task
```

## Best Practices

1. Task Definition
   - Use async functions for all tasks
   - Type hint everything properly
   - Handle cancellation gracefully
   - Document task behavior

2. Error Handling
   - Use try/except in tasks
   - Propagate errors appropriately
   - Clean up resources on errors
   - Log task failures

3. Performance
   - Use asyncio.gather for parallel tasks
   - Avoid blocking operations
   - Handle backpressure properly
   - Profile task execution

## Testing Strategy

1. Unit Tests
   - Test individual task types
   - Verify error handling
   - Check state management
   - Test cancellation

2. Integration Tests
   - Test task composition
   - Verify message flow
   - Check resource cleanup
   - Test error propagation

3. Performance Tests
   - Measure task throughput
   - Check memory usage
   - Test under load
   - Verify scaling

## Advanced Patterns

1. Task Groups
```python
async def parallel_tasks(*tasks: Callable) -> None:
    async with TaskGroup() as tg:
        for task in tasks:
            tg.create_task(task)
```

2. Cancellation
```python
async def cancellable_task(agent: Agent[T]) -> None:
    try:
        async with AsyncExitStack() as stack:
            while True:
                if await agent.try_receive():
                    # Process data
                    pass
    except asyncio.CancelledError:
        # Clean up
        pass
```

3. Resource Management
```python
class ManagedTask:
    async def __aenter__(self):
        # Setup resources
        pass
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup
        pass
```

## Migration Tips

1. Always use async/await consistently
2. Type hint everything for better IDE support
3. Handle task cancellation properly
4. Test error scenarios thoroughly
5. Document async behavior clearly
6. Profile task performance
7. Use modern Python features
