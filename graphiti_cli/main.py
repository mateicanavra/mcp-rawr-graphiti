#!/usr/bin/env python3
"""
Main entry point for the Graphiti CLI tool.
This module defines the Typer CLI application and command structure.
"""
import typer
from pathlib import Path
from typing_extensions import Annotated  # Preferred for Typer >= 0.9

# Import command functions and core utilities
from . import commands
from .core import LogLevel, get_repo_root

# --- Application Constants ---
APP_DESCRIPTION = "CLI for managing Graphiti MCP Server projects and Docker environment."
APP_MARKUP_MODE = "markdown"  # Nicer help text formatting

# --- Default Values ---
DEFAULT_DIR = Path(".")

# --- CLI Option Constants ---
OPT_DETACHED_LONG = "--detached"
OPT_DETACHED_SHORT = "-d"
OPT_LOG_LEVEL = "--log-level"

# --- Command Emojis ---
EMOJI_INIT = "✨"
EMOJI_ENTITY = "📄"
EMOJI_RULES = "🔗"
EMOJI_UP = "🚀"
EMOJI_DOWN = "🛑"
EMOJI_RESTART = "🔄"
EMOJI_RELOAD = "⚡"
EMOJI_COMPOSE = "⚙️"

# --- Help Text Constants ---
# App-level help
HELP_DETACHED = "Run containers in detached mode."
HELP_DETACHED_UP = "Run 'up' in detached mode after 'down'."
HELP_LOG_LEVEL = "Set logging level for containers."
HELP_LOG_LEVEL_COMPOSE = "Set logging level for Docker Compose execution."

# Command help texts
HELP_CMD_INIT = f"Initialize a project: create ai/graph structure with config, entities dir, and rules. {EMOJI_INIT}"
HELP_CMD_ENTITY = f"Create a new entity type set directory and template file within a project's ai/graph/entities directory. {EMOJI_ENTITY}"
HELP_CMD_RULES = f"Setup/update Cursor rules symlinks and schema template for a project. {EMOJI_RULES}"
HELP_CMD_UP = f"Start all containers using Docker Compose (builds first). {EMOJI_UP}"
HELP_CMD_DOWN = f"Stop and remove all containers using Docker Compose. {EMOJI_DOWN}"
HELP_CMD_RESTART = f"Restart all containers: runs 'down' then 'up'. {EMOJI_RESTART}"
HELP_CMD_RELOAD = f"Restart a specific running service container. {EMOJI_RELOAD}"
HELP_CMD_COMPOSE = f"Generate docker-compose.yml from base and project configs. {EMOJI_COMPOSE}"

# Argument help texts
HELP_ARG_PROJECT_NAME = "Name of the target project."
HELP_ARG_TARGET_DIR = "Target project root directory."
HELP_ARG_ENTITY_NAME = "Name for the new entity type set (e.g., 'my-entities')."
HELP_ARG_TARGET_DIR_CONFIG = "Target project root directory containing ai/graph/mcp-config.yaml."
HELP_ARG_PROJECT_NAME_RULES = "Name of the target project for rule setup."
HELP_ARG_SERVICE_NAME = "Name of the service to reload (e.g., 'mcp-test-project-1-main')."

# Initialize Typer app
app = typer.Typer(
    help=APP_DESCRIPTION,
    no_args_is_help=True,  # Show help if no command is given
    rich_markup_mode=APP_MARKUP_MODE
)

# --- Callback to ensure repo path is found early ---
@app.callback()
def main_callback(ctx: typer.Context):
    """
    Main callback to perform setup before any command runs.
    Ensures the MCP_GRAPHITI_REPO_PATH is found.
    """
    # Ensure repo root is detected/set early.
    # get_repo_root() will print messages and exit if not found.
    _ = get_repo_root()


# --- Define Commands (delegating to functions in commands.py) ---

@app.command()
def init(
    project_name: Annotated[str, typer.Argument(help=HELP_ARG_PROJECT_NAME)],
    target_dir: Annotated[Path, typer.Argument(
        help=HELP_ARG_TARGET_DIR,
        exists=False,  # Allow creating the directory
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True  # Convert to absolute path
    )] = DEFAULT_DIR
):
    """
    Initialize a project: create ai/graph structure with config, entities dir, and rules. ✨
    """
    commands.init_project(project_name, target_dir)

@app.command()
def entity(
    set_name: Annotated[str, typer.Argument(help=HELP_ARG_ENTITY_NAME)],
    target_dir: Annotated[Path, typer.Argument(
        help=HELP_ARG_TARGET_DIR_CONFIG,
        exists=True,  # Must exist for entity creation
        file_okay=False,
        dir_okay=True,
        resolve_path=True
    )] = DEFAULT_DIR
):
    """
    Create a new entity type set directory and template file within a project's ai/graph/entities directory. 📄
    """
    commands.create_entity_set(set_name, target_dir)

@app.command()
def rules(
    project_name: Annotated[str, typer.Argument(help=HELP_ARG_PROJECT_NAME_RULES)],
    target_dir: Annotated[Path, typer.Argument(
        help=HELP_ARG_TARGET_DIR,
        exists=True,  # Must exist for rules setup
        file_okay=False,
        dir_okay=True,
        resolve_path=True
    )] = DEFAULT_DIR
):
    """
    Setup/update Cursor rules symlinks and schema template for a project. 🔗
    """
    commands.setup_rules(project_name, target_dir)

@app.command()
def up(
    detached: Annotated[bool, typer.Option(OPT_DETACHED_LONG, OPT_DETACHED_SHORT, help=HELP_DETACHED)] = False,
    log_level: Annotated[LogLevel, typer.Option(OPT_LOG_LEVEL, help=HELP_LOG_LEVEL, case_sensitive=False)] = LogLevel.info
):
    """
    Start all containers using Docker Compose (builds first). 🚀
    """
    commands.docker_up(detached, log_level.value)

@app.command()
def down(
    log_level: Annotated[LogLevel, typer.Option(OPT_LOG_LEVEL, help=HELP_LOG_LEVEL_COMPOSE, case_sensitive=False)] = LogLevel.info
):
    """
    Stop and remove all containers using Docker Compose. 🛑
    """
    commands.docker_down(log_level.value)

@app.command()
def restart(
    detached: Annotated[bool, typer.Option(OPT_DETACHED_LONG, OPT_DETACHED_SHORT, help=HELP_DETACHED_UP)] = False,
    log_level: Annotated[LogLevel, typer.Option(OPT_LOG_LEVEL, help=HELP_LOG_LEVEL, case_sensitive=False)] = LogLevel.info
):
    """
    Restart all containers: runs 'down' then 'up'. 🔄
    """
    commands.docker_restart(detached, log_level.value)

@app.command()
def reload(
    service_name: Annotated[str, typer.Argument(help=HELP_ARG_SERVICE_NAME)]
):
    """
    Restart a specific running service container. ⚡
    """
    commands.docker_reload(service_name)

@app.command()
def compose():
    """
    Generate docker-compose.yml from base and project configs. ⚙️
    """
    commands.docker_compose_generate()


# Allow running the script directly for development/testing
if __name__ == "__main__":
    app()
