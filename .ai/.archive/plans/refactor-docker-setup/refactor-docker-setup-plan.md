Okay, here is the step-by-step implementation plan to update your Docker configuration based on our final agreed-upon design, including support for the `--destroy-graph` flag.

This plan assumes you have the final versions of `docker-compose.yml-NEW`, `Dockerfile-NEW`, and `entrypoint.sh-NEW` (as generated in our previous interactions) available.

**Objective:** Refactor the Docker setup to use an entrypoint script for command execution, centralize configuration using YAML anchors, improve maintainability, and add environment variable control for the `--destroy-graph` flag.

**Assumptions:**

-   You are working in the root directory of your project where the `Dockerfile` and `docker-compose.yml` files reside.
-   Docker and Docker Compose are installed and functioning correctly.
-   You have the final proposed file contents available (referred to conceptually as `-NEW` versions).

---

**Implementation Plan**

**Step 1: Create the Entrypoint Script (`entrypoint.sh`)**

1.  **Action:** Create a new file named `entrypoint.sh` in the same directory as your `Dockerfile`.
2.  **Content:** Paste the following content into `entrypoint.sh`. This includes the logic to handle the `MCP_DESTROY_GRAPH` environment variable.

    ```bash
    #!/bin/sh
    # docker-entrypoint.sh
    # This script constructs and executes the graphiti_mcp_server command
    # based on environment variables set in docker-compose.yml.

    # Exit immediately if a command exits with a non-zero status.
    set -e

    # Base command parts
    CMD_PREFIX="uv run graphiti_mcp_server.py"
    CMD_ARGS="--transport sse" # Common arguments

    # Append arguments based on environment variables

    # --group-id (Required or has default handling in script?)
    if [ -n "$MCP_GROUP_ID" ]; then
      CMD_ARGS="$CMD_ARGS --group-id \"$MCP_GROUP_ID\""
    else
      echo "Warning: MCP_GROUP_ID environment variable not set."
      # Decide: exit 1? Or let the python script handle default/error?
    fi

    # --use-custom-entities (Boolean flag)
    # Adjust check if different values like "1", "yes" are used
    if [ "$MCP_USE_CUSTOM_ENTITIES" = "true" ]; then
      CMD_ARGS="$CMD_ARGS --use-custom-entities"
    fi

    # --entity-type-dir (Optional path)
    if [ -n "$MCP_ENTITY_TYPE_DIR" ]; then
      CMD_ARGS="$CMD_ARGS --entity-type-dir \"$MCP_ENTITY_TYPE_DIR\""
    fi

    # --entity-types (Optional space-separated list)
    # Assumes the python script handles a space-separated list after the flag.
    if [ -n "$MCP_ENTITY_TYPES" ]; then
       CMD_ARGS="$CMD_ARGS --entity-types $MCP_ENTITY_TYPES"
    fi

    # --destroy-graph (Boolean flag)
    if [ "$MCP_DESTROY_GRAPH" = "true" ]; then
      CMD_ARGS="$CMD_ARGS --destroy-graph"
      echo "Warning: --destroy-graph flag is set. Graph data will be cleared on startup."
    fi

    # Add logic for any other configurable flags here...

    # Combine prefix and arguments
    FULL_CMD="$CMD_PREFIX $CMD_ARGS"

    echo "--------------------------------------------------"
    echo " Running MCP Server with Group ID: ${MCP_GROUP_ID:-<Not Set>}"
    echo " Executing command: $FULL_CMD"
    echo "--------------------------------------------------"

    # Use 'exec' to replace the shell process with the Python process.
    # "$@" passes along any arguments that might have been added via
    # 'command:' in docker-compose.yml (though we aren't using them here).
    exec $FULL_CMD "$@"
    ```

3.  **Note:** Ensure this file is saved with Linux line endings (LF) if you are working on Windows, as it will run inside a Linux container.

**Step 2: Update the `Dockerfile`**

1.  **Action:** Modify your existing `Dockerfile`.
2.  **Changes:**
    -   Add instructions to `COPY` the `entrypoint.sh` script into the image and make it executable (`chmod +x`).
    -   Set the `ENTRYPOINT` instruction to use the script.
    -   Remove the old `CMD` instruction if it exists, as the `ENTRYPOINT` now handles execution.
3.  **Content:** Replace the end of your `Dockerfile` with the following structure (adjust paths like `/app` if your `WORKDIR` is different):

    ```dockerfile
    # (Keep your existing FROM, WORKDIR, apt-get, uv install, ENV PATH, COPY pyproject, uv sync, COPY code lines...)

    # --- Add Entrypoint Script ---
    # Copy the entrypoint script into the working directory
    COPY entrypoint.sh .
    # Make it executable
    RUN chmod +x ./entrypoint.sh
    # ---------------------------

    # Set environment variables (keep PYTHONUNBUFFERED=1)
    ENV PYTHONUNBUFFERED=1

    # Create a non-root user and group (keep this section)
    RUN groupadd --system appuser && useradd --system --gid appuser appuser

    # Change ownership of the app directory to the new user
    # Ensure entrypoint.sh is also owned correctly
    RUN chown -R appuser:appuser /app

    # Switch to the non-root user (keep this)
    USER appuser

    # --- Set Entrypoint ---
    # Use the script as the main container command
    ENTRYPOINT ["./entrypoint.sh"]

    # Remove any previous CMD instruction like:
    # CMD ["uv", "run", "graphiti_mcp_server.py"]
    ```

**Step 3: Replace `docker-compose.yml`**

1.  **Action:** Replace the _entire content_ of your existing `docker-compose.yml` file.
2.  **Content:** Use the final proposed `docker-compose.yml` content, which incorporates the refined naming, default handling, base definitions, and environment variables for the entrypoint script. _Crucially, this version adds the `MCP_DESTROY_GRAPH` environment variable to the MCP services._

    ```yaml
    # docker-compose.yml
    version: "3.8"

    # --- Base Definitions ---

    x-mcp-healthcheck:
        &mcp-healthcheck # Healthcheck targets the internal MCP port/endpoint, using the default/env var
        test:
            [
                "CMD-SHELL",
                "curl -s -I --max-time 1 http://localhost:${MCP_ROOT_CONTAINER_PORT:-8000}/sse | grep -q 'text/event-stream' || exit 1",
            ]
        interval: 30s
        timeout: 10s
        retries: 5
        start_period: 5s

    x-neo4j-connection: &neo4j-connection
        # Neo4j connection details. Uses the internal port defined by the neo4j service.
        # User/Password are validated when starting the neo4j service itself.
        NEO4J_URI: "bolt://neo4j:${NEO4J_CONTAINER_BOLT_PORT:-7687}"
        NEO4J_USER: "${NEO4J_USER}" # Value required by neo4j service
        NEO4J_PASSWORD: "${NEO4J_PASSWORD}" # Value required by neo4j service

    x-mcp-env: &mcp-env # Common environment variables for MCP servers
        MODEL_NAME: "${MODEL_NAME:-gpt-4o}"
        OPENAI_API_KEY: ${OPENAI_API_KEY?Please set OPENAI_API_KEY in your .env file} # Still required here as MCP needs it directly
        OPENAI_BASE_URL: ${OPENAI_BASE_URL:-https://api.openai.com/v1}
        GRAPHITI_LOG_LEVEL: ${GRAPHITI_LOG_LEVEL:-info}
        PATH: "/app:/root/.local/bin:${PATH}" # Ensure app and uv paths are included

    # Base definition for ALL graphiti MCP services
    x-graphiti-mcp-base: &graphiti-mcp-base
        build:
            context: .
            dockerfile: Dockerfile # Assumes Dockerfile sets up the entrypoint script
        env_file:
            - path: .env
              required: false
        environment:
            # Merge common MCP env and neo4j connection details
            <<: [*mcp-env, *neo4j-connection]
        healthcheck:
            <<: *mcp-healthcheck
        restart: unless-stopped
        # Execution is handled by the ENTRYPOINT script defined in the Dockerfile

    # Base definition specifically for CUSTOM graphiti MCP services
    x-graphiti-mcp-custom-base: &graphiti-mcp-custom-base
        <<: *graphiti-mcp-base # Inherit all properties from the main base
        depends_on:
            # Custom servers depend on both Neo4j and the Core MCP server being healthy
            neo4j:
                condition: service_healthy
            graphiti-mcp-core:
                condition: service_healthy
        # Environment variables specific to custom servers (added per-service) configure the entrypoint script

    # --- Services ---
    services:
        # --- Database ---
        neo4j:
            image: neo4j:5.26.0
            container_name: ${NEO4J_CONTAINER_NAME:-graphiti-mcp-neo4j}
            ports:
                # Expose Neo4j HTTP and Bolt ports, internal ports have defaults
                - "${NEO4J_HOST_HTTP_PORT:-7474}:${NEO4J_CONTAINER_HTTP_PORT:-7474}" # HTTP
                - "${NEO4J_HOST_BOLT_PORT:-7687}:${NEO4J_CONTAINER_BOLT_PORT:-7687}" # Bolt
            environment:
                # Enforce mandatory User/Password here. Memory settings configurable.
                - NEO4J_AUTH=${NEO4J_USER?Please set NEO4J_USER in your .env file}/${NEO4J_PASSWORD?Please set NEO4J_PASSWORD in your .env file}
                - NEO4J_server_memory_heap_initial__size=${NEO4J_HEAP_INITIAL:-512m}
                - NEO4J_server_memory_heap_max__size=${NEO4J_HEAP_MAX:-1G}
                - NEO4J_server_memory_pagecache_size=${NEO4J_PAGECACHE:-512m}
            volumes:
                - neo4j_data:/data
                - neo4j_logs:/logs
            healthcheck:
                # Specific healthcheck for Neo4j HTTP interface using its internal port
                test:
                    [
                        "CMD",
                        "wget",
                        "-O",
                        "/dev/null",
                        "http://localhost:${NEO4J_CONTAINER_HTTP_PORT:-7474}",
                    ]
                interval: 10s
                timeout: 5s
                retries: 5
                start_period: 30s

        # --- Core MCP Server (Required) ---
        graphiti-mcp-core:
            <<: *graphiti-mcp-base # Inherits from the main MCP base
            container_name: ${MCP_CORE_CONTAINER_NAME:-graphiti-mcp-core}
            depends_on:
                neo4j:
                    condition: service_healthy
            ports:
                # Map host port to the default/env var internal MCP port
                - "${MCP_HOST_PORT_CORE:-8000}:${MCP_ROOT_CONTAINER_PORT:-8000}"
            environment:
                # --- Configuration for entrypoint.sh ---
                MCP_GROUP_ID: "core-api"
                MCP_USE_CUSTOM_ENTITIES: "true"
                MCP_ENTITY_TYPE_DIR: "entity_types/base"
                # MCP_ENTITY_TYPES: "" # Explicitly empty/unset
                MCP_DESTROY_GRAPH: "false" # Default to false

        # --- Custom MCP Server Example 1 (Optional Template) ---
        graphiti-mcp-custom-1:
            <<: *graphiti-mcp-custom-base # Inherit from the CUSTOM MCP base
            container_name: ${MCP_CUSTOM_1_CONTAINER_NAME:-graphiti-mcp-custom-1}
            ports:
                - "${MCP_CUSTOM_HOST_PORT_1:-8001}:${MCP_ROOT_CONTAINER_PORT:-8000}"
            environment:
                # --- Configuration for entrypoint.sh ---
                MCP_GROUP_ID: "custom-group-1"
                MCP_USE_CUSTOM_ENTITIES: "true"
                MCP_ENTITY_TYPE_DIR: "entity_types/custom_1"
                # MCP_ENTITY_TYPES: ""
                MCP_DESTROY_GRAPH: "false" # Default to false

        # --- Custom MCP Server Example 2 (Optional Template) ---
        graphiti-mcp-custom-2:
            <<: *graphiti-mcp-custom-base # Inherit from the CUSTOM MCP base
            container_name: ${MCP_CUSTOM_2_CONTAINER_NAME:-graphiti-mcp-custom-2}
            ports:
                - "${MCP_CUSTOM_HOST_PORT_2:-8002}:${MCP_ROOT_CONTAINER_PORT:-8000}"
            environment:
                # --- Configuration for entrypoint.sh ---
                MCP_GROUP_ID: "another-custom-group"
                MCP_USE_CUSTOM_ENTITIES: "true"
                # MCP_ENTITY_TYPE_DIR: ""
                MCP_ENTITY_TYPES: "SpecificTypeA SpecificTypeB"
                MCP_DESTROY_GRAPH: "false" # Default to false

        # --- Add more custom MCP server definitions below following the pattern ---

    # --- Volumes ---
    volumes:
        neo4j_data: # Persists Neo4j graph data
        neo4j_logs: # Persists Neo4j logs
    ```

