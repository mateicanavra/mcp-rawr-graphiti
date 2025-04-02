# Installation and Verification Guide for INSTALL Agent

This guide provides step-by-step instructions to set up and verify the Graphiti MCP Server repository. Execute each step sequentially and verify success as indicated.

## Phase 1: Understanding & Contextualization

1. **Analyze Documentation:** Read the primary `README.md` file located at the repository root.
   * **Action:** (Internal Analysis - No command needed from INSTALL Agent for reading)
   * **Verification:** None required for this internal step.

2. **Generate Summary:** Based on the documentation, formulate a 2-3 sentence summary of the project's purpose.
   * **Action:** (Internal Analysis & Generation)
   * **Output Example:** "The Graphiti MCP Server is a system that allows AI agents to interact with a knowledge graph for persistent memory, entity extraction, and relationship tracking using the Graphiti framework. It exposes Graphiti functionality via the Model Context Protocol (MCP) with SSE or Stdio transport options and provides a CLI tool for project initialization, entity management, and Docker environment control."
   * **Verification:** Ensure a summary is generated.

## Phase 2: Prerequisite Identification, Verification & Setup

3. **Check Git:** Verify if `git` is installed.
   * **Action:**
     ```bash
     git --version
     ```
   * **Verification:** Check if the command executes successfully (exit code 0) and outputs a version string. Report failure otherwise.

4. **Check Python 3.10+:** Verify if Python 3 is installed and the version is 3.10 or higher.
   * **Action:**
     ```bash
     python3 --version
     ```
   * **Verification:** Check exit code 0. Parse the output (e.g., `Python 3.11.4`) and confirm the version meets the requirement (≥ 3.10). Report failure otherwise.

5. **Check Docker:** Verify if Docker is installed and running.
   * **Action:**
     ```bash
     docker --version && docker info
     ```
   * **Verification:** Check if both commands execute successfully (exit code 0). The first command should output a version string, and the second should show Docker system information. If either fails, report failure.

6. **Check Docker Compose:** Verify if Docker Compose is installed.
   * **Action:**
     ```bash
     docker compose version
     ```
   * **Verification:** Check if the command executes successfully (exit code 0) and outputs a version string. Report failure otherwise.

7. **Install UV Tool:** Install the UV package manager if not already installed.
   * **First, check if UV is installed:**
     ```bash
     uv --version || echo "UV not installed"
     ```
   * **Install UV if needed:** (Installation method depends on platform)
     ```bash
     # If UV is not installed, use pip to install it
     if ! command -v uv &> /dev/null; then
       pip install uv
     fi
     ```
   * **Verification:** Check if uv is now available
     ```bash
     uv --version
     ```
   * **Verification:** Check exit code 0 and that a version string is output. Report failure otherwise.

8. **Clone Repository:** Clone the project repository (replace with actual repository URL).
   * **Action:**
     ```bash
     git clone https://github.com/your-org/rawr-mcp-graphiti.git
     ```
   * **Verification:** Check exit code 0. Verify that a directory named `rawr-mcp-graphiti` now exists.
     ```bash
     ls -la rawr-mcp-graphiti
     ```
   * **Report failure if directory doesn't exist or is empty.**

9. **Navigate to Repository:** Change to the repository directory.
   * **Action:**
     ```bash
     cd rawr-mcp-graphiti
     ```
   * **Verification:** Confirm current directory is the repository root.
     ```bash
     pwd | grep -q "rawr-mcp-graphiti$" && echo "Successfully changed to repository directory" || echo "Failed to change directory"
     ```

## Phase 3: Core Repository Installation & Configuration

10. **Configure Environment:** Create and configure the environment file.
    * **Action:**
      ```bash
      cp .env.example .env
      ```
    * **Verification:** Check that the .env file exists
      ```bash
      [ -f .env ] && echo ".env file created successfully" || echo "Failed to create .env file"
      ```
    * **Note to INSTALL Agent:** The `.env` file contains sensitive configuration values that need to be manually set by the user. For testing purposes, the default values in `.env.example` can be used, but in production, the user should be prompted to update:
      * `NEO4J_PASSWORD` (required - strong password for Neo4j database)
      * `OPENAI_API_KEY` (required if using OpenAI services)
      * Other optional settings as needed

