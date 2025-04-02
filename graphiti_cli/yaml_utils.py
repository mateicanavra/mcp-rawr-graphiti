#!/usr/bin/env python3
"""
YAML utility functions for the Graphiti CLI.
Contains functions for loading/saving YAML files, updating the registry,
and generating the Docker Compose configuration.
"""
import sys
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
import os
import json
from typing import Optional, List, Dict, Any, Union

from .core import get_repo_root
from constants import (
    # Colors for output
    RED, GREEN, YELLOW, CYAN, NC,
    # Docker/container constants
    CONTAINER_ENTITY_PATH, DEFAULT_PORT_START, DEFAULT_MCP_CONTAINER_PORT_VAR,
    # Directory structure
    DIR_AI, DIR_GRAPH, DIR_ENTITIES, 
    # Environment variables
    ENV_MCP_GROUP_ID, ENV_MCP_USE_CUSTOM_ENTITIES, ENV_MCP_USE_CUSTOM_ENTITIES_VALUE, ENV_MCP_ENTITY_TYPE_DIR,
    # File and path constants
    BASE_COMPOSE_FILENAME, PROJECTS_REGISTRY_FILENAME, DOCKER_COMPOSE_OUTPUT_FILENAME,
    # Project container path
    PROJECT_CONTAINER_ENTITY_PATH,
    # Registry file keys
    REGISTRY_PROJECTS_KEY, REGISTRY_ROOT_DIR_KEY, REGISTRY_CONFIG_FILE_KEY, REGISTRY_ENABLED_KEY,
    # Compose file keys
    COMPOSE_SERVICES_KEY, COMPOSE_CUSTOM_BASE_ANCHOR_KEY, COMPOSE_CONTAINER_NAME_KEY,
    COMPOSE_PORTS_KEY, COMPOSE_ENVIRONMENT_KEY, COMPOSE_VOLUMES_KEY,
    # Project config keys
    PROJECT_SERVICES_KEY, PROJECT_SERVER_ID_KEY, PROJECT_ENTITY_DIR_KEY, 
    PROJECT_CONTAINER_NAME_KEY, PROJECT_PORT_DEFAULT_KEY, PROJECT_GROUP_ID_KEY, PROJECT_ENVIRONMENT_KEY,
    # Configuration keys
    CONFIG_KEY_SYNC_CURSOR_MCP_CONFIG,
    # Service name constants
    SERVICE_NAME_PREFIX,
    ENV_MCP_ENTITY_TYPES
)
from .core import LogLevel

# --- Project AI Graph Dirs ---
PROJECT_AI_GRAPH_DIRS = [DIR_AI, DIR_GRAPH]  # Standard subdirectory path for project entities

# --- Registry File Header Constants ---
REGISTRY_HEADER_LINES = [
    "# !! WARNING: This file is managed by the 'graphiti init' command. !!",
    "# !! Avoid manual edits unless absolutely necessary.                 !!",
    "#",
    "# Maps project names to their configuration details.",
    "# Paths should be absolute for reliability.",
]

# --- Docker Compose Header Constants ---
DOCKER_COMPOSE_HEADER_LINES = [
    "# Generated by graphiti CLI",
    "# Do not edit this file directly. Modify base-compose.yaml or project-specific mcp-config.yaml files instead.",
    "",
    "# --- Custom MCP Services Info ---"
]

# --- YAML Instances ---
yaml_rt = YAML()  # Round-Trip for preserving structure/comments
yaml_rt.preserve_quotes = True
yaml_rt.indent(mapping=2, sequence=4, offset=2)

yaml_safe = YAML(typ='safe')  # Safe loader for reading untrusted/simple config

# --- File Handling ---
def load_yaml_file(file_path: Path, safe: bool = False) -> Optional[Any]:
    """
    Loads a YAML file, handling errors.
    
    Args:
        file_path (Path): Path to the YAML file
        safe (bool): Whether to use the safe loader (True) or round-trip loader (False)
        
    Returns:
        Optional[Any]: The parsed YAML data, or None if loading failed
    """
    yaml_loader = yaml_safe if safe else yaml_rt
    if not file_path.is_file():
        print(f"Warning: YAML file not found or is not a file: {file_path}")
        return None
    try:
        with file_path.open('r') as f:
            return yaml_loader.load(f)
    except Exception as e:
        print(f"Error parsing YAML file '{file_path}': {e}")
        return None  # Or raise specific exception

