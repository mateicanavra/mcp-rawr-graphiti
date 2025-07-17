# Graphiti MCP Server • Fast Multi‑Project Knowledge Graphs

*Fork & extension of the official [****`getzep/graphiti`****\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* MCP server]—adding multi‑server, single‑DB support and a DX‑focused CLI.*

> **Build per‑project temporal knowledge graphs that your AI agents can query over the [Model Context Protocol]—all in one command.**

---

## Quick Start

```bash
# 1 · Install the CLI
pipx install 'git+https://github.com/rawr-ai/mcp-graphiti.git'
#   ↳ rawr-mcp-graphiti isn't on PyPI yet; this installs straight from Git.
#     We'll publish the package soon. Once installed, the `graphiti` command
#     is available globally from any directory.

# 2 · Generate compose + IDE configs
#    (can be run from **any** directory — the CLI locates your repo automatically)
cd rawr-mcp-graphiti
graphiti compose              # reads mcp-projects.yaml

# 3 · Launch services (Neo4j + servers)
graphiti up -d                # ports 8000, 8001, …

# 4 · Init a new project
cd path/to/my-kg        # switch to the project repo root
graphiti init [my-kg]   # writes mcp-config.yaml here

# 5 · Reload only that project
graphiti reload mcp-my-kg
```

Once containers are running you can:

- Hit `http://localhost:8000/status` for a health check.
- Open Neo4j browser at `http://localhost:7474` (credentials in `.env`).
- Point any MCP-compatible client to `http://localhost:800{N}/sse`.

---

## Why this repo exists

Graphiti already turns unstructured text into a **temporal graph** stored in Neo4j—each server ingests text, extracts entities & relationships via LLMs, and records every change as time‑stamped episodes so agents can ask versioned questions, but most IDEs and agent frameworks (Cursor, VS Code, LangGraph, Autogen, …) speak **MCP**—they expect an HTTP/SSE endpoint that they can list in a `mcp.json` file.\
Typical workflows force you to hand‑roll a dedicated server for every project. To remove that manual step, this CLI auto‑generates a *Docker Compose* file that spins up:

- **one Neo4j instance** (shared storage)
- **one “root” MCP server** (playground / smoke tests)
- **N project‑scoped MCP servers**—each with its own `group_id`, entity rules and OpenAI model

Unlike the upstream example, which assumes **one server per docker‑compose file**, this fork automates **N servers against a single Neo4j** so you get:

| Benefit                   | Why it matters                                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------------------- |
| **Project isolation**     | Different extraction rules or models can’t collide.                                               |
| **Editor auto‑discovery** | `.cursor/mcp.json` is rewritten with the right port for each project—open the repo, tools appear. |
| **Crash containment**     | A runaway prompt that floods the graph only takes down *its* container.                           |
| **Zero‑downtime tweaks**  | Hot‑swap entity YAML or LLM model for *project B* without restarting *project A*.                 |

If your workload is small and homogeneous you *can* run a single server—just comment out the project entries in `mcp-projects.yaml`.  The defaults aim for safety and DX first.

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

- `group_id` — every Graphiti write/read is namespaced by this string.  The CLI passes it as an env‑var so each container stays in its lane.
path/to/your/project/ai/graph/entities/` inside a project. Mount‑only volumes keep them read‑only to other projects.
- The **Compose generator** walks `mcp-projects.yaml`, assigns the next free port starting at `8001`, then patches `.cursor/mcp.json` for seamless editor support.

---

## Quick start in depth

### 1. Clone & configure

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

### 2. Install the CLI

*Users* — `pipx install 'git+https://github.com/rawr-ai/mcp-graphiti.git'`  # install from Git until published
*Contributors* — `python -m venv .venv && source .venv/bin/activate && uv pip sync uv.lock && pip install -e .`

### 3. Spin it up

```bash
graphiti compose   # generates docker-compose.yml
graphiti up -d
```

### 4. Create a project

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

|  Question                            |  Answer                                                                                                                                                |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Can I collapse to one server?**    | Yes—delete projects from `mcp-projects.yaml` or set `MCP_SINGLE_SERVER=true` and rerun `compose`.                                                      |
| **Is isolation only through ports?** | No, every query includes `group_id`; the extra container gives you crash & dependency isolation.                                                       |
| **Can I put a gateway in front?**    | Sure—any API gateway or reverse proxy can inject `group_id` (JWT claim, header, etc.) and route to the root server for a claims‑based single endpoint. |

---

## Danger zone

Set `NEO4J_DESTROY_ENTIRE_GRAPH=true` **only when you really mean to wipe ALL projects.** The next `graphiti up` will obliterate every node, relationship and episode.

---

## Roadmap & contributions

- **RAWR CLI integration** — expose everything here under a `rawr graph` subcommand to drive the whole RAWR stack with one top‑level tool.
- **`graphiti prune`** — one‑liner to garbage‑collect orphaned `group_id` graphs and reclaim Neo4j disk space.

PRs and issues welcome!

---

© 2025 rawr‑ai • MIT License