11. **Create Virtual Environment:** Set up a Python virtual environment for development.
    * **Action:**
      ```bash
      python3 -m venv .venv
      ```
    * **Verification:** Check that the .venv directory exists
      ```bash
      [ -d .venv ] && echo "Virtual environment created successfully" || echo "Failed to create virtual environment"
      ```

12. **Activate Virtual Environment:** Activate the Python virtual environment.
    * **Action:**
      ```bash
      source .venv/bin/activate
      ```
    * **Verification:** Check that the virtual environment is active
      ```bash
      echo $VIRTUAL_ENV | grep -q ".venv$" && echo "Virtual environment activated successfully" || echo "Failed to activate virtual environment"
      ```

13. **Install Dependencies:** Use UV to install dependencies from the lock file.
    * **Action:**
      ```bash
      uv pip sync uv.lock
      ```
    * **Verification:** Check exit code 0. If the command fails, report the error.
      ```bash
      echo $? | grep -q "0" && echo "Dependencies installed successfully" || echo "Failed to install dependencies"
      ```

14. **Install CLI in Editable Mode:** Install the package in editable mode for development.
    * **Action:**
      ```bash
      pip install -e .
      ```
    * **Verification:** Check exit code 0. Verify the CLI is installed and accessible.
      ```bash
      which graphiti && echo "CLI installed successfully" || echo "Failed to install CLI"
      ```

## Phase 4: Example/Template Initialization

15. **Note on Project Initialization:** 
    * The Graphiti CLI includes a `graphiti init` command to create new projects, but this is typically a user-specific workflow. 
    * This step is optional for basic system verification and would be performed after Phase 5 verification confirms the core system is working.
    * Example usage (not required for basic installation verification):
      ```bash
      # Navigate to directory where you want to create a project
      # cd /path/to/projects
      # graphiti init my-new-ai-project
      ```

## Phase 5: Build, Test & Verification

16. **Verify Setup:** Run the check-setup command to verify the installation and environment.
    * **Action:**
      ```bash
      graphiti check-setup
      ```
    * **Verification:** Check exit code 0. The output should indicate that all checks passed. If any check fails, report the specific failure.

17. **Generate Docker Compose Configuration:** Generate the Docker Compose configuration file.
    * **Action:**
      ```bash
      graphiti compose
      ```
    * **Verification:** Check exit code 0. Verify that the docker-compose.yml file was created.
      ```bash
      [ -f docker-compose.yml ] && echo "Docker Compose file generated successfully" || echo "Failed to generate Docker Compose file"
      ```

18. **Start Services:** Start the Docker services in detached mode.
    * **Action:**
      ```bash
      graphiti up -d
      ```
    * **Verification:** Check exit code 0. Verify that containers are running.
      ```bash
      docker ps | grep -q "graphiti-mcp-root" && echo "Services started successfully" || echo "Failed to start services"
      ```

19. **Check Neo4j Status:** Verify Neo4j database is running.
    * **Action:**
      ```bash
      docker ps | grep -q "neo4j" && echo "Neo4j is running" || echo "Neo4j is not running"
      ```
    * **Verification:** The output should indicate that Neo4j is running.

20. **Check MCP Server Logs:** Check logs for the main MCP server to verify it's functioning correctly.
    * **Action:**
      ```bash
      docker logs $(docker ps -q --filter name=graphiti-mcp-root) 2>&1 | grep -q "Starting server" && echo "MCP server started successfully" || echo "MCP server may not have started properly"
      ```
    * **Verification:** The output should indicate that the MCP server started successfully.

21. **Stop Services:** Stop all Docker services to clean up.
    * **Action:**
      ```bash
      graphiti down
      ```
    * **Verification:** Check exit code 0. Verify that containers are stopped.
      ```bash
      docker ps | grep -q "graphiti-mcp" || echo "Services stopped successfully"
      ```

## Final Verification Report

Based on the results of the above steps, the INSTALL Agent should generate a final installation status report indicating:

1. Whether the installation was successful
2. Summary of project generated in Phase 1
3. Any failed steps and their error messages
4. Successful verification of core functionality

---

Note: This guide assumes a Linux/Unix-like environment (including macOS). For Windows environments, some commands (particularly activation of the virtual environment and path syntax) would need to be adjusted. 