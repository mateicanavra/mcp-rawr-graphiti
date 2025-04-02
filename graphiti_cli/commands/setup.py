#!/usr/bin/env python3
"""
Setup verification commands for the Graphiti CLI tool.
This module contains functions for verifying the environment setup.
"""
import sys
import shutil
from pathlib import Path
import os
import dotenv

from ..utils.config import get_repo_root
from ..utils.process import run_command
from constants import (
    # ANSI colors
    RED, GREEN, YELLOW, CYAN, BOLD, NC,
    # Environment variables
    ENV_GRAPHITI_LOG_LEVEL,
)

def check_setup():
    """
    Verify that the environment is set up correctly for running Graphiti MCP.
    """
    print(f"{BOLD}Running setup checks...{NC}")
    all_ok = True
    
    # 1. Check Repo Root
    print(f"  Checking repository root detection...", end=" ")
    try:
        repo_root = get_repo_root()
        if repo_root and repo_root.is_dir():
            print(f"{GREEN}OK ({repo_root}){NC}")
        else:
            print(f"{RED}Failed (Could not determine repository root){NC}")
            all_ok = False
    except SystemExit:  # get_repo_root exits if not found
        # Error message already printed by get_repo_root
        all_ok = False
    except Exception as e:
        print(f"{RED}Failed ({e}){NC}")
        all_ok = False
        
    # 2. Check .env file and essential variables
    print(f"  Checking .env file and essential variables...", end=" ")
    try:
        # Explicitly load from .env in the repo root
        # dotenv.load_dotenv() by default searches parent dirs, which might be confusing
        env_path = get_repo_root() / ".env"
        if env_path.exists():
            loaded = dotenv.load_dotenv(dotenv_path=env_path, override=True)
            if not loaded:
                print(f"{YELLOW}Warning: Found .env file but failed to load it.{NC}")
            
            # Check essential variables
            missing_vars = []
            required_vars = ["NEO4J_USER", "NEO4J_PASSWORD", "OPENAI_API_KEY"]
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if not missing_vars:
                print(f"{GREEN}OK (Loaded {env_path}, required variables present){NC}")
            else:
                print(f"{RED}Failed (Missing variables: {', '.join(missing_vars)}){NC}")
                all_ok = False
        else:
            print(f"{RED}Failed (.env file not found at {env_path}){NC}")
            all_ok = False
    except Exception as e:
        print(f"{RED}Failed (Error checking .env: {e}){NC}")
        all_ok = False

    # 3. Check Docker command availability and daemon status
    print(f"  Checking Docker status...", end=" ")
    docker_ok = False
    try:
        # Check if docker command exists
        if shutil.which("docker"):
            # Check if docker daemon is running (simple check using docker info)
            result = run_command(["docker", "info"], check=False) # Don't exit on failure here
            if result.returncode == 0:
                print(f"{GREEN}OK (Docker command found and daemon appears responsive){NC}")
                docker_ok = True
            else:
                print(f"{RED}Failed (Docker command found, but daemon seems unresponsive or errored){NC}")
                print(f"  {YELLOW}Tip: Ensure Docker Desktop or Docker Engine service is running.{NC}")
                all_ok = False
        else:
            print(f"{RED}Failed (Docker command not found in PATH){NC}")
            print(f"  {YELLOW}Tip: Ensure Docker is installed and its command is in your system's PATH.{NC}")
            all_ok = False
    except Exception as e:
        print(f"{RED}Failed (Error checking Docker: {e}){NC}")
        all_ok = False

    # Final Summary
    print("-" * 20)
    if all_ok:
        print(f"{GREEN}{BOLD}Setup checks passed successfully!{NC}")
        print(f"You should be able to run {CYAN}graphiti compose{NC} and {CYAN}graphiti up{NC}.")
    else:
        print(f"{RED}{BOLD}Some setup checks failed.{NC} Please review the messages above.")
        sys.exit(1) # Exit with error code if checks fail 