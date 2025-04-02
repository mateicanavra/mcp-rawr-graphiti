# Graphiti MCP Server

This repository contains the Graphiti Model Context Protocol (MCP) Server and its associated command-line interface (CLI) tool. It allows AI agents to interact with a knowledge graph for persistent memory, entity extraction, and relationship tracking using the Graphiti framework.

## Features

*   Exposes Graphiti functionality via MCP (SSE or Stdio transport).
*   Provides tools for adding/searching episodes, nodes, and facts in a knowledge graph.
*   Supports custom entity type definitions for tailored extraction.
*   Includes a CLI (`graphiti`) for project initialization, entity management, and Docker environment control.
*   Uses Docker Compose for easy deployment of the MCP server(s) and Neo4j database.
*   Leverages `uv` for fast dependency management.

## Prerequisites

*   **Python:** Version 3.10 or higher (`python3 --version`). Python 3.11+ recommended (as used in Dockerfile).
*   **Docker & Docker Compose:** Required to run the Neo4j database and MCP server containers. Install from [Docker's official website](https://docs.docker.com/get-docker/).
*   **`uv`:** A fast Python package installer and resolver. If you don't have it, install it first (requires `pip` or `curl`):
    ```bash
    # Using pip (recommended if you have Python/pip already)
    pip install uv
    # Or using curl
    # curl -LsSf https://astral.sh/uv/install.sh | sh
    # source $HOME/.cargo/env # Or equivalent for your shell if using curl method
    
    # Verify installation
    uv --version
    ```
*   **Git:** For cloning the repository.

## Global CLI Installation (Recommended for General Use)

If you only intend to *use* the `graphiti` CLI (e.g., to manage projects or run Docker services) and not actively develop the CLI itself, installing it globally using `pipx` is the recommended approach. This avoids dependency conflicts with other Python projects.

**Prerequisites:**

*   You still need **Docker & Docker Compose** installed to run the actual MCP server and database.
*   Ensure you have `pipx` installed. If not:
    ```bash
    # Install pipx (requires Python and pip)
    python3 -m pip install --user pipx
    # Add pipx to your PATH
    python3 -m pipx ensurepath
    # Close and reopen your terminal or source your shell profile for PATH changes to take effect
    ```

**Installation:**

Assuming the package `rawr-mcp-graphiti` is published on PyPI:

```bash
pipx install rawr-mcp-graphiti
```

**Usage Note:**

Even when installed globally, the `graphiti` CLI commands (like `compose`, `up`, `check-setup`, `init`) usually need to know the context of the project you're working on. Therefore, you will typically need to:

*   **Run `graphiti` commands from within the root directory** of the project you want to manage (the directory containing the `.env` file and where `docker-compose.yml` will be generated).
*   OR (less common for `pipx` installs), set the `MCP_GRAPHITI_REPO_PATH` environment variable if required by specific workflows running outside a project context.

This global installation mainly simplifies access to the `graphiti` command itself without needing to activate a specific virtual environment for the CLI.

## Installation and Setup (for Development)

Follow these steps if you intend to modify or contribute to the `graphiti` CLI or the MCP server codebase itself.

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd rawr-mcp-graphiti # Or your chosen directory name
    ```

2.  **Configure Environment:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   **Edit `.env`:** Fill in the required secrets and configurations:
        *   `NEO4J_USER`, `NEO4J_PASSWORD`: Credentials for the Neo4j database.
        *   `OPENAI_API_KEY`: Your OpenAI API key (required for entity extraction/LLM features).
        *   `MODEL_NAME`: (Optional) Specify the OpenAI model (defaults to `gpt-4o`).
        *   Adjust Neo4j ports/memory settings if needed.
        *   `MCP_GRAPHITI_REPO_PATH`: (Optional) Set this environment variable **only** if you need to run the `graphiti` CLI from outside this repository's root directory OR if the CLI needs to reference external files (e.g., shared rules). **For the standard Docker-based workflow described below, this variable is typically NOT required.** If needed, set it to the absolute path of this repository's root directory:
            ```bash
            # Example for .bashrc or .zshrc
            # export MCP_GRAPHITI_REPO_PATH=/path/to/your/mcp-rawr-graphiti
            ```

3.  **Set up Python Virtual Environment:**
    *   Create a virtual environment using Python's built-in `venv` (using `python3` is recommended for clarity):
        ```bash
        python3 -m venv .venv
        ```
    *   Activate the virtual environment:
        *   **macOS/Linux:** `source .venv/bin/activate`
        *   **Windows:** `.venv\Scripts\activate`
    *   You should see `(.venv)` prepended to your shell prompt.

4.  **Install Dependencies:**
    *   Use `uv` to install dependencies based on the lock file (`uv.lock`). This file ensures reproducible builds.
    *   *(Note: If `uv.lock` is missing, you'll need to generate it first. See Development Notes below).*
    ```bash
    uv pip sync uv.lock
    ```

5.  **Install the CLI:**
    *   Install the `rawr-mcp-graphiti` package itself in editable mode. This makes the `graphiti` command available within your activated virtual environment.
        ```bash
        uv pip install -e .
        ```
    *   Verify the CLI installation:
        ```bash
        graphiti --help
        ```

## Verifying Your Setup

Before attempting to run the Docker services, it's recommended to verify your local environment setup using the `check-setup` command:

```bash
# Make sure your virtual environment is active
graphiti check-setup
```

This command will perform several checks:

*   **Repository Root:** Ensures the CLI can correctly identify the project's root directory.
*   **`.env` File:** Checks if the `.env` file exists at the root and if essential variables (`NEO4J_USER`, `NEO4J_PASSWORD`, `OPENAI_API_KEY`) are loaded.
*   **Docker Status:** Verifies that the `docker` command is available in your `PATH` and that the Docker daemon appears to be running and responsive.

If all checks pass, you'll see a success message. If any checks fail, it will provide specific error messages and tips to help you resolve the issues before proceeding.

## Running the Services (Docker)

The MCP server and its Neo4j database run as Docker containers managed by Docker Compose.

1.  **Generate Docker Compose Configuration:**
    *   The `graphiti` CLI generates the final `docker-compose.yml` from `base-compose.yaml` and project definitions in `mcp-projects.yaml`.
    *   Run the compose command:
        ```bash
        graphiti compose
        ```
    *   This command reads `mcp-projects.yaml`. If you initialize new projects using `graphiti init`, this file will be updated automatically with *absolute paths* to your projects. Ensure these paths are correct for your system, as they are used for Docker volume mounts.

2.  **Start Services:**
    *   Build and start the containers (Neo4j, root MCP server, and any project-specific servers defined in `mcp-projects.yaml`):
        ```bash
        graphiti up
        ```
    *   To run in detached mode (in the background):
        ```bash
        graphiti up -d
        ```
    *   The first time you run this, Docker will build the `graphiti-mcp-server` image, which may take a few minutes. Subsequent starts will be faster.
    *   The root MCP server will typically be available at `http://localhost:8000` (or the port specified by `MCP_ROOT_HOST_PORT` in `.env`). Project-specific servers will be available on ports assigned sequentially starting from 8001 (or as configured in their respective `mcp-config.yaml` files).
    *   You can usually access the Neo4j Browser UI in your web browser at `http://localhost:7474` to interact with the database directly (use the credentials from your `.env` file).

3.  **Check Status:**
    *   View running containers: `docker ps`
    *   View logs: `graphiti logs` or `docker compose logs -f [service_name]` (e.g., `docker compose logs -f graphiti-mcp-root`)

4.  **Stop Services:**
    *   Stop and remove the containers:
        ```bash
        graphiti down
        ```

5.  **Other Docker Commands:**
    *   Restart services: `graphiti restart [-d]`
    *   Reload (restart) a specific service: `graphiti reload <service_name>` (e.g., `graphiti reload graphiti-mcp-root`)

## Using the `graphiti` CLI

The `graphiti` CLI helps manage projects and the Docker environment. Run `graphiti --help` to see all commands. Key commands include:

*   `graphiti init <project_name> [target_dir]`: Initializes a new project structure (including `ai/graph/mcp-config.yaml`, `ai/graph/entities/`, and Cursor rules). Updates `mcp-projects.yaml`.
*   `graphiti entity <set_name> [target_dir]`: Creates a new entity definition file template within an existing project's `entities` directory.
*   `graphiti rules <project_name> [target_dir]`: Sets up or updates symlinks for Cursor AI rules for a project.
*   `graphiti compose`: Generates/updates `docker-compose.yml`.
*   `graphiti up|down|restart|reload`: Manages the Docker Compose stack.

## Development Notes

*   **Generating `uv.lock`:** If the `uv.lock` file is missing or out of date, you can regenerate it from `pyproject.toml` using:
    ```bash
    uv pip compile pyproject.toml --output-file uv.lock
    # Or potentially just: uv pip lock
    # Commit the updated uv.lock file to the repository.
    ```
*   **Local `graphiti-core` Development:** If you are developing `graphiti-core` locally alongside this server:
    1.  Build the `graphiti-core` wheel file (e.g., `python3 -m build`) in the `graphiti-core` repository. This creates files in its `dist/` directory.
    2.  Ensure the `dist/` directory containing the `.whl` file exists at the *root* of the *main Graphiti repository* (one level above `mcp_server`). The path might need adjustment depending on your exact structure post-extraction.
    3.  In `mcp_server/pyproject.toml`, ensure the line `graphiti-core @ file:///dist/...` is uncommented and points to the correct wheel file name. Comment out the line starting with `graphiti-core>=...`.
    4.  When you run `graphiti up`, the build process will copy the local wheel from the `dist/` directory and install it inside the Docker image.
*   **Running Server without Docker:** You can run the server directly for debugging (though Docker is recommended for full setup):
    ```bash
    # Ensure .env is loaded or variables are exported
    # Activate venv: source .venv/bin/activate
    # Example:
    uv run python3 graphiti_mcp_server.py --transport sse --group-id my-test-group --log-level debug
    # Add other flags like --use-custom-entities, --entity-type-dir as needed
    ```

## ⚠️ DANGER ZONE: Clearing the Database ⚠️

The environment variable `NEO4J_DESTROY_ENTIRE_GRAPH` in your `.env` file is **extremely dangerous**.

*   **Setting `NEO4J_DESTROY_ENTIRE_GRAPH=true` will PERMANENTLY DELETE ALL DATA in your Neo4j database when the containers start.**
*   This affects **ALL** knowledge graphs, not just a specific `group_id`.
*   **This action cannot be undone.**
*   Only set this to `true` if you are absolutely certain you want to wipe the entire database.
*   **Immediately** comment it out or set it back to `false` after use to prevent accidental data loss on subsequent restarts.

## Alternative Installation/Distribution Methods

**(This section is less relevant if using the recommended `pipx` method above for general use)**

While the **development setup** described above works well for contributors, simpler methods could be considered for distributing the CLI or the server to end-users:

1.  **Publish CLI to PyPI:** Package `graphiti_cli` and its dependencies and publish it to the Python Package Index (PyPI). Users could then install it globally or in a virtual environment using `pip install graphiti-mcp-cli` (or a chosen package name). **This is the prerequisite for the recommended `pipx` installation method described above.**
2.  **Containerized CLI:** Create a Docker image specifically for running the CLI. Users would run `docker run -it --rm -v $(pwd):/workspace -v /var/run/docker.sock:/var/run/docker.sock <cli-image-name> graphiti ...` commands. This encapsulates Python dependencies but adds Docker complexity to CLI usage.
3.  **All-in-One Docker Image:** A more complex approach could involve a single Docker image entrypoint that can either start the server *or* execute CLI commands.

The **development setup** (local install via `uv pip install -e .`) combined with Docker Compose (`graphiti up`) provides a good balance for developers actively working with the codebase. Publishing to PyPI and using `pipx` is the most user-friendly approach for distributing the CLI widely for general use.
