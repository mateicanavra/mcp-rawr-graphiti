#!/usr/bin/env python3
"""
Configuration handling utilities for the Graphiti CLI tool.
"""
import os
import sys
from pathlib import Path
from typing import Optional

# Import shared constants from central constants module
from constants import (
    # ANSI colors
    RED, GREEN, YELLOW, BLUE, CYAN, BOLD, NC,
    # Environment variables
    ENV_REPO_PATH,
    # Files
    FILE_PYPROJECT_TOML,
    # Directory structure
    DIR_ENTITIES,
)
from ..utils.paths import _validate_repo_path

# --- Constants for Configuration ---
CONFIG_DIR_NAME = ".config/graphiti"
CONFIG_FILE_NAME = "repo_path.txt"

def get_config_path() -> Path:
    """Gets the path to the user-specific config file (plain text)."""
    home = Path.home()
    config_dir = home / CONFIG_DIR_NAME
    return config_dir / CONFIG_FILE_NAME

def load_config() -> Optional[str]:
    """Loads the repository path from the user-specific config file (plain text)."""
    config_path = get_config_path()
    if config_path.is_file(): # Check if it's a file, not just exists
        try:
            with open(config_path, 'r') as f:
                path_str = f.readline().strip()
                return path_str if path_str else None # Return None if file is empty
        except Exception as e:
            print(f"{YELLOW}Warning: Could not load config file {config_path}: {e}{NC}")
    return None

def save_config(repo_path_str: str):
    """Saves the repository path to the user-specific config file (plain text)."""
    config_path = get_config_path()
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            f.write(repo_path_str + '\n') # Write path with newline
    except Exception as e:
        print(f"{RED}Error: Could not save config file {config_path}: {e}{NC}")

def _get_validated_path_from_config() -> Optional[Path]:
    """Attempts to load and validate the repo path from the config text file."""
    path_str = load_config() # Loads path string directly
    if path_str:
        # Basic validation: Check if it looks like an absolute path before creating Path object
        # This is a basic sanity check, _validate_repo_path does the real check.
        if not os.path.isabs(path_str) and not path_str.startswith('~'):
             print(f"{YELLOW}Warning: Path '{path_str}' from config file is not absolute. Ignoring.{NC}")
             return None
             
        try:
            # Resolve ~ and make absolute
            repo_path = Path(path_str).expanduser().resolve()
            if _validate_repo_path(repo_path):
                return repo_path
            else:
                print(f"{YELLOW}Warning: Path '{repo_path}' from config file is invalid. Ignoring.{NC}")
        except Exception as e:
             print(f"{YELLOW}Warning: Error processing path '{path_str}' from config file: {e}. Ignoring.{NC}")
    return None

def _prompt_and_save_repo_path() -> Optional[Path]:
    """Prompts the user for the repo path, validates it, and saves it."""
    print(f"{YELLOW}Could not automatically locate the rawr-mcp-graphiti repository directory.{NC}")
    print("This directory contains essential configuration files (like base-compose.yaml).")
    
    while True:
        try:
            path_str = input(f"Please enter the {BOLD}absolute path{NC} to your cloned 'rawr-mcp-graphiti' repository: ").strip()
            if not path_str:
                print(f"{RED}Path cannot be empty. Please try again or press Ctrl+C to exit.{NC}")
                continue
                
            repo_path = Path(path_str).expanduser().resolve() # Expand ~ and make absolute
            
            if _validate_repo_path(repo_path):
                save_config(str(repo_path)) # Save path string directly
                print(f"{GREEN}Repository path saved to {get_config_path()}.{NC}")
                return repo_path
            else:
                print(f"{RED}Invalid path: '{repo_path}'. Directory must exist and contain '{FILE_PYPROJECT_TOML}', 'graphiti_cli/', and '{DIR_ENTITIES}/'.{NC}")
                print(f"{YELLOW}Please ensure you provide the correct absolute path.{NC}")
        except EOFError:
            print(f"\n{RED}Operation cancelled by user.{NC}")
            return None
        except KeyboardInterrupt:
            print(f"\n{RED}Operation cancelled by user.{NC}")
            return None
        except Exception as e:
            print(f"{RED}An unexpected error occurred: {e}{NC}")
            return None # Exit loop on unexpected error

def _find_repo_root() -> Optional[Path]:
    """
    Internal function to find the repository root directory using multiple strategies.

    Order of discovery:
    1. Environment Variable (`MCP_GRAPHITI_REPO_PATH`)
    2. User Configuration File (`~/.config/graphiti/repo_path.txt`)
    3. Relative path guessing (based on __file__ location, cwd) - Less reliable for installed CLIs.
    4. Prompt user if none of the above work.

    Returns:
        Optional[Path]: The absolute path to the repository root, or None if not found and user cancels prompt.
    """
    # 1. Check environment variable first (as an override)
    if ENV_REPO_PATH in os.environ:
        path_str = os.environ[ENV_REPO_PATH]
        repo_path = Path(path_str).expanduser().resolve()
        if _validate_repo_path(repo_path):
            return repo_path
        else:
             # Clearer warning if env var is set but invalid
             print(f"{YELLOW}Warning: Environment variable {ENV_REPO_PATH} is set ('{path_str}') but points to an invalid repository path. Trying other methods...{NC}")

    # 2. Check user configuration file
    config_path = _get_validated_path_from_config()
    if config_path:
        return config_path

    # 3. Try relative path guessing (less reliable for pipx installs)
    # Based on script location
    try:
        current_file = Path(__file__).resolve()
        if "graphiti_cli" in current_file.parts:
            potential_root = current_file.parents[1]
            if _validate_repo_path(potential_root):
                return potential_root
    except NameError: # __file__ might not be defined in some contexts (e.g. frozen executables)
        pass 

    # Based on current directory
    current_dir = Path.cwd()
    if _validate_repo_path(current_dir):
        return current_dir
    
    # Based on parent directory
    parent_dir = current_dir.parent
    if _validate_repo_path(parent_dir):
        return parent_dir

    # 4. Prompt user if no path found yet
    return _prompt_and_save_repo_path() # This will prompt, validate, save, and return the path, or None

def get_repo_root() -> Path:
    """
    Get the repository root directory, exiting if not found.

    This function now incorporates config file reading and user prompting.

    Returns:
        Path: The absolute path to the repository root.

    Raises:
        SystemExit: If the repository root cannot be found (e.g., user cancels prompt).
    """
    repo_root = _find_repo_root()
    if repo_root is None:
        # Error message is now handled within _prompt_and_save_repo_path if prompting fails
        print(f"{RED}Error: Could not determine the rawr-mcp-graphiti repository root.{NC}")
        print(f"Please ensure it exists and is accessible, or try setting the {CYAN}{ENV_REPO_PATH}{NC} environment variable.")
        sys.exit(1)
    return repo_root 