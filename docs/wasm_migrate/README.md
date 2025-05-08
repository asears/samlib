# WASM Migration Guide

This directory contains documentation for the migration of SamLib to WebAssembly and TypeScript.

## Migration Process

1. [Core Components](./core_components.md)
2. [Agent System](./agent_migration.md)
3. [Channel System](./channel_migration.md)
4. [Task System](./task_migration.md)
5. [Post Office](./postoffice_migration.md)
6. [Environment](./environment_migration.md)

## Architecture Overview

The WASM version of SamLib is structured into two main parts:
1. Core functionality implemented in Rust and compiled to WebAssembly
2. TypeScript wrapper providing a more ergonomic API for JavaScript/TypeScript users

### Design Decisions

- Performance-critical components are implemented in Rust and compiled to WASM
- Channel and queue implementations use Web Workers for true parallelism
- TypeScript provides type safety and better IDE integration
- Bun is used as the runtime for better performance
