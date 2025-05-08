FROM mcr.microsoft.com/devcontainers/rust:1-bullseye

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g bun

# Install WASM tools
RUN curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh \
    && cargo install wasm-bindgen-cli

# Install build essentials
RUN apt-get update && apt-get install -y build-essential cmake

WORKDIR /workspace
