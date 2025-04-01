Okay, here is the detailed, step-by-step implementation plan based on the "Central Generation with Project YAML Config (No Project `.env`)" architecture. This plan is designed for an expert implementation agent.

**Overall Goal:** Refactor the system to allow project repositories to define their custom MCP servers via a local YAML file, managed and run centrally from the `mcp-server` repository, ensuring only one `neo4j` and `graphiti-mcp-root` instance.

**Target Architecture Summary:** Central `mcp-server` repo runs `docker compose` using a generated `docker-compose.yml`. The generator reads a central `mcp-projects.yaml` registry (auto-managed by `graphiti init`) to find project-specific `mcp-config.yaml` files. These project configs define custom services, non-secret settings, and relative entity paths. The generator creates the final compose file, injecting project environment settings and volume mounts for project entities. `graphiti_mcp_server.py` loads both base and project-specific entities.

---

**Phase 1: Foundational Changes (Central Repo: `mcp-server`)**

**Step 1.1: Create Project Registry File** [COMPLETED]

*   **Objective:** Establish the central registry file.
*   **File:** `mcp-server/mcp-projects.yaml`
*   **Action:** Create this new file with the following initial content:
    ```yaml
    # !! WARNING: This file is managed by the 'graphiti init' command. !!
    # !! Avoid manual edits unless absolutely necessary.                 !!
    #
    # Maps project names to their configuration details.
    # Paths should be absolute for reliability.
    projects: {}
    # Example Entry (will be added by 'graphiti init'):
    # alpha:
    #   config_file: /abs/path/to/project-alpha/mcp-config.yaml
    #   root_dir: /abs/path/to/project-alpha
    #   enabled: true
    ```
*   **Acceptance Criteria:** The file `mcp-server/mcp-projects.yaml` exists with the specified structure and comments.

**Step 1.2: Enhance Generator (`generate_compose.py`) - Load Registry & Modify Loop** [COMPLETED]

*   **Objective:** Update the generator to read the new registry instead of `custom_servers.yaml`.
*   **File:** `mcp-server/generate_compose.py`
*   **Actions:**
    1.  Import `os` at the top.
    2.  Define `MCP_PROJECTS_FILE = 'mcp-projects.yaml'` near other constants (@LINE:13).
    3.  Remove the constant `CUSTOM_SERVERS_CONFIG_FILE = 'custom_servers.yaml'` (@LINE:12).
    4.  **Replace** the "Load Custom Server Configurations" block (approx. @LINE:42-@LINE:64):
        *   Load `MCP_PROJECTS_FILE` using `yaml.load()` (consider `YAML(typ='safe')` for this registry file).
        *   Handle `FileNotFoundError` (log warning, set `projects_registry = {'projects': {}}`).
        *   Handle parsing errors (log warning/error, exit or proceed cautiously).
    5.  **Replace** the outer loop structure in "Generate and Add Custom Service Definitions" (approx. @LINE:81):
        *   Remove the old loop `for n, server_conf in enumerate(custom_mcp_servers):`.
        *   Initialize an overall service index `overall_service_index = 0`.
        *   Start a new loop: `for project_name, project_data in projects_registry.get('projects', {}).items():`.
        *   Inside this loop, check `if not project_data.get('enabled', False): continue`.
        *   Load the project's config file: `project_config_path = project_data.get('config_file')`. Add error handling (file not found, parse error - log warning and skip project). Use `yaml.load()` (safe load).
        *   Start an inner loop: `for server_conf in project_config.get('services', []):`.
        *   Inside the inner loop, retrieve `server_id = server_conf.get('id')`. Add validation (skip service if no id).
        *   Increment `overall_service_index` at the end of the inner loop.
*   **Acceptance Criteria:**
    *   `generate_compose.py` attempts to load `mcp-projects.yaml`.
    *   The script iterates through enabled projects found in the registry.
    *   For each enabled project, it attempts to load the specified project configuration file.
    *   It then iterates through the `services` defined within that project configuration.
    *   The old `custom_servers.yaml` logic is removed.

**Step 1.3: Enhance Generator (`generate_compose.py`) - Resolve Paths & Add Volumes** [COMPLETED]

