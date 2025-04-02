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

# --- Path Finding Functions ---
def _find_repo_root() -> Optional[Path]:
    """
    Internal function to find the repository root directory.
    
    The repository root is identified by the presence of:
    - A graphiti_cli/ directory
    - A entity_types/ directory
    - A pyproject.toml file
    
    Returns:
        Optional[Path]: The absolute path to the repository root, or None if not found.
    """
    # First check environment variable
    if ENV_REPO_PATH in os.environ:
        repo_path = Path(os.environ[ENV_REPO_PATH])
        if _validate_repo_path(repo_path):
            return repo_path.resolve()
        print(f"{YELLOW}Warning: {ENV_REPO_PATH} is set but points to invalid path: {repo_path}{NC}")
    
    # Try to find the repo root automatically based on script location
    # Current script should be in graphiti_cli/core.py
    current_file = Path(__file__).resolve()
    if "graphiti_cli" in current_file.parts:
        # Go up to the parent of graphiti_cli to reach repo root
        potential_root = current_file.parents[1]  # One level up from core.py
        if _validate_repo_path(potential_root):
            return potential_root
        
    # Check current directory
    current_dir = Path.cwd()
    if _validate_repo_path(current_dir):
        return current_dir
    
    # Check one level up
    parent_dir = current_dir.parent
    if _validate_repo_path(parent_dir):
        return parent_dir
    
    return None

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
    
    Returns:
        Path: The absolute path to the repository root
    """
    repo_root = _find_repo_root()
    if repo_root is None:
        print(f"{RED}Error: Could not find repository root.{NC}")
        print(f"Please set the {CYAN}{ENV_REPO_PATH}{NC} environment variable to the root of your mcp-graphiti repository.")
        print(f"Example: {YELLOW}export {ENV_REPO_PATH}=/path/to/mcp-graphiti{NC}")
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