def write_yaml_file(data: Any, file_path: Path, header: Optional[List[str]] = None):
    """
    Writes data to a YAML file using round-trip dumper.
    
    Args:
        data (Any): The data to write to the file
        file_path (Path): Path to the output file
        header (Optional[List[str]]): Optional list of comment lines to add at the top of the file
    
    Raises:
        IOError: If the file cannot be written
        Exception: For other errors
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open('w') as f:
            if header:
                f.write("\n".join(header) + "\n\n")  # Add extra newline
            yaml_rt.dump(data, f)
    except IOError as e:
        print(f"Error writing YAML file '{file_path}': {e}")
        raise  # Re-raise after printing
    except Exception as e:
        print(f"An unexpected error occurred during YAML dumping to '{file_path}': {e}")
        raise

# --- Logic from _yaml_helper.py ---
def update_registry_logic(
    registry_file: Path,
    project_name: str,
    root_dir: Path,  # Expecting resolved absolute path
    config_file: Path,  # Expecting resolved absolute path
    enabled: bool = True
) -> bool:
    """
    Updates the central project registry file (mcp-projects.yaml).
    Corresponds to the logic in the old _yaml_helper.py.
    
    Args:
        registry_file (Path): Path to the registry file
        project_name (str): Name of the project
        root_dir (Path): Absolute path to the project root directory
        config_file (Path): Absolute path to the project config file
        enabled (bool): Whether the project should be enabled
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"Updating registry '{registry_file}' for project '{project_name}'")
    if not root_dir.is_absolute() or not config_file.is_absolute():
        print("Error: Project root_dir and config_file must be absolute paths.")
        return False

    if not config_file.exists():
        print(f"Warning: Project config file '{config_file}' does not exist.")
        # Allow continuing for init scenarios

    # Create registry file with header if it doesn't exist
    if not registry_file.exists():
        print(f"Creating new registry file: {registry_file}")
        initial_data = CommentedMap({REGISTRY_PROJECTS_KEY: CommentedMap()})
        try:
            write_yaml_file(initial_data, registry_file, header=REGISTRY_HEADER_LINES)
        except Exception:
            return False  # Error handled in write_yaml_file

    # Load existing registry data using round-trip loader
    data = load_yaml_file(registry_file, safe=False)
    if data is None:
        print(f"Error: Could not load registry file {registry_file}")
        return False

    if not isinstance(data, dict) or REGISTRY_PROJECTS_KEY not in data:
        print(f"Error: Invalid registry file format in {registry_file}. Missing '{REGISTRY_PROJECTS_KEY}' key.")
        return False

    # Ensure 'projects' key exists and is a map
    if data.get(REGISTRY_PROJECTS_KEY) is None:
        data[REGISTRY_PROJECTS_KEY] = CommentedMap()
    elif not isinstance(data[REGISTRY_PROJECTS_KEY], dict):
        print(f"Error: '{REGISTRY_PROJECTS_KEY}' key in {registry_file} is not a dictionary.")
        return False

    # Add or update the project entry (convert Paths to strings for YAML)
    project_entry = CommentedMap({
        REGISTRY_ROOT_DIR_KEY: str(root_dir),
        REGISTRY_CONFIG_FILE_KEY: str(config_file),
        REGISTRY_ENABLED_KEY: enabled
    })
    data[REGISTRY_PROJECTS_KEY][project_name] = project_entry

    # Write back to the registry file
    try:
        # Preserve header by reading first few lines if necessary (complex)
        # Simpler: Assume header is managed manually or re-added if file recreated.
        # We rewrite the whole file here.
        write_yaml_file(data, registry_file)
        print(f"Successfully updated registry for project '{project_name}'")
        return True
    except Exception:
        return False  # Error handled in write_yaml_file

