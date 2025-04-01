Okay, here is a step-by-step implementation plan for another AI agent to execute the security improvements (items 1-6) discussed previously. This plan focuses on modifying the necessary files within the `mcp_server` directory and potentially the root `.gitignore`.

**Objective:**

Implement security enhancements for the `mcp_server` component to prevent accidental secret leakage in the public repository and improve container security hygiene for local deployment. This involves managing secrets via environment variables loaded from a `.env` file, removing secrets from the build process, running the container as a non-root user, and parameterizing container names.

**Relevant Files:**

*   `mcp_server/docker-compose.yml`
*   `mcp_server/Dockerfile`
*   `mcp_server/.env.example`
*   `.gitignore` (at the repository root)

**Implementation Plan:**

**Phase 1: Secret Management Improvements**

1.  **Modify `docker-compose.yml` for Neo4j Password:**
    *   **File:** `mcp_server/docker-compose.yml`
    *   **Action:** Locate the `environment:` section for the `neo4j` service (around @LINE:21 in the provided markdown context). Replace the hardcoded `NEO4J_AUTH` line.
    *   **Replace:**
        ```yaml
              - NEO4J_AUTH=neo4j/password
        ```
    *   **With:** (Using `${VAR?Error}` syntax to force the user to set it)
        ```yaml
              - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD?Please set NEO4J_PASSWORD in your .env file}
        ```

2.  **Modify `docker-compose.yml` to Remove OpenAI API Key from Build Arguments:**
    *   **File:** `mcp_server/docker-compose.yml`
    *   **Action:** Locate the `build:` section for the `mcp-server` service. Remove the entire `args:` block within it (around @LINE:10 in the provided markdown context). The runtime `environment:` variable for `OPENAI_API_KEY` should remain untouched.
    *   **Remove:**
        ```yaml
          args:
            - OPENAI_API_KEY=${OPENAI_API_KEY}
        ```

3.  **Modify `Dockerfile` to Remove OpenAI API Key Build Argument Handling:**
    *   **File:** `mcp_server/Dockerfile`
    *   **Action:** Remove the lines that declare and use the `OPENAI_API_KEY` build argument (around @LINE:4 and @LINE:10 in the provided markdown context).
    *   **Remove:**
        ```Dockerfile
        ARG OPENAI_API_KEY
        ```
    *   **Remove:**
        ```Dockerfile
        ENV OPENAI_API_KEY=$OPENAI_API_KEY
        ```

4.  **Update `.env.example` with Required and Optional Variables:**
    *   **File:** `mcp_server/.env.example`
    *   **Action:** Add or ensure the following variables are present with comments explaining their purpose and instructing the user to set them in their actual `.env` file.
    *   **Add:**
        ```dotenv
        # --- Required Secrets ---
        # Set your OpenAI API key here
        OPENAI_API_KEY=your_openai_api_key_here

        # Set a strong password for the local Neo4j database instance
        # The username will be 'neo4j'
        NEO4J_PASSWORD=your_strong_neo4j_password_here

        # --- Optional Configuration ---
        # You can override the default container names if needed
        # MCP_SERVER_CONTAINER_NAME=graphiti-mcp-magic-candidates
        # NEO4J_CONTAINER_NAME=graphiti-mcp-neo4j

        # Optional: Set the log level for the mcp-server (debug, info, warn, error, fatal)
        # GRAPHITI_LOG_LEVEL=info
        ```

5.  **Verify `.gitignore` Contains `.env`:**
    *   **File:** `.gitignore` (at the repository root)
    *   **Action:** Check if the file contains a line exactly matching `.env`. If not, add it on a new line. This prevents accidental commits of the user's actual secrets.
    *   **Ensure this line exists:**
        ```
        .env
        ```

**Phase 2: Container Hygiene and Configuration**

6.  **Modify `Dockerfile` to Run as Non-Root User:**
    *   **File:** `mcp_server/Dockerfile`
    *   **Action:** Add instructions to create a non-root user/group, change ownership of the application directory, and switch to that user before the `CMD` instruction.
    *   **Add (Place these lines *after* `uv sync` and WORKDIR/COPY commands, but *before* the final `CMD`):**
        ```Dockerfile
        # Create a non-root user and group
        RUN groupadd --system appuser && useradd --system --gid appuser appuser

        # Change ownership of the app directory to the new user
        # Ensure the path '/app' matches your WORKDIR or where app files reside
        RUN chown -R appuser:appuser /app

        # Switch to the non-root user
        USER appuser
        ```
    *   **(Note:** Verify `/app` is the correct path based on `WORKDIR` or `COPY` destinations in the Dockerfile).

7.  **Modify `docker-compose.yml` to Parameterize Container Names:**
    *   **File:** `mcp_server/docker-compose.yml`
    *   **Action:** Update the `container_name` directives for both services to use environment variables with default values.
    *   **Locate and Replace (`mcp-server` service, around @LINE:8):**
        *   **From:** `container_name: graphiti-mcp-magic-candidates`
        *   **To:** `container_name: ${MCP_SERVER_CONTAINER_NAME:-graphiti-mcp-magic-candidates}`
    *   **Locate and Replace (`neo4j` service, around @LINE:19):**
        *   **From:** `container_name: graphiti-mcp-neo4j`
        *   **To:** `container_name: ${NEO4J_CONTAINER_NAME:-graphiti-mcp-neo4j}`

**Testing and Verification Steps (Manual):**

1.  **Create `.env`:** Copy `mcp_server/.env.example` to `mcp_server/.env`. Fill in valid (dummy or real) values for `OPENAI_API_KEY` and `NEO4J_PASSWORD`.
2.  **Build:** Run `docker compose build` from the `mcp_server` directory. It should complete without errors.
3.  **Run (Test Neo4j Password Requirement):** Temporarily comment out `NEO4J_PASSWORD` in your `.env` file. Run `docker compose up`. The command should fail with an error message indicating `NEO4J_PASSWORD` is not set. Restore the variable in `.env`.
4.  **Run (Normal):** Run `docker compose up`. Both containers should start successfully.
5.  **Check User:** Once running, execute `docker compose exec mcp-server whoami`. The output should be `appuser`.
6.  **Check Container Names:** Run `docker ps`. Verify the container names match the defaults (`graphiti-mcp-magic-candidates`, `graphiti-mcp-neo4j`) or the custom names if set in `.env`.
7.  **Check API Key Runtime:** Execute `docker compose exec mcp-server printenv OPENAI_API_KEY`. It should print the key value you set in `.env`.
8.  **(Optional) Inspect Image:** Use tools like `docker history graphiti-mcp-server:latest` or `docker scan` / `trivy image` to check layers. Confirm the API key doesn't appear in build arguments within the image history/layers.

This plan provides specific, actionable steps to address the identified security concerns for the public `mcp_server` repository intended for local use.