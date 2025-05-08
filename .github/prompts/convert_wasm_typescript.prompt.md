# Convert Code to typescript and WASM

Let's convert this entire codebase from rust to typescript and WASM with modern practices.  

Create a folder called wasm/samlib converting the cpp code in src/samlib and rust code in rust/samlib and python code in python/samlib and ocaml in ocaml/samlib.

Create a .codespaces/wasm folder with a github codespaces definition and docker file for wasm. 

create a docs/wasm_migrate folder with markdown documentation detailing the process for each file's conversion.

include github workflows to build the code for format and style rules, to run tests.

Create a readme file for building, formatting, testing and debugging on Windows and Linux using typescript and wasm tools such as bun.