*   **Objective:** Calculate absolute entity paths and add volume mounts to service definitions.
*   **File:** `mcp-server/generate_compose.py`
*   **Actions:**
    1.  Define `CONTAINER_ENTITY_PATH = "/app/project_entities"` near constants (@LINE:13).
    2.  Inside the *inner* service loop (after getting `server_conf`):
        *   Get `relative_entity_dir = server_conf.get('entity_dir')`. Add validation (log warning/skip service if missing).
        *   Get `project_root_dir = project_data.get('root_dir')`. Add validation (log warning/skip project if missing).
        *   Calculate `abs_host_entity_path = os.path.abspath(os.path.join(project_root_dir, relative_entity_dir))`.
        *   Ensure the `new_service` map (created via `CommentedMap()`) has a `volumes` key initialized as an empty list if it doesn't exist.
        *   Append the volume string: `new_service.setdefault('volumes', []).append(f"{abs_host_entity_path}:{CONTAINER_ENTITY_PATH}:ro")`. (Using `:ro` for read-only mount is safer).
*   **Acceptance Criteria:**
    *   The generator calculates the absolute path on the host for the project's entity directory.
    *   A `volumes` section is added/appended to each generated custom service definition, mapping the host path to `/app/project_entities` (read-only).

**Step 1.4: Enhance Generator (`generate_compose.py`) - Update Environment Variables** [COMPLETED]

*   **Objective:** Set `MCP_ENTITY_TYPE_DIR` correctly and merge project-specific environment variables.
*   **File:** `mcp-server/generate_compose.py`
*   **Actions:**
    1.  Inside the inner service loop, locate the `env_vars = CommentedMap()` creation (@LINE:110).
    2.  Modify the setting of `MCP_ENTITY_TYPE_DIR` (@LINE:115): Set it directly to the container path: `env_vars['MCP_ENTITY_TYPE_DIR'] = CONTAINER_ENTITY_PATH`.
    3.  Remove the `if entity_types is not None:` block (@LINE:117-@LINE:121) if the `types` key in project config is no longer supported (confirm this - current `custom_servers.yaml` uses it @LINE:17). *If `types` is still needed*, ensure `MCP_ENTITY_TYPES` is added correctly to `env_vars`. **Plan Decision:** Let's assume `types` is deprecated for V1 simplicity; remove the block.
    4.  Get the project environment dictionary: `project_environment = server_conf.get('environment', {})`.
    5.  Merge `project_environment` into `env_vars`: `env_vars.update(project_environment)`. This ensures project-specific vars are added. *Note: `ruamel.yaml`'s `CommentedMap` update preserves order and comments if possible.*
*   **Acceptance Criteria:**
    *   The `MCP_ENTITY_TYPE_DIR` environment variable in generated services is set to `/app/project_entities`.
    *   Any key-value pairs defined under the `environment:` key in the project's `mcp-config.yaml` are added to the service's environment definition.
    *   The logic for the `types` key (and `MCP_ENTITY_TYPES` env var) is removed (or confirmed working if kept).

**Step 1.5: Enhance Generator (`generate_compose.py`) - Update Port/Container Name Logic** [COMPLETED]

*   **Objective:** Source ports and container names directly from project config or generator defaults.
*   **File:** `mcp-server/generate_compose.py`
*   **Actions:**
    1.  Inside the inner service loop, **remove** the lines defining `container_name_var` (@LINE:95) and `port_var` (@LINE:96).
    2.  **Replace** the `port_mapping` definition (@LINE:101):
        *   Get `port_default = server_conf.get('port_default')`.
        *   If `port_default is None`: `port_default = DEFAULT_PORT_START + overall_service_index + 1` (Use the index tracking overall services across all projects).
        *   Define `port_mapping = f"{port_default}:${{{DEFAULT_MCP_CONTAINER_PORT_VAR}}}"`.
        *   Ensure `new_service['ports'] = [port_mapping]` (@LINE:109) uses this new `port_mapping`.
    3.  **Replace** the `container_name` definition (@LINE:108):
        *   Get `container_name = server_conf.get('container_name')`.
        *   If `container_name is None`: `container_name = f"mcp-{server_id}"`.
        *   Set `new_service['container_name'] = container_name`.
