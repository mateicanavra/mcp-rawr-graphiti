# Installation &amp; Usage Specification: RAWR Graphiti MCP Server

## Section 1: Metadata &amp; Overview

-   **ProjectName**: rawr-mcp-graphiti
-   **PrimaryLanguage**: Python
-   **PrimaryFramework**: None (Uses Typer for CLI, relies on `graphiti-core` and `mcp` libraries)
-   **RepositoryURL**: (Assumed to be the current repository)
-   **BriefDescription**: Provides a Graphiti MCP Server and CLI tool for AI agent interaction with a knowledge graph, using Neo4j for storage and Docker for deployment.
-   **SpecificationVersion**: 1.1
-   **GeneratedTimestamp**: 2025-04-04T19:13:00Z
-   **AssumedEnvironment**: Linux/macOS with Python 3.10+, Docker, Git, and `uv`.

## Section 2: Prerequisite Identification, Verification &amp; Setup

1.  **Task**: Check Git installed
    *   **Command**: `git --version`
    *   **Verification**: Expect exit code 0. Output should match regex `^git version \d+\.\d+.*`.

2.  **Task**: Check Python version >= 3.10
    *   **Command**: `python3 --version`
    *   **Verification**: Expect exit code 0. Output should match regex `^Python 3\.(10|1[1-9]|\d{2,})\.\d+`.

3.  **Task**: Check Docker installed and running
    *   **Command**: `docker info`
    *   **Verification**: Expect exit code 0. Output should contain "Docker Root Dir:" and "Server Version:". If it fails, ensure Docker Desktop or Docker Engine service is installed and running.

4.  **Task**: Check `uv` installed
    *   **Command**: `uv --version`
    *   **Verification**: Expect exit code 0. Output should match regex `^uv \d+\.\d+\.\d+.*`.

5.  **Task**: Install `uv` (if needed)
    *   **Condition**: Only if `uv --version` fails (non-zero exit code).
    *   **Option 1 (Requires pip)**:
        *   **Command**: `pip install uv`
        *   **Verification**: Run `uv --version`, expect exit code 0.
    *   **Option 2 (Using curl)**:
        *   **Command**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
        *   **Post-Install**: Follow instructions from the script to add `uv` to PATH (e.g., `source $HOME/.cargo/env` or similar).
        *   **Verification**: Close and reopen terminal or source profile, then run `uv --version`, expect exit code 0.

6.  **Task**: Clone Repository
    *   **Command**: `git clone <repository-url> rawr-mcp-graphiti` (Replace `<repository-url>` with the actual URL)
    *   **Verification**: Expect exit code 0. Directory `rawr-mcp-graphiti` must exist.

## Section 3: Core Installation &amp; Configuration

*(Choose **one** of the following methods based on your needs)*

### Method 1: Standard User Installation (using `pipx`)

*This is the recommended method for using the `graphiti` CLI without modifying its code.*

7.  **Task**: Check/Install `pipx`
    *   **Command (Check)**: `pipx --version`
    *   **Verification (Check)**: Expect exit code 0.
    *   **Command (Install if needed)**: `python3 -m pip install --user pipx &amp;&amp; python3 -m pipx ensurepath`
    *   **Post-Install**: Close and reopen terminal or source shell profile (`~/.bashrc`, `~/.zshrc`, etc.).
    *   **Verification (Install)**: Run `pipx --version`, expect exit code 0.

8.  **Task**: Navigate to Cloned Repository Directory
    *   **Command**: `cd rawr-mcp-graphiti`
    *   **Verification**: `pwd` output must end with `/rawr-mcp-graphiti`.

9.  **Task**: Create Environment Configuration File
    *   **Command**: `cp .env.example .env`
    *   **Verification**: File `.env` must exist in the current directory.

10. **Task**: Configure Environment Variables
    *   **Action**: Manually edit the `.env` file.
    *   **Details**: Fill in required values for `NEO4J_USER`, `NEO4J_PASSWORD`, and `OPENAI_API_KEY`. Review other variables (ports, model name, etc.) and adjust if necessary.
    *   **Verification**: Run `grep -q "your_strong_neo4j_password_here" .env`. Expect exit code 1 (meaning the placeholder is gone). Run `grep -q "your_openai_api_key_here" .env`. Expect exit code 1.

