# Installation and Verification Guide for INSTALL Agent: rawr-mcp-graphiti

This guide provides step-by-step instructions for an automated agent to clone, set up prerequisites, install the `graphiti` CLI using the recommended `pipx` method, configure the environment, and verify the basic functionality of the Graphiti MCP Server stack using Docker.

**Assumptions:**
*   The agent operates in a Unix-like shell environment (e.g., Bash, Zsh) with standard utilities (`uname`, `curl`, `grep`, `which`, etc.).
*   The agent will attempt to detect the primary package manager (`apt`, `brew`). If detection fails, it will default to using `apt` commands, assuming a Debian/Ubuntu-based Linux system.
*   The agent has permissions to install packages (potentially using `sudo` for `apt`/`yum`) and run Docker commands. `brew` typically does not require `sudo`.
*   The agent can store and retrieve the absolute path to the cloned repository, referred to as `<CLONED_REPO_PATH>`.
*   The agent cannot provide secret values; manual intervention or an external mechanism is required to populate the `.env` file after it's created.

Execute each step sequentially and verify success as indicated. Report failure if any verification step does not pass.

## Phase 1: Understanding & Contextualization

1.  **Analyze Documentation:** (Internal Agent Task) Read the primary `README.md` file provided in the repository context. Focus on understanding the project's purpose, features, and general architecture.
    *   **Action:** (Internal Analysis - No command execution)
    *   **Verification:** None required for this internal step.
2.  **Generate Summary:** (Internal Agent Task) Based *only* on the `README.md`, formulate a concise 2-3 sentence summary of the project's purpose.
    *   **Action:** (Internal Analysis & Generation)
    *   **Output:** Store the generated summary for final reporting.
    *   **Verification:** Ensure a non-empty summary string is generated.

## Phase 2: Prerequisite Identification, Verification & Setup

3.  **Detect Operating System and Package Manager:** Determine the OS and identify the available system package manager. Store the primary package manager found (e.g., 'apt', 'brew', 'unknown').
    *   **Action:**
        ```bash
        OS_TYPE=$(uname)
        PKG_MANAGER="unknown"
        if [ "$OS_TYPE" = "Linux" ]; then
            if command -v apt-get &> /dev/null; then
                PKG_MANAGER="apt"
            elif command -v yum &> /dev/null; then
                # Add yum support if needed, though apt is more common
                PKG_MANAGER="yum" # Placeholder, commands below focus on apt/brew
                echo "Detected yum (support might be limited in this script)"
            fi
        elif [ "$OS_TYPE" = "Darwin" ]; then
            if command -v brew &> /dev/null; then
                PKG_MANAGER="brew"
            fi
        fi
        echo "Detected OS: $OS_TYPE"
        echo "Detected Package Manager: $PKG_MANAGER"
        # Store $PKG_MANAGER for subsequent steps
        ```
    *   **Verification:** Check the exit code is 0. Note the detected OS and Package Manager (`$PKG_MANAGER`) for conditional execution in subsequent steps. If `PKG_MANAGER` is "unknown", installation steps might need to rely on manual instructions or alternative methods (like `curl` for `uv`).

4.  **Check Git:** Verify if `git` is installed.
    *   **Action:**
        ```bash
        git --version
        ```
    *   **Verification:** Check exit code 0 and version output. Report failure otherwise.
5.  **Install Git (if needed):** If `git --version` failed, install `git` using the detected package manager.
    *   **Action (Conditional):** *Only if Step 4 failed. Execute the command corresponding to the detected `$PKG_MANAGER`.*
        *   If `$PKG_MANAGER` == "apt":
            ```bash
            sudo apt-get update && sudo apt-get install -y git
            ```
        *   If `$PKG_MANAGER` == "brew":
            ```bash
            brew install git
            ```
        *   If `$PKG_MANAGER` == "unknown" or other:
            ```bash
            echo "Package manager not detected or unsupported. Please install Git manually following instructions for your OS."
            # Agent should report failure here as it cannot proceed automatically.
            exit 1
            ```
    *   **Verification:** After running the relevant command (if executed), re-run `git --version`. Check exit code 0 and version output. Report failure otherwise.

