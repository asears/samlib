# MPMC Queue Migration Guide

## Overview

The original C++ implementation (`mpmc_queue.hpp`) provides a lock-free multiple-producer-multiple-consumer queue. This document details the migration of this component to idiomatic Rust.

## Key Changes

### Memory Model
- C++: Uses atomics and memory ordering directly
- Rust: Leverages `crossbeam::queue::ArrayQueue` or custom implementation using `atomic` module

### Implementation Strategy

1. **Phase 1: Safe Wrapper**
   - Initially implement using `crossbeam::queue::ArrayQueue`
   - Maintain similar interface but with Rust's type safety
   - Use `Result` for error handling instead of boolean returns

2. **Phase 2: Custom Implementation**
   - Implement custom lock-free queue if needed for specific performance requirements
   - Use Rust's atomic types (`AtomicUsize`, etc.)
   - Leverage Rust's stronger memory model guarantees

## Code Migration Example

C++ Original:
```cpp
template<typename T>
class MPMCQueue {
    // ... existing implementation
};
```

Rust Implementation:
```rust
use crossbeam::queue::ArrayQueue;
use std::sync::Arc;

pub struct MPMCQueue<T> {
    inner: Arc<ArrayQueue<T>>,
}

impl<T> MPMCQueue<T> {
    pub fn new(capacity: usize) -> Self {
        Self {
            inner: Arc::new(ArrayQueue::new(capacity)),
        }
    }

    pub fn try_push(&self, value: T) -> Result<(), T> {
        self.inner.push(value)
    }

    pub fn try_pop(&self) -> Option<T> {
        self.inner.pop()
    }
}
```

## Testing Strategy

1. Port existing C++ tests to Rust using `tokio-test`
2. Add new Rust-specific tests for memory safety
3. Implement benchmarks using `criterion`

## Performance Considerations

- Monitor allocation patterns
- Compare performance with C++ implementation
- Profile contention points
- Consider custom allocator if needed
