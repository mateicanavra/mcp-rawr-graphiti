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

## Installation and Setup Guide

This guide covers how to install the `graphiti` CLI and set up the necessary environment. Choose the path that best suits your needs:

1.  **For Regular Users (Recommended):** Install the CLI globally using `pipx` for managing projects and running services.
2.  **For Developers:** Set up a local development environment using `venv` if you plan to modify the CLI or server code.

---

### 1. Standard Installation for Users (Using `pipx`)

This is the **strongly recommended** method if you primarily want to *use* the `graphiti` CLI to initialize projects, manage entities, and run the Docker services. `pipx` installs the CLI into an isolated environment, making it available system-wide without interfering with other Python projects.

**Why `pipx`?**

*   **Isolation:** Prevents dependency conflicts.
*   **Clean Global Environment:** Keeps your system Python tidy.
*   **Safety:** Avoids issues with `sudo pip` or modifying system Python.

**Prerequisites:**

*   **Python:** 3.10+ (`python3 --version`).
*   **Docker & Docker Compose:** Install from [Docker's official website](https://docs.docker.com/get-docker/).
*   **`uv`:** Follow the instructions in the [Prerequisites](#prerequisites) section above.
*   **`pipx`:** If you don't have it:
    ```bash
    # Install pipx (requires Python and pip)
    python3 -m pip install --user pipx
    # Add pipx to your PATH
    python3 -m pipx ensurepath
    # Close and reopen your terminal, or source your shell profile (e.g., ~/.zshrc, ~/.bashrc)
    ```

**Steps:**

1.  **Clone This Repository:** You need the source code to build the CLI and access configuration files (like `base-compose.yaml`). Clone it to a stable location (e.g., `~/dev/rawr-mcp-graphiti`).
    ```bash
    # Choose a suitable parent directory
    cd ~/dev
    git clone <repository-url> rawr-mcp-graphiti
    cd rawr-mcp-graphiti
    ```

2.  **Configure Environment Variables (Optional but Recommended):**
    *   Copy the example `.env` file *within the cloned repository*:
        ```bash
        # Make sure you are in the cloned repo directory (e.g., ~/dev/rawr-mcp-graphiti)
        cp .env.example .env
        ```
    *   **Edit `.env`:** Fill in required secrets and configurations (Neo4j credentials, OpenAI key, etc.). See the "Configure Environment" section under Developer Setup for details.

3.  **Install CLI using `pipx`:** Navigate to the root of the cloned repository (`rawr-mcp-graphiti`) in your terminal and run:
    ```bash
    # Make sure you are in the cloned repo directory
    pipx install . --include-deps
    ```
    *   This installs the `rawr-mcp-graphiti` package into an isolated `pipx` environment.
    *   `--include-deps` ensures necessary runtime dependencies are included.

4.  **First Run & Repo Path Configuration:**
    *   The first time you run a `graphiti` command that needs to access the repository (like `graphiti check-setup` or `graphiti compose`), it might not find the repository automatically.
    *   If it can't find it, the CLI will **prompt you interactively** to enter the absolute path to where you cloned the `rawr-mcp-graphiti` repository.
    *   Enter the correct absolute path (e.g., `path/to/this/repo/`).
    *   The CLI will validate the path and save it to a configuration file (`~/.config/graphiti/repo_path.txt`) for future use.
    ```bash
    # Example: Run check-setup from ANY directory after installation
    graphiti check-setup
    # If needed, it will prompt for the repo path here.
    ```

5.  **Verify Installation:**
    ```bash
    # Check where pipx installed it
    which graphiti
    # Should output a path like: <user_home>/.local/bin/graphiti

    # Verify the CLI runs and can find the repo (due to MCP_GRAPHITI_REPO_PATH)
    # Run this from ANY directory (e.g., your home directory `cd ~`)
    graphiti --help
    graphiti check-setup # This should now work from anywhere without prompting (if configured)
    ```
    *   If `check-setup` fails, ensure the path saved in `~/.config/graphiti/repo_path.txt` is correct, or remove the file and run the command again to be re-prompted.

6.  **Updating:** To update after pulling changes in the repository:
    ```bash
    # Navigate back to the repository root
    cd /path/to/your/rawr-mcp-graphiti
    # Pull the latest changes
    git pull
    # Upgrade the pipx installation
    pipx upgrade rawr-mcp-graphiti
    # If needed, force a reinstall from the updated source:
    # pipx reinstall --force rawr-mcp-graphiti
    ```

**Summary for Users:** Clone the repo, copy/edit `.env`, install with `pipx`. Run a command like `graphiti check-setup`; if prompted, provide the absolute path to the cloned repo. The path will be saved automatically for future use.

---

### 2. Local Development Installation (Using `venv`)

Follow these steps *only* if you intend to modify or contribute to the `graphiti` CLI or the MCP server codebase itself. This setup uses a Python virtual environment (`.venv`) and an editable installation, allowing code changes to be reflected immediately when running `graphiti` *within the activated environment*.

**Prerequisites:**

*   Same as for Standard Installation (Python, Docker, `uv`). `pipx` is not required for this method.

**Steps:**

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url> rawr-mcp-graphiti
    cd rawr-mcp-graphiti
    ```

2.  **Configure Environment:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   **Edit `.env`:** Fill in required secrets and configurations:
        *   `NEO4J_USER`, `NEO4J_PASSWORD`: Credentials for Neo4j.
        *   `OPENAI_API_KEY`: OpenAI key.
        *   `MODEL_NAME`: (Optional) OpenAI model.
        *   Adjust other settings (ports, memory) if needed.
        *   `MCP_GRAPHITI_REPO_PATH`: While the CLI run from within the active `venv` and repo root *might* find the root automatically, relying on the auto-prompt or the config file (`~/.config/graphiti/repo_path.txt`) generated on first use (even within the venv) is the recommended approach now. You can still set the environment variable as a manual override if needed.

3.  **Set up Python Virtual Environment:**
    ```bash
    # Create the virtual environment
    python3 -m venv .venv
    # Activate it (example for macOS/Linux)
    source .venv/bin/activate
    # You should see (.venv) in your prompt
    ```

4.  **Install Dependencies:**
    *   Use `uv` to install dependencies from the lock file into the active `venv`.
    ```bash
    # Make sure (.venv) is active
    uv pip sync uv.lock
    ```

5.  **Install CLI in Editable Mode:**
    *   Install the package itself in *editable* mode (`-e`). This links the `graphiti` command within the `venv` directly to your source code.
    ```bash
    # Make sure (.venv) is active
    pip install -e .
    # ('uv pip install -e .' should also work)
    ```

6.  **Verify Installation:**
    ```bash
    # Verify it's using the venv path
    which graphiti
    # Should output path inside your .venv/bin/

    # Verify the CLI runs (ensure venv is active)
    graphiti --help
    graphiti check-setup # Run from repo root
    ```

**Summary for Developers:** Clone, copy/edit `.env`, set up `.venv`, activate it, `uv pip sync`, `pip install -e .`. Run commands from within the repo root with the `venv` active. The repo path will be auto-detected or prompted for and saved on first use.

---

## Understanding Which `graphiti` You're Using

*   **Global (`pipx`)**: If no `(.venv)` is in your prompt, you're likely using the `pipx` version. It relies on the path stored in `~/.config/graphiti/repo_path.txt` (or prompts on first use). Updates require `pipx upgrade`.
*   **Local (`venv`)**: If `(.venv)` is in your prompt (after `source .venv/bin/activate`), you're using the *editable* development version. Code changes are live. Ideally, run from the repo root. Deactivate with `deactivate`.

---

## Verifying Your Setup

Regardless of the installation method, use `check-setup`.

*   **If using `pipx`:** Run `graphiti check-setup` from *any* directory. It relies on the configured path in `~/.config/graphiti/repo_path.txt` (or prompts).
*   **If using `venv`:** Activate the `venv` (`source .venv/bin/activate`) and run `graphiti check-setup` from the *repository root directory*.

```bash
# Example for pipx user (run from anywhere):
graphiti check-setup

# Example for developer (activate venv first, run from repo root):
# source .venv/bin/activate
# graphiti check-setup
```

This command checks:

*   **Repository Root:** Finds the root (via config file `~/.config/graphiti/repo_path.txt`, env var override, or relative paths for venv).
*   **`.env` File:** Checks if the `.env` file exists *at the identified repository root* and if essential variables are loaded.
*   **Docker Status:** Verifies that the `docker` command is available in your `PATH` and that the Docker daemon appears to be running and responsive.

If all checks pass, you're ready to proceed.

## Running the Services (Docker)

The MCP server and its Neo4j database run as Docker containers managed by Docker Compose. **These commands (`compose`, `up`, `down`, etc.) must be run from the root of the `rawr-mcp-graphiti` repository.** Ensure your CLI (either `pipx` or `venv`) is set up correctly and can find the repository root.

1.  **Generate Docker Compose Configuration:**
    *   The `graphiti` CLI generates the final `docker-compose.yml` from `base-compose.yaml` (in the repo) and project definitions in `mcp-projects.yaml` (also in the repo).
    *   Navigate to the repository root and run:
        ```bash
        # cd /path/to/your/rawr-mcp-graphiti
        graphiti compose
        ```
    *   This command reads `mcp-projects.yaml`. If you initialize new projects using `graphiti init`, this file will be updated automatically with *absolute paths* to your projects. Ensure these paths are correct for your system, as they are used for Docker volume mounts.
    *   It also updates the `.cursor/mcp.json` file in each enabled project's root directory.

2.  **Start Services:**
    *   Build and start the containers (Neo4j, root MCP server, and any project-specific servers defined in `mcp-projects.yaml`):
        ```bash
        graphiti up
        ```
    *   To run in detached mode (in the background):
        ```bash
        graphiti up -d
        ```
    *   The first time you run this, Docker may build the `graphiti-mcp-server` image. Subsequent starts are faster.
    *   The root MCP server will typically be available at `http://localhost:8000` (or the port specified by `MCP_ROOT_HOST_PORT` in `.env`). Project-specific servers will be available on ports assigned sequentially starting from 8001 (or as configured in their respective `mcp-config.yaml` files). Check the output of `graphiti compose` for port assignments.
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
    *   Restart services: `graphiti restart [-d]` (Runs `down` then `up`)
    *   Reload (restart) a specific service: `graphiti reload <service_name>` (e.g., `graphiti reload graphiti-mcp-root`)

## Using the `graphiti` CLI

The `graphiti` CLI helps manage projects and the Docker environment. Run `graphiti --help` to see all commands.

**Key Command Locations:**

*   **Run from Repository Root (`rawr-mcp-graphiti/`):**
    *   `graphiti compose`: Generates `docker-compose.yml`.
    *   `graphiti up|down|restart|reload|logs`: Manages Docker services.
    *   `graphiti check-setup`: Verifies setup (especially useful here for venv users).
*   **Run from Project Parent Directory:**
    *   `graphiti init <project_name> [target_dir]`: Initializes a new project structure in the specified directory.
*   **Run from Existing Project Root Directory:**
    *   `graphiti entity <set_name>`: Creates a new entity definition template within this project's `entities` directory.
    *   `graphiti rules <project_name>`: Sets up/updates Cursor rule symlinks for this project.

**Example Workflow:**

1.  Install CLI (`pipx` recommended for users).
2.  `cd /path/to/your/rawr-mcp-graphiti`
3.  `graphiti compose`
4.  `graphiti up -d` (Start services)
5.  `cd /path/to/where/you/keep/projects`
6.  `graphiti init my-new-ai-project`
7.  `cd my-new-ai-project`
path/to/your/project/ai/graph/entities/`)
9.  Edit `user-profiles.yaml`...
10. The `my-new-ai-project` is now registered in `mcp-projects.yaml` (in the repo root). If you re-run `graphiti compose` and `graphiti up -d` (from the repo root), a dedicated MCP server instance for this project might be started (depending on the base config).

## Development Notes

*   **Generating `uv.lock`:** If the `uv.lock` file is missing or out of date, you can regenerate it from `pyproject.toml` using:
    ```bash
    # Activate venv
    uv pip compile pyproject.toml --output-file uv.lock
    # Or potentially just: uv pip lock
    # Commit the updated uv.lock file to the repository.
    ```
*   **Local `graphiti-core` Development:** If you are developing `graphiti-core` locally alongside this server:
    1.  Build the `graphiti-core` wheel file (e.g., `python3 -m build`) in the `graphiti-core` repository. This creates files in its `dist/` directory.
    2.  Ensure the `dist/` directory containing the `.whl` file exists at the *root* of the *main Graphiti repository* (one level above `rawr-mcp-graphiti`). The path might need adjustment depending on your exact structure post-extraction.
    3.  In `rawr-mcp-graphiti/pyproject.toml`, ensure the line `graphiti-core = {path = "../dist/graphiti_core-...-py3-none-any.whl"}` (adjust path/filename) is uncommented. Comment out the versioned line `graphiti-core>=...`.
    4.  Re-run `uv pip sync uv.lock` or `pip install -e .` in your venv.
    5.  The Docker build process might also need adjustment if it doesn't automatically pick up the local wheel installation from the venv. Consider adding a `COPY ../dist /dist` and `RUN uv pip install /dist/*.whl` in the Dockerfile's builder stage if needed.
*   **Running Server without Docker:** You can run the server directly for debugging:
    ```bash
    # Ensure .env is loaded or variables are exported
    # Activate venv: source .venv/bin/activate
    # Example:
    python3 graphiti_mcp_server.py --transport sse --group-id my-test-group --log-level debug
    # Add other flags like --use-custom-entities, --entity-type-dir as needed
    ```

## ⚠️ DANGER ZONE: Clearing the Database ⚠️

The environment variable `NEO4J_DESTROY_ENTIRE_GRAPH` in your `.env` file is **extremely dangerous**.

*   **Setting `NEO4J_DESTROY_ENTIRE_GRAPH=true` will PERMANENTLY DELETE ALL DATA in your Neo4j database when the containers start.**
*   This affects **ALL** knowledge graphs, not just a specific `group_id`.
*   **This action cannot be undone.**
*   Only set this to `true` if you are absolutely certain you want to wipe the entire database.
*   **Immediately** comment it out or set it back to `false` after use to prevent accidental data loss on subsequent restarts.
