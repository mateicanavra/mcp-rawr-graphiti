#!/usr/bin/env python3
"""
Shared constants for the Graphiti MCP server ecosystem.
This module centralizes constants used across different components.
"""
import logging
from enum import Enum

# --- Logging Constants ---
# Constants related to Graphiti's logging mechanism
DEFAULT_LOG_LEVEL_STR = "info"                 # Default logging level as a string
DEFAULT_LOG_LEVEL = logging.INFO               # Default logging level as a Python logging constant
ENV_GRAPHITI_LOG_LEVEL = "GRAPHITI_LOG_LEVEL"  # Environment variable name for configuring the logging level

# ADDED LogLevel Enum here
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

# --- Directory Structure Constants ---
# Standard directories used in Graphiti project structure
DIR_AI = "ai"                  # AI-related files
DIR_GRAPH = "graph"            # Knowledge graph data
DIR_ENTITIES = "entities"      # Entity definitions
DIR_MCP_SERVER = "mcp_server"  # MCP server code
DIR_ENTITIES = "entities"  # Entity definitions for knowledge graph
DIR_DIST = "dist"              # Distribution directory for built packages
DIR_PROJECT_ASSETS = "project_assets"  # Directory containing project initialization assets

# Standard files used in Graphiti projects
FILE_GIT_KEEP = ".gitkeep"           # Placeholder to preserve empty directories in Git
FILE_PYPROJECT_TOML = "pyproject.toml"  # Python project definition file

# --- Regex Constants ---
# Regular expression for validating entity and project names (alphanumeric, underscore, and hyphen)
REGEX_VALID_NAME = r'^[a-zA-Z0-9_-]+$'

# --- Environment Variable Constants ---
# Environment variables used to configure Graphiti MCP server behavior
ENV_REPO_PATH = "MCP_GRAPHITI_REPO_PATH"  # Path to the Graphiti MCP repository
ENV_MCP_GROUP_ID = "MCP_GROUP_ID"         # Group ID (namespace) for graph data
ENV_MCP_USE_CUSTOM_ENTITIES = "MCP_USE_CUSTOM_ENTITIES"  # Whether to use custom entity extraction
ENV_MCP_USE_CUSTOM_ENTITIES_VALUE = "true"  # Value to enable custom entity extraction
ENV_MCP_ENTITIES_DIR = "MCP_ENTITIES_DIR"  # Directory for custom entity definitions
ENV_MCP_ENTITIES = "MCP_ENTITIES"  # Added

# --- Container Path Constants ---
# Paths used within Docker containers for entity mounting
CONTAINER_ENTITY_PATH = "/app/entities"  # Default entities
PROJECT_CONTAINER_ENTITY_PATH = "/app/project_entities"  # Project-specific entity definitions

# --- Docker/Port Constants ---
DEFAULT_PORT_START = 8000  # Starting port number for containers (assigned sequentially)
DEFAULT_MCP_CONTAINER_PORT_VAR = "MCP_PORT"  # Environment variable for MCP server port

# --- Default Model Constants ---
DEFAULT_LLM_MODEL = "gpt-4o"  # Default language model to use if none specified

# --- Registry and Compose File Constants ---
# Filenames for Docker Compose and project registry configuration
BASE_COMPOSE_FILENAME = "base-compose.yaml"  # Base Docker Compose template
PROJECTS_REGISTRY_FILENAME = "mcp-projects.yaml"  # Central registry of Graphiti MCP projects
DOCKER_COMPOSE_OUTPUT_FILENAME = "docker-compose.yml"  # Generated Docker Compose config

# --- Configuration File Constants ---
CONFIG_FILENAME = "mcp-config.yaml"  # Project-specific MCP configuration file
ENTITY_FILE_EXTENSION = ".py"        # File extension for Python entity definitions

# --- Configuration Key Constants ---
# Keys used in configuration files for MCP settings
CONFIG_KEY_SERVICES = "services"            # Services section
CONFIG_KEY_ID = "id"                        # Server ID
CONFIG_KEY_CONTAINER_NAME = "container_name"  # Docker container name
CONFIG_KEY_PORT_DEFAULT = "port_default"    # Default port
CONFIG_KEY_GROUP_ID = "group_id"            # Group ID for namespacing
CONFIG_KEY_ENTITIES_DIR = "entities_dir"        # Entity directory path
CONFIG_KEY_ENVIRONMENT = "environment"      # Environment variables
CONFIG_KEY_SYNC_CURSOR_MCP_CONFIG = "sync_cursor_mcp_config" # Flag to sync mcp.json

# --- Registry File Key Constants ---
# Keys used in the project registry file (mcp-projects.yaml)
REGISTRY_PROJECTS_KEY = "projects"          # Dictionary of all projects
REGISTRY_ROOT_DIR_KEY = "root_dir"          # Project root directory path
REGISTRY_CONFIG_FILE_KEY = "config_file"    # Project config file path
REGISTRY_ENABLED_KEY = "enabled"            # Project enabled status flag

# --- Compose File Key Constants ---
# Keys used in Docker Compose configuration files
COMPOSE_SERVICES_KEY = "services"                  # Services section
COMPOSE_CUSTOM_BASE_ANCHOR_KEY = "x-graphiti-mcp-custom-base"  # Base service anchor
COMPOSE_CONTAINER_NAME_KEY = "container_name"      # Container name
COMPOSE_PORTS_KEY = "ports"                        # Port mappings
COMPOSE_ENVIRONMENT_KEY = "environment"            # Environment variables
COMPOSE_VOLUMES_KEY = "volumes"                    # Volume mappings

# --- Project Config Key Constants ---
# Keys used in project-specific configuration files (mcp-config.yaml)
PROJECT_SERVICES_KEY = "services"                  # Services section
PROJECT_SERVER_ID_KEY = "id"                       # Server ID
PROJECT_ENTITIES_DIR_KEY = "entities_dir"              # Entity directory
PROJECT_CONTAINER_NAME_KEY = "container_name"      # Container name
PROJECT_PORT_DEFAULT_KEY = "port_default"          # Default port
PROJECT_GROUP_ID_KEY = "group_id"                  # Group ID
PROJECT_ENVIRONMENT_KEY = "environment"            # Environment variables

# --- Default Value Constants ---
# Default values used when specific settings are not provided
DEFAULT_CUSTOM_CONTAINER_NAME = "custom-name"  # Default container name for custom services
DEFAULT_CUSTOM_PORT = "8001"                   # Default port for custom services
DEFAULT_ENTITIES_DIR_NAME = "entities"           # Default name for entity directories

# --- Service Name Constants ---
SERVICE_NAME_PREFIX = "mcp-"  # Prefix used for all Graphiti MCP service names

# --- ANSI Color Constants ---
# ANSI escape codes used to color or format terminal output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
BOLD = '\033[1m'
NC = '\033[0m'  # Reset or "no color" code

# --- Package Constants ---
# Constants for package and dependency management
PACKAGE_LOCAL_WHEEL_MARKER = "graphiti-core @ file:///dist/"  # Marker for local installations
PACKAGE_PUBLISHED_PREFIX = "graphiti-core>="                  # Prefix for published packages 