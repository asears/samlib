# Samlib C++ to Rust Migration Guide

This document outlines the process of migrating the Samlib C++ messaging and agent framework to Rust. The migration prioritizes idiomatic Rust patterns while maintaining the core functionality of the original library.

## Project Structure

The Rust implementation is organized as follows:

```
rust/samlib/
├── Cargo.toml         # Rust project and dependency definitions
├── src/
│   ├── agent.rs      # Agent traits and implementations
│   ├── channel.rs    # Channel implementations
│   ├── environment.rs # Runtime environment
│   ├── executor.rs   # Task executor
│   ├── postoffice.rs # Message routing
│   └── queue.rs      # MPMC queue implementations
```

## Key Migration Considerations

1. **Memory Management**: 
   - C++ smart pointers → Rust ownership system
   - `std::shared_ptr` → `Arc` (Atomic Reference Counting)
   - `std::unique_ptr` → `Box` or owned types

2. **Concurrency Models**:
   - C++ threads → Tokio async/await
   - Thread pools → Tokio runtime
   - Mutexes → Rust's `Mutex` or `parking_lot::Mutex`

3. **Message Passing**:
   - MPMC Queue → crossbeam channels or custom implementations
   - Mailbox adapters → Trait-based channel abstractions

## File-by-File Migration Status

| C++ File | Rust File | Status | Notes |
|----------|-----------|--------|-------|
| agent.hpp | agent.rs | Pending | - |
| channel.hpp | channel.rs | Pending | - |
| environment.hpp | environment.rs | Pending | - |
| executor.hpp | executor.rs | Pending | - |
| postoffice.hpp | postoffice.rs | Pending | - |
| mpmc_queue.hpp | queue.rs | Pending | - |
