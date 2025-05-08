FROM mcr.microsoft.com/devcontainers/rust:latest

# Install additional OS packages
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    cmake \
    build-essential \
    lldb

# Install cargo tools
RUN cargo install cargo-watch cargo-edit cargo-expand

# Clean up
RUN apt-get autoremove -y && apt-get clean -y
