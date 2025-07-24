FROM --platform=$BUILDPLATFORM python:3.11-slim AS base

# Set environment variables to prevent buffering issues with logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Install curl (needed for the container health‑check) and a *pinned* version of
# uv.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    # Install uv
    && pip install --no-cache-dir uv==0.6.14 \
    # Verify installation
    && uv --version \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- Build Stage ---
# Use a build stage to install dependencies
# This helps leverage Docker layer caching
FROM base AS builder

# Create dist directory for local wheel installation if needed
RUN mkdir -p /dist/

# Copy the dist directory contents (containing local wheels)
# This step allows installing local packages like graphiti-core
# Ensure 'dist' exists in your project root and contains necessary wheels before building
# COPY dist/* /dist/ # Commented out as it's not needed when using published graphiti-core

# Copy project configuration
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv sync (faster than pip install)
# This installs dependencies specified in pyproject.toml based on uv.lock
# Add --system to allow installation into the container's Python environment
RUN uv pip sync uv.lock --system

# If you want to install the project itself (rawr-mcp-graphiti), uncomment the line below
# This makes 'constants.py', 'graphiti_mcp_server.py', etc., available as installed modules
# RUN uv pip install . --no-deps --system


# --- Final Stage ---
# Start from the base image again for a cleaner final image
FROM base

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# Binaries installed with the dependencies (if any) live in /usr/local/bin which is
# already present in the base stage, so no extra COPY step is required.

# Copy application code
COPY graphiti_mcp_server.py ./
COPY constants.py ./
COPY entities/ ./entities/
COPY entrypoint.sh .

# Make entrypoint script executable
RUN chmod +x ./entrypoint.sh

# --------------------------------------------------
# Security hardening – drop root privileges
# --------------------------------------------------
# 1. Create an unprivileged user *after* all packages are installed.
# 2. Give it ownership over /app so the process can write logs, etc.
# 3. Switch to that user for the remainder of the image lifetime.

RUN useradd --create-home --shell /usr/sbin/nologin --uid 1000 graphiti \
    && chown -R graphiti:graphiti /app

USER graphiti
WORKDIR /app

# Expose the default MCP port (adjust if needed)
EXPOSE 8010

# --------------------------------------------------
# Entrypoint / default command
# --------------------------------------------------

ENTRYPOINT ["./entrypoint.sh"]

# Default command can be overridden (e.g., to specify group_id)
# Example: docker run <image> --group-id my_project
CMD ["--transport", "sse"]