6.  **Check Python 3.10+:** Verify if `python3` is installed and the version is 3.10 or higher.
    *   **Action:**
        ```bash
        python3 --version
        ```
    *   **Verification:** Check exit code 0. Parse the output (e.g., `Python 3.11.5`) and confirm the major version is 3 and the minor version is 10 or greater. Report failure otherwise.
7.  **Install Python 3 & Pip (if needed):** If `python3 --version` failed or the version is too low, install a compatible version and `pip`.
    *   **Action (Conditional):** *Only if Step 6 failed. Execute the command corresponding to the detected `$PKG_MANAGER`.*
        *   If `$PKG_MANAGER` == "apt":
            ```bash
            # Installs default python3; may need adjustment for specific versions
            sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
            ```
        *   If `$PKG_MANAGER` == "brew":
            ```bash
            # Brew typically installs a recent version. Ensure it meets 3.10+
            brew install python3
            ```
        *   If `$PKG_MANAGER` == "unknown" or other:
            ```bash
            echo "Package manager not detected or unsupported. Please install Python 3.10+ and pip manually following instructions for your OS."
            # Agent should report failure here.
            exit 1
            ```
    *   **Verification:** After running the command (if executed), re-run `python3 --version`. Check exit code 0 and version requirement. Run `pip3 --version` and check exit code 0. Report failure otherwise.

8.  **Check `uv`:** Verify if `uv` is installed.
    *   **Action:**
        ```bash
        uv --version
        ```
    *   **Verification:** Check exit code 0 and version output. Report failure otherwise.
9.  **Install `uv` (if needed):** If `uv --version` failed, install `uv`. Prioritize `pip`, fallback to `curl`.
    *   **Action (Conditional):** *Only if Step 8 failed:*
        ```bash
        # Try pip first
        pip3 install uv || {
          echo "pip3 install uv failed, attempting curl method...";
          curl -LsSf https://astral.sh/uv/install.sh | sh && \
          # Attempt to source environment variables for the current session if curl was used
          # This is best-effort; a new shell might be needed for PATH changes to take effect
          if [ -f "$HOME/.cargo/env" ]; then source "$HOME/.cargo/env"; \
          elif [ -f "$HOME/.profile" ]; then source "$HOME/.profile"; \
          elif [ -f "$HOME/.bash_profile" ]; then source "$HOME/.bash_profile"; \
          elif [ -f "$HOME/.bashrc" ]; then source "$HOME/.bashrc"; \
          elif [ -f "$HOME/.zshrc" ]; then source "$HOME/.zshrc"; fi
        }
        ```
    *   **Verification:** After running the command (if executed), re-run `uv --version`. Check exit code 0 and version output. Report failure otherwise. (Note: If `curl` method was used, the command might still fail in the *same* session if the PATH was not successfully updated by the sourcing attempt.)

10. **Check `pipx`:** Verify if `pipx` is installed.
    *   **Action:**
        ```bash
        pipx --version
        ```
    *   **Verification:** Check exit code 0 and version output. Report failure otherwise.
11. **Install `pipx` (if needed):** If `pipx --version` failed, install `pipx` using `pip` and ensure its path is configured.
    *   **Action (Conditional):** *Only if Step 10 failed:*
        ```bash
        python3 -m pip install --user pipx
        python3 -m pipx ensurepath
        ```
    *   **Verification:** Check exit code 0 for both commands. Inform that the PATH might need updating in the current session (e.g., `source ~/.bashrc` or similar). Subsequent `pipx` commands assume `ensurepath` worked for future sessions or the agent updates its PATH. Report failure if install commands had non-zero exit codes.

12. **Check Docker:** Verify if the `docker` command is available.
    *   **Action:**
        ```bash
        docker --version
        ```
    *   **Verification:** Check exit code 0 and version output. Report failure otherwise.
