Okay, I have analyzed the provided repository snapshot (`graphiti-mcp-repo.md`) and the user's request.

Here's my review report focusing on the request to update the README for a fresh installation scenario, assuming `mcp_server` is extracted into its own repository.

## Review Report: README Update and Installation Process

**Objective:** Analyze the provided codebase snapshot to generate accurate, up-to-date README instructions for setting up the `mcp_server` project as a standalone repository for a new developer. Evaluate alternative installation methods.

**Date:** 2024-08-27

---

### 1. CONTEXT ANALYSIS

*   **Original Requirements:** The user wants to extract the `mcp_server` directory into a new repository and needs clear instructions for a fresh developer setup. The existing `README.md` is outdated.
*   **Implementation Details:** The setup involves Python environment management (likely `venv`), dependency installation using `uv`, a custom CLI tool (`graphiti`) built with Typer, Docker/Docker Compose for running services (Neo4j, MCP servers), and configuration via `.env` and YAML files.
*   **Architectural Context:** The system consists of a core server (`graphiti_mcp_server.py`), a CLI (`graphiti_cli/`), entity definitions (`entity_types/`), Docker configuration (`Dockerfile`, `base-compose.yaml`, generated `docker-compose.yml`), and project management files (`mcp-projects.yaml`).
*   **Impact:** The primary output required is updated documentation (`README.md`) reflecting the current setup process based on the provided files. A secondary goal is to suggest potential improvements to the installation/distribution process.

### 2. CODE QUALITY ASSESSMENT

*   **Structure:** The CLI (`graphiti_cli/`) is well-structured with separation of concerns (main, commands, core, yaml_utils). Constants are centralized (`constants.py` @LINE:1286).
*   **Standards:** Code generally follows Python best practices. Type hints are used extensively. `uv` is used for dependency management, which is modern and efficient.
*   **Readability:** Code is generally readable, with comments and docstrings. CLI help messages are informative (`graphiti_cli/main.py` @LINE:590).
*   **Error Handling:** Basic error handling exists (e.g., checking file existence, catching exceptions in CLI commands). Docker Compose execution includes `check=True` (@LINE:525).
*   **Dependencies:** Dependencies are managed via `pyproject.toml` (@LINE:1655) and `uv.lock` (mentioned in `Dockerfile` @LINE:1479 and `.repomixignore` @LINE:1199). The distinction between local wheel (`graphiti-core @ file:///dist/...`) and published package (`graphiti-core>=...`) is important for development vs. distribution.
*   **Documentation:** Docstrings are present in many places, especially entity definitions and CLI commands. However, the main `README.md` is acknowledged as outdated (Critical documentation issue).

### 3. ARCHITECTURAL REVIEW

*   **CLI & Server:** Clear separation between the CLI tool for management and the actual MCP server runtime.
*   **Configuration:** Configuration relies on `.env` for secrets/environment variables and YAML files (`mcp-config.yaml`, `mcp-projects.yaml`) for project structure and service definitions.
*   **Dockerization:** The `Dockerfile` (@LINE:1451) uses multi-stage builds effectively. `base-compose.yaml` (@LINE:1207) uses anchors well for DRY configuration. The generation of `docker-compose.yml` (@LINE:1348) via `graphiti compose` (implemented in `yaml_utils.py` @LINE:869) centralizes service definition logic.
*   **Potential Issue (Extraction):** The CLI heavily relies on finding a "repository root" containing `mcp_server` (`core.py` @LINE:457, `get_repo_root`). If `mcp_server` *becomes* the root, this logic might still work if run from within that directory, but relying on the `MCP_GRAPHITI_REPO_PATH` environment variable (@LINE:466) becomes more critical for robustness, especially if the CLI needs to reference files outside the immediate project (like the `rules/` which might be co-located or referenced differently post-extraction).
*   **Potential Issue (Extraction):** The `mcp-projects.yaml` (@LINE:1631) registry uses absolute paths. While necessary for Docker volume mounts, this needs careful handling and clear documentation, especially if projects reside outside the main `mcp_server` repo. The `graphiti init` command manages this, but users need to understand the implications.

### 4. SECURITY ASSESSMENT

*   **Secrets Management:** Secrets (`NEO4J_PASSWORD`, `OPENAI_API_KEY`) are correctly handled via `.env` file, excluded from version control (`.gitignore` via `.repomixignore` @LINE:1199, `.env` in `repomix.config.json` @LINE:1700). `.env.example` (@LINE:1158) provides a safe template.
*   **Dangerous Operation:** The `NEO4J_DESTROY_ENTIRE_GRAPH` environment variable (@LINE:1193, @LINE:1544) is extremely dangerous. While documented with warnings in `.env.example` and the `entrypoint.sh` log, its existence poses a risk. It should be heavily emphasized in the README.
*   **Input Validation:** Assumed to be handled by MCP/FastMCP and Pydantic models within the server logic.

### 5. PERFORMANCE REVIEW

*   **Dependency Installation:** Using `uv pip sync` (@LINE:1482) is generally faster than `pip install`.
*   **Docker:** Multi-stage builds optimize image size and build times.
*   **Server:** Async implementation (`graphiti_mcp_server.py` @LINE:1000) using `asyncio` and `FastMCP` is appropriate for I/O-bound tasks. The background episode processing queue (`process_episode_queue` @LINE:1000) prevents blocking the main API.

### 6. DOCUMENTATION REVIEW

*   **Inline/Docstrings:** Generally good, especially for entities and CLI commands.
*   **README:** Confirmed outdated (Critical).
*   **Configuration Files:** Comments in `base-compose.yaml` (@LINE:1207) and `.env.example` (@LINE:1158) are helpful. Headers in generated `docker-compose.yml` (@LINE:1348) and `mcp-projects.yaml` (@LINE:1631) provide context.
*   **Rules:** Markdown files in `rules/` (@LINE:797, @LINE:823, @LINE:869, @LINE:925) document schema and maintenance processes for AI interaction.

### 7. ISSUE CLASSIFICATION

*   **Critical:**
    *   Outdated `README.md`. Needs complete rewrite for fresh installation instructions.
*   **Major:**
    *   Potential fragility in `get_repo_root` logic (@LINE:457) if `mcp_server` is extracted and the CLI is run from unexpected locations without `MCP_GRAPHITI_REPO_PATH` set. Needs clear documentation.
    *   Reliance on absolute paths in `mcp-projects.yaml` (@LINE:1631) requires careful user understanding and management, especially post-extraction.
*   **Minor:**
    *   The `Dockerfile` (@LINE:1486) comments out `uv pip install .`. This means the server is run via `uv run graphiti_mcp_server.py` (@LINE:1556) inside the container, not as an installed package. This works but is slightly less standard than installing the package itself.
*   **Nitpicks:** None relevant to the core request.

### 8. RECOMMENDATIONS

1.  **Replace `README.md`:** Use the generated content below.
2.  **Clarify `MCP_GRAPHITI_REPO_PATH`:** Emphasize its use in the new README, especially if the CLI needs to interact with files outside the immediate `mcp_server` directory (e.g., shared rules, projects located elsewhere).
3.  **Explain `mcp-projects.yaml`:** Detail its purpose and the requirement for absolute paths in the README.
4.  **Highlight `NEO4J_DESTROY_ENTIRE_GRAPH`:** Add a prominent warning section in the README about this flag.
5.  **Consider Alternative Distribution:** Evaluate publishing the CLI to PyPI or providing a fully containerized CLI experience to simplify setup for end-users (see section below).

---

### Proposed `README.md` Content

```markdown
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

*   **Python:** Version 3.10 or higher (Python 3.11 recommended, as used in Dockerfile).
*   **Docker & Docker Compose:** Required to run the Neo4j database and MCP server containers. Install from [Docker's official website](https://docs.docker.com/get-docker/).
*   **`uv`:** A fast Python package installer and resolver. Install it system-wide:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Follow instructions to add uv to your PATH if needed
    source $HOME/.cargo/env # Or equivalent for your shell
    uv --version # Verify installation
    ```
*   **Git:** For cloning the repository.

## Installation and Setup

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd mcp-server # Or your chosen directory name
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
        *   *(Optional but Recommended)* `MCP_GRAPHITI_REPO_PATH`: If you intend to run the `graphiti` CLI from directories outside this repository root OR if the CLI needs to reference files outside this directory (e.g., shared rules, projects elsewhere), set this environment variable to the absolute path of this repository's root directory.
            ```bash
            # Example for .bashrc or .zshrc
            export MCP_GRAPHITI_REPO_PATH=/path/to/your/mcp-server
            ```

3.  **Set up Python Virtual Environment:**
    *   Create a virtual environment using Python's built-in `venv`:
        ```bash
        python -m venv .venv
        ```
    *   Activate the virtual environment:
        *   **macOS/Linux:** `source .venv/bin/activate`
        *   **Windows:** `.venv\Scripts\activate`
    *   You should see `(.venv)` prepended to your shell prompt.

4.  **Install Dependencies:**
    *   Use `uv` to install dependencies based on the lock file:
        ```bash
        uv pip sync uv.lock
        ```
    *   This ensures everyone uses the exact same dependency versions.

5.  **Install the CLI:**
    *   Install the `mcp-server` package itself in editable mode. This makes the `graphiti` command available within your activated virtual environment.
        ```bash
        uv pip install -e .
        ```
    *   Verify the CLI installation:
        ```bash
        graphiti --help
        ```

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

*   **Local `graphiti-core` Development:** If you are developing `graphiti-core` locally alongside this server:
    1.  Build the `graphiti-core` wheel file (e.g., `python -m build`) in the `graphiti-core` repository. This creates files in its `dist/` directory.
    2.  Ensure the `dist/` directory containing the `.whl` file exists at the *root* of the *main Graphiti repository* (one level above `mcp_server`). The path might need adjustment depending on your exact structure post-extraction.
    3.  In `mcp_server/pyproject.toml`, ensure the line `graphiti-core @ file:///dist/...` is uncommented and points to the correct wheel file name. Comment out the line starting with `graphiti-core>=...`.
    4.  When you run `graphiti up`, the build process (`Dockerfile` @LINE:1476) will copy the local wheel from the `dist/` directory and install it inside the Docker image.
*   **Running Server without Docker:** You can run the server directly for debugging (though Docker is recommended for full setup):
    ```bash
    # Ensure .env is loaded or variables are exported
    # Activate venv: source .venv/bin/activate
    uv run graphiti_mcp_server.py --transport sse --group-id my-test-group --log-level debug
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

While the current setup works well for developers contributing to this repository, simpler methods could be considered for distributing the CLI or the server to end-users:

1.  **Publish CLI to PyPI:** Package `graphiti_cli` and its dependencies and publish it to the Python Package Index (PyPI). Users could then install it globally or in a virtual environment using `pip install graphiti-mcp-cli` (or a chosen package name). This simplifies CLI setup significantly but still requires users to manage Docker for the services.
2.  **Containerized CLI:** Create a Docker image specifically for running the CLI. Users would run `docker run -it --rm -v $(pwd):/workspace -v /var/run/docker.sock:/var/run/docker.sock <cli-image-name> graphiti ...` commands. This encapsulates Python dependencies but adds Docker complexity to CLI usage.
3.  **All-in-One Docker Image:** A more complex approach could involve a single Docker image entrypoint that can either start the server *or* execute CLI commands.

The current method (local install via `uv pip install .`) combined with Docker Compose (`graphiti up`) provides a good balance for developers actively working with the codebase. Publishing to PyPI would be the most user-friendly approach for distributing the CLI widely.
```

---

This updated README should provide a much clearer path for a new developer setting up the project. Remember to adjust repository URLs and potentially refine the explanation of `MCP_GRAPHITI_REPO_PATH` based on the final structure after extraction.