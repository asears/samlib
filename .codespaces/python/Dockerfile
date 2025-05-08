FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set working directory
WORKDIR /workspace

# Copy requirements from pyproject.toml
COPY pyproject.toml .

# Install dependencies using uv
RUN uv pip install --system ".[dev]"

# Set Python path
ENV PYTHONPATH=/workspace/python

# Default command
CMD ["bash"]
