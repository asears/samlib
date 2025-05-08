# Python Migration Guide for SAMLib

This document details the process of migrating the SAMLib (Simple Agent/Actor Model Library) from C++ to Python, focusing on modern Python practices and async/await patterns.

## Overview

The Python implementation maintains the core concepts of the original C++/Rust implementation while leveraging Python's strengths:

- Async/await for concurrency
- Type hints for better IDE support and code safety
- Modern packaging with pyproject.toml
- Comprehensive test coverage
- Code quality tools (ruff, black)

## Key Components

1. **Agent System**
   - BaseAgent: Core messaging functionality
   - Agent: Concrete implementation with task execution
   - AgentRef: Reference type for agent communication

2. **Channel System**
   - Async MPMC (Multi-Producer Multi-Consumer) queue
   - Built on Python's asyncio.Queue
   - Support for blocking and non-blocking operations

3. **Executor**
   - Handles asynchronous task execution
   - Thread pool management
   - Graceful shutdown support

4. **Environment**
   - Manages agent lifecycle
   - Handles channel creation and management
   - Provides agent naming and lookup

## Migration Details

See the following detailed guides:
- [Agent Migration](./agent_migration.md)
- [Channel Migration](./channel_migration.md)
- [Environment Migration](./environment_migration.md)
- [Task System Migration](./task_migration.md)

## Key Differences from C++

1. **Asynchronous Design**
   - Python uses async/await instead of C++'s threading model
   - More explicit concurrency control
   - Better integration with event loops

2. **Type System**
   - Python's type hints vs C++ templates
   - Runtime vs compile-time type checking
   - Generic type support through typing module

3. **Memory Management**
   - Python's garbage collection vs C++ RAII
   - Simplified resource management
   - Automatic cleanup of channels and agents

4. **Error Handling**
   - Python exceptions vs C++ error handling
   - More Pythonic error propagation
   - Better integration with async/await error handling

## Testing and Verification

The Python implementation includes:
- Unit tests using pytest
- Async test support with pytest-asyncio
- Coverage reporting
- CI/CD pipeline using GitHub Actions