*   **Acceptance Criteria:**
    *   The generator no longer looks for `*_PORT` or `*_CONTAINER_NAME` environment variables for custom services.
    *   Ports are assigned based on `port_default` in project config, or sequentially otherwise.
    *   Container names are assigned based on `container_name` in project config, or derived from the service `id` otherwise.

**Step 1.6: Enhance Generator (`generate_compose.py`) - Ensure Base Merge** [COMPLETED]

*   **Objective:** Verify that shared configurations are still inherited correctly.
*   **File:** `mcp-server/generate_compose.py`
*   **Actions:**
    1.  Confirm the line `new_service.add_yaml_merge([(0, custom_base_anchor_obj)])` (@LINE:126) is still present within the inner service loop and functions as expected.
*   **Acceptance Criteria:** Generated custom services in `docker-compose.yml` contain `<<: *graphiti-mcp-custom-base`.

**Step 1.7: Adapt Server Script (`graphiti_mcp_server.py`) - Entity Loading** [COMPLETED]

*   **Objective:** Enable loading of both base and project-specific entity types.
*   **File:** `mcp-server/graphiti_mcp_server.py`
*   **Actions:**
    1.  Inside the `initialize_server` function (after `args = parser.parse_args()` approx. @LINE:761):
    2.  Define the expected path for base types within the container: `container_base_entity_dir = "/app/entity_types/base"` (Ensure this matches Dockerfile copy destination).
    3.  Add logic to *always* load base types first:
        ```python
        if os.path.exists(container_base_entity_dir) and os.path.isdir(container_base_entity_dir):
            logger.info(f'Loading base entity types from: {container_base_entity_dir}')
            load_entity_types_from_directory(container_base_entity_dir)
        else:
            logger.warning(f"Base entity types directory not found at: {container_base_entity_dir}")
        ```
    4.  Add logic to load project-specific types if the directory is provided and different:
        ```python
        project_entity_dir = args.entity_type_dir # From --entity-type-dir arg
        if project_entity_dir:
             # Resolve paths to handle potential symlinks or relative paths inside container if needed
             abs_project_dir = os.path.abspath(project_entity_dir)
             abs_base_dir = os.path.abspath(container_base_entity_dir)
             if abs_project_dir != abs_base_dir:
                  if os.path.exists(abs_project_dir) and os.path.isdir(abs_project_dir):
                      logger.info(f'Loading project-specific entity types from: {abs_project_dir}')
                      load_entity_types_from_directory(abs_project_dir)
                  else:
                      logger.warning(f"Project entity types directory not found or not a directory: {abs_project_dir}")
             else:
                  logger.info(f"Project entity directory '{project_entity_dir}' is the same as base, skipping redundant load.")
        ```
    5.  Ensure `load_entity_types_from_directory` (@LINE:811) handles being called multiple times correctly (the current implementation using a global registry `@LINE:28` should be fine).
*   **Acceptance Criteria:**
    *   The server logs attempts to load base entities.
    *   If a custom service container has a volume mounted at `/app/project_entities` and `MCP_ENTITY_TYPE_DIR` set to that path, the server logs attempts to load entities from that directory as well.
    *   The final list of registered entities includes both base and project-specific types.

**Step 1.8: Verify Dockerfile** [COMPLETED]

*   **Objective:** Confirm base entities are copied into the image.
*   **File:** `Dockerfile` (provided in clipboard)
*   **Actions:**
    1.  Verify the line `COPY entity_types/ ./entity_types/` (@LINE:21) is present and correctly copies `mcp-server/entity_types/base` into `/app/entity_types/base` within the image.
*   **Acceptance Criteria:** The Docker build process includes the base entity type definitions.

---

**Phase 2: CLI and Project Workflow**

**Step 2.1: Create YAML Helper Script (Optional but Recommended)** [COMPLETED]

*   **Objective:** Provide a robust way for the bash `graphiti` script to modify `mcp-projects.yaml`.
*   **File:** `mcp-server/scripts/_yaml_helper.py` (New File)
*   **Actions:**
    1.  Create the Python script.
    2.  Use `argparse` to handle command-line arguments (e.g., `update-registry`, `--registry-file`, `--project-name`, `--root-dir`, `--config-file`).
    3.  Use `ruamel.yaml` (specifically `YAML()` for round-trip loading/dumping) to:
        *   Load the specified registry file.
        *   Navigate to `data['projects']`.
        *   Add or update the entry for the given project name with the provided absolute paths (`root_dir`, `config_file`) and set `enabled: true`.
        *   Write the modified data back to the registry file, preserving comments and formatting.
    4.  Include error handling (file not found, parsing errors, key errors).
*   **Acceptance Criteria:** A Python script exists that can reliably add/update project entries in `mcp-projects.yaml` via command-line arguments.

**Step 2.2: Enhance CLI (`scripts/graphiti`) - `init` Command** [COMPLETED]

*   **Objective:** Automate project setup and registration in `mcp-projects.yaml`.
*   **File:** `mcp-server/scripts/graphiti`
*   **Actions:**
    1.  Locate the `init` command block (@LINE:377).
    2.  **Remove** the call to `_link_dev_files "$TARGET_DIR"` (@LINE:387).
    3.  Add commands to create a template `mcp-config.yaml` in `$TARGET_DIR`. Example content:
        ```bash
        cat > "$TARGET_DIR/mcp-config.yaml" << EOF
        # Configuration for project: $PROJECT_NAME
        services:
          - id: ${PROJECT_NAME}-main # Service ID (used for default naming)
            # container_name: "custom-name" # Optional: Specify custom container name
            # port_default: 8001           # Optional: Specify custom host port
            group_id: "$PROJECT_NAME"     # Graph group ID
            entity_dir: "entities"       # Relative path to entity definitions within project
            # environment:                 # Optional: Add non-secret env vars here
            #   MY_FLAG: "true"
        EOF
        echo -e "Created template ${CYAN}$TARGET_DIR/mcp-config.yaml${NC}"
        ```
    4.  Add command to create the entity directory: `mkdir -p "$TARGET_DIR/entities"` and add a placeholder `.gitkeep` or example file.
    5.  Implement the registry update:
        *   Get absolute path of target dir: `ABS_TARGET_DIR=$(cd "$TARGET_DIR" && pwd)`
        *   Define absolute config path: `ABS_CONFIG_PATH="$ABS_TARGET_DIR/mcp-config.yaml"`
        *   Define central registry path: `CENTRAL_REGISTRY_PATH="$SOURCE_SERVER_DIR/mcp-projects.yaml"`
        *   Call the helper script (assuming Option A from thought process):
            ```bash
            echo -e "Updating central project registry: ${CYAN}$CENTRAL_REGISTRY_PATH${NC}"
            python "$SOURCE_SERVER_DIR/scripts/_yaml_helper.py" update-registry \
              --registry-file "$CENTRAL_REGISTRY_PATH" \
              --project-name "$PROJECT_NAME" \
              --root-dir "$ABS_TARGET_DIR" \
              --config-file "$ABS_CONFIG_PATH"
            # Add error checking based on python script exit code
            if [ $? -ne 0 ]; then
              echo -e "${RED}Error: Failed to update project registry.${NC}"
              # Decide whether to exit or just warn
              exit 1
            fi
            ```
*   **Acceptance Criteria:**
    *   `graphiti init <name> <dir>` creates `mcp-config.yaml` and `entities/` dir in `<dir>`.
    *   It correctly calls the YAML helper script (or other method) to add/update the project entry in `mcp-projects.yaml` with absolute paths.
    *   The obsolete linking step is removed.

**Step 2.3: Enhance CLI (`scripts/graphiti`) - Update Compose/Run Commands** [COMPLETED]

*   **Objective:** Ensure Docker Compose commands use the centrally generated file correctly.
*   **File:** `mcp-server/scripts/graphiti`
*   **Actions:**
    1.  Verify the `compose` command (@LINE:590) simply runs `python generate_compose.py` within the `$MCP_SERVER_DIR` context.
    2.  Verify the `up`, `down`, `restart` commands (@LINE:400, @LINE:471, @LINE:536) correctly `cd` to `$MCP_SERVER_DIR`, call `_ensure_docker_compose_file` (which runs the generator), and then execute `docker compose ...`.
*   **Acceptance Criteria:** The `compose`, `up`, `down`, `restart` commands function correctly with the new generator logic, operating within the central `mcp-server` directory.

**Step 2.4: Enhance CLI (`scripts/graphiti`) - Remove `link` Command** [COMPLETED]

*   **Objective:** Remove the obsolete symlinking functionality.
*   **File:** `mcp-server/scripts/graphiti`
*   **Actions:**
    1.  Delete the `_link_dev_files` function (approx. @LINE:58-@LINE:74).
    2.  Delete the `elif [[ "$COMMAND" == "link" ]];` block (approx. @LINE:579-@LINE:584).
    3.  Remove `"link"` from the command list in the `usage` function (@LINE:13).
    4.  Remove the "Arguments for link" section from the `usage` function (@LINE:25-@LINE:27).
    5.  Update the default command logic (@LINE:371): Change `COMMAND="${1:-link}"` to something sensible, perhaps default to showing usage or remove the default entirely: `COMMAND="${1}"`. If removing the default, add a check: `if [ -z "$COMMAND" ]; then usage; fi`. Let's choose to default to usage if no command is given.
        *   Change `@LINE:371` to `COMMAND="${1}"`.
        *   Add after `@LINE:372`:
            ```bash
            if [ -z "$COMMAND" ]; then
              echo -e "${YELLOW}No command specified.${NC}"
              usage
            fi
            ```
*   **Acceptance Criteria:**
    *   The `_link_dev_files` function is removed.
    *   The `link` command logic block is removed.
    *   The `usage` function no longer mentions the `link` command.
    *   Running `graphiti` with no command now shows the usage help text.

---

**Phase 3: Testing and Documentation**

**Step 3.1: Create Sample Projects** [COMPLETED]

*   **Objective:** Set up test projects to validate the new workflow.
*   **Actions:**
    1.  Create two new directories outside `mcp-server`, e.g., `/workspace/test-project-1` and `/workspace/test-project-2`.
    2.  In `test-project-1`:
        *   Create a basic `entities/` directory with a simple Pydantic model `TestEntity1.py`.
        *   Prepare a basic `mcp-config.yaml`:
            ```yaml
            # /workspace/test-project-1/mcp-config.yaml
            services:
              - id: test1-main
                port_default: 8051 # Assign a unique, available port
                container_name: "mcp-test1-service"
                group_id: "test-project-1"
                entity_dir: "entities"
                environment:
                  TEST_PROJECT_FLAG: "Project1"
            ```
    3.  In `test-project-2`:
        *   Create `entities/` with `TestEntity2.py`.
        *   Prepare `mcp-config.yaml`:
            ```yaml
            # /workspace/test-project-2/mcp-config.yaml
            services:
              - id: test2-aux
                # Rely on generator defaults for port/name
                group_id: "test-project-2"
                entity_dir: "entities"
                environment:
                  TEST_PROJECT_FLAG: "Project2"
                  ANOTHER_FLAG: "enabled"
            ```
*   **Acceptance Criteria:** Two distinct project directories exist, each containing a basic entity definition and an `mcp-config.yaml` file defining at least one service.

**Step 3.2: Test `graphiti init`** [COMPLETED]

*   **Objective:** Verify project initialization and registry update.
*   **Actions:**
    1.  Navigate to `/workspace/test-project-1`.
    2.  Run `../mcp-server/scripts/graphiti init test-project-1 .` (adjust path to `graphiti` as needed).
    3.  Verify console output indicates success and registry update.
    4.  Inspect `/workspace/mcp-server/mcp-projects.yaml`. Check if an entry for `test-project-1` exists with correct absolute paths and `enabled: true`.
    5.  Verify `.cursor/rules/graphiti` structure is created in `test-project-1`.
    6.  Repeat steps 1-5 for `test-project-2`.
*   **Acceptance Criteria:** Both test projects are successfully registered in `mcp-projects.yaml` with correct absolute paths. Rules directories are created.

**Step 3.3: Test `graphiti compose`** [COMPLETED]

*   **Objective:** Verify correct generation of the combined `docker-compose.yml`.
*   **Actions:**
    1.  Navigate to `/workspace/mcp-server`.
    2.  Run `scripts/graphiti compose`.
    3.  Verify console output indicates success.
    4.  Inspect the generated `docker-compose.yml`:
        *   Check for services `neo4j`, `graphiti-mcp-root`, `mcp-test1-main`, `mcp-test2-aux`.
        *   Verify `mcp-test1-main`:
            *   Has `container_name: "mcp-test1-service"`.
            *   Has `ports: ["8051:8000"]` (or correct mapping based on `MCP_ROOT_CONTAINER_PORT`).
            *   Has correct `volumes` mount for `/workspace/test-project-1/entities` to `/app/project_entities`.
            *   Has `environment` including `MCP_GROUP_ID: "test-project-1"`, `MCP_ENTITY_TYPE_DIR: "/app/project_entities"`, `TEST_PROJECT_FLAG: "Project1"`, and inherited base env vars.
        *   Verify `mcp-test2-aux`:
            *   Has default container name (e.g., `mcp-test2-aux`).
            *   Has default sequential port (e.g., `8002:8000`).
            *   Has correct `volumes` mount for `/workspace/test-project-2/entities`.
            *   Has `environment` including `MCP_GROUP_ID: "test-project-2"`, `MCP_ENTITY_TYPE_DIR: "/app/project_entities"`, `TEST_PROJECT_FLAG: "Project2"`, `ANOTHER_FLAG: "enabled"`, and inherited base env vars.
*   **Acceptance Criteria:** The generated `docker-compose.yml` accurately reflects the combination of `base-compose.yaml` and the configurations from both registered test projects.

**Step 3.4: Test `graphiti up`/`down`/`restart`** [COMPLETED]

*   **Objective:** Verify the full stack runs correctly.
*   **Actions:**
    1.  Navigate to `/workspace/mcp-server`.
    2.  Run `scripts/graphiti up -d` (detached mode for easier testing).
    3.  Check container status (`docker ps`). Verify all four containers (`neo4j`, `graphiti-mcp-root`, `mcp-test1-service`, `mcp-test2-aux`) are running.
    4.  Check logs (`docker logs mcp-test1-service`, `docker logs mcp-test2-aux`). Verify:
        *   Logs indicate loading of base entities.
        *   Logs indicate loading of project-specific entities (`TestEntity1`, `TestEntity2`).
        *   Correct `MCP_GROUP_ID` and other environment variables are logged/used.
    5.  (Optional) Test basic functionality via `curl` or MCP client if available.
    6.  Run `scripts/graphiti down`. Verify all containers are stopped and removed.
    7.  Run `scripts/graphiti restart -d`. Verify containers stop and restart successfully.
*   **Acceptance Criteria:** All defined services start correctly, load appropriate entities, use correct configurations, and can be managed via the `graphiti` CLI commands.

**Step 3.5: Update Documentation**

*   **Objective:** Reflect the new architecture and workflow in documentation.
*   **Files:** `README.md`, potentially other `.md` files. Remove/Update `docker-compose.template.yml`.
*   **Actions:**
    1.  Update `README.md`:
        *   Describe the new architecture (central control, project configs, registry).
        *   Explain the updated `graphiti init` workflow for setting up a project.
        *   Explain the structure and purpose of `mcp-config.yaml`.
        *   Explain the purpose of `mcp-projects.yaml` (and warn against manual editing).
        *   Document the `graphiti compose`, `up`, `down`, `restart` commands, emphasizing they run from the central repo.
        *   Remove references to the old `custom_servers.yaml` and symlinking (`link` command).
    2.  Decide fate of `docker-compose.template.yml`: Either remove it entirely or update it drastically to only show the *base* services and explain that custom services are added via the generation process. Removing might be cleaner.
    3.  Review rule files (`graphiti-mcp-core-rules.md`, etc.) for any outdated references to configuration or workflow.
*   **Acceptance Criteria:** Documentation accurately reflects the V1 architecture and usage. Obsolete documentation is removed or updated.