11. **Task**: Install CLI using `pipx`
    *   **Context**: Ensure you are in the repository root directory (`rawr-mcp-graphiti`).
    *   **Command**: `pipx install . --include-deps`
    *   **Verification**: Run `which graphiti`. Output should point to a path within the `~/.local/pipx/venvs/` directory. Run `graphiti --help`, expect exit code 0 and help message display.

12. **Task**: Configure CLI Repository Path (First Run)
    *   **Action**: Run a CLI command that requires repository access from *any* directory.
    *   **Command**: `graphiti check-setup`
    *   **Behavior**: If the CLI cannot find the repository, it will prompt interactively for the absolute path to the cloned `rawr-mcp-graphiti` directory.
    *   **Input**: Provide the correct absolute path when prompted (e.g., `/path/to/your/rawr-mcp-graphiti`).
    *   **Verification**: The command should complete successfully after configuration. The path should be saved in `~/.config/graphiti/repo_path.txt`. Subsequent runs of `graphiti check-setup` from any directory should succeed without prompting.

### Method 2: Local Development Installation (using `venv`)

*Use this method only if you plan to modify the `graphiti` CLI or server code.*

7.  **Task**: Navigate to Cloned Repository Directory
    *   **Command**: `cd rawr-mcp-graphiti`
    *   **Verification**: `pwd` output must end with `/rawr-mcp-graphiti`.

8.  **Task**: Create Environment Configuration File
    *   **Command**: `cp .env.example .env`
    *   **Verification**: File `.env` must exist in the current directory.

9.  **Task**: Configure Environment Variables
    *   **Action**: Manually edit the `.env` file.
    *   **Details**: Fill in required values for `NEO4J_USER`, `NEO4J_PASSWORD`, and `OPENAI_API_KEY`. Review other variables.
    *   **Verification**: Run `grep -q "your_strong_neo4j_password_here" .env`. Expect exit code 1. Run `grep -q "your_openai_api_key_here" .env`. Expect exit code 1.

10. **Task**: Create Python Virtual Environment
    *   **Command**: `python3 -m venv .venv`
    *   **Verification**: Directory `.venv` must exist.

11. **Task**: Activate Virtual Environment
    *   **Command (Linux/macOS)**: `source .venv/bin/activate`
    *   **Command (Windows Git Bash)**: `source .venv/Scripts/activate`
    *   **Command (Windows CMD)**: `.venv\Scripts\activate.bat`
    *   **Command (Windows PowerShell)**: `.venv\Scripts\Activate.ps1` (Execution policy may need adjustment: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)
    *   **Verification**: Shell prompt should be prefixed with `(.venv)`. Run `which python` (Linux/macOS) or `where python` (Windows), output should point inside the `.venv` directory.

12. **Task**: Install Dependencies using `uv`
    *   **Context**: Ensure virtual environment is active.
    *   **Command**: `uv pip sync uv.lock`
    *   **Verification**: Expect exit code 0. Run `uv pip list | grep graphiti-core`. Expect output showing `graphiti-core` installed.

13. **Task**: Install CLI in Editable Mode
    *   **Context**: Ensure virtual environment is active.
    *   **Command**: `pip install -e .`
    *   **Verification**: Expect exit code 0. Run `which graphiti` (Linux/macOS) or `where graphiti` (Windows), output should point inside the `.venv` directory's bin/Scripts folder. Run `graphiti --help`, expect exit code 0.

## Section 4: Environment Verification

14. **Task**: Verify Full Setup
    *   **Context**:
        *   If using `pipx`: Run from *any* directory. Ensure repo path was configured (Step 12, Method 1).
        *   If using `venv`: Activate the venv (`source .venv/bin/activate`) and run from the *repository root* (`rawr-mcp-graphiti`).
    *   **Command**: `graphiti check-setup`
    *   **Verification**: Expect exit code 0. Output should indicate:
        *   Repository root found.
        *   `.env` file loaded and required variables (`NEO4J_USER`, `NEO4J_PASSWORD`, `OPENAI_API_KEY`) present.
        *   Docker command found and daemon responsive.

## Section 5: Running Services &amp; Basic Usage Verification

*These commands generally need to be run from the repository root (`rawr-mcp-graphiti`). If using `venv`, ensure it's activated.*

