# SAMLib OCaml

A modern OCaml implementation of the Simple Agent/Actor Model Library.

## Prerequisites

### Windows
1. Install OCaml for Windows:
   ```powershell
   # Using Chocolatey
   choco install ocaml
   ```
2. Install OPAM:
   ```powershell
   # Download and run the installer
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/ocaml/opam/master/shell/install.sh'))
   ```

### Linux
```bash
# Ubuntu/Debian
sudo apt-get install opam
# Initialize OPAM
opam init
```

## Building

1. Install dependencies:
   ```shell
   opam install . --deps-only
   ```

2. Build the project:
   ```shell
   dune build
   ```

3. Run tests:
   ```shell
   dune runtest
   ```

## Development

### Code Formatting
Format code using OCamlformat:
```shell
dune build @fmt
```

Apply formatting fixes:
```shell
dune build @fmt --auto-promote
```

### Testing
Run specific test files:
```shell
dune runtest test/test_channel.ml
```

Run tests with coverage:
```shell
dune runtest --instrument-with bisect_ppx --force
bisect-ppx-report html
```

### Documentation
Generate documentation:
```shell
dune build @doc
```

View documentation:
- Windows: `start _build/default/_doc/_html/index.html`
- Linux: `xdg-open _build/default/_doc/_html/index.html`

## Debugging

### Using OCamldebug
1. Build with debug symbols:
   ```shell
   dune build --profile dev
   ```

2. Start debugger:
   ```shell
   ocamldebug _build/default/test/test_channel.bc
   ```

### Using VS Code
1. Install OCaml Platform extension
2. Set breakpoints in your code
3. Use the Debug view to start debugging

## Project Structure

```
ocaml/samlib/
├── lib/              # Core library implementation
│   ├── agent.ml     # Agent implementation
│   ├── channel.ml   # Message passing channels
│   └── environment.ml # Actor system environment
├── test/            # Unit tests
└── examples/        # Example applications
```