**Step 4: Review and Update `.env` File**

1.  **Action:** Carefully review your existing `.env` file (create one if it doesn't exist).
2.  **Changes:**
    -   Ensure mandatory variables like `NEO4J_USER`, `NEO4J_PASSWORD`, and `OPENAI_API_KEY` are set correctly.
    -   Update or add variables for the new configurable host ports and container names (e.g., `MCP_HOST_PORT_CORE`, `MCP_CUSTOM_HOST_PORT_1`, `NEO4J_HOST_HTTP_PORT`).
    -   Add `MCP_DESTROY_GRAPH=true` if you want to enable graph destruction for a specific service (though it's safer to keep the default `false` in the compose file and only set it temporarily in `.env` for specific runs if needed).
    -   Remove any old variables that are no longer used by the new `docker-compose.yml` (e.g., `MAGIC_API_PORT`, `CIV7_PORT`).
3.  **Example `.env` Structure:**

    ```env
    # .env file

    # --- Neo4j Configuration ---
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=your_secure_password # <-- CHANGE THIS
    # Optional: Override Neo4j host ports if needed (defaults are 7474, 7687)
    # NEO4J_HOST_HTTP_PORT=7474
    # NEO4J_HOST_BOLT_PORT=7687
    # Optional: Override Neo4j internal container ports (less common)
    # NEO4J_CONTAINER_HTTP_PORT=7474
    # NEO4J_CONTAINER_BOLT_PORT=7687
    # Optional: Override memory settings
    # NEO4J_HEAP_INITIAL=512m
    # NEO4J_HEAP_MAX=1G
    # NEO4J_PAGECACHE=512m

    # --- OpenAI Configuration ---
    OPENAI_API_KEY=sk-your_openai_api_key # <-- CHANGE THIS
    # Optional: Override OpenAI model or base URL
    # MODEL_NAME=gpt-4o
    # OPENAI_BASE_URL=https://api.openai.com/v1

    # --- Graphiti MCP Configuration ---
    # Optional: Override the default internal port for all MCP servers
    # MCP_ROOT_CONTAINER_PORT=8000
    # Optional: Override log level
    # GRAPHITI_LOG_LEVEL=debug

    # --- Service Specific Ports & Names (Optional Overrides) ---

    # Core Server (Host Port default: 8000)
    # MCP_CORE_CONTAINER_NAME=graphiti-mcp-core
    # MCP_HOST_PORT_CORE=8000

    # Custom Server 1 (Host Port default: 8001)
    # MCP_CUSTOM_1_CONTAINER_NAME=my-first-custom-mcp
    # MCP_CUSTOM_HOST_PORT_1=8001

    # Custom Server 2 (Host Port default: 8002)
    # MCP_CUSTOM_2_CONTAINER_NAME=my-second-custom-mcp
    # MCP_CUSTOM_HOST_PORT_2=8002

    # --- Dangerous Flags (Use with caution) ---
    # Set to "true" to enable graph destruction on startup for relevant service(s)
    # MCP_DESTROY_GRAPH=false
    ```

**Step 5: Build and Test**

1.  **Action:** Rebuild the Docker images to include the changes in the `Dockerfile` and the new `entrypoint.sh`.
2.  **Command:** `docker compose build`
3.  **Action:** Start the services.
4.  **Command:** `docker compose up -d`
5.  **Action:** Check the logs for errors, particularly for the MCP services. Look for the output from the `entrypoint.sh` script confirming the command being executed.
6.  **Command:** `docker compose logs graphiti-mcp-core` (and for custom services)
7.  **Action:** Verify services are running and healthy.
8.  **Command:** `docker compose ps`
9.  **Action:** Perform basic functional tests:
    -   Access the Neo4j browser (e.g., `http://localhost:7474`).
    -   Send a request to one of the MCP server's host ports (e.g., try the `/status` endpoint or add/search an episode via an API client if available).
    -   Test overriding a port in `.env`, run `docker compose up -d --force-recreate`, and check `docker ps` to confirm the new port mapping.
    -   (Carefully) Test the destroy flag: Set `MCP_DESTROY_GRAPH=true` in `.env` for `graphiti-mcp-core`, run `docker compose up -d --force-recreate graphiti-mcp-core`, check its logs for the warning and confirmation, then check if the graph data is gone. **Remember to set it back to `false` afterwards.**

---

**Acceptance Criteria:**

-   `docker compose build` completes successfully.
-   `docker compose up -d` starts all containers without errors.
-   Logs for MCP services show the `entrypoint.sh` output indicating the correct command arguments are being constructed based on environment variables.
-   MCP services connect successfully to Neo4j (check logs and `/status` endpoint if accessible).
-   Port mappings defined in `.env` or defaults are correctly applied (verified with `docker ps`).
-   Setting `MCP_DESTROY_GRAPH=true` in the `.env` file results in the `--destroy-graph` flag being added to the command executed by the entrypoint script (visible in logs).

**Potential Risks:**

-   File Permissions: Ensure `entrypoint.sh` is executable (`chmod +x` in Dockerfile handles this within the container, but check local permissions if issues arise).
-   Line Endings: Ensure `entrypoint.sh` uses LF line endings.
-   Typos: Double-check environment variable names in `docker-compose.yml` and `.env`.
-   `.env` Loading: Ensure the `.env` file is in the correct location relative to where `docker compose` commands are run.

---

This plan provides a clear path to implementing the refined Docker configuration. Remember to back up your existing files before making changes.
