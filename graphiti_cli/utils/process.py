#!/usr/bin/env python3
"""
Process execution utilities for the Graphiti CLI tool.
"""
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Union, Dict, Any

# Import shared constants from central constants module
from constants import (
    # ANSI colors
    RED, YELLOW, CYAN, NC
)

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