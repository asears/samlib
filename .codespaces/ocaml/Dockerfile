FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install OCaml and OPAM
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential \
    curl \
    git \
    m4 \
    pkg-config \
    unzip \
    bubblewrap \
    && rm -rf /var/lib/apt/lists/*

# Install OPAM
RUN curl -fsSL https://raw.githubusercontent.com/ocaml/opam/master/shell/install.sh | sh -s

# Initialize OPAM and install OCaml
RUN useradd -m vscode \
    && su vscode -c "opam init --auto-setup --disable-sandboxing" \
    && su vscode -c "opam switch create 4.14.1" \
    && su vscode -c "opam install -y \
        dune \
        ocaml-lsp-server \
        ocamlformat \
        utop \
        odoc \
        ounit2 \
        core \
        async \
        ppx_jane \
        ppx_deriving \
        menhir"

# Add OPAM environment to PATH
ENV PATH="/home/vscode/.opam/4.14.1/bin:${PATH}"
ENV CAML_LD_LIBRARY_PATH="/home/vscode/.opam/4.14.1/lib/stublibs"
