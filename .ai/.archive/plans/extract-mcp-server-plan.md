# Migration Plan: Extract `mcp_server` Orchestrator to Standalone Repository

## 1. Objective

Extract the `mcp_server` directory into a new, standalone GitHub repository (e.g., `graphiti-mcp-orchestrator`). This repository will preserve the original functionality of `mcp_server` as a central orchestrator, responsible for:
*   Managing project definitions via `mcp-projects.yaml`.
*   Generating a multi-service `docker-compose.yml` using `scripts/graphiti` and `base-compose.yaml`.
*   Running the Neo4j database, the root MCP server, and any project-specific MCP server instances defined in the registry.

The repository should contain updated documentation (`README.md`) explaining its role and usage as an orchestrator.

## 2. Assumptions

*   The `graphiti-core` dependency is available via PyPI (`graphiti-core>=0.8.5`).
*   The **absolute paths** defined in `mcp-projects.yaml` (for `config_file` and `root_dir` of external projects) are valid and accessible from the environment where the `./scripts/graphiti` commands and `docker compose up` will be executed. This is crucial for mounting configuration and entity directories into the respective project containers.
*   The primary interaction method for managing the services is through the bash script `./scripts/graphiti` (e.g., `compose`, `up`, `down`).
*   The Python CLI defined in `graphiti_cli/` and installed via `uv pip install .` (as `graphiti`) serves a potentially different or auxiliary purpose compared to the bash script `./scripts/graphiti`. (This needs clarification in the README).
*   Python 3.11+ and `uv` are required for running the orchestration scripts and potentially the Python CLI.
*   Docker and Docker Compose are required for running the services.
*   A `.env` file in the repository root is used for required secrets (OpenAI API key, Neo4j credentials).

## 3. Migration Steps

1.  **Create GitHub Repository:**
    *   Action: Create a new public GitHub repository (e.g., `graphiti-mcp-orchestrator`).
    *   Owner: (Your GitHub username/organization)

2.  **Copy Files:**
    *   Action: Copy the relevant contents of the current `mcp_server` directory to the root of the new `graphiti-mcp-orchestrator` repository.
    *   Files/Dirs to **Copy**: `scripts/`, `mcp-projects.yaml`, `base-compose.yaml`, `Dockerfile`, `graphiti_mcp_server.py`, `constants.py`, `entity_types/` (containing the 'base' entities), `graphiti_cli/`, `pyproject.toml`, `.env.example`, `README.md` (will be replaced), `.python-version`, `entrypoint.sh`, `rules/` (if applicable), `docs/` (if applicable), `docker-compose.yml` (copy the last generated version as a reference, but it will be ignored by git and regenerated).
    *   Files/Dirs to **Exclude/Delete**: `.venv/`, `__pycache__/`, `*.egg-info`, `llm_cache/`, `.ai/`, `dist/`, `uv.lock` (will be regenerated), `.env`.
    *   Files to **Create/Update**: A new `.gitignore`.

3.  **Clean Up & Verify:**
    *   Action: Verify `pyproject.toml`.
        *   Confirm the `graphiti-core` dependency points to the PyPI version (`"graphiti-core>=0.8.5"`).
        *   Verify `[project.scripts]` defines `graphiti = "graphiti_cli.main:app"` (this makes the Python CLI available if installed).
        *   Verify `[tool.setuptools.packages.find]` includes `graphiti_cli`.
        *   Verify `[tool.setuptools.py-modules]` includes `constants`.
    *   Action: Verify `Dockerfile`.
        *   Ensure `COPY dist/* /dist/` line is absent or commented out.
        *   Verify all necessary source files for the *root* MCP server (`graphiti_mcp_server.py`, `constants.py`, `entity_types/base/`, `entrypoint.sh`) are copied.
    *   Action: Verify `mcp-projects.yaml`.
        *   Crucially, ensure the absolute paths listed for external projects are correct for the target deployment environment. This file will likely need **manual adjustment** by the user after cloning the new repository.
    *   Action: Verify `scripts/graphiti`.
        *   Ensure script paths and commands (like `python`, `docker compose`) are appropriate for the target environment.
    *   Action: Create `.gitignore`.
        *   Add entries: `.venv`, `__pycache__`, `*.pyc`, `*.egg-info`, `build/`, `dist/`, `.env`, `llm_cache/`, `.DS_Store`, `docker-compose.yml` (Important: this file is generated).
    *   Action: Regenerate `uv.lock`.
        *   Navigate to the new repository root in your terminal.
        *   Activate virtual environment (`uv venv`, `source .venv/bin/activate`).
        *   Run `uv lock`.
        *   Commit the newly generated `uv.lock` file.

