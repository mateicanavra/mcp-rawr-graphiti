#!/usr/bin/env python3
"""
YAML utility functions for the Graphiti CLI.
Contains functions for loading/saving YAML files with standardized error handling.
"""
from pathlib import Path
from ruamel.yaml import YAML
from typing import Optional, List, Any

# --- YAML Instances ---
yaml_rt = YAML()  # Round-Trip for preserving structure/comments
yaml_rt.preserve_quotes = True
yaml_rt.indent(mapping=2, sequence=4, offset=2)

yaml_safe = YAML(typ='safe')  # Safe loader for reading untrusted/simple config

# --- File Handling ---
def load_yaml_file(file_path: Path, safe: bool = False) -> Optional[Any]:
    """
    Loads a YAML file, handling errors.
    
    Args:
        file_path (Path): Path to the YAML file
        safe (bool): Whether to use the safe loader (True) or round-trip loader (False)
        
    Returns:
        Optional[Any]: The parsed YAML data, or None if loading failed
    """
    yaml_loader = yaml_safe if safe else yaml_rt
    if not file_path.is_file():
        print(f"Warning: YAML file not found or is not a file: {file_path}")
        return None
    try:
        with file_path.open('r') as f:
            return yaml_loader.load(f)
    except Exception as e:
        print(f"Error parsing YAML file '{file_path}': {e}")
        return None  # Or raise specific exception

def write_yaml_file(data: Any, file_path: Path, header: Optional[List[str]] = None):
    """
    Writes data to a YAML file using round-trip dumper.
    
    Args:
        data (Any): The data to write to the file
        file_path (Path): Path to the output file
        header (Optional[List[str]]): Optional list of comment lines to add at the top of the file
    
    Raises:
        IOError: If the file cannot be written
        Exception: For other errors
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open('w') as f:
            if header:
                f.write("\n".join(header) + "\n\n")  # Add extra newline
            yaml_rt.dump(data, f)
    except IOError as e:
        print(f"Error writing YAML file '{file_path}': {e}")
        raise  # Re-raise after printing
    except Exception as e:
        print(f"An unexpected error occurred during YAML dumping to '{file_path}': {e}")
        raise
