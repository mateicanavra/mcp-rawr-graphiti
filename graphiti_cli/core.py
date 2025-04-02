#!/usr/bin/env python3
"""
Core utility functions for the Graphiti CLI tool.
Contains path finding, subprocess execution, and common constants.
"""
import os
import sys
import subprocess
from pathlib import Path
from enum import Enum
import shutil
from typing import List, Optional, Union, Dict, Any

# Import shared constants from central constants module
from constants import (
    # ANSI colors
    RED, GREEN, YELLOW, BLUE, CYAN, BOLD, NC,
    # Directory structure
    DIR_MCP_SERVER, DIR_ENTITY_TYPES, DIR_AI, DIR_GRAPH, DIR_ENTITIES, DIR_DIST,
    # Files
    FILE_PYPROJECT_TOML, FILE_GIT_KEEP,
    # Validation
    REGEX_VALID_NAME,
    # Docker/container defaults
    DEFAULT_PORT_START, DEFAULT_MCP_CONTAINER_PORT_VAR, CONTAINER_ENTITY_PATH,
    # Environment variables
    ENV_REPO_PATH,
    # Package constants
    PACKAGE_LOCAL_WHEEL_MARKER, PACKAGE_PUBLISHED_PREFIX
)

# --- Constants for Configuration ---
CONFIG_DIR_NAME = ".config/graphiti"
CONFIG_FILE_NAME = "repo_path.txt" # Changed from config.yaml
# CONFIG_REPO_PATH_KEY = "repository_path" # No longer needed for plain text

# --- Enums ---
class LogLevel(str, Enum):
    """
    Log levels for Docker Compose and container execution.
    """
    debug = "debug"
    info = "info"
    warn = "warn"
    error = "error"
    fatal = "fatal"
    
    def __str__(self) -> str:
        return self.value

# --- Configuration Handling ---

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

# --- Path Finding Functions ---

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
                # config = load_config() # No need to load existing config for plain text overwrite
                # config[CONFIG_REPO_PATH_KEY] = str(repo_path) # Store as string
                save_config(str(repo_path)) # Save path string directly
                print(f"{GREEN}Repository path saved to {get_config_path()}.{NC}")
                return repo_path
            else:
                print(f"{RED}Invalid path: '{repo_path}'. Directory must exist and contain '{FILE_PYPROJECT_TOML}', 'graphiti_cli/', and '{DIR_ENTITY_TYPES}/'.{NC}")
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
            # print(f"{BLUE}Using repo path from environment variable {ENV_REPO_PATH}: {repo_path}{NC}") # Optional: Debug message
            return repo_path
        else:
             # Clearer warning if env var is set but invalid
             print(f"{YELLOW}Warning: Environment variable {ENV_REPO_PATH} is set ('{path_str}') but points to an invalid repository path. Trying other methods...{NC}")

    # 2. Check user configuration file
    config_path = _get_validated_path_from_config()
    if config_path:
        # print(f"{BLUE}Using repo path from config file: {config_path}{NC}") # Optional: Debug message
        return config_path

    # 3. Try relative path guessing (less reliable for pipx installs)
    # Based on script location
    try:
        current_file = Path(__file__).resolve()
        if "graphiti_cli" in current_file.parts:
            potential_root = current_file.parents[1]
            if _validate_repo_path(potential_root):
                # print(f"{BLUE}Using repo path based on script location: {potential_root}{NC}") # Optional: Debug message
                return potential_root
    except NameError: # __file__ might not be defined in some contexts (e.g. frozen executables)
        pass 

    # Based on current directory
    current_dir = Path.cwd()
    if _validate_repo_path(current_dir):
        # print(f"{BLUE}Using repo path based on current directory: {current_dir}{NC}") # Optional: Debug message
        return current_dir
    
    # Based on parent directory
    parent_dir = current_dir.parent
    if _validate_repo_path(parent_dir):
        # print(f"{BLUE}Using repo path based on parent directory: {parent_dir}{NC}") # Optional: Debug message
        return parent_dir

    # 4. Prompt user if no path found yet
    # print(f"{YELLOW}Could not find repository root via environment, config, or relative paths. Prompting user...{NC}") # Optional: Debug message
    return _prompt_and_save_repo_path() # This will prompt, validate, save, and return the path, or None

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

def get_mcp_server_dir() -> Path:
    """
    Get the server directory path (which is now the repository root).
    
    Returns:
        Path: The absolute path to the repository root
    """
    return get_repo_root()

# --- Process Execution Functions ---
def run_command(
    cmd: List[str], 
    check: bool = False, 
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[Union[str, Path]] = None
) -> subprocess.CompletedProcess:
    """
    Run a command in a subprocess with proper error handling.
    Output is streamed to stdout/stderr by default.
    
    Args:
        cmd (List[str]): Command and arguments as a list
        check (bool): If True, check the return code and raise CalledProcessError if non-zero
        env (Optional[Dict[str, str]]): Environment variables to set for the command
        cwd (Optional[Union[str, Path]]): Directory to run the command in
        
    Returns:
        subprocess.CompletedProcess: Result of the command
    """
    cmd_str = " ".join(cmd)
    
    # Use current environment and update with any provided environment variables
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    
    try:
        return subprocess.run(
            cmd,
            check=check,
            env=merged_env,
            cwd=cwd,
            text=True,
            capture_output=False  # Allow output to stream to terminal
        )
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error: Command failed with exit code {e.returncode}:{NC}")
        print(f"Command: {CYAN}{cmd_str}{NC}")
        # Note: with capture_output=False, e.stdout and e.stderr will be None
        # Error output will have been streamed directly to the terminal
        if e.stdout:
            print(f"{YELLOW}--- Command output ---{NC}")
            print(e.stdout)
        if e.stderr:
            print(f"{RED}--- Command error ---{NC}")
            print(e.stderr)
        if check:
            sys.exit(e.returncode)
        raise
    except Exception as e:
        print(f"{RED}Error: Failed to execute command: {cmd_str}{NC}")
        print(f"Error details: {e}")
        if check:
            sys.exit(1)
        raise

def run_docker_compose(
    subcmd: List[str], 
    log_level: str = LogLevel.info.value, 
    detached: bool = False
) -> None:
    """
    Run a docker compose command with consistent environment settings.
    
    Args:
        subcmd (List[str]): Docker compose subcommand and arguments
        log_level (str): Log level to set in environment
        detached (bool): Whether to add the -d flag for detached mode
    """
    repo_root = get_repo_root()
    
    # Ensure the docker-compose.yml file exists
    ensure_docker_compose_file()
    
    # Add -d flag if detached mode is requested
    if detached and subcmd[0] in ["up", "restart"]:  # Add restart for consistency
        subcmd.append("-d")
    
    # Prepare full command
    cmd = ["docker", "compose"] + subcmd
    
    print(f"Running Docker Compose from: {CYAN}{repo_root}{NC}")
    print(f"Command: {' '.join(cmd)}")
    if log_level != LogLevel.info.value:
        print(f"Log level: {CYAN}{log_level}{NC}")
    
    # Execute the command - Pass the log level as an environment variable
    env = {"GRAPHITI_LOG_LEVEL": log_level}
    run_command(cmd, check=True, env=env, cwd=repo_root)

def ensure_docker_compose_file() -> None:
    """
    Ensure that the docker-compose.yml file exists by generating it if necessary.
    """
    repo_root = get_repo_root()
    compose_file = repo_root / "docker-compose.yml"
    
    # Use our Python utility (to be implemented in yaml_utils.py) instead of the script
    # Will be implemented after yaml_utils.py is created
    from . import yaml_utils
    try:
        yaml_utils.generate_compose_logic(repo_root)  # Generate with default log level initially
    except Exception as e:
        print(f"{YELLOW}Continuing with existing file if it exists.{NC}")
    
    # Check if the file exists now
    if not compose_file.exists():
        print(f"{RED}Error: docker-compose.yml file does not exist and could not be generated.{NC}")
        sys.exit(1)

def ensure_dist_for_build() -> None:
    """
    Ensure that the dist directory is available for Docker build if needed.
    
    This function checks if the graphiti-core package is configured to use a local wheel.
    If so, it ensures the dist directory exists and copies the wheel files.
    """
    repo_root = get_repo_root()
    
    print(f"{BOLD}Checking build configuration...{NC}")
    
    # Check pyproject.toml to see if we're using local wheel
    pyproject_path = repo_root / FILE_PYPROJECT_TOML
    try:
        with open(pyproject_path, 'r') as f:
            pyproject_content = f.read()
            
        # Check if we're using local wheel and not published package
        # Fix: Check for the marker ONLY in uncommented lines
        using_local_wheel = any(
            PACKAGE_LOCAL_WHEEL_MARKER in line
            for line in pyproject_content.splitlines()
            if not line.strip().startswith('#')
        )
        using_published = any(
            line.strip().startswith(PACKAGE_PUBLISHED_PREFIX) 
            for line in pyproject_content.splitlines()
            if not line.strip().startswith('#')
        )
        
        if not using_local_wheel or using_published:
            print(f"{CYAN}Using published graphiti-core package. Skipping local wheel setup.{NC}")
            return
        
        print(f"{CYAN}Local graphiti-core wheel configuration detected.{NC}")
        
        # Source and target paths
        dist_dir = repo_root / DIR_DIST
        
        # Check if dist exists
        if not dist_dir.is_dir():
            print(f"{RED}Error: dist directory not found at {dist_dir}{NC}")
            print(f"Please build the graphiti-core wheel first.")
            sys.exit(1)
        
        # Find wheel files
        wheel_files = list(dist_dir.glob("*.whl"))
        if not wheel_files:
            print(f"{RED}Error: No wheel files found in {dist_dir}{NC}")
            print(f"Please build the graphiti-core wheel first.")
            sys.exit(1)
        
        print(f"{GREEN}Dist directory verified for Docker build.{NC}")
    
    except Exception as e:
        print(f"{RED}Error checking build configuration: {e}{NC}")
        print(f"{YELLOW}Please ensure your pyproject.toml is properly configured.{NC}")
        sys.exit(1)
