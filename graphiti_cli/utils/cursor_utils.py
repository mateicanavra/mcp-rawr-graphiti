#!/usr/bin/env python3
"""
Cursor IDE integration utilities for the Graphiti CLI.
Contains functions for managing Cursor IDE configuration files.
"""
import json
from pathlib import Path

from constants import (
    # Colors for output
    RED, GREEN, YELLOW, NC,
)

def update_cursor_mcp_json(
    project_root_dir: Path,
    server_id: str,
    host_port: int,
    transport: str = "sse"
) -> bool:
    """
    Updates or creates the .cursor/mcp.json file in the project directory
    to include the MCP server configuration.
    
    Args:
        project_root_dir (Path): Root directory of the project
        server_id (str): Server ID (used for the key in mcpServers object)
        host_port (int): Host port number for the MCP server
        transport (str): Transport protocol (default: "sse")
        
    Returns:
        bool: True if successful, False otherwise
    """
    cursor_dir = project_root_dir / ".cursor"
    mcp_config_path = cursor_dir / "mcp.json"
    
    # Create .cursor directory if it doesn't exist
    try:
        cursor_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"{RED}Error creating .cursor directory at {cursor_dir}: {e}{NC}")
        return False
    
    # Prepare the MCP server entry
    key = f"graphiti-{server_id}"
    if transport == "sse":
        mcp_entry = {
            "transport": "sse",
            "url": f"http://localhost:{host_port}/sse"
        }
    else:
        # Fallback to stdio if transport is not "sse"
        print(f"{YELLOW}Warning: Unsupported transport '{transport}' for Cursor MCP config. Using 'sse'.{NC}")
        mcp_entry = {
            "transport": "sse",
            "url": f"http://localhost:{host_port}/sse"
        }
    
    # Read existing config if available
    config_data = {"mcpServers": {}}
    if mcp_config_path.exists():
        try:
            with open(mcp_config_path, 'r') as f:
                config_data = json.load(f)
                if not isinstance(config_data, dict):
                    print(f"{YELLOW}Warning: Invalid mcp.json format. Overwriting.{NC}")
                    config_data = {"mcpServers": {}}
                elif "mcpServers" not in config_data:
                    config_data["mcpServers"] = {}
        except (json.JSONDecodeError, OSError) as e:
            print(f"{YELLOW}Warning: Error reading existing mcp.json, creating new file: {e}{NC}")
            config_data = {"mcpServers": {}}
    
    # Update the config with the new server entry
    config_data["mcpServers"][key] = mcp_entry
    
    # Write the updated config back to file
    try:
        with open(mcp_config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        print(f"{GREEN}Updated Cursor MCP config at {mcp_config_path} with server {key} on port {host_port}{NC}")
        return True
    except OSError as e:
        print(f"{RED}Error writing Cursor MCP config to {mcp_config_path}: {e}{NC}")
        return False 