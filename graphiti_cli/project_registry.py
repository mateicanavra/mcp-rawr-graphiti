#!/usr/bin/env python3
"""
Project registry utilities for the Graphiti CLI.
Contains functions for managing the central project registry,
which maps project names to their configuration details.
"""
from pathlib import Path
from typing import Dict, Any

from .yaml_utils import load_yaml_file, write_yaml_file
from constants import (
    # Colors for output
    RED, YELLOW,
    # Registry file keys
    REGISTRY_PROJECTS_KEY, REGISTRY_ROOT_DIR_KEY, REGISTRY_CONFIG_FILE_KEY, REGISTRY_ENABLED_KEY
)

# --- Registry File Header Constants ---
REGISTRY_HEADER_LINES = [
    "# !! WARNING: This file is managed by the 'graphiti init' command. !!",
    "# !! Avoid manual edits unless absolutely necessary.                 !!",
    "#",
    "# Maps project names to their configuration details.",
    "# Paths should be absolute for reliability.",
]

def update_registry_logic(
    registry_file: Path,
    project_name: str,
    root_dir: Path,  # Expecting resolved absolute path
    config_file: Path,  # Expecting resolved absolute path
    enabled: bool = True
) -> bool:
    """
    Updates the central project registry file (mcp-projects.yaml).
    
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
        initial_data = {REGISTRY_PROJECTS_KEY: {}}
        try:
            write_yaml_file(initial_data, registry_file, header=REGISTRY_HEADER_LINES)
        except Exception:
            return False  # Error handled in write_yaml_file

    # Load existing registry data
    data = load_yaml_file(registry_file, safe=False)
    if data is None:
        print(f"Error: Could not load registry file {registry_file}")
        return False

    if not isinstance(data, dict) or REGISTRY_PROJECTS_KEY not in data:
        print(f"Error: Invalid registry file format in {registry_file}. Missing '{REGISTRY_PROJECTS_KEY}' key.")
        return False

    # Ensure 'projects' key exists and is a map
    if data.get(REGISTRY_PROJECTS_KEY) is None:
        data[REGISTRY_PROJECTS_KEY] = {}
    elif not isinstance(data[REGISTRY_PROJECTS_KEY], dict):
        print(f"Error: '{REGISTRY_PROJECTS_KEY}' key in {registry_file} is not a dictionary.")
        return False

    # Add or update the project entry (convert Paths to strings for YAML)
    project_entry = {
        REGISTRY_ROOT_DIR_KEY: str(root_dir),
        REGISTRY_CONFIG_FILE_KEY: str(config_file),
        REGISTRY_ENABLED_KEY: enabled
    }
    data[REGISTRY_PROJECTS_KEY][project_name] = project_entry

    # Write back to the registry file
    try:
        write_yaml_file(data, registry_file, header=REGISTRY_HEADER_LINES)
        print(f"Successfully updated registry for project '{project_name}'")
        return True
    except Exception:
        return False  # Error handled in write_yaml_file
