# Graphiti MCP Server Configuration

This document details the configuration options for the Graphiti MCP Server ecosystem, including the project registry, individual project configurations, the root server, and general environment settings.

## 1. Project Registry (`mcp-projects.yaml`)

This file, located in the repository root, acts as a central registry defining which projects the `graphiti_cli` tool should manage.

| Key              | Description                                                                 | Type   | Default | Required | Example                                                                      |
| :--------------- | :-------------------------------------------------------------------------- | :----- | :------ | :------- | :--------------------------------------------------------------------------- |
| `projects`       | Top-level key containing a dictionary of all registered projects.           | dict   | N/A     | Yes      | `projects:`                                                                  |
| `[project_name]` | User-defined key for each project (e.g., `my-app`, `data-analysis`).        | dict   | N/A     | Yes      | `my-app:`                                                                    |
| `root_dir`       | Absolute path to the root directory of the project on the host machine.     | string | N/A     | Yes      | `root_dir: /path/to/your/project`                                            |
path/to/your/project/ai/graph/mcp-config.yaml`                |
| `enabled`        | Set to `true` to include this project when running commands like `up`, `down`. | bool   | `false` | Yes      | `enabled: true`                                                              |

**Example `mcp-projects.yaml`:**

```yaml
# mcp-projects.yaml
projects:
  project-A:
    root_dir: /path/to/your/project
path/to/your/project/ai/graph/mcp-config.yaml
    enabled: true
  project-B:
    root_dir: /path/to/your/project
path/to/your/project/ai/graph/mcp-config.yaml
    enabled: true
```

---

## 2. Project Configuration (`mcp-config.yaml`)

path/to/your/project/ai/graph/mcp-config.yaml`). This file defines the specific MCP server instance(s) for that project.

The configuration is structured under the `services` key, which is a list of service definitions.

| Key (`services` list item) | Description                                                                                                                               | Type                | Default                               | Required | Example                                                              |
| :------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- | :------------------ | :------------------------------------ | :------- | :------------------------------------------------------------------- |
| `id`                       | Unique identifier for this service within the project. Used to form the Docker service name (`mcp-<id>`).                                   | string              | N/A                                   | Yes      | `id: main-service`                                                   |
| `container_name`           | Custom name for the Docker container.                                                                                                     | string              | `mcp-<id>`                            | No       | `container_name: my-app-mcp`                                         |
| `port_default`             | Host port to map to the container's MCP port. If omitted, ports are assigned sequentially starting from 8001.                               | integer             | Auto-assigned (8001+)                 | No       | `port_default: 8005`                                                 |
| `group_id`                 | Namespace for graph data within Neo4j. Isolates this service's data.                                                                      | string              | Project name from `mcp-projects.yaml` | No       | `group_id: my-app-knowledge`                                         |
| `entities_dir`             | Specifies entity definitions to load. Can be a single path (load all recursively) or a list of subdirectory paths (load selectively). Paths are relative to the project's `ai/graph/` directory. | string OR list(string) | N/A                                   | Yes      | `"entities"` OR `["entities/core", "entities/custom"]`               |
| `include_root_entities`    | If `false`, prevents the server from loading the base entities located in the root `/app/entities` directory inside the container.           | boolean             | `true`                                | No       | `include_root_entities: false`                                       |
| `environment`              | A dictionary of additional, non-secret environment variables to set specifically for this service's container.                            | dict                | `{}`                                  | No       | `environment: { SPECIFIC_SETTING: "value", LOG_DETAIL: "verbose" }` |
| `sync_cursor_mcp_config`   | If `true`, automatically updates the project's `.cursor/mcp.json` file with this server's details during `graphiti compose` or `graphiti up`. | boolean             | `true`                                | No       | `sync_cursor_mcp_config: false`                                      |

**Example `mcp-config.yaml`:**

```yaml
path/to/your/project/ai/graph/mcp-config.yaml
services:
  - id: project-A # Service ID
    group_id: "project-A" # Graph group ID
    # Load only entities from 'entities' subdir relative to ai/graph/
    entities_dir: "entities"
    # Prevent loading base /app/entities
    include_root_entities: false
    environment: # Optional environment variables
      GRAPHITI_LOG_LEVEL: "debug"
    sync_cursor_mcp_config: true # Update .cursor/mcp.json

  - id: secondary-processor # Another service in the same project
    port_default: 8002
    group_id: "secondary-processing"
    # Load all entities under ai/graph/all_defs/
    entities_dir: "all_defs"
    # include_root_entities defaults to true
```

---

## 3. Root Server Configuration (`.env` -> `base-compose.yaml`)

The `graphiti-mcp-root` service defined in `base-compose.yaml` acts as a foundational server. Its configuration is primarily controlled via environment variables set in the `.env` file located in the repository root.

