#!/usr/bin/env python3
"""
Project registry utilities for the Graphiti CLI.
Contains functions for managing the central project registry,
which maps project names to their configuration details.
"""
import os
from pathlib import Path
from typing import Dict, Any

from ..utils.yaml_utils import load_yaml_file, write_yaml_file
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
    "# Paths should be relative to this file's location (repo root).",
]

def update_registry_logic(
    registry_file: Path,
    project_name: str,
    root_dir: Path,  # Project root directory path (can be relative or absolute)
    config_file: Path,  # Project config file path (can be relative or absolute)
    enabled: bool = True
) -> bool:
    """
    Updates the central project registry file (mcp-projects.yaml).
    
    Args:
        registry_file (Path): Path to the registry file
        project_name (str): Name of the project
        root_dir (Path): Path to the project root directory (will be stored relative to registry_file)
        config_file (Path): Path to the project config file (will be stored relative to registry_file)
        enabled (bool): Whether the project should be enabled
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"Updating registry '{registry_file}' for project '{project_name}'")
    # Resolve paths relative to the registry file's directory (repo root)
    # This ensures consistency even if absolute paths are passed in.
    registry_dir = registry_file.parent.resolve()
    root_dir_abs = root_dir.resolve()
    config_file_abs = config_file.resolve()

    try:
        root_dir_relative = os.path.relpath(root_dir_abs, start=registry_dir)
        config_file_relative = os.path.relpath(config_file_abs, start=registry_dir)
    except ValueError as e:
        print(f"{RED}Error calculating relative paths (are paths on different drives?): {e}{NC}")
        print(f"  Registry Dir: {registry_dir}")
        print(f"  Root Dir Abs: {root_dir_abs}")
        print(f"  Config File Abs: {config_file_abs}")
        return False

    if not config_file_abs.exists():
        print(f"{YELLOW}Warning: Project config file '{config_file_abs}' does not exist (using path '{config_file_relative}').{NC}")
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
        REGISTRY_ROOT_DIR_KEY: root_dir_relative,
        REGISTRY_CONFIG_FILE_KEY: config_file_relative,
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