13. **Check Docker Compose:** Verify if `docker compose` (v2+) command is available.
    *   **Action:**
        ```bash
        docker compose version
        ```
    *   **Verification:** Check exit code 0 and version output. Report failure otherwise.
14. **Check Docker Daemon:** Verify if the Docker daemon is running and responsive.
    *   **Action:**
        ```bash
        docker info
        ```
    *   **Verification:** Check exit code 0. Look for "Server Version:" or similar indicators of success in the output. Report failure otherwise. (Note: Docker installation itself is assumed to be handled externally as per README).

15. **Confirm Repository Clone Location:** Ask the user where they want to clone the repository.
    *   **Action:** Interact with the user by asking:
        ```
        Please specify the directory where you'd like to clone the 'rawr-mcp-graphiti' repository.
        Press Enter to use the current directory ($(pwd)) as the parent directory.
        ```
    *   **Verification:** Wait for user input. If empty, use the current directory as the parent. If a path is provided, verify it exists and is writable. Store the chosen parent directory path as `<PARENT_DIR>`.

16. **Clone Repository:** Clone the project repository into the specified location.
    *   **Action:**
        ```bash
        # Replace <repository-url> with the actual Git repository URL
        git clone <repository-url> <PARENT_DIR>/rawr-mcp-graphiti
        ```
    *   **Verification:** Check exit code 0. Verify that a directory named `rawr-mcp-graphiti` now exists in the chosen parent directory. Determine and store its absolute path `<CLONED_REPO_PATH>`. Report failure otherwise.

## Phase 3: Core Repository Installation & Configuration (pipx method)

17. **Navigate to Repo Directory:** Change the current directory to the cloned repository root.
    *   **Action:**
        ```bash
        cd <CLONED_REPO_PATH>
        ```
    *   **Verification:** Run `pwd` and confirm the current path matches `<CLONED_REPO_PATH>`.
18. **Create `.env` File:** Copy the example environment file.
    *   **Action:**
        ```bash
        cp .env.example .env
        ```
    *   **Verification:** Check exit code 0. Verify that the file `.env` exists in the current directory (`<CLONED_REPO_PATH>`).
19. **Report `.env` Requirement:** Inform the user or controlling process that the `.env` file (`<CLONED_REPO_PATH>/.env`) needs to be populated with necessary secrets (e.g., `NEO4J_PASSWORD`, `OPENAI_API_KEY`) before proceeding with steps that rely on them (like `graphiti up`).
    *   **Action:** (Reporting - No command execution)
    *   **Verification:** Ensure the report/notification is issued.
20. **Install CLI with `pipx`:** Install the `graphiti` CLI tool from the local repository source using `pipx`.
    *   **Action:**
        ```bash
        # Ensure current directory is <CLONED_REPO_PATH>
        pipx install . --include-deps
        ```
    *   **Verification:** Check exit code 0.
21. **Configure CLI Repository Path (First Run):** Run a CLI command that triggers the path detection. The CLI should now automatically save the path to `~/.config/graphiti/repo_path.txt` if found or prompted for.
    *   **Action:** Execute `graphiti check-setup`.
        *   *If the command output contains a prompt asking for the repository path:* Provide the stored `<CLONED_REPO_PATH>` value as input.
        *   *If the command completes without prompting:* Proceed to verification.
    *   **Command:**
        ```bash
        graphiti check-setup
        ```
    *   **Verification:** Check the command exit code (should be 0 if the path was found, configured, or successfully entered). Check the output for success messages related to finding the repo path. Verify that the config file `~/.config/graphiti/repo_path.txt` now exists and contains the correct `<CLONED_REPO_PATH>`. Report failure if the command exits non-zero or the prompt interaction fails.
22. **Verify CLI Installation:** Check that the `graphiti` command is available in the PATH (via pipx) and responds. Run this check from outside the repo directory to ensure the path configuration works.
    *   **Action:**
        ```bash
        cd ~ # Change to home directory (or any directory outside the repo)
        which graphiti
        graphiti --help
        graphiti check-setup # Run again from outside
        ```
    *   **Verification:**
        *   `which graphiti`: Check exit code 0 and ensure the output path contains `.local/bin/graphiti`.
        *   `graphiti --help`: Check exit code 0 and verify help text is displayed.
        *   `graphiti check-setup`: Check exit code 0 and verify output indicates success (finding repo root via config file, finding `.env`, Docker running).
        *   Report failure otherwise.

## Phase 4: Example/Template Initialization (If Applicable)

*   (Skipped) The core setup involves installing the CLI and server environment. Project initialization (`graphiti init`) is part of the user workflow *after* this setup is complete and verified.

## Phase 5: Build, Test & Verification

23. **Navigate to Repo Directory:** Ensure the current directory is the repository root.
    *   **Action:**
        ```bash
        cd <CLONED_REPO_PATH>
        ```
    *   **Verification:** Run `pwd` and confirm the current path matches `<CLONED_REPO_PATH>`.
24. **Generate Docker Compose Configuration:** Run the `graphiti compose` command to generate the `docker-compose.yml` file.
    *   **Action:**
        ```bash
        graphiti compose
        ```
    *   **Verification:** Check exit code 0. Verify that the file `docker-compose.yml` exists in the current directory (`<CLONED_REPO_PATH>`). Check command output for success messages and port assignments. Report failure otherwise.
25. **Start Docker Services:** Start the Neo4j and MCP server containers in detached mode. **Requires `.env` to be correctly populated.**
    *   **Action:**
        ```bash
        graphiti up -d
        ```
    *   **Verification:** Check exit code 0. Wait for a reasonable time (e.g., 30-90 seconds) for containers to initialize and become healthy. Report failure if the command fails immediately or if subsequent checks fail due to startup issues (potentially related to incorrect `.env` values).
26. **Verify Running Containers:** List running Docker containers and check for the expected services.
    *   **Action:**
        ```bash
        docker ps
        ```
    *   **Verification:** Check exit code 0. Parse the output to confirm that containers related to `neo4j` (e.g., `graphiti-mcp-neo4j`) and the root MCP server (e.g., `graphiti-mcp-root`) are listed and have a status indicating they are running and healthy (e.g., "Up X seconds (healthy)"). Report failure otherwise.
27. **Verify Neo4j Health:** Check if the Neo4j browser UI is accessible (assumes default port 7474).
    *   **Action:**
        ```bash
        curl -s -I --max-time 10 http://localhost:7474
        ```
    *   **Verification:** Check exit code 0. Verify that the output includes `HTTP/1.1 200 OK`. Report failure otherwise.
28. **Verify Root MCP Server Health:** Check the status endpoint of the root MCP server (assumes default port 8000).
    *   **Action:**
        ```bash
        curl -s --max-time 10 http://localhost:8000/http://graphiti/status
        ```
    *   **Verification:** Check exit code 0. Verify that the output is valid JSON and contains `"status": "ok"`. Report failure otherwise.
29. **Final Setup Verification:** Run `graphiti check-setup` again from the repository root to perform the CLI's internal checks while services are running.
    *   **Action:**
        ```bash
        # Ensure current directory is <CLONED_REPO_PATH>
        graphiti check-setup
        ```
    *   **Verification:** Check exit code 0. Verify the output confirms checks for Repo Root, `.env` File, and Docker Status passed. Report failure otherwise.
30. **Stop Docker Services:** Stop and remove the containers after successful verification.
    *   **Action:**
        ```bash
        graphiti down
        ```
    *   **Verification:** Check exit code 0. Run `docker ps` again and verify that the `neo4j` and `graphiti-mcp-root` containers are no longer listed. Report failure otherwise.

**Conclusion:** If all steps and verifications completed successfully, the `rawr-mcp-graphiti` CLI and its associated Docker environment are installed and verified. The system is ready for use (e.g., running `graphiti init`, `graphiti up` again for actual work, after ensuring `.env` is correctly populated).