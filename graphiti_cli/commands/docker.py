#!/usr/bin/env python3
"""
Docker-related commands for the Graphiti CLI tool.
This module contains functions for managing Docker container operations.
"""
import sys
from pathlib import Path
from typing import List

from ..utils.config import get_repo_root
from ..utils.process import run_command
from constants import (
    # Logging
    DEFAULT_LOG_LEVEL_STR,
    LogLevel,
    # ANSI colors
    RED, GREEN, YELLOW, BLUE, CYAN, BOLD, NC,
    # Files and directories
    FILE_PYPROJECT_TOML, DIR_DIST,
    # Package constants
    PACKAGE_LOCAL_WHEEL_MARKER, PACKAGE_PUBLISHED_PREFIX
)
from ..logic import compose_generator

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
    This is called before commands like 'up', 'down', 'restart' to ensure
    the compose file reflects the latest project configurations.
    """
    print("Ensuring docker-compose.yml is up-to-date...")
    repo_root = get_repo_root()
    compose_file = repo_root / "docker-compose.yml"

    if not compose_file.is_file():
        print(f"{YELLOW}docker-compose.yml not found. Generating...{NC}")
        try:
            # Use the already imported module
            compose_generator.generate_compose_logic(repo_root)
            # Success message is often printed within the generation logic itself
            # print(f"{GREEN}Successfully generated docker-compose.yml{NC}")
        except Exception as e: # Catch other potential errors during generation
            print(f"{RED}Error generating docker-compose.yml: {e}{NC}")
            # Optionally, print more traceback info here for debugging
            # import traceback
            # traceback.print_exc()
            sys.exit(1)
    # else: # Optional: Add check for outdated file and regenerate if needed
    #     print(f"{GREEN}Found existing docker-compose.yml: {compose_file}{NC}")

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

def docker_up(detached: bool, log_level: str):
    """
    Start all containers using Docker Compose (builds first).
    Always regenerates the docker-compose.yml file to ensure latest configuration.
    
    Args:
        detached (bool): Whether to run in detached mode
        log_level (str): Log level to use
    """
    ensure_dist_for_build()
    
    # Always regenerate the docker-compose.yml file to ensure latest configuration
    repo_root = get_repo_root()
    print(f"{CYAN}Regenerating docker-compose.yml to ensure latest configuration...{NC}")
    compose_generator.generate_compose_logic(repo_root)
    
    cmd = ["up", "--build", "--force-recreate"]
    run_docker_compose(cmd, log_level, detached)
    print(f"{GREEN}Docker compose up completed.{NC}")

def docker_down(log_level: str):
    """
    Stop and remove all containers using Docker Compose.
    
    Args:
        log_level (str): Log level to use
    """
    run_docker_compose(["down"], log_level)
    print(f"{GREEN}Docker compose down completed.{NC}")

def docker_restart(detached: bool, log_level: str):
    """
    Restart all containers: runs 'down' then 'up'.
    
    Args:
        detached (bool): Whether to run in detached mode
        log_level (str): Log level to use
    """
    print(f"{BOLD}Restarting Graphiti containers: first down, then up...{NC}")
    run_docker_compose(["down"], log_level)
    docker_up(detached, log_level)
    print(f"{GREEN}Restart sequence completed.{NC}")

def docker_reload(service_name: str):
    """
    Restart a specific running service container.
    Always regenerates the docker-compose.yml file to ensure latest configuration.
    
    Args:
        service_name (str): Name of the service to reload
    """
    ensure_docker_compose_file()
    print(f"{BOLD}Attempting to restart service '{CYAN}{service_name}{NC}'...{NC}")
    
    # Always regenerate the docker-compose.yml file to ensure latest configuration
    repo_root = get_repo_root()
    print(f"{CYAN}Regenerating docker-compose.yml to ensure latest configuration...{NC}")
    compose_generator.generate_compose_logic(repo_root)
    
    try:
        run_docker_compose(["restart", service_name], log_level=DEFAULT_LOG_LEVEL_STR)
        print(f"{GREEN}Service '{service_name}' restarted successfully.{NC}")
    except Exception:
        print(f"{RED}Failed to restart service '{service_name}'. Check service name and if stack is running.{NC}")
        sys.exit(1)

def docker_compose_generate():
    """
    Generate docker-compose.yml from base and project configs.
    """
    print(f"{BOLD}Generating docker-compose.yml from templates...{NC}")
    ensure_docker_compose_file()
    try:
        repo_root = get_repo_root()
        compose_generator.generate_compose_logic(repo_root)  # Generate with default level
        # Success message printed within generate_compose_logic
    except Exception as e:
        print(f"{RED}Error: Failed to generate docker-compose.yml file: {e}{NC}")
        sys.exit(1) 