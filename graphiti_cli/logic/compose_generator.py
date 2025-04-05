#!/usr/bin/env python3
"""
Docker Compose generation utilities for the Graphiti CLI.
Contains functions for generating the Docker Compose configuration
based on project-specific configurations.
"""
import sys
from pathlib import Path
import json
import os
from typing import Optional, List, Dict, Any, Union

from ..utils.yaml_utils import load_yaml_file, write_yaml_file
from ..utils.config import get_repo_root
from ..utils.cursor_utils import update_cursor_mcp_json
from ruamel.yaml.comments import CommentedMap
from constants import (
    # Colors for output
    RED, GREEN, YELLOW, CYAN, NC,
    # Docker/container constants
    CONTAINER_ENTITY_PATH, DEFAULT_PORT_START, DEFAULT_MCP_CONTAINER_PORT_VAR,
    # Directory structure
    DIR_AI, DIR_GRAPH, DIR_ENTITIES, 
    # Environment variables
    ENV_MCP_GROUP_ID, ENV_MCP_USE_CUSTOM_ENTITIES, ENV_MCP_USE_CUSTOM_ENTITIES_VALUE, ENV_MCP_ENTITIES_DIR,
    ENV_MCP_ENTITIES,
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
    PROJECT_SERVICES_KEY, PROJECT_SERVER_ID_KEY, PROJECT_ENTITIES_DIR_KEY, 
    PROJECT_CONTAINER_NAME_KEY, PROJECT_PORT_DEFAULT_KEY, PROJECT_GROUP_ID_KEY, PROJECT_ENVIRONMENT_KEY, PROJECT_INCLUDE_ROOT_ENTITIES_KEY, # Added
    # Configuration keys
    CONFIG_KEY_SYNC_CURSOR_MCP_CONFIG,
    # Service name constants
    SERVICE_NAME_PREFIX,
    # Enums (Import LogLevel from constants now)
    LogLevel,
    # Environment variables (ensure new one is imported)
    ENV_MCP_INCLUDE_ROOT_ENTITIES # Added
)

# --- Docker Compose Header Constants ---
DOCKER_COMPOSE_HEADER_LINES = [
    "# Generated by graphiti CLI",
    "# Do not edit this file directly. Modify base-compose.yaml or project-specific mcp-config.yaml files instead.",
    "",
    "# --- Custom MCP Services Info ---"
]