| Environment Variable          | Description                                                                                             | Type   | Default            | Required | Example (`.env`)                               |
| :---------------------------- | :------------------------------------------------------------------------------------------------------ | :----- | :----------------- | :------- | :--------------------------------------------- |
| `MCP_ROOT_CONTAINER_NAME`     | Name for the root MCP server container.                                                                 | string | `graphiti-mcp-root`| No       | `MCP_ROOT_CONTAINER_NAME=graphiti-root-server` |
| `MCP_ROOT_HOST_PORT`          | Host port mapped to the root server's container port.                                                   | int    | `8000`             | No       | `MCP_ROOT_HOST_PORT=8000`                      |
| `MCP_ROOT_GROUP_ID`           | Graph namespace for the root server.                                                                    | string | `root`             | No       | `MCP_ROOT_GROUP_ID=root-graph`                 |
| `MCP_ROOT_USE_CUSTOM_ENTITIES`| Enable entity extraction for the root server? (Set as string "true" or "false").                        | string | `"true"`           | No       | `MCP_ROOT_USE_CUSTOM_ENTITIES="true"`          |
| `MCP_ROOT_ENTITIES_DIR`       | Host path (relative to repo root) containing entity definitions to mount for the root server.           | string | `entities`         | No       | `MCP_ROOT_ENTITIES_DIR=base_entities`          |
| `MCP_ROOT_ENTITIES`           | Comma-separated list of subdirectories within `MCP_ROOT_ENTITIES_DIR` to load selectively. Empty loads all. | string | `""`               | No       | `MCP_ROOT_ENTITIES="core,utils"`               |
| `MCP_ROOT_LOG_LEVEL`          | Log level specifically for the root server container.                                                   | string | `info`             | No       | `MCP_ROOT_LOG_LEVEL=debug`                     |

**Note:** The `MCP_ROOT_CONTAINER_PORT` variable also exists but primarily controls the internal container port and is less relevant for user configuration.

---

## 4. General Environment Variables (`.env`)

These variables in the `.env` file configure shared services (like Neo4j) or provide defaults for all MCP server instances (unless overridden).

| Environment Variable       | Description                                                                                             | Type   | Default                      | Required | Example (`.env`)                               |
| :------------------------- | :------------------------------------------------------------------------------------------------------ | :----- | :--------------------------- | :------- | :--------------------------------------------- |
| `NEO4J_USER`               | Username for Neo4j database authentication.                                                             | string | N/A                          | Yes      | `NEO4J_USER=neo4j`                             |
| `NEO4J_PASSWORD`           | Password for Neo4j database authentication.                                                             | string | N/A                          | Yes      | `NEO4J_PASSWORD=your_secure_password`          |
| `NEO4J_HOST_HTTP_PORT`     | Host port mapped to Neo4j's HTTP interface.                                                             | int    | `7474`                       | No       | `NEO4J_HOST_HTTP_PORT=7474`                    |
| `NEO4J_HOST_BOLT_PORT`     | Host port mapped to Neo4j's Bolt interface.                                                             | int    | `7687`                       | No       | `NEO4J_HOST_BOLT_PORT=7687`                    |
| `NEO4J_CONTAINER_NAME`     | Name for the Neo4j container.                                                                           | string | `graphiti-mcp-neo4j`         | No       | `NEO4J_CONTAINER_NAME=neo4j-db`                |
| `NEO4J_HEAP_INITIAL`       | Initial Java heap size for Neo4j (e.g., "512m", "1g").                                                   | string | `512m`                       | No       | `NEO4J_HEAP_INITIAL=1g`                        |
| `NEO4J_HEAP_MAX`           | Maximum Java heap size for Neo4j (e.g., "1g", "2g").                                                    | string | `1G`                         | No       | `NEO4J_HEAP_MAX=2g`                            |
| `NEO4J_PAGECACHE`          | Page cache size for Neo4j (e.g., "512m", "1g").                                                         | string | `512m`                       | No       | `NEO4J_PAGECACHE=1g`                           |
| `OPENAI_API_KEY`           | Your OpenAI API key. Required if using OpenAI models.                                                   | string | N/A                          | Yes*     | `OPENAI_API_KEY=sk-xxxxxxxxxx`                 |
| `OPENAI_BASE_URL`          | Base URL for the OpenAI API (or compatible alternative).                                                | string | `https://api.openai.com/v1`  | No       | `OPENAI_BASE_URL=http://localhost:1234/v1`     |
| `MODEL_NAME`               | Default LLM model name used by MCP servers if not overridden.                                           | string | `gpt-4o`                     | No       | `MODEL_NAME=gpt-3.5-turbo`                     |
| `GRAPHITI_LOG_LEVEL`       | Default log level for *all* MCP servers (root and project) unless overridden by specific configuration. | string | `info`                       | No       | `GRAPHITI_LOG_LEVEL=debug`                     |
| `GRAPHITI_ENV`             | Sets the operating environment. If set to `dev` or `development`, allows using the default Neo4j password (`'password'`) for local setup. **Do not use `dev` in production.** | string | `production` (implied) | No       | `GRAPHITI_ENV=dev`                             |
| `MCP_GRAPHITI_REPO_PATH`   | Explicit path to the repository root (usually auto-detected by the CLI).                                | string | Auto-detected                | No       | `MCP_GRAPHITI_REPO_PATH=/path/to/repo`         |

*Required if using OpenAI-based features.*

**Security Note on `NEO4J_PASSWORD`:**

*   For security reasons, the application will **refuse to start** if `NEO4J_PASSWORD` is set to the default value `'password'`.
*   This check is bypassed **only** if the `GRAPHITI_ENV` variable (see table above) is explicitly set to `'dev'` or `'development'`, intended solely for local development setups.
*   **Never** use the default password or set `GRAPHITI_ENV=dev` in production or any non-development environment. Always use a strong, unique password for `NEO4J_PASSWORD`.
