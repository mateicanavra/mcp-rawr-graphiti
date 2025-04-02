#!/usr/bin/env python3
"""
Path-related utility functions for the Graphiti CLI tool.
"""
import os
from pathlib import Path

# Import shared constants from central constants module
from constants import (
    # Files
    FILE_PYPROJECT_TOML,
    # Directory structure
    DIR_ENTITY_TYPES,
)

def _validate_repo_path(path: Path) -> bool:
    """
    Validates that a given path is a valid repository root.
    
    Args:
        path (Path): Path to validate
        
    Returns:
        bool: True if the path is a valid repository root, False otherwise
    """
    if not path.is_dir():
        return False
    
    # Check for essential directories
    graphiti_cli_dir = path / "graphiti_cli"
    entity_types_dir = path / DIR_ENTITY_TYPES
    pyproject_file = path / FILE_PYPROJECT_TOML
    
    return graphiti_cli_dir.is_dir() and entity_types_dir.is_dir() and pyproject_file.is_file()

def get_mcp_server_dir() -> Path:
    """
    Get the server directory path (which is now the repository root).
    
    Returns:
        Path: The absolute path to the repository root
    """
    from ..utils.config import get_repo_root
    return get_repo_root() 