#!/usr/bin/env python3
"""
Project management commands for the Graphiti CLI tool.
This module contains functions for initializing and managing Graphiti projects.
"""
import sys
import os
import re  # For entity name validation
from pathlib import Path

from ..utils.config import get_repo_root
from constants import (
    # ANSI colors
    RED, GREEN, YELLOW, CYAN, BOLD, NC,
    # Configuration constants
    CONFIG_FILENAME, ENTITY_FILE_EXTENSION,
    CONFIG_KEY_SERVICES, CONFIG_KEY_ID, CONFIG_KEY_CONTAINER_NAME, 
    CONFIG_KEY_PORT_DEFAULT, CONFIG_KEY_GROUP_ID, CONFIG_KEY_ENTITIES_DIR,
    CONFIG_KEY_ENVIRONMENT, CONFIG_KEY_SYNC_CURSOR_MCP_CONFIG,
    # Default values
    DEFAULT_CUSTOM_CONTAINER_NAME, DEFAULT_CUSTOM_PORT, DEFAULT_ENTITIES_DIR_NAME,
    # Environment variables
    ENV_GRAPHITI_LOG_LEVEL,
    # Logging
    DEFAULT_LOG_LEVEL_STR,
    # Directory structure
    DIR_AI, DIR_GRAPH, DIR_ENTITIES, FILE_GIT_KEEP, DIR_PROJECT_ASSETS,
    # Validation
    REGEX_VALID_NAME,
    # Service name constants
    DEFAULT_SERVICE_SUFFIX
)
from ..utils.yaml_utils import load_yaml_file
from ..logic.project_registry import update_registry_logic

# --- Project Assets Constants ---
DIR_RULES = "rules"
DIR_ENTITY_TEMPLATES = "entity_templates"
DIR_EXAMPLES = "examples"
DIR_TEMPLATES = "templates"
FILE_CORE_RULE = "graphiti-mcp-core-rules.md"
FILE_MAINT_RULE = "graphiti-knowledge-graph-maintenance.md"
FILE_SCHEMA_TEMPLATE = "schema_template.py"
FILE_ENTITY_EXAMPLE = "custom_entity_example.py"

# --- Entity Template Constants ---
ENTITY_CLASS_PATTERN = "class Product(BaseModel):"
ENTITY_DESC_PATTERN_PRODUCT = "A Product represents"
ENTITY_DESC_PATTERN_ABOUT_PRODUCTS = "about Products mentioned"
ENTITY_DESC_PATTERN_PRODUCT_NAMES = "product names"
ENTITY_DESC_PATTERN_PRODUCT_BELONGS = "the product belongs"
ENTITY_DESC_PATTERN_PRODUCT_DESC = "description of the product"