def generate_compose_logic(
    repo_root: Path
):
    """
    Generates the final docker-compose.yml by merging base and project configs.
    
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
            # --- MODIFIED: Read entities_dir config (can be str or list) ---
            entities_dir_config = server_conf.get(PROJECT_ENTITIES_DIR_KEY)

            if not server_id or not entities_dir_config: # Check if config exists
                print(f"{YELLOW}Warning: Skipping service '{server_id}' in project '{project_name}' due to missing '{PROJECT_SERVER_ID_KEY}' or '{PROJECT_ENTITIES_DIR_KEY}'.{NC}")
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
                    update_cursor_mcp_json(project_root_dir, server_id, host_port)
                except (ValueError, TypeError) as e:
                    print(f"{YELLOW}Warning: Could not update Cursor MCP config due to invalid port: {e}{NC}")

            # --- Build Service Definition using CommentedMap ---
            new_service = CommentedMap()  # Use CommentedMap instead of regular dict
            # Add the merge key first using the anchor object
            new_service.add_yaml_merge([(0, custom_base_anchor_obj)])  # Merge base config

            new_service[COMPOSE_CONTAINER_NAME_KEY] = container_name
            new_service[COMPOSE_PORTS_KEY] = [port_mapping]  # Ports must be a list

            # --- Environment Variables ---
            env_vars = CommentedMap()  # Use CommentedMap instead of regular dict
            mcp_group_id = server_conf.get(PROJECT_GROUP_ID_KEY, project_name)  # Default group_id to project_name
            env_vars[ENV_MCP_GROUP_ID] = mcp_group_id
            # Set the default for custom entity usage FIRST
            env_vars[ENV_MCP_USE_CUSTOM_ENTITIES] = ENV_MCP_USE_CUSTOM_ENTITIES_VALUE # Default to True

            # --- NEW: Determine volume mount path and selection spec based on entities_dir_config type ---
            host_entity_path_rel_project = None # Path relative to project_root_dir for volume mount
            abs_host_entity_path = None # Absolute path for existence checks
            selection_spec = ""
            valid_config = True
            base_graph_path = project_root_dir / DIR_AI / DIR_GRAPH

            if isinstance(entities_dir_config, str):
                # Single directory specified (load all)
                relative_path = Path(entities_dir_config) # Relative to ai/graph/
                # Path relative to project root
                host_entity_path_rel_project = Path(DIR_AI) / DIR_GRAPH / relative_path
                abs_host_entity_path = project_root_dir / host_entity_path_rel_project # Keep absolute path for existence check
                if not abs_host_entity_path.is_dir(): # Check absolute path
                    # Add project_name context
                    print(f"{YELLOW}Warning (Project: '{project_name}', Service: '{service_name}'): Entity directory '{abs_host_entity_path}' does not exist. Volume mount might fail.{NC}")
                selection_spec = "" # Load all within the mounted dir

            elif isinstance(entities_dir_config, list):
                # List of subdirectories specified (selective load)
                if not entities_dir_config:
                    # Handle empty list: Default to loading all from standard 'entities' dir
                    # Add project_name context
                    print(f"{YELLOW}Warning (Project: '{project_name}', Service: '{service_name}'): Empty list provided for '{PROJECT_ENTITIES_DIR_KEY}'. Defaulting to loading all from '{DIR_ENTITIES}'.{NC}")
                    relative_path = Path(DIR_ENTITIES) # Use constant DIR_ENTITIES
                    # Path relative to project root
                    host_entity_path_rel_project = Path(DIR_AI) / DIR_GRAPH / relative_path
                    abs_host_entity_path = project_root_dir / host_entity_path_rel_project # Keep absolute path for existence check
                    if not abs_host_entity_path.is_dir():
                         # Add project_name context
                         print(f"{YELLOW}Warning (Project: '{project_name}', Service: '{service_name}'): Default entity directory '{abs_host_entity_path}' does not exist.{NC}") # Check absolute path
                    selection_spec = ""
                else:
                    # Process the list
                    # Keep absolute paths for commonpath logic and existence checks for now
                    absolute_paths = [(project_root_dir / DIR_AI / DIR_GRAPH / p).resolve() for p in entities_dir_config]
                    # Store relative paths for volume mount construction
                    relative_paths_to_project = [Path(DIR_AI) / DIR_GRAPH / p for p in entities_dir_config]

                    # Find common parent directory (absolute)
                    try:
                        common_parent_abs = Path(os.path.commonpath(absolute_paths))
                        if not common_parent_abs.is_dir():
                             common_parent_abs = common_parent_abs.parent # Use parent if common path is a file/subdir itself
                    except ValueError:
                         # Add project_name context
                         print(f"{RED}Error (Project: '{project_name}', Service: '{service_name}'): Cannot determine common parent for '{PROJECT_ENTITIES_DIR_KEY}' list. Paths might be invalid or on different drives.{NC}")
                         valid_config = False

                    if valid_config:
                        # Validate all paths share the *same* immediate parent
                        first_parent = absolute_paths[0].parent
                        if not all(p.parent == first_parent for p in absolute_paths):
                            # Add project_name context
                            print(f"{RED}Error (Project: '{project_name}', Service: '{service_name}'): Paths in '{PROJECT_ENTITIES_DIR_KEY}' list do not share the same immediate parent directory ('{first_parent}').{NC}")
                            valid_config = False
                        # Ensure the calculated common parent is the immediate parent
                        elif first_parent != common_parent_abs:
                             # Add project_name context
                             print(f"{RED}Error (Project: '{project_name}', Service: '{service_name}'): Paths in '{PROJECT_ENTITIES_DIR_KEY}' list must reside directly under a single common parent. Found parent '{first_parent}', but common path resolves differently ('{common_parent_abs}'). Check paths.{NC}")
                             valid_config = False


                    if valid_config:
                        abs_host_entity_path = common_parent_abs # Keep absolute path for checks
                        # Determine the common parent relative to project root for volume mount
                        try:
                            # Use string representations of relative paths for commonpath
                            common_parent_rel_project = Path(os.path.commonpath([str(p) for p in relative_paths_to_project]))
                            # Check if the common path itself exists and is a directory relative to project_root_dir
                            if not (project_root_dir / common_parent_rel_project).is_dir():
                                 common_parent_rel_project = common_parent_rel_project.parent # Use parent if needed
                            host_entity_path_rel_project = common_parent_rel_project
                        except ValueError:
                             # This should have been caught earlier, but handle defensively
                             print(f"{RED}Internal Error (Project: '{project_name}', Service: '{service_name}'): Could not determine relative common parent path.{NC}")
                             valid_config = False # Mark as invalid if relative path fails
                             host_entity_path_rel_project = None # Ensure it's None

                        # Extract subdirs and validate existence
                        subdirs_to_select = []
                        for p_abs in absolute_paths:
                            subdir_name = p_abs.name
                            if not p_abs.is_dir():
                                # Add project_name context
                                print(f"{RED}Error (Project: '{project_name}', Service: '{service_name}'): Specified entity path '{p_abs}' is not a directory or does not exist.{NC}")
                                valid_config = False
                                break # Stop validation on first error
                            subdirs_to_select.append(subdir_name)

                        if valid_config:
                            # Validate subdir names don't contain commas
                            invalid_names = [name for name in subdirs_to_select if ',' in name]
                            if invalid_names:
                                # Add project_name context
                                print(f"{RED}Error (Project: '{project_name}', Service: '{service_name}'): Subdirectory names in '{PROJECT_ENTITIES_DIR_KEY}' cannot contain commas. Invalid names: {invalid_names}{NC}")
                                valid_config = False
                            else:
                                selection_spec = ",".join(subdirs_to_select)
            else:
                # Invalid type for entities_dir
                # Add project_name context
                print(f"{RED}Error (Project: '{project_name}', Service: '{service_name}'): Invalid type for '{PROJECT_ENTITIES_DIR_KEY}'. Expected string or list, got {type(entities_dir_config)}.{NC}")
                valid_config = False

            # --- Check validity before proceeding ---
            if not valid_config:
                # Add project_name context
                print(f"{RED}Skipping service '{service_name}' in project '{project_name}' due to invalid entity configuration.{NC}")
                continue # Skip to the next service in the loop

            # --- Set container path env var (always the same fixed path) ---
            env_vars[ENV_MCP_ENTITIES_DIR] = PROJECT_CONTAINER_ENTITY_PATH

            # Add project-specific environment variables from mcp-config.yaml
            # This allows overriding the default MCP_USE_CUSTOM_ENTITIES=true if set to "false" in the config,
            # and handles MCP_ENTITIES (setting to "" if not present)
            # --- MODIFIED: Set MCP_ENTITIES based *only* on the derived selection_spec ---
            env_vars[ENV_MCP_ENTITIES] = selection_spec

            # --- NEW: Handle include_root_entities flag ---
            # Default to True if the key is missing or not a boolean
            include_root = server_conf.get(PROJECT_INCLUDE_ROOT_ENTITIES_KEY, True)
            if not isinstance(include_root, bool):
                print(f"{YELLOW}Warning (Project: '{project_name}', Service: '{service_name}'): Invalid value for '{PROJECT_INCLUDE_ROOT_ENTITIES_KEY}'. Expected boolean, got {type(include_root)}. Defaulting to 'true'.{NC}")
                include_root = True
            # Set the environment variable as a string "true" or "false"
            env_vars[ENV_MCP_INCLUDE_ROOT_ENTITIES] = str(include_root).lower()
            # --- End NEW ---

            # Add other project-specific environment variables from mcp-config.yaml
            project_environment = server_conf.get(PROJECT_ENVIRONMENT_KEY, {})
            if isinstance(project_environment, dict):
                # Ensure MCP_ENTITIES from this logic isn't overwritten if accidentally present in project_environment
                project_environment.pop(ENV_MCP_ENTITIES, None)
                env_vars.update(project_environment)
            else:
                print(f"Warning: Invalid '{PROJECT_ENVIRONMENT_KEY}' section for service '{service_name}' in '{project_config_path}'. Expected a dictionary.")

            new_service[COMPOSE_ENVIRONMENT_KEY] = env_vars

            # --- Volumes ---
            # Ensure volumes list exists (might be added by anchor merge, check needed?)
            # setdefault is safer if anchor doesn't guarantee 'volumes'
            if COMPOSE_VOLUMES_KEY not in new_service:
                new_service[COMPOSE_VOLUMES_KEY] = []
            elif not isinstance(new_service[COMPOSE_VOLUMES_KEY], list):
                print(f"Warning: '{COMPOSE_VOLUMES_KEY}' merged from anchor for service '{service_name}' is not a list. Overwriting.")
                new_service[COMPOSE_VOLUMES_KEY] = []

            # --- MODIFIED: Append the entity volume mount using determined path ---
            # --- MODIFIED: Append the entity volume mount using determined relative path and placeholder ---
            if valid_config and host_entity_path_rel_project: # Check validity and if relative path was determined
                # Use POSIX path separators for consistency in the compose file
                host_path_str = host_entity_path_rel_project.as_posix()
                # Use mandatory environment variable placeholder
                # Ensure PROJECT_ROOT_DIR is defined in the environment where docker-compose runs
                volume_string = f"${{PROJECT_ROOT_DIR:?PROJECT_ROOT_DIR environment variable must be set}}/{host_path_str}:{PROJECT_CONTAINER_ENTITY_PATH}:ro"
                new_service[COMPOSE_VOLUMES_KEY].append(volume_string)
            elif valid_config and not host_entity_path_rel_project:
                 # This might happen if logic determines no mount is needed (e.g., empty list handled differently)
                 # Or if there was an internal error determining the relative path
                 print(f"{YELLOW}Warning (Project: '{project_name}', Service: '{service_name}'): No host entity path determined for volume mount. Skipping mount.{NC}")
            # else: # valid_config is False, error already printed

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
