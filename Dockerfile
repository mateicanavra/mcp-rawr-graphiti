FROM --platform=$BUILDPLATFORM python:3.11-slim AS base

# Set environment variables to prevent buffering issues with logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Install curl, install uv, add its dir to the current PATH, and verify in one step
RUN apt-get update && apt-get install -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Install uv using the recommended installer script
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    # Add uv's ACTUAL installation directory to the PATH for this RUN command's shell
    && export PATH="/root/.local/bin:${PATH}" \
    # Verify uv installation within the same RUN command
    && uv --version

# Add uv's ACTUAL installation directory to the ENV PATH for subsequent stages and the final image
ENV PATH="/root/.local/bin:${PATH}"

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
# Also copy binaries installed by dependencies (like uv itself if installed via pip in builder)
COPY --from=builder /root/.local/bin /root/.local/bin

# Copy application code
COPY graphiti_mcp_server.py ./
COPY constants.py ./
COPY entities/ ./entities/
COPY entrypoint.sh .

# Make entrypoint script executable
RUN chmod +x ./entrypoint.sh

# Expose the default MCP port (adjust if needed)
EXPOSE 8000

# Set the entrypoint script to run when the container starts
ENTRYPOINT ["./entrypoint.sh"]

# Default command can be overridden (e.g., to specify group_id)
# Example: docker run <image> --group-id my_project
CMD ["--transport", "sse"]
