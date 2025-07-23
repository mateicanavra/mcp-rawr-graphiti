# Graphiti MCP Server

Fork of the [getzep/graphiti](https://github.com/getzep/graphiti) example with a focus on developer experience and multi‑project support. Graphiti extracts entities and relationships from text and stores them in Neo4j. This repo adds a CLI that spins up a root server plus project‑specific MCP servers in Docker so several knowledge graphs share the same database.

## Quick Start

1. **Install and clone**
   ```bash
   pipx install 'git+https://github.com/rawr-ai/mcp-graphiti.git'
   git clone https://github.com/rawr-ai/mcp-graphiti.git
   cd mcp-graphiti
   cp .env.example .env  # fill in Neo4j credentials and your OpenAI key
   ```
2. **Launch services**
   ```bash
   graphiti compose   # generates docker-compose.yml and updates .cursor/mcp.json
   graphiti up -d
   ```
   The root server runs on port **8000**; project containers start at **8001**.
3. **Create a project**
   ```bash
   cd /path/to/my-kg
   graphiti init my-kg        # writes ai/graph/mcp-config.yaml
   # add entity definitions under ai/graph/entities/
   ```
   Rerun `graphiti compose && graphiti up -d` from anywhere to start its container.

Once running you can:
- Check `http://localhost:8000/graphiti/status`.
- Connect MCP‑compatible tools to `http://localhost:800{N}/sse`.
- Browse Neo4j at `http://localhost:7474` using the credentials in `.env`.

### Security note
If `NEO4J_PASSWORD` remains `password` the server refuses to start unless `GRAPHITI_ENV=dev`. Always use a strong password in production.

## Why this fork?
The upstream repository assumes one server per compose file. Here a single compose file manages many project servers that share Neo4j. Each service gets its own `group_id`, entities and model so projects stay isolated while running on the same database.

### Highlights
- **Project isolation** – different extraction rules or models never collide.
- **Editor auto‑discovery** – ports are written to `.cursor/mcp.json`.
- **Crash containment** – a bad prompt only restarts its container.
- **Hot reload** – tweak a project's config and run `graphiti reload <container>`.

Leave `mcp-projects.yaml` empty if you only need the root server.

## Danger zone
Setting `NEO4J_DESTROY_ENTIRE_GRAPH=true` wipes *all* projects the next time you run `graphiti up`. Use with care.

## Contributing
PRs and issues are welcome.

© 2025 rawr‑ai • MIT License
