# Channel Migration Guide

This document details the migration of the channel system from C++ MPMC queues to Python's async queue implementation.

## Overview

The original C++ implementation uses multiple MPMC (Multi-Producer Multi-Consumer) queue implementations:
- ConcurrentQueue
- AtomicQueue
- MPMCQueue
- Custom queue implementation

The Python version consolidates these into a single async implementation using `asyncio.Queue`.

## Design Decisions

### 1. Queue Selection

Why asyncio.Queue:
- Built into Python's standard library
- Native async/await support
- Thread-safe implementation
- Configurable capacity
- Integrated with Python's async event loop

### 2. Async API

C++ blocking operations become async in Python:
```python
async def send(self, value: T) -> bool:
    await self._queue.put(value)

async def receive(self) -> Optional[T]:
    return await self._queue.get()
```

### 3. Close Semantics

The Python implementation adds explicit close semantics:
- Channel tracks closed state
- Prevents new messages after closing
- Allows draining existing messages
- Supports graceful shutdown

## Key Differences

### 1. Memory Model

C++ Version:
```cpp
template<typename T>
class mpmc_queue {
    std::atomic<T> elements_[SIZE];
    std::atomic_bool stop_flag;
};
```

Python Version:
```python
class Channel(Generic[T]):
    def __init__(self, capacity: int = 64):
        self._queue = asyncio.Queue[T](maxsize=capacity)
        self._closed = False
```

### 2. Error Handling

C++ uses return values:
```cpp
bool send(const value_type& value) {
    if (!stop_flag)
        return this->enqueue(value);
    return false;
}
```

Python uses exceptions and Optional:
```python
async def try_receive(self) -> Optional[T]:
    try:
        return self._queue.get_nowait()
    except asyncio.QueueEmpty:
        return None
```

### 3. Synchronization

C++ uses atomic operations:
```cpp
std::atomic_bool stop_flag = false;
void close() {
    stop_flag = true;
}
```

Python uses asyncio primitives:
```python
def close(self) -> None:
    self._closed = True
    # Remaining messages can still be received
```

## Performance Considerations

1. Queue Capacity
   - Default size of 64 matches C++ implementation
   - Configurable based on use case
   - Consider memory vs contention tradeoffs

2. Backpressure
   - asyncio.Queue provides automatic backpressure
   - Bounded queues prevent memory exhaustion
   - Async operations handle high load gracefully

3. Thread Safety
   - asyncio.Queue is thread-safe
   - No need for explicit synchronization
   - Safe interaction with event loop

## Testing Strategy

1. Basic Operations
   - Send/receive functionality
   - Order preservation
   - Capacity limits

2. Concurrency
   - Multiple producers
   - Multiple consumers
   - High concurrency scenarios

3. Close Behavior
   - Proper draining
   - No new messages
   - Resource cleanup

## Migration Patterns

### 1. Replace Atomic Operations

From C++:
```cpp
bool try_dequeue(T& value) {
    return this->try_pop(value);
}
```

To Python:
```python
async def try_receive(self) -> Optional[T]:
    try:
        return self._queue.get_nowait()
    except asyncio.QueueEmpty:
        return None
```

### 2. Handle Shutdown

From C++:
```cpp
void close() {
    stop_flag = true;
    base_t::close();
}
```

To Python:
```python
def close(self) -> None:
    self._closed = True
```

## Best Practices

1. Always check closed state before operations
2. Use try_receive for non-blocking operations
3. Handle QueueEmpty exceptions appropriately
4. Implement proper cleanup in close()
5. Document queue capacity requirements