15. **Task**: Generate Docker Compose File
    *   **Context**: Run from repository root.
    *   **Command**: `graphiti compose`
    *   **Verification**: Expect exit code 0. File `docker-compose.yml` must be created or updated in the repository root. Check command output for assigned ports.

16. **Task**: Start Docker Services
    *   **Context**: Run from repository root.
    *   **Command**: `graphiti up -d`
    *   **Verification**: Expect exit code 0. Run `docker ps`. Output should list containers (e.g., `graphiti-mcp-root`, `neo4j`) with status "Up" or "healthy". Access Neo4j Browser at `http://localhost:7474` (using `.env` credentials). Access root MCP server health check endpoint (e.g., `curl -s http://localhost:8000/sse` should show event stream headers, or check health status via UI if available).

17. **Task**: Check Service Logs (Optional)
    *   **Context**: Run from repository root.
    *   **Command**: `graphiti logs` or `docker compose logs -f graphiti-mcp-root`
    *   **Verification**: Observe log output for errors or successful startup messages. Press Ctrl+C to stop following logs.

18. **Task**: Stop Docker Services
    *   **Context**: Run from repository root.
    *   **Command**: `graphiti down`
    *   **Verification**: Expect exit code 0. Run `docker ps`. The `graphiti-mcp-root` and `neo4j` containers should no longer be listed.

19. **Task**: Run Unit Tests (Developer Setup Only)
    *   **Context**: Run from repository root with `venv` activated.
    *   **Command (Install Dev Deps)**: `pip install -e ".[dev]"`
    *   **Verification (Install Dev Deps)**: Expect exit code 0.
    *   **Command (Run Tests)**: `pytest`
    *   **Verification (Run Tests)**: Expect exit code 0. Output should indicate tests passed (e.g., "... passed in ...s").

## Section 6: Key Codebase Pointers

-   **MainEntryPoint**:
    -   Server: `graphiti_mcp_server.py`
    -   CLI: `graphiti_cli/main.py`
-   **ConfigurationFiles**:
    -   Primary User Config: `.env` (copied from `.env.example`)
    -   Dependency/Project: `pyproject.toml`, `uv.lock`
    -   Docker Base: `base-compose.yaml`
    -   Generated Docker Config: `docker-compose.yml` (generated by `graphiti compose`)
    -   Project Registry: `mcp-projects.yaml` (managed by `graphiti init`)
    -   CLI Config: `~/.config/graphiti/repo_path.txt` (created on first run if needed)
-   **CoreModules**:
    -   CLI Logic: `graphiti_cli/`
    -   Entity Definitions: `entities/` (base definitions)
        - Project entities live under `ai/graph/entities/` in each project
        - `graphiti entity <set_name>` scaffolds strict Pydantic models
        - Example templates: [`project_assets/entity_templates`](../project_assets/entity_templates/)
        - Design guide: [`docs/entity-design-guidelines.md`](entity-design-guidelines.md)
-   **DataStorage**: Neo4j Database (data stored in Docker volume `neo4j_data`)
-   **Tests**: `tests/` (contains unit and functional tests)
-   **Docs**: `README.md`, `CONFIGURATION.md`, `docs/`

## Section 7: Getting Started / Next Steps

-   **RunApplication**: `cd /path/to/rawr-mcp-graphiti &amp;&amp; graphiti up -d`
-   **RunTests**: (Requires dev setup) Activate venv, `cd /path/to/rawr-mcp-graphiti`, `pip install -e ".[dev]"`, `pytest`
-   **KeyConfiguration**:
    -   Edit `.env` in the repository root for secrets (Neo4j, OpenAI) and core settings.
    -   Use `graphiti init <project_name>` to register a project and scaffold `ai/graph/` with a sample entity.
    -   Use `graphiti entity <set_name>` within a project directory to add more entity files automatically configured with `ConfigDict(extra="forbid")`.
-   **APIEndpoint**:
    -   Root MCP Server: `http://localhost:8000` (default, check `.env` or `graphiti compose` output)
    -   Neo4j Browser UI: `http://localhost:7474` (default)
-   **FurtherDocumentation**:
    -   `README.md` (Overview, detailed setup)
    -   `CONFIGURATION.md` (Deeper dive into configuration files)
    *   `graphiti --help` (CLI command reference)
    *   `tests/README.md` (Testing details)