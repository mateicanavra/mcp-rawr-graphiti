**Objective:** Refactor the `mcp_server` entity type management for improved modularity, auto-discovery, and reusability across projects. Also, establish a robust system for guiding AI agents via Cursor rules.

**Status: Phase 1 Complete, Phase 1 Cleanup Complete, Phase 2 Complete, Phase 2b Complete, Phase 2c Complete**

**1. Directory Structure & Registry Logic Implementation:**

*   **Goal:** Establish a clear separation between entity type definitions and the registry mechanism.
*   **Implementation:**
    *   The core registry logic (state and functions: `register_entity_type`, `get_entity_types`, `get_entity_type_subset`) resides in `mcp_server/entity_registry.py`.
    *   `mcp_server/entity_types/` serves as the main package directory for entity type *definitions*.
    *   `mcp_server/entity_types/__init__.py` makes the `entity_types` directory a Python package and re-exports the registry functions from `entity_registry.py`, allowing imports like `from mcp_server.entity_types import get_entity_types`.
    *   Specific sets of entity type definitions are organized into subdirectories, e.g., `mcp_server/entity_types/base/` and `mcp_server/entity_types/example/`.
    *   The auto-loader function (`load_entity_types_from_directory` in `graphiti_mcp_server.py`) dynamically imports `.py` files from specified directories (e.g., `entity_types/base` by default, or paths provided via `--entity-type-dir`), inspects them for valid Pydantic models with docstrings, and registers them using `register_entity_type` (which resolves to the function in `entity_registry.py`).
*   **Outcome:** The structure aligns with the initial plan, achieving the desired separation of concerns.

**2. Phase 1 Cleanup: COMPLETED ✓**

The following refinements have been implemented for enhanced clarity and adherence to the principle of least redundancy:

*   **Redundant Sub-Package Initializers:** Verified that `mcp_server/entity_types/base/__init__.py` and `mcp_server/entity_types/example/__init__.py` do not exist in the codebase, so no action was needed.
*   **Redundant Explicit Imports:** Successfully removed the following line from `mcp_server/graphiti_mcp_server.py`:
    ```python
    from mcp_server.entity_types.base import requirements, preferences, procedures
    ```
    This import was not functionally required for runtime registration because the auto-loader handles the discovery and registration of these types from the `entity_types/base` directory. Removing it reinforces reliance on the dynamic loading mechanism and simplifies the top-level namespace.

**3. Phase 2 - `graphiti` Dev Symlinking Script: COMPLETED ✓**

*   **Objective:** Create a globally executable shell script (`graphiti`) to facilitate the reuse of entity type definitions and the Docker Compose configuration in other projects by creating symlinks for **development purposes**.
*   **Implementation:**
    *   **Script Creation:** Created the `graphiti` shell script in `mcp_server/scripts/` directory.
    *   **Command:** Implemented the `link-dev-files [DIR]` command (and made it the default if no command is given).
    *   **Environment Variable:** The script uses the `MCP_GRAPHITI_REPO_PATH` environment variable.
    *   **Target Directory:** Accepts an optional target directory, defaulting to the current directory.
    *   **Symlink Creation:** Creates symbolic links for `entity_types` and `docker-compose.yml`.
    *   **Error Handling & Docs:** Added checks and documentation.
    *   **Testing:** Tested successfully.
*   **Outcome:** The `link-dev-files` command works as expected for setting up development environments.

**4. Phase 2b - `graphiti` Cursor Rules Setup & AI Guidance Framework: COMPLETED ✓**

*   **Objective:** Define a structured system for guiding AI agents using Cursor rules and enhance the `graphiti` script to automate the setup of these rules in target projects.
*   **Implementation:**
    *   **Rule Definition:** Designed a three-tier rule system:
        *   `graphiti-mcp-core-rules.md`: General tool usage and principles.
        *   `graphiti-knowledge-graph-maintenance.md`: Process for updating project schemas.
        *   `graphiti-[project-name]-schema.mdc`: Project-specific entities, relationships, and rules (template generated).
    *   **Rule Content:** Created and refined the content for the core and maintenance rules, including background/references. Created an example project schema (`graphiti-example-schema.md`).
    *   **File Organization:** Moved rules (`.md`) and the schema template (`.md`) into a structured `mcp_server/rules/` directory (with `templates/` and `examples/` subdirs).
    *   **`graphiti` Script Enhancement:** Added the `setup-rules PROJECT_NAME [DIR]` command to:
        *   Create `.cursor/rules/graphiti` in the target directory.
        *   Symlink the core and maintenance `.md` rules as `.mdc` files.
        *   Generate the project-specific schema `.mdc` file from the `.md` template, substituting the project name.
    *   **Testing:** Manual verification of file structure and script logic.
*   **Outcome:** A well-defined AI guidance system is in place, and the `graphiti setup-rules` command automates its deployment into user projects.

**4c. Phase 2c - `graphiti` Script Testing & Bug Fixes: COMPLETED ✓**

*   **Objective:** Test the new `graphiti init` command and ensure it correctly performs both file linking and rule setup functions.
*   **Implementation:**
    *   **Issue Identification:** During testing, discovered that the helper functions (`_link_dev_files` and `_setup_rules`) were defined after they were called in the script, causing a "command not found" error.
    *   **Bug Fix:** Moved the function definitions to earlier in the script, before the command parsing logic, following the principle that in Bash functions must be defined before they're called.
    *   **Testing Methodology:** 
        *   Created a test directory on the desktop (`~/Desktop/graphiti_test`)
        *   Set the required environment variable (`MCP_GRAPHITI_REPO_PATH`)
        *   Ran the `graphiti init test-project .` command
        *   Verified correct creation of symlinks and rule files
        *   Validated proper substitution of project name in schema template
    *   **Cleanup:** Removed test directory after successful validation
*   **Outcome:** The `graphiti init` command now works correctly, properly orchestrating both the `link-dev-files` and `setup-rules` functionality in a single command for streamlined project setup.

**5. Plan for Testing Auto-Loading via Docker Compose (Phase 3 - NEXT):**

*   **Objective:** Verify that the `--entity-type-dir` argument correctly limits the auto-loading scope when running services via Docker Compose.
*   **Prerequisites:** Phase 1 Cleanup complete.
*   **Implementation Steps:**
    *   Modify the `command` section of services in `mcp_server/docker-compose.yml`.
    *   **Test Case 1 (Base Only):** For one service (e.g., `graphiti-magic-api`), ensure the command includes `--use-custom-entities` but *only* specifies the base directory: `"--entity-type-dir", "mcp_server/entity_types/base"`.
    *   **Test Case 2 (Example Only):** For another service (e.g., `graphiti-civ7`), modify the command to load *only* the example types: `"--entity-type-dir", "mcp_server/entity_types/example"`.
    *   **Test Case 3 (Specific Subset via CLI - Optional):** Explore using the `--entity-types` argument.
    *   **Execution:** Run `docker compose down && docker compose up --build --force-recreate`.
    *   **Verification:** Examine service logs (`docker compose logs <service_name>`) to confirm correct entity types are loaded per service based on the `--entity-type-dir` argument.

**Next Steps:**

1.  **Testing `graphiti setup-rules`:** Perform a functional test of the new `graphiti setup-rules` command in a clean temporary directory to ensure it creates the correct structure, links, and files. **COMPLETED ✓**
2.  **Implement Phase 3:** Modify `docker-compose.yml` and perform auto-loading testing as outlined above.