def init_project(project_name: str, target_dir: Path):
    """
    Initialize a new Graphiti project.
    
    Args:
        project_name (str): Name of the project
        target_dir (Path): Target directory for the project
    """
    # Basic validation
    if not re.fullmatch(REGEX_VALID_NAME, project_name):
        print(f"{RED}Error: Invalid PROJECT_NAME '{project_name}'. Use only letters, numbers, underscores, and hyphens.{NC}")
        sys.exit(1)

    print(f"Initializing Graphiti project '{CYAN}{project_name}{NC}' in '{CYAN}{target_dir}{NC}'...")

    # Create ai/graph directory structure
    graph_dir = target_dir / DIR_AI / DIR_GRAPH
    try:
        graph_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory structure: {CYAN}{graph_dir}{NC}")
    except OSError as e:
        print(f"{RED}Error creating directory structure {graph_dir}: {e}{NC}")
        sys.exit(1)

    # Create mcp-config.yaml in ai/graph directory
    config_path = graph_dir / CONFIG_FILENAME
    config_content = f"""# Configuration for project: {project_name}
{CONFIG_KEY_SERVICES}:
  - {CONFIG_KEY_ID}: {project_name}{DEFAULT_SERVICE_SUFFIX}  # Service ID (used for default naming)
    # {CONFIG_KEY_CONTAINER_NAME}: "{DEFAULT_CUSTOM_CONTAINER_NAME}"  # Optional: Specify custom container name
    # {CONFIG_KEY_PORT_DEFAULT}: {DEFAULT_CUSTOM_PORT}             # Optional: Specify custom host port
    {CONFIG_KEY_GROUP_ID}: "{project_name}"       # Graph group ID
    {CONFIG_KEY_ENTITIES_DIR}: "{DEFAULT_ENTITIES_DIR_NAME}"           # Relative path to entity definitions within ai/graph
    {CONFIG_KEY_ENVIRONMENT}:                     # Optional: Add non-secret env vars here
      {ENV_GRAPHITI_LOG_LEVEL}: "{DEFAULT_LOG_LEVEL_STR}"
    {CONFIG_KEY_SYNC_CURSOR_MCP_CONFIG}: true   # Automatically update .cursor/mcp.json during 'compose'
"""
    try:
        config_path.write_text(config_content)
        print(f"Created template {CYAN}{config_path}{NC}")
    except OSError as e:
        print(f"{RED}Error creating config file {config_path}: {e}{NC}")
        sys.exit(1)

    # Create entities directory within ai/graph
    entities_dir = graph_dir / DIR_ENTITIES
    try:
        entities_dir.mkdir(exist_ok=True)
        (entities_dir / FILE_GIT_KEEP).touch(exist_ok=True)  # Create or update timestamp
        print(f"Created entities directory: {CYAN}{entities_dir}{NC}")
    except OSError as e:
        print(f"{RED}Error creating entities directory {entities_dir}: {e}{NC}")
        sys.exit(1)

    # Set up rules
    setup_rules(project_name, target_dir)  # Call the rules setup logic

    # Update central registry
    repo_root = get_repo_root()
    registry_path = repo_root / "mcp-projects.yaml"
    print(f"Updating central project registry: {CYAN}{registry_path}{NC}")
    try:
        # Ensure paths are absolute before passing
        success = update_registry_logic(
            registry_file=registry_path,
            project_name=project_name,
            root_dir=target_dir.resolve(),
            config_file=config_path.resolve(),
            enabled=True
        )
        if not success:
            print(f"{RED}Error: Failed to update project registry (see previous errors).{NC}")
            sys.exit(1)
    except Exception as e:
        print(f"{RED}Error updating project registry: {e}{NC}")
        sys.exit(1)

    print(f"{GREEN}Graphiti project '{project_name}' initialization complete.{NC}")
    print(f"You can now create entity definitions in: {CYAN}{entities_dir}{NC}")


