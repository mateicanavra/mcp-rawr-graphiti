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

# --entities-dir (Optional path)
if [ -n "$MCP_ENTITIES_DIR" ]; then
  CMD_ARGS="$CMD_ARGS --entities-dir $MCP_ENTITIES_DIR"
fi

# --entities (Optional space-separated list)
# Assumes the python script handles a space-separated list after the flag.
if [ -n "$MCP_ENTITIES" ]; then
   CMD_ARGS="$CMD_ARGS --entities $MCP_ENTITIES"
fi

# --log-level (Pass based on ENV var)
# Read the env var set by docker compose (from .env or compose override)
if [ -n "$GRAPHITI_LOG_LEVEL" ]; then
  CMD_ARGS="$CMD_ARGS --log-level $GRAPHITI_LOG_LEVEL"
fi

# --destroy-graph (Boolean flag)
if [ "$NEO4J_DESTROY_ENTIRE_GRAPH" = "true" ]; then
  CMD_ARGS="$CMD_ARGS --destroy-graph"
  echo "!!! DANGER !!! NEO4J_DESTROY_ENTIRE_GRAPH flag is set to 'true'."
  echo "!!! WARNING !!! This will PERMANENTLY DELETE ALL DATA in the Neo4j database, not just data for this group."
  echo "                 Set to 'false' immediately after use to prevent accidental data loss."
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