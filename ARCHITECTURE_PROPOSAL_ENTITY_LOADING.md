# Architectural Proposal: Selective Entity Loading

**Version:** 1.1 (Revised based on review and user feedback)
**Date:** 2025-04-03

## 1. Goal

Allow Graphiti MCP server instances, configured via `graphiti_cli`, to selectively load Python entity definitions from specific subdirectories within a project's `ai/graph/` structure, while still using a single Docker volume mount for the parent directory containing these subdirectories. Provide a fallback mechanism to load all entities if no specific selection is made.

## 2. Proposed Solution

Modify the configuration format, CLI compose generation logic, and server runtime entity loading mechanism.

### 2.1. Configuration (`mcp-config.yaml` Update)

-   **Key:** `entities_dir` (within each service definition under `services`)
-   **Type:** This key will now accept either:
    -   A **single string**: Represents a relative path from the project's `ai/graph/` directory (e.g., `"entities"`). This signifies the intention to load **all** entities found recursively within this directory (maintaining backward compatibility).
    -   A **list of strings**: Each string represents a relative path to a subdirectory from the project's `ai/graph/` directory (e.g., `["entities/thing", "entities/person"]`). This signifies the intention to load **only** the entities found recursively within these specific subdirectories.
-   **Constraint:** If a list is provided, all paths within the list **must** share the same immediate parent directory relative to `ai/graph/`. The CLI will validate this.
-   **Example (`mcp-config.yaml` snippet):**
    ```yaml
    services:
      - server_id: my-service-all
path/to/your/project/ai/graph/entities/
        entities_dir: "entities"
        # ... other config ...
      - server_id: my-service-subset
path/to/your/project/ai/graph/entities/thing/
path/to/your/project/ai/graph/entities/person/
        entities_dir:
          - "entities/thing"
          - "entities/person"
        # ... other config ...
    ```

### 2.2. CLI Tooling (`graphiti_cli/logic/compose_generator.py` Update)

-   **Read `entities_dir`:** Load the `entities_dir` value from the project's `mcp-config.yaml` for each service.
-   **Determine Volume Mount Path and Selection Spec:**
    -   **If `entities_dir` is a string:**
        -   **Host Path:** Calculate the absolute host path to this directory (e.g., `project_root / DIR_AI / DIR_GRAPH / entities_dir_string`).
        -   **Selection Spec:** Set the selection specifier to an empty string (`""`).
    -   **If `entities_dir` is a list:**
        -   **Find Common Parent:** Determine the common immediate parent directory relative to `ai/graph/` for all paths in the list.
            -   *Validation:* Verify that all paths share the *same* immediate parent. If not, print an error and stop generation for this service/project.
        -   **Host Path:** Calculate the absolute host path to this **common parent directory**.
        -   **Selection Spec:** Extract the final component (subdirectory name) from each path in the original list (e.g., `["thing", "person"]`).
            -   *Validation:* Verify that each of these subdirectories exists on the host filesystem under the common parent directory. If not, print an error and stop.
            -   Join these subdirectory names into a single **comma-separated string** (e.g., `"thing,person"`).
-   **Generate `docker-compose.yml`:**
    -   **Volume Mount:** Mount the determined absolute **Host Path** (either the single directory or the common parent) to the fixed container path (`PROJECT_CONTAINER_ENTITY_PATH`). Use read-only (`:ro`).
    -   **Environment Variable:** Set the `MCP_ENTITIES` environment variable for the service to the determined **Selection Spec** (either `""` or the comma-separated list of subdirectory names).

### 2.3. Server Runtime (`graphiti_mcp_server.py` Update)

-   **Argument Parsing:** Ensure the `--entities` command-line argument is parsed (likely already done via `entrypoint.sh` reading `MCP_ENTITIES`). Store this comma-separated string value (the "Selection Spec").
-   **Modify `load_entities_from_directory(directory_path: str, subdir_selection_spec: str)`:**
    -   Rename the second parameter for clarity (e.g., `subdir_selection_spec`).
    -   **Check `subdir_selection_spec`:**
        -   If empty/`None`: Recursively find and load all `.py` files within the base `directory_path`.
        -   If **not** empty:
            -   Split the spec string by commas.
            -   For each `subdir_name`:
                -   Construct the full path: `target_dir = Path(directory_path) / subdir_name`.
                -   *Validation:* Check if `target_dir` exists and is a directory. Log a warning if not, continue.
                -   If valid: Recursively find and load all `.py` files within `target_dir`.
            -   *(Comment out file loading):* Logic for handling direct `.py` file paths in the spec is commented out for this iteration.*
    -   **Error Handling:** Wrap dynamic module import/loading calls within `try...except (ImportError, SyntaxError, Exception) as e:`. Log detailed errors for failed modules but allow the server to continue starting up.
-   **Update Call Site:** Pass the parsed `--entities` argument value to `load_entities_from_directory`.
-   **Remove Redundant Filtering:** Remove/comment out the logic in `add_episode` that previously used `config.entity_subset`.

### 2.4. Documentation & Limitations

-   Document the new behavior of `entities_dir` (string vs. list).
-   Document that subdirectory names specified via the list method cannot contain commas.
-   Mention that the server attempts robust loading (logs errors, continues startup).

## 3. Rationale

-   Simplifies configuration by overloading `entities_dir`.
-   Focuses initial implementation on subdirectory selection.
-   Incorporates necessary validation in the CLI for early feedback.
-   Improves server startup robustness with error handling for entity modules.
-   Maintains a single volume mount per service.

## 4. Next Steps

-   Implement the changes in `graphiti_cli/logic/compose_generator.py`.
-   Implement the changes in `graphiti_mcp_server.py` (argument parsing, `load_entities_from_directory`, error handling, call site update, `add_episode` cleanup).
-   Add unit/functional tests for the new logic.
-   Update relevant documentation.