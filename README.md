# Graphiti MCP Server • Fast Multi‑Project Knowledge Graphs

*Fork & extension of the official [****`getzep/graphiti`****\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* MCP server]—adding multi‑server, single‑DB support and a DX‑focused CLI.*

> **Build per‑project temporal knowledge graphs that your AI agents can query over the [Model Context Protocol]—all in one command.**

---

## Why this repo exists

Graphiti already turns unstructured text into a **temporal graph** stored in Neo4j—each server ingests text, extracts entities & relationships via LLMs, and records every change as time‑stamped episodes so agents can ask versioned questions, but most IDEs and agent frameworks (Cursor, VS Code, LangGraph, Autogen, …) speak **MCP**—they expect an HTTP/SSE endpoint that they can list in a `mcp.json` file.\
Typical workflows force you to hand‑roll a dedicated server for every project. To remove that manual step, this CLI auto‑generates a *Docker Compose* file that spins up:

- **one Neo4j instance** (shared storage)
- **one "root" MCP server** (playground / smoke tests)
- **N project‑scoped MCP servers**—each with its own `group_id`, entity rules and OpenAI model

Unlike the upstream example, which assumes **one server per docker‑compose file**, this fork automates **N servers against a single Neo4j** so you get:

| Benefit                   | Why it matters                                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------------------- |
| **Project isolation**     | Different extraction rules or models can't collide.                                               |
| **Editor auto‑discovery** | `.cursor/mcp.json` is rewritten with the right port for each project—open the repo, tools appear. |
| **Crash containment**     | A runaway prompt that floods the graph only takes down *its* container.                           |
| **Zero‑downtime tweaks**  | Hot‑swap entity YAML or LLM model for *project B* without restarting *project A*.                 |

If your workload is small and homogeneous you *can* run a single server—just comment out the project entries in `mcp-projects.yaml`.  The defaults aim for safety and DX first.

---

## Troubleshooting & Manual Setup

If you encounter issues with the CLI tool (such as `ImportError: cannot import name 'commands'`), you can set up Graphiti MCP manually using Docker:

### 1. Configure Environment

```bash
git clone https://github.com/rawr-ai/mcp-graphiti.git
cd mcp-graphiti
cp .env.example .env
```

Edit the `.env` file to:
- Add your OpenAI API key
- Set a secure Neo4j password (must be at least 8 characters)
- Make sure `GRAPHITI_ENV=dev` is set for local testing
- Make sure `MCP_ROOT_ENTITIES=` is empty or commented out to avoid command line errors

### 2. Start Services with Docker Compose

```bash
# Copy the base compose template
cp base-compose.yaml docker-compose.yml

# Create basic projects config
cat > mcp-projects.yaml << EOF
projects:
  - name: root
    path: .
    model: gpt-4o
EOF

# Start the services
docker compose up -d
```

### 3. Create Project Structure Manually

```bash
# Create basic project structure
mkdir -p ~/projects/myproject/ai/graph/entities

# Create entity definitions
cat > ~/projects/myproject/ai/graph/entities/basic.yaml << EOF
entity_types:
  - name: Feature
    description: A software feature or capability
    properties:
      - name: name
        description: Name of the feature
      - name: status
        description: Development status
      - name: priority
        description: Priority level
  
  - name: Document
    description: A document or resource
    properties:
      - name: title
        description: Title of the document
      - name: type
        description: Type of document
EOF

# Set up Cursor integration
mkdir -p ~/projects/myproject/.cursor
cat > ~/projects/myproject/.cursor/mcp.json << EOF
{
  "mcpServers": {
    "graphiti": {
      "transport": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
EOF
```

### 4. Adding Additional Project-Specific Servers (Manual)

To add a project-specific server, edit your `docker-compose.yml` to add a new service:

```yaml
  mcp-myproject:
    image: mcp-graphiti-graphiti-mcp-root
    container_name: mcp-myproject
    restart: unless-stopped
    environment:
      - NEO4J_URI=${NEO4J_URI:-bolt://neo4j:7687}
      - NEO4J_USER=${NEO4J_USER:-neo4j}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_BASE_URL=${OPENAI_BASE_URL:-https://api.openai.com/v1}
      - MODEL_NAME=${MODEL_NAME:-gpt-4o}
      - MCP_GROUP_ID=myproject
      - MCP_USE_CUSTOM_ENTITIES=true
      - MCP_ENTITIES_DIR=/app/entities
    ports:
      - "8001:8000"
    volumes:
      - ~/projects/myproject/ai/graph/entities:/app/entities
    depends_on:
      neo4j:
        condition: service_healthy
```

Then restart the new service:

```bash
docker compose up -d
```

Update your project's Cursor config to point to the new port:

```bash
cat > ~/projects/myproject/.cursor/mcp.json << EOF
{
  "mcpServers": {
    "graphiti": {
      "transport": "sse",
      "url": "http://localhost:8001/sse"
    }
  }
}
EOF
```

### API Endpoint Notes

- The SSE endpoint is the primary interface for MCP clients: `/sse`
- The `/status` endpoint mentioned in the documentation doesn't exist (returns 404)
- Use Neo4j browser at `http://localhost:7474` to directly inspect your knowledge graph

---

## Five‑second tour