# --- Logic from generate_compose.py ---
def generate_compose_logic(
    repo_root: Path
):
    """
    Generates the final docker-compose.yml by merging base and project configs.
    Corresponds to the logic in the old generate_compose.py.
    
    Args:
        repo_root (Path): Path to the repository root directory
    """
    print("Generating docker-compose.yml...")
    base_compose_path = repo_root / BASE_COMPOSE_FILENAME
    projects_registry_path = repo_root / PROJECTS_REGISTRY_FILENAME
    output_compose_path = repo_root / DOCKER_COMPOSE_OUTPUT_FILENAME

    # Load base compose file
    compose_data = load_yaml_file(base_compose_path, safe=False)
    if compose_data is None or not isinstance(compose_data, dict):
        print(f"Error: Failed to load or parse base compose file: {base_compose_path}")
        sys.exit(1)

    if COMPOSE_SERVICES_KEY not in compose_data or not isinstance(compose_data.get(COMPOSE_SERVICES_KEY), dict):
        print(f"Error: Invalid structure in '{base_compose_path}'. Missing '{COMPOSE_SERVICES_KEY}' dictionary.")
        sys.exit(1)

    # Load project registry safely
    projects_registry = load_yaml_file(projects_registry_path, safe=True)
    if projects_registry is None:
        print(f"Warning: Project registry file '{projects_registry_path}' not found or failed to parse. No custom services will be added.")
        projects_registry = {REGISTRY_PROJECTS_KEY: {}}
    elif REGISTRY_PROJECTS_KEY not in projects_registry or not isinstance(projects_registry[REGISTRY_PROJECTS_KEY], dict):
        print(f"Warning: Invalid format or missing '{REGISTRY_PROJECTS_KEY}' key in '{projects_registry_path}'. No custom services will be added.")
        projects_registry = {REGISTRY_PROJECTS_KEY: {}}

    # --- Generate Custom Service Definitions ---
    services_map = compose_data[COMPOSE_SERVICES_KEY]  # Should be CommentedMap

    # Find the anchor object for merging
    custom_base_anchor_obj = compose_data.get(COMPOSE_CUSTOM_BASE_ANCHOR_KEY)
    if not custom_base_anchor_obj:
        print(f"{RED}Error: Could not find '{COMPOSE_CUSTOM_BASE_ANCHOR_KEY}' definition in {base_compose_path}.{NC}")
        sys.exit(1)

    overall_service_index = 0
    # Iterate through projects from the registry
    for project_name, project_data in projects_registry.get(REGISTRY_PROJECTS_KEY, {}).items():
        if not isinstance(project_data, dict) or not project_data.get(REGISTRY_ENABLED_KEY, False):
            continue  # Skip disabled or invalid projects

        project_config_path_str = project_data.get(REGISTRY_CONFIG_FILE_KEY)
        project_root_dir_str = project_data.get(REGISTRY_ROOT_DIR_KEY)

        if not project_config_path_str or not project_root_dir_str:
            print(f"Warning: Skipping project '{project_name}' due to missing '{REGISTRY_CONFIG_FILE_KEY}' or '{REGISTRY_ROOT_DIR_KEY}'.")
            continue

        project_config_path = Path(project_config_path_str)
        project_root_dir = Path(project_root_dir_str)

        # Load the project's specific mcp-config.yaml
        project_config = load_yaml_file(project_config_path, safe=True)
        if project_config is None:
            print(f"Warning: Skipping project '{project_name}' because config file '{project_config_path}' could not be loaded.")
            continue

        if PROJECT_SERVICES_KEY not in project_config or not isinstance(project_config[PROJECT_SERVICES_KEY], list):
            print(f"Warning: Skipping project '{project_name}' due to missing or invalid '{PROJECT_SERVICES_KEY}' list in '{project_config_path}'.")
            continue

        # Iterate through services defined in the project's config
        for server_conf in project_config[PROJECT_SERVICES_KEY]:
            if not isinstance(server_conf, dict):
                print(f"Warning: Skipping invalid service entry in '{project_config_path}': {server_conf}")
                continue

            server_id = server_conf.get(PROJECT_SERVER_ID_KEY)
            entity_type_dir = server_conf.get(PROJECT_ENTITY_DIR_KEY)  # Relative path within project

            if not server_id or not entity_type_dir:
                print(f"Warning: Skipping service in '{project_name}' due to missing '{PROJECT_SERVER_ID_KEY}' or '{PROJECT_ENTITY_DIR_KEY}': {server_conf}")
                continue

            # --- Determine Service Configuration ---
            service_name = f"{SERVICE_NAME_PREFIX}{server_id}"
            container_name = server_conf.get(PROJECT_CONTAINER_NAME_KEY, service_name)  # Default to service_name
            port_default = server_conf.get(PROJECT_PORT_DEFAULT_KEY, DEFAULT_PORT_START + overall_service_index + 1)
            port_mapping = f"{port_default}:${{{DEFAULT_MCP_CONTAINER_PORT_VAR}}}"  # Use f-string

            # Update the .cursor/mcp.json file if sync_cursor_mcp_config is enabled (default: true)
            sync_cursor_mcp_config = server_conf.get(CONFIG_KEY_SYNC_CURSOR_MCP_CONFIG, True)
            if sync_cursor_mcp_config:
                # Use int value of port_default (it could be a string from the config)
                try:
                    host_port = int(port_default)
                    _update_cursor_mcp_json(project_root_dir, server_id, host_port)
                except (ValueError, TypeError) as e:
                    print(f"{YELLOW}Warning: Could not update Cursor MCP config due to invalid port: {e}{NC}")

            # --- Build Service Definition using CommentedMap ---
            new_service = CommentedMap()
            # Add the merge key first using the anchor object
            new_service.add_yaml_merge([(0, custom_base_anchor_obj)])  # Merge base config

            new_service[COMPOSE_CONTAINER_NAME_KEY] = container_name
            new_service[COMPOSE_PORTS_KEY] = [port_mapping]  # Ports must be a list

            # --- Environment Variables ---
            env_vars = CommentedMap()  # Use CommentedMap to preserve order if needed
            mcp_group_id = server_conf.get(PROJECT_GROUP_ID_KEY, project_name)  # Default group_id to project_name
            env_vars[ENV_MCP_GROUP_ID] = mcp_group_id
            env_vars[ENV_MCP_USE_CUSTOM_ENTITIES] = ENV_MCP_USE_CUSTOM_ENTITIES_VALUE  # Assume true if defined here

            # Calculate absolute host path for entity volume mount
            abs_host_entity_path = (project_root_dir / DIR_AI / DIR_GRAPH / entity_type_dir).resolve()
            if not abs_host_entity_path.is_dir():
                print(f"Warning: Entity directory '{abs_host_entity_path}' for service '{service_name}' does not exist. Volume mount might fail.")
                # Continue anyway, Docker will create an empty dir inside container if host path doesn't exist

            # Set container path for entity directory env var
            env_vars[ENV_MCP_ENTITY_TYPE_DIR] = PROJECT_CONTAINER_ENTITY_PATH

            # Add project-specific environment variables from mcp-config.yaml
            project_environment = server_conf.get(PROJECT_ENVIRONMENT_KEY, {})
            if isinstance(project_environment, dict):
                # Check if MCP_ENTITY_TYPES is already defined in the project config
                if ENV_MCP_ENTITY_TYPES not in project_environment:
                    # If not defined, set it to empty string by default
                    # This prevents accidental overrides from .env and triggers default behavior in entrypoint.sh
                    env_vars[ENV_MCP_ENTITY_TYPES] = ""
                # Merge project-specific environment variables AFTER setting the default
                env_vars.update(project_environment)
            else:
                print(f"Warning: Invalid '{PROJECT_ENVIRONMENT_KEY}' section for service '{service_name}' in '{project_config_path}'. Expected a dictionary.")
            
            # If MCP_ENTITY_TYPES was NOT in project_environment, but we haven't set it yet (e.g., project_environment was empty)
            # ensure it's set to empty string.
            if ENV_MCP_ENTITY_TYPES not in env_vars:
                 env_vars[ENV_ENTITY_TYPES] = ""

            new_service[COMPOSE_ENVIRONMENT_KEY] = env_vars

            # --- Volumes ---
            # Ensure volumes list exists (might be added by anchor merge, check needed?)
            # setdefault is safer if anchor doesn't guarantee 'volumes'
            if COMPOSE_VOLUMES_KEY not in new_service:
                new_service[COMPOSE_VOLUMES_KEY] = []
            elif not isinstance(new_service[COMPOSE_VOLUMES_KEY], list):
                print(f"Warning: '{COMPOSE_VOLUMES_KEY}' merged from anchor for service '{service_name}' is not a list. Overwriting.")
                new_service[COMPOSE_VOLUMES_KEY] = []

            # Append the entity volume mount (read-only)
            new_service[COMPOSE_VOLUMES_KEY].append(f"{abs_host_entity_path}:{PROJECT_CONTAINER_ENTITY_PATH}:ro")

            # --- Add to Services Map ---
            services_map[service_name] = new_service
            overall_service_index += 1

    # --- Write Output File ---
    header = DOCKER_COMPOSE_HEADER_LINES + [
        f"# Default Ports: Assigned sequentially starting from {DEFAULT_PORT_START + 1}",
        "#              Can be overridden by specifying 'port_default' in project's mcp-config.yaml.",
    ]
    try:
        write_yaml_file(compose_data, output_compose_path, header=header)
        print(f"Successfully generated '{output_compose_path}'.")
    except Exception:
        # Error already printed by write_yaml_file
        sys.exit(1)

def _update_cursor_mcp_json(
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
