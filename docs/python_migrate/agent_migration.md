# Agent Migration Guide

This document details the migration of the agent system from C++ to Python, explaining key design decisions and implementation details.

## Overview

The C++ agent system uses templates and RAII for type safety and resource management. In Python, we achieve similar goals using:
- Type hints for compile-time type checking
- Async/await for concurrency
- Context managers for resource cleanup

## Key Changes

### BaseAgent

C++ Version:
```cpp
template<typename T>
class base_agent : public agent_worker {
  // Uses templates for message type
  // Manual thread management
  // Synchronous message passing
};
```

Python Version:
```python
class BaseAgent(Generic[T]):
    # Uses Generic type for message type
    # Async/await for operations
    # Automatic thread management
```

### Agent References

The C++ AgentRef uses shared pointers for lifecycle management. In Python:
- Reference counting is automatic
- Type safety through Generic types
- Async message passing

### State Management

Original C++ implementation uses:
```cpp
struct my_state { };
template<typename Env, typename Tin, typename State=empty_state>
class agent : public base_agent<Tin>, public State
```

Python equivalent uses composition over inheritance:
```python
@dataclass
class State:
    pass

class Agent(BaseAgent[T], Generic[T]):
    def __init__(self, environment: Any, task: callable, state: Optional[State] = None):
        self.state = state
```

## Migration Patterns

### 1. Message Passing

C++ synchronous:
```cpp
bool send(const T& value) {
    return mailbox.send(value);
}
```

Python asynchronous:
```python
async def send(self, value: T) -> bool:
    return await self.mailbox.send(value)
```

### 2. Task Execution

C++ thread-based:
```cpp
void run(const std::stop_token& st) {
    while (!st.stop_requested()) {
        task(*this);
    }
}
```

Python async:
```python
async def run(self) -> None:
    while self._running.is_set():
        await self.task(self)
```

### 3. Error Handling

C++ uses return values and exceptions:
```cpp
std::optional<T> try_receive() {
    return mailbox.try_receive();
}
```

Python uses exceptions and Optional:
```python
async def try_receive(self) -> Optional[T]:
    try:
        return await self.mailbox.try_receive()
    except Exception:
        return None
```

## Testing Considerations

1. Async Testing
   - Use pytest.mark.asyncio for async tests
   - Test both successful and failed message passing
   - Verify proper cleanup

2. State Management
   - Test state initialization
   - Verify state isolation between agents
   - Check state persistence

3. Error Handling
   - Test message send/receive timeouts
   - Verify proper error propagation
   - Check cleanup on errors

## Best Practices

1. Always use type hints
2. Implement proper cleanup in __del__
3. Use asyncio.Events for synchronization
4. Handle task cancellation gracefully
5. Document async behavior clearly
