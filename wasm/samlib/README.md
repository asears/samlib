# WASM SamLib

This is the WebAssembly and TypeScript implementation of SamLib, providing actor-model based concurrency primitives for web applications.

## Structure

- `src/` - TypeScript source files
- `src/wasm/` - WebAssembly modules
- `tests/` - Test files
- `examples/` - Example usage

## Building

### Prerequisites

- Node.js 18+
- Bun 1.0+
- wasm-pack
- wasm-bindgen

### Development Setup

```bash
# Install dependencies
bun install

# Build WASM modules
bun run build:wasm

# Build TypeScript
bun run build

# Run tests
bun test

# Format code
bun run format
```

## Documentation

See the [`docs/wasm_migrate`](../../docs/wasm_migrate) folder for detailed migration documentation.