def setup_rules(project_name: str, target_dir: Path):
    """
    Set up Cursor rules for a project.
    
    Args:
        project_name (str): The name of the project.
        target_dir (Path): The root directory of the project.
    """
    repo_root = get_repo_root()
    print(f"Setting up Graphiti Cursor rules for project '{CYAN}{project_name}{NC}' in {CYAN}{target_dir}{NC}")

    rules_source_dir = repo_root / DIR_PROJECT_ASSETS / DIR_RULES
    # The destination directory within the project's .cursor structure
    cursor_rules_dir = target_dir / ".cursor" / "rules" / "graphiti"

    try:
        cursor_rules_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created/verified rules directory: {CYAN}{cursor_rules_dir}{NC}")

        core_rule_src = rules_source_dir / FILE_CORE_RULE
        maint_rule_src = rules_source_dir / FILE_MAINT_RULE
        schema_template_src = rules_source_dir / DIR_TEMPLATES / FILE_SCHEMA_TEMPLATE

        core_rule_link = cursor_rules_dir / "graphiti-mcp-core-rules.mdc"
        maint_rule_link = cursor_rules_dir / "graphiti-knowledge-graph-maintenance.mdc"
        target_schema_file = cursor_rules_dir / f"graphiti-{project_name}-schema.mdc"

        # Check source files
        missing_files = []
        if not core_rule_src.is_file(): missing_files.append(core_rule_src)
        if not maint_rule_src.is_file(): missing_files.append(maint_rule_src)
        if not schema_template_src.is_file(): missing_files.append(schema_template_src)
        if missing_files:
            print(f"{RED}Error: Source rule/template files not found:{NC}")
            for f in missing_files: print(f"  - {f}")
            sys.exit(1)

        # Create/Update symlinks using relative paths for better portability
        try:
            core_rel_path = os.path.relpath(core_rule_src.resolve(), start=cursor_rules_dir.resolve())
            maint_rel_path = os.path.relpath(maint_rule_src.resolve(), start=cursor_rules_dir.resolve())
        except ValueError:
            # Handle case where paths are on different drives (Windows) - fall back to absolute
            print(f"{YELLOW}Warning: Cannot create relative symlink paths (different drives?). Using absolute paths.{NC}")
            core_rel_path = core_rule_src.resolve()
            maint_rel_path = maint_rule_src.resolve()

        # Unlink if it exists and is not the correct link target
        if core_rule_link.is_symlink():
            if core_rule_link.readlink() != Path(core_rel_path):
                core_rule_link.unlink()
        elif core_rule_link.exists():  # It exists but isn't a symlink
            core_rule_link.unlink()

        if not core_rule_link.exists():
            core_rule_link.symlink_to(core_rel_path)
            print(f"Linking core rule: {CYAN}{core_rule_link.name}{NC} -> {CYAN}{core_rel_path}{NC}")
        else:
            print(f"Core rule link already exists: {CYAN}{core_rule_link.name}{NC}")

        if maint_rule_link.is_symlink():
            if maint_rule_link.readlink() != Path(maint_rel_path):
                maint_rule_link.unlink()
        elif maint_rule_link.exists():
            maint_rule_link.unlink()

        if not maint_rule_link.exists():
            maint_rule_link.symlink_to(maint_rel_path)
            print(f"Linking maintenance rule: {CYAN}{maint_rule_link.name}{NC} -> {CYAN}{maint_rel_path}{NC}")
        else:
            print(f"Maintenance rule link already exists: {CYAN}{maint_rule_link.name}{NC}")

        # Generate schema file from template
        if target_schema_file.exists():
            print(f"{YELLOW}Warning: Project schema file already exists, skipping template generation: {target_schema_file}{NC}")
        else:
            print(f"Generating template project schema file: {CYAN}{target_schema_file}{NC}")
            template_content = schema_template_src.read_text()
            schema_content = template_content.replace("__PROJECT_NAME__", project_name)
            target_schema_file.write_text(schema_content)

        print(f"{GREEN}Graphiti Cursor rules setup complete for project '{project_name}'.{NC}")

    except OSError as e:
        print(f"{RED}Error setting up rules: {e}{NC}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}An unexpected error occurred during rule setup: {e}{NC}")
        sys.exit(1)


def _to_pascal_case(snake_str: str) -> str:
    """
    Converts snake_case or kebab-case to PascalCase.
    
    Args:
        snake_str (str): String in snake_case or kebab-case
        
    Returns:
        str: String in PascalCase
    """
    parts = re.split('_|-', snake_str)
    return "".join(part.capitalize() for part in parts)


def create_entity_set(entity_name: str, target_dir: Path):
    """
    Create a new entity file directly in a project's entities directory.
    
    Args:
        entity_name (str): Name for the new entity
        target_dir (Path): Target project root directory
    """
    # Validate entity_name format
    if not re.fullmatch(REGEX_VALID_NAME, entity_name):
        print(f"{RED}Error: Invalid entity name '{entity_name}'. Use only letters, numbers, underscores, and hyphens.{NC}")
        sys.exit(1)
        
    # Load project configuration from ai/graph directory
    graph_dir = target_dir / DIR_AI / DIR_GRAPH
    config_path = graph_dir / CONFIG_FILENAME
    if not config_path.is_file():
        print(f"{RED}Error: Project configuration file not found: {config_path}{NC}")
        print(f"Make sure the project has been initialized with 'graphiti init' first.")
        sys.exit(1)
        
    project_config = load_yaml_file(config_path, safe=True)
    if project_config is None:
        print(f"{RED}Error: Failed to load project configuration from: {config_path}{NC}")
        sys.exit(1)
        
    # Validate project config structure
    if CONFIG_KEY_SERVICES not in project_config or not isinstance(project_config[CONFIG_KEY_SERVICES], list) or not project_config[CONFIG_KEY_SERVICES]:
        print(f"{RED}Error: Invalid or missing '{CONFIG_KEY_SERVICES}' section in project configuration: {config_path}{NC}")
        sys.exit(1)
        
    # Extract the entity directory name from the first service entry
    entity_dir_name = project_config.get(CONFIG_KEY_SERVICES, [{}])[0].get(CONFIG_KEY_ENTITIES_DIR, DEFAULT_ENTITIES_DIR_NAME)
    
    # Calculate paths - entities directory directly in graph_dir
    project_entity_dir = graph_dir / entity_dir_name
    
    # Generate file name with the entity class name (without Entity suffix)
    class_name = _to_pascal_case(entity_name)
    entity_file_path = project_entity_dir / f"{class_name}{ENTITY_FILE_EXTENSION}"  # Name file after class
    
    # Check if the entity file already exists
    if entity_file_path.exists():
        print(f"{RED}Error: Entity file '{class_name}{ENTITY_FILE_EXTENSION}' already exists at: {entity_file_path}{NC}")
        sys.exit(1)
        
    # Get path to template file from repo
    repo_root = get_repo_root()
    example_template_path = repo_root / DIR_PROJECT_ASSETS / DIR_ENTITY_TEMPLATES / DIR_EXAMPLES / FILE_ENTITY_EXAMPLE
    
    try:
        # Create the project entity directory if it doesn't exist
        project_entity_dir.mkdir(parents=True, exist_ok=True)

        if not example_template_path.is_file():
            print(f"{YELLOW}Warning: Template file not found: {example_template_path}{NC}")
            print("Creating a minimal entity file instead.")
            minimal_content = f"""from pydantic import BaseModel, Field, ConfigDict

class {class_name}(BaseModel):
    \"\"\"Entity definition for '{entity_name}'.\"\"\"

    # Disallow undeclared fields so the schema uses additionalProperties:false
    model_config = ConfigDict(extra="forbid")

    example_field: str = Field(
        ...,
        description='An example field.',
    )
"""
            entity_file_path.write_text(minimal_content)
        else:
            template_content = example_template_path.read_text()
            # Perform replacements carefully
            content = template_content.replace(ENTITY_CLASS_PATTERN, f"class {class_name}(BaseModel):")
            # Replace descriptions, trying to be specific
            content = content.replace(ENTITY_DESC_PATTERN_PRODUCT, f"A {class_name} represents")
            content = content.replace(ENTITY_DESC_PATTERN_ABOUT_PRODUCTS, f"about {class_name} entities mentioned")
            content = content.replace(ENTITY_DESC_PATTERN_PRODUCT_NAMES, f"{entity_name} names")
            content = content.replace(ENTITY_DESC_PATTERN_PRODUCT_BELONGS, f"the {entity_name} belongs")
            content = content.replace(ENTITY_DESC_PATTERN_PRODUCT_DESC, f"description of the {entity_name}")
            # Add more replacements if needed based on the template content

            entity_file_path.write_text(content)
        
        print(f"Created entity file: {CYAN}{entity_file_path}{NC}")
        print(f"{GREEN}Entity '{entity_name}' successfully created.{NC}")
        print(f"You can now edit the entity definition in: {CYAN}{entity_file_path}{NC}")

    except OSError as e:
        print(f"{RED}Error creating entity '{entity_name}': {e}{NC}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}An unexpected error occurred creating entity '{entity_name}': {e}{NC}")
        sys.exit(1) 