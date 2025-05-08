# Environment Migration Guide

This document details the migration of the runtime/environment system from C++ to Python, explaining the architectural changes and implementation details.

## Overview

The C++ implementation uses a template-based runtime system with a postoffice for message routing. The Python version simplifies this design while maintaining the core functionality through async/await patterns.

## Architecture Changes

### Runtime to Environment

C++ Version:
```cpp
template<typename Env>
class runtime {
    std::shared_ptr<postoffice> msg_sys;
    std::shared_ptr<agent_def_t> agents;
    std::shared_ptr<agent_ref_name_t> agent_names;
};
```

Python Version:
```python
class Environment:
    def __init__(self):
        self._msg_sys = PostOffice()
        self._agents: Dict[str, AgentRef] = {}
```

Key differences:
- Simplified inheritance model
- Python dictionary for agent tracking
- Native async support
- Pythonic naming conventions

## Component Integration

### 1. Agent Management

C++ Template-based approach:
```cpp
template<typename A, typename... Args>
agent_ref<typename A::message_type> create_agent(Args... args);
```

Python Type-safe approach:
```python
def make_agent(self, msg_type: type[T], task: callable, name: str = "") -> AgentRef[T]:
    """Create a new agent with the given task."""
```

### 2. Message Routing

C++ Postoffice integration:
```cpp
template<typename T>
constexpr channel<T>& make_channel() {
    return msg_sys->make_channel<T>();
}
```

Python async channels:
```python
def make_channel(self, channel_type: type[T]) -> Channel[T]:
    """Create a new channel of the specified type."""
    return self._msg_sys.make_channel(channel_type)
```

## State Management

### Global State

C++ version uses template specialization:
```cpp
struct environment : public runtime<environment> { };
```

Python version uses composition:
```python
class Environment:
    def __init__(self, auto_start: bool = True):
        self._active = False
        self._auto_start = auto_start
```

### Lifecycle Management

1. Startup
```python
def start_agents(self) -> None:
    """Start all agents."""
    self._active = True
    for agent_ref in self._agents.values():
        agent_ref.start()
```

2. Shutdown
```python
def stop_agents(self) -> None:
    """Stop all agents."""
    self._active = False
    self._msg_sys.close()
    for agent_ref in self._agents.values():
        agent_ref.stop()
```

## Migration Patterns

### 1. Agent Creation

From C++:
```cpp
template<typename In, typename Fn>
agent_ref<In> make_agent(Fn fn, std::string name = "")
```

To Python:
```python
def make_agent(self, msg_type: type[T], task: callable, name: str = "") -> AgentRef[T]:
    if not name:
        name = f"_{self._agent_counter}"
    agent = Agent[msg_type](self, task)
    return AgentRef[msg_type](agent)
```

### 2. Reference Management

From C++ shared pointers:
```cpp
std::shared_ptr<agent_def_t> agents;
```

To Python references:
```python
self._agents: Dict[str, AgentRef] = {}
```

## Best Practices

1. Type Safety
   - Use Generic types consistently
   - Leverage type hints for better IDE support
   - Document type requirements

2. Resource Management
   - Implement proper cleanup in stop_agents
   - Use context managers where appropriate
   - Handle agent lifecycle carefully

3. Error Handling
   - Propagate agent errors appropriately
   - Clean up resources on errors
   - Provide meaningful error messages

## Testing Considerations

1. Environment Setup/Teardown
   - Test auto-start functionality
   - Verify proper agent cleanup
   - Check channel cleanup

2. Agent Integration
   - Test agent creation and naming
   - Verify message routing
   - Check state isolation

3. Error Scenarios
   - Test agent failure handling
   - Verify environment cleanup
   - Check error propagation

## Performance Notes

1. Agent Management
   - Dictionary lookups for agent references
   - Efficient channel creation
   - Minimal overhead in message routing

2. Resource Usage
   - Proper cleanup of channels
   - Efficient agent tracking
   - Memory-friendly implementation