```bash
# 1 · Install CLI (isolated)
pipx install 'rawr-mcp-graphiti[cli]'  # or: git clone && pipx install .
#   ↳ Once installed, the `graphiti` command is available globally from any directory.

# 2 · Generate compose + IDE configs
#    (can be run from **any** directory — the CLI locates your repo automatically)
cd rawr-mcp-graphiti
graphiti compose              # reads mcp-projects.yaml

# 3 · Launch services (Neo4j + servers)
graphiti up -d                # ports 8000, 8001, …

# 4 · Init a new project
cd path/to/my‑kg        # switch to the project repo root
graphiti init [my-kg]   # writes mcp-config.yaml here

# 5 · Reload only that project
graphiti reload mcp-my-kg
```

Once containers are running you can:

- Open Neo4j browser at `http://localhost:7474` (credentials in `.env`).
- Point any MCP‑compatible client to `http://localhost:800{N}/sse`.

---

## How it works under the hood

```text
┌────────────┐      ┌───────────────────┐
│  IDE / AI  │──SSE│  graphiti‑mcp‑A    │
└────────────┘      │  group_id=proj‑A  │
      ▲             └────────┬──────────┘
      │  SSE                 │ Cypher
      │             ┌────────▼──────────┐
      │             │  Neo4j (temporal) │
      │             └────────┬──────────┘
┌────────────┐      ┌────────▼──────────┐
│  HTTP/CLI  │──SSE│  graphiti‑mcp‑B    │
└────────────┘      │  group_id=proj‑B  │
                    └───────────────────┘
```

- `group_id` — every Graphiti write/read is namespaced by this string.  The CLI passes it as an env‑var so each container stays in its lane.
path/to/your/project/ai/graph/entities/` inside a project. Mount‑only volumes keep them read‑only to other projects.
- The **Compose generator** walks `mcp-projects.yaml`, assigns the next free port starting at `8001`, then patches `.cursor/mcp.json` for seamless editor support.

---

## Quick start in depth

### 1. Clone & configure

```bash
git clone https://github.com/rawr-ai/mcp-graphiti.git
cd mcp-graphiti
cp .env.example .env   # add Neo4j creds & OpenAI key
> **Important Security Note:** The application includes a security check to prevent the use of the default Neo4j password (`'password'`) in production environments.
>
> *   If `NEO4J_PASSWORD` is set to `'password'`, the server will **refuse to start** and raise an error *unless* the `GRAPHITI_ENV` environment variable is explicitly set to `'dev'` or `'development'`.
> *   For any deployment other than local development, you **must** set `NEO4J_PASSWORD` to a strong, unique password in your `.env` file.
> *   Setting `GRAPHITI_ENV=dev` bypasses this check *only* for facilitating local development setups. Do **not** use `GRAPHITI_ENV=dev` in production.

```

### 2. Install the CLI

*Users* (recommended) — `pipx install . --include-deps`\
*Contributors* — `python -m venv .venv && source .venv/bin/activate && uv pip sync uv.lock && pip install -e .`

### 3. Spin it up

```bash
graphiti compose   # generates docker-compose.yml
graphiti up -d
```

### 4. Create a project

```bash
cd ~/code
graphiti init acme‑support‑bot   # run in the **root** of the new project repo
cd acme‑support‑bot
# add entity YAMLs under ai/graph/entities/*.yaml
```

From anywhere on your machine, run `graphiti compose && graphiti up -d` to pick up the new project.  A new server starts on the next port with `group_id=acme-support-bot`.


### Project Configuration (`mcp-projects.yaml`)

The `mcp-projects.yaml` file at the repository root is used to define and manage the individual projects that the `graphiti` CLI tools will recognize and manage. It allows you to configure multiple, isolated Graphiti MCP server instances running against a single Neo4j database.

Key points:

*   **Project Definitions:** This file lists the projects, specifying details like their root directory path (relative to the repository root) and any specific configurations.
*   **`.gitignore` Default:** By default, `mcp-projects.yaml` is included in the `.gitignore` file. This prevents accidental commits of potentially private project lists, especially in public forks or clones of this repository.
*   **Managing Private Projects:** If you are using this repository structure to manage your own private projects, you should remove the `mcp-projects.yaml` entry from your local `.gitignore` file.

The `graphiti compose` command reads this file to generate the necessary `docker-compose.yml` configuration.

---

## Single‑vs‑multi server FAQ

|  Question                            |  Answer                                                                                                                                                |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Can I collapse to one server?**    | Yes—delete projects from `mcp-projects.yaml` or set `MCP_SINGLE_SERVER=true` and rerun `compose`.                                                      |
| **Is isolation only through ports?** | No, every query includes `group_id`; the extra container gives you crash & dependency isolation.                                                       |
| **Can I put a gateway in front?**    | Sure—any API gateway or reverse proxy can inject `group_id` (JWT claim, header, etc.) and route to the root server for a claims‑based single endpoint. |

---

## Danger zone

Set `NEO4J_DESTROY_ENTIRE_GRAPH=true` **only when you really mean to wipe ALL projects.** The next `graphiti up` will obliterate every node, relationship and episode.

---

## Roadmap & contributions

- **RAWR CLI integration** — expose everything here under a `rawr graph` subcommand to drive the whole RAWR stack with one top‑level tool.
- **`graphiti prune`** — one‑liner to garbage‑collect orphaned `group_id` graphs and reclaim Neo4j disk space.

PRs and issues welcome!

---

© 2025 rawr‑ai • MIT License