4.  **Update Documentation (`README.md`):**
    *   Action: Replace the entire content of `README.md` with updated instructions explaining the orchestrator role.
    *   Focus: Purpose (central orchestrator), prerequisites (Python, uv, Docker, Docker Compose), setup (clone, venv, `uv sync`), configuration (`.env`, **crucially `mcp-projects.yaml` path adjustments**), workflow (`./scripts/graphiti compose`, `./scripts/graphiti up`, `./scripts/graphiti down`), adding/managing projects, explanation of included services (Neo4j, root server, project servers), clarification between `./scripts/graphiti` and the Python `graphiti` CLI.

5.  **Testing (Crucial):**
    *   Action: Simulate a fresh developer setup by cloning the new `graphiti-mcp-orchestrator` repository into a completely separate directory.
    *   Follow the new `README.md` instructions *precisely*.
    *   **Critically**: Manually edit `mcp-projects.yaml` in the cloned repo to ensure the absolute paths point to valid locations on the test machine.
    *   Create and populate the `.env` file.
    *   **Acceptance Criteria:**
        *   Prerequisite checks pass.
        *   `uv venv` and `source .venv/bin/activate` work.
        *   `uv sync` completes successfully.
        *   `./scripts/graphiti compose` runs without errors and generates a `docker-compose.yml` containing `neo4j`, `graphiti-mcp-root`, and all services defined in the (edited) `mcp-projects.yaml`.
        *   `./scripts/graphiti up -d` starts all defined containers successfully.
        *   `docker compose ps` shows all services as running/healthy.
        *   `docker compose logs <service_name>` (for neo4j, graphiti-mcp-root, and project-specific services) shows successful startup and expected behaviour (e.g., root server connects to Neo4j, project servers load their entities).
        *   Basic functionality test: Connect to the `graphiti-mcp-root` service (e.g., port 8000 via SSE) using an MCP client and verify `get_status` works. If possible, test connectivity/functionality of one of the project-specific services.
        *   `./scripts/graphiti down` stops and removes all containers.
        *   (Optional) `uv pip install .` followed by `graphiti --help` works, demonstrating the Python CLI is installable.

## 4. Potential Risks & Dependencies

*   **Path Brittleness:** The system is highly dependent on the correctness of **absolute paths** in `mcp-projects.yaml`. Incorrect paths are the most likely cause of failure. The README must strongly emphasize the need for users to verify/edit these paths after cloning.
*   **Environment Differences:** The orchestration script `./scripts/graphiti` might rely on specific shell commands or environment variables that differ between development and deployment machines.
*   **CLI Confusion:** The existence of two `graphiti` commands (`./scripts/graphiti` vs. the Python one installed via `pip`) requires clear documentation.
*   **`graphiti-core`:** Relies on `graphiti-core>=0.8.5` being accessible from PyPI.

## 5. Next Steps

1.  Execute steps 1-3 (Create Repo, Copy Files, Clean Up & Verify, Regenerate Lockfile).
2.  Generate and commit the updated `README.md` content (Step 4).
3.  Perform comprehensive Testing (Step 5), paying close attention to path adjustments in `mcp-projects.yaml`.
4.  Iteratively fix any issues discovered during testing.
5.  Finalize the repository structure, code, and documentation. 