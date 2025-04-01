This file is a merged representation of a subset of the codebase, containing files not matching ignore patterns, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching these patterns are excluded: .venv/**, uv.lock, dist/**, .ai/**, llm_cache/**, scripts/README.md, README.md, docs/**, *.egg-info/**, __pycache__/**, *.pyc, *.pyo, .python-version, .env, *.log
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

## Additional Info

# Directory Structure
```
entity_types/
  base/
    preferences.py
    procedures.py
    requirements.py
  example/
    company_entity.py
    custom_entity_example.py
  graphiti/
    ArchitecturalPattern.py
    DataPipeline.py
    IntegrationPattern.py
    RetrievalMethod.py
    TemporalModel.py
  __init__.py
  entity_registry.py
graphiti_cli/
  commands.py
  core.py
  main.py
  yaml_utils.py
rules/
  examples/
    graphiti-example-schema.md
  templates/
    project_schema_template.md
  graphiti-knowledge-graph-maintenance.md
  graphiti-mcp-core-rules.md
.env.example
.repomixignore
base-compose.yaml
constants.py
docker-compose.yml
Dockerfile
entrypoint.sh
graphiti_mcp_server.py
mcp_config_sse_example.json
mcp_config_stdio_example.json
mcp-projects.yaml
pyproject.toml
repomix.config.json
```

# Files

## File: entity_types/base/preferences.py
```python
"""Preference entity type for Graphiti MCP Server."""

from pydantic import BaseModel, Field


class Preference(BaseModel):
    """A Preference represents a user's expressed like, dislike, or preference for something.

    Instructions for identifying and extracting preferences:
    1. Look for explicit statements of preference such as "I like/love/enjoy/prefer X" or "I don't like/hate/dislike X"
    2. Pay attention to comparative statements ("I prefer X over Y")
    3. Consider the emotional tone when users mention certain topics
    4. Extract only preferences that are clearly expressed, not assumptions
    5. Categorize the preference appropriately based on its domain (food, music, brands, etc.)
    6. Include relevant qualifiers (e.g., "likes spicy food" rather than just "likes food")
    7. Only extract preferences directly stated by the user, not preferences of others they mention
    8. Provide a concise but specific description that captures the nature of the preference
    """

    category: str = Field(
        ...,
        description="The category of the preference. (e.g., 'Brands', 'Food', 'Music')",
    )
    description: str = Field(
        ...,
        description='Brief description of the preference. Only use information mentioned in the context to write this description.',
    )
```

## File: entity_types/base/procedures.py
```python
"""Procedure entity type for Graphiti MCP Server."""

from pydantic import BaseModel, Field


class Procedure(BaseModel):
    """A Procedure informing the agent what actions to take or how to perform in certain scenarios. Procedures are typically composed of several steps.

    Instructions for identifying and extracting procedures:
    1. Look for sequential instructions or steps ("First do X, then do Y")
    2. Identify explicit directives or commands ("Always do X when Y happens")
    3. Pay attention to conditional statements ("If X occurs, then do Y")
    4. Extract procedures that have clear beginning and end points
    5. Focus on actionable instructions rather than general information
    6. Preserve the original sequence and dependencies between steps
    7. Include any specified conditions or triggers for the procedure
    8. Capture any stated purpose or goal of the procedure
    9. Summarize complex procedures while maintaining critical details
    """

    description: str = Field(
        ...,
        description='Brief description of the procedure. Only use information mentioned in the context to write this description.',
    )
```

## File: entity_types/base/requirements.py
```python
"""Requirement entity type for Graphiti MCP Server."""

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    """A Requirement represents a specific need, feature, or functionality that a product or service must fulfill.

    Always ensure an edge is created between the requirement and the project it belongs to, and clearly indicate on the
    edge that the requirement is a requirement.

    Instructions for identifying and extracting requirements:
    1. Look for explicit statements of needs or necessities ("We need X", "X is required", "X must have Y")
    2. Identify functional specifications that describe what the system should do
    3. Pay attention to non-functional requirements like performance, security, or usability criteria
    4. Extract constraints or limitations that must be adhered to
    5. Focus on clear, specific, and measurable requirements rather than vague wishes
    6. Capture the priority or importance if mentioned ("critical", "high priority", etc.)
    7. Include any dependencies between requirements when explicitly stated
    8. Preserve the original intent and scope of the requirement
    9. Categorize requirements appropriately based on their domain or function
    """

    project_name: str = Field(
        ...,
        description='The name of the project to which the requirement belongs.',
    )
    description: str = Field(
        ...,
        description='Description of the requirement. Only use information mentioned in the context to write this description.',
    )

# No need for explicit registration - will be auto-registered
```

## File: entity_types/example/company_entity.py
```python
"""Definition for a Company entity type."""

from pydantic import BaseModel, Field


class Company(BaseModel):
    """
    **AI Persona:** You are an expert entity extraction assistant.
    
    **Task:** Identify and extract information about Companies mentioned in the provided text context.
    A Company represents a business organization.

    **Context:** The user will provide text containing potential mentions of companies.

    **Extraction Instructions:**
    Your goal is to accurately populate the fields (`name`, `industry`) 
    based *only* on information explicitly or implicitly stated in the text.

    1.  **Identify Core Mentions:** Look for explicit mentions of business organizations, corporations, startups, etc.
    2.  **Extract Name:** Identify company names, often proper nouns or capitalized sequences.
    3.  **Extract Industry:** Determine the company's industry (e.g., "Technology", "Retail", "Finance") based on context or explicit mentions.
    4.  **Handle Ambiguity:** If information for a field is missing or unclear, indicate that.

    **Output Format:** Respond with the extracted data structured according to this Pydantic model.
    """

    name: str = Field(
        ...,
        description='The specific name of the company as mentioned in the text.',
    )
    industry: str | None = Field(
        default=None,
        description='The industry the company operates in (e.g., "Technology", "Finance"), if mentioned.',
    )
```

## File: entity_types/example/custom_entity_example.py
```python
"""Example of how to create a custom entity type for Graphiti MCP Server."""

from pydantic import BaseModel, Field


class Product(BaseModel):
    """
    **AI Persona:** You are an expert entity extraction assistant.
    
    **Task:** Identify and extract information about Products mentioned in the provided text context.
    A Product represents a specific good or service that a company offers.

    **Context:** The user will provide text containing potential mentions of products.

    **Extraction Instructions:**
    Your goal is to accurately populate the fields (`name`, `description`, `category`) 
    based *only* on information explicitly or implicitly stated in the text.

    1.  **Identify Core Mentions:** Look for explicit mentions of commercial goods or services.
    2.  **Extract Name:** Identify product names, especially proper nouns, capitalized words, or terms near trademark symbols (™, ®).
    3.  **Extract Description:** Synthesize a concise description using details about features, purpose, pricing, or availability found *only* in the text.
    4.  **Extract Category:** Determine the product category (e.g., "Software", "Hardware", "Service") based on the description or explicit mentions.
    5.  **Refine Details:** Pay attention to specifications, technical details, stated benefits, unique selling points, variations, or models mentioned, and incorporate relevant details into the description.
    6.  **Handle Ambiguity:** If information for a field is missing or unclear in the text, indicate that rather than making assumptions.

    **Output Format:** Respond with the extracted data structured according to this Pydantic model.
    """

    name: str = Field(
        ...,
        description='The specific name of the product as mentioned in the text.',
    )
    description: str = Field(
        ...,
        description='A concise description of the product, synthesized *only* from information present in the provided text context.',
    )
    category: str = Field(
        ...,
        description='The category the product belongs to (e.g., "Electronics", "Software", "Service") based on the text.',
    )
```

## File: entity_types/graphiti/ArchitecturalPattern.py
```python
"""Definition of the ArchitecturalPattern entity type for Graphiti."""

from pydantic import BaseModel, Field
from typing import List, Optional


class ArchitecturalPatternEntity(BaseModel):
    """
    **AI Persona:** You are an expert software architecture analyst.
    
    **Task:** Identify and extract information about architectural patterns used in the Graphiti framework.
    ArchitecturalPatternEntity represents a high-level design pattern, principle, or architectural approach used in the system.

    **Context:** The text will contain descriptions of system architecture, code organization, or design principles.

    **Extraction Instructions:**
    Your goal is to accurately populate the fields about architectural patterns based *only* on information explicitly or implicitly stated in the text.

    1.  **Identify Pattern Mentions:** Look for explicit references to design patterns, architectural styles, or structural organization approaches.
    2.  **Extract Name:** Identify the specific pattern name (e.g., "Dependency Inversion", "Plugin Architecture", "Modular Design").
    3.  **Extract Description:** Synthesize a concise description explaining what the pattern is and how it's used in Graphiti.
    4.  **Extract Benefits:** Note any explicit or implicit benefits mentioned about why this pattern was chosen.
    5.  **Extract Implementation Details:** Capture how the pattern is implemented in the codebase, including key classes or components.
    6.  **Extract Related Components:** Identify which system components or modules implement or are affected by this pattern.
    7.  **Handle Ambiguity:** If information for a field is missing or unclear in the text, leave the optional fields empty.

    **Output Format:** Respond with the extracted data structured according to this Pydantic model.
    """

    name: str = Field(
        ...,
        description='The specific name of the architectural pattern (e.g., "Dependency Inversion", "Plugin Architecture").',
    )
    description: str = Field(
        ...,
        description='A concise description of what the pattern is and how it functions in the system architecture.',
    )
    benefits: Optional[List[str]] = Field(
        None,
        description='The advantages or benefits this pattern provides to the system (e.g., "extensibility", "maintainability").',
    )
    implementation_details: Optional[str] = Field(
        None,
        description='How the pattern is implemented in the codebase, including key classes, interfaces, or components.',
    )
    related_components: Optional[List[str]] = Field(
        None,
        description='System components or modules that implement or are directly affected by this pattern.',
    )
```

## File: entity_types/graphiti/DataPipeline.py
```python
"""Definition of the DataPipeline entity type for Graphiti."""

from pydantic import BaseModel, Field
from typing import List, Optional


class DataPipelineEntity(BaseModel):
    """
    **AI Persona:** You are an expert data engineer and systems analyst.
    
    **Task:** Identify and extract information about data processing pipelines in the Graphiti framework.
    DataPipelineEntity represents a workflow or sequence of operations that transform, process, or move data within the system.

    **Context:** The text will contain descriptions of data flows, ETL processes, or information processing sequences.

    **Extraction Instructions:**
    Your goal is to accurately populate the fields about data pipelines based *only* on information explicitly or implicitly stated in the text.

    1.  **Identify Pipeline Mentions:** Look for descriptions of sequential data processing, transformations, or workflows.
    2.  **Extract Name:** Identify the specific pipeline name or purpose (e.g., "Entity Extraction Pipeline", "Knowledge Graph Update Pipeline").
    3.  **Extract Description:** Synthesize a concise description of the pipeline's overall purpose and function.
    4.  **Extract Stages:** Identify the discrete steps or stages in the pipeline process.
    5.  **Extract Input/Output:** Determine what data enters the pipeline and what results from it.
    6.  **Extract Components:** Note which system components are involved in implementing this pipeline.
    7.  **Handle Ambiguity:** If information for a field is missing or unclear in the text, leave the optional fields empty.

    **Output Format:** Respond with the extracted data structured according to this Pydantic model.
    """

    name: str = Field(
        ...,
        description='The specific name or purpose of the data pipeline (e.g., "Entity Extraction Pipeline").',
    )
    description: str = Field(
        ...,
        description='A concise description of the pipeline\'s overall purpose and function in the system.',
    )
    stages: Optional[List[str]] = Field(
        None,
        description='The discrete steps or stages in the pipeline process, in sequential order.',
    )
    input_data: Optional[str] = Field(
        None,
        description='The type or source of data that enters the pipeline for processing.',
    )
    output_data: Optional[str] = Field(
        None,
        description='The resulting data or artifacts produced by the pipeline.',
    )
    components: Optional[List[str]] = Field(
        None,
        description='System components or modules involved in implementing this pipeline.',
    )
```

## File: entity_types/graphiti/IntegrationPattern.py
```python
"""Definition of the IntegrationPattern entity type for Graphiti."""

from pydantic import BaseModel, Field
from typing import List, Optional


class IntegrationPatternEntity(BaseModel):
    """
    **AI Persona:** You are an expert in systems integration and API design.
    
    **Task:** Identify and extract information about integration patterns used in the Graphiti framework.
    IntegrationPatternEntity represents an approach or technique for connecting Graphiti with external systems, databases, or services.

    **Context:** The text will contain descriptions of how Graphiti interfaces with external components, APIs, or data sources.

    **Extraction Instructions:**
    Your goal is to accurately populate the fields about integration patterns based *only* on information explicitly or implicitly stated in the text.

    1.  **Identify Integration Pattern Mentions:** Look for descriptions of how Graphiti connects to external systems or services.
    2.  **Extract Name:** Identify the specific integration pattern name (e.g., "Plugin Architecture", "API Abstraction Layer").
    3.  **Extract Description:** Synthesize a concise description of how the integration pattern works and what integration need it addresses.
    4.  **Extract Interfaces:** Identify the specific interfaces, APIs, or protocols used by this integration pattern.
    5.  **Extract External Systems:** Note which external systems, services, or databases are integrated using this pattern.
    6.  **Extract Implementation Details:** Capture how the integration is technically implemented in the codebase.
    7.  **Extract Benefits:** Identify the benefits or advantages this integration pattern provides.
    8.  **Handle Ambiguity:** If information for a field is missing or unclear in the text, leave the optional fields empty.

    **Output Format:** Respond with the extracted data structured according to this Pydantic model.
    """

    name: str = Field(
        ...,
        description='The specific name of the integration pattern (e.g., "Plugin Architecture", "API Abstraction Layer").',
    )
    description: str = Field(
        ...,
        description='A concise description of how the integration pattern works and what integration need it addresses.',
    )
    interfaces: Optional[List[str]] = Field(
        None,
        description='The specific interfaces, APIs, or protocols used by this integration pattern.',
    )
    external_systems: Optional[List[str]] = Field(
        None,
        description='External systems, services, or databases that are integrated using this pattern.',
    )
    implementation_details: Optional[str] = Field(
        None,
        description='How the integration is technically implemented in the codebase.',
    )
    benefits: Optional[List[str]] = Field(
        None,
        description='The benefits or advantages this integration pattern provides.',
    )
```

## File: entity_types/graphiti/RetrievalMethod.py
```python
"""Definition of the RetrievalMethod entity type for Graphiti."""

from pydantic import BaseModel, Field
from typing import List, Optional


class RetrievalMethodEntity(BaseModel):
    """
    **AI Persona:** You are an expert in information retrieval and search systems.
    
    **Task:** Identify and extract information about data retrieval methods used in the Graphiti framework.
    RetrievalMethodEntity represents an approach or technique for finding and retrieving information from the knowledge graph.

    **Context:** The text will contain descriptions of search mechanisms, query approaches, or information access methods.

    **Extraction Instructions:**
    Your goal is to accurately populate the fields about retrieval methods based *only* on information explicitly or implicitly stated in the text.

    1.  **Identify Retrieval Method Mentions:** Look for descriptions of search algorithms, querying approaches, or information access techniques.
    2.  **Extract Name:** Identify the specific retrieval method name (e.g., "Semantic Search", "Graph Traversal", "Keyword Matching").
    3.  **Extract Description:** Synthesize a concise description of how the retrieval method works and what problem it solves.
    4.  **Extract Algorithms:** Identify the specific algorithms or techniques employed by this retrieval method.
    5.  **Extract Strengths:** Note any stated advantages or strengths of this retrieval approach.
    6.  **Extract Limitations:** Capture any described limitations or constraints of this method.
    7.  **Extract Use Cases:** Identify specific use cases where this retrieval method is particularly effective.
    8.  **Handle Ambiguity:** If information for a field is missing or unclear in the text, leave the optional fields empty.

    **Output Format:** Respond with the extracted data structured according to this Pydantic model.
    """

    name: str = Field(
        ...,
        description='The specific name of the retrieval method (e.g., "Semantic Search", "Graph Traversal").',
    )
    description: str = Field(
        ...,
        description='A concise description of how the retrieval method works and what information access need it addresses.',
    )
    algorithms: Optional[List[str]] = Field(
        None,
        description='The specific algorithms or techniques employed by this retrieval method.',
    )
    strengths: Optional[List[str]] = Field(
        None,
        description='The advantages or strengths of this retrieval approach.',
    )
    limitations: Optional[List[str]] = Field(
        None,
        description='The limitations or constraints of this retrieval method.',
    )
    use_cases: Optional[List[str]] = Field(
        None,
        description='Specific scenarios or use cases where this retrieval method is particularly effective.',
    )
```

## File: entity_types/graphiti/TemporalModel.py
```python
"""Definition of the TemporalModel entity type for Graphiti."""

from pydantic import BaseModel, Field
from typing import List, Optional


class TemporalModelEntity(BaseModel):
    """
    **AI Persona:** You are an expert in temporal data modeling and time-aware databases.
    
    **Task:** Identify and extract information about temporal data models used in the Graphiti framework.
    TemporalModelEntity represents an approach to modeling data that incorporates time dimensions.

    **Context:** The text will contain descriptions of how time is represented, tracked, and queried in the system.

    **Extraction Instructions:**
    Your goal is to accurately populate the fields about temporal data models based *only* on information explicitly or implicitly stated in the text.

    1.  **Identify Temporal Model Mentions:** Look for descriptions of how time is represented in data structures.
    2.  **Extract Name:** Identify the specific temporal model approach (e.g., "Bi-temporal Model", "Valid-time Tracking").
    3.  **Extract Description:** Synthesize a concise description of how the temporal model works and what problem it solves.
    4.  **Extract Time Dimensions:** Identify which dimensions of time are captured (e.g., system time, valid time, transaction time).
    5.  **Extract Query Capabilities:** Note any information about how temporal data can be queried or retrieved.
    6.  **Extract Implementation:** Capture details about how the temporal model is implemented in the database.
    7.  **Extract Use Cases:** Identify specific use cases or scenarios where this temporal model provides value.
    8.  **Handle Ambiguity:** If information for a field is missing or unclear in the text, leave the optional fields empty.

    **Output Format:** Respond with the extracted data structured according to this Pydantic model.
    """

    name: str = Field(
        ...,
        description='The specific name or type of the temporal model (e.g., "Bi-temporal Model", "Valid-time Tracking").',
    )
    description: str = Field(
        ...,
        description='A concise description of how the temporal model works and what problem it solves.',
    )
    time_dimensions: Optional[List[str]] = Field(
        None,
        description='The dimensions of time that are captured (e.g., "system time", "valid time", "transaction time").',
    )
    query_capabilities: Optional[str] = Field(
        None,
        description='How temporal data can be queried or retrieved, including any special query features.',
    )
    implementation: Optional[str] = Field(
        None,
        description='How the temporal model is implemented in the database or data structures.',
    )
    use_cases: Optional[List[str]] = Field(
        None,
        description='Specific use cases or scenarios where this temporal model provides value.',
    )
```

## File: entity_types/__init__.py
```python
"""Entity Types package.

This package contains entity type definitions for Graphiti MCP Server.
"""

from entity_types.entity_registry import (
    register_entity_type,
    get_entity_types,
    get_entity_type_subset,
)
```

## File: entity_types/entity_registry.py
```python
"""Entity Types Registry for Graphiti MCP Server.

This module provides a registry to manage entity types in a modular way.
"""

from typing import Dict, Type

from pydantic import BaseModel

# Global registry to store entity types
_ENTITY_REGISTRY: Dict[str, Type[BaseModel]] = {}


def register_entity_type(name: str, entity_class: Type[BaseModel]) -> None:
    """Register an entity type with the registry.

    Args:
        name: The name of the entity type
        entity_class: The Pydantic model class for the entity type
    """
    _ENTITY_REGISTRY[name] = entity_class


def get_entity_types() -> Dict[str, Type[BaseModel]]:
    """Get all registered entity types.

    Returns:
        A dictionary mapping entity type names to their Pydantic model classes
    """
    # Return the actual registry reference, not a copy
    return _ENTITY_REGISTRY


def get_entity_type_subset(names: list[str]) -> Dict[str, Type[BaseModel]]:
    """Get a subset of registered entity types.

    Args:
        names: List of entity type names to include

    Returns:
        A dictionary containing only the specified entity types
    """
    return {name: _ENTITY_REGISTRY[name] for name in names if name in _ENTITY_REGISTRY}
```

## File: graphiti_cli/commands.py
```python
#!/usr/bin/env python3
"""
Command implementations for the Graphiti CLI tool.
This module contains the functions that are called by the CLI commands.
"""
import sys
import shutil
from pathlib import Path
import os
import re  # For entity name validation

from . import core
from . import yaml_utils
from constants import (
    # Configuration constants
    CONFIG_FILENAME, ENTITY_FILE_EXTENSION,
    CONFIG_KEY_SERVICES, CONFIG_KEY_ID, CONFIG_KEY_CONTAINER_NAME, 
    CONFIG_KEY_PORT_DEFAULT, CONFIG_KEY_GROUP_ID, CONFIG_KEY_ENTITY_DIR,
    CONFIG_KEY_ENVIRONMENT,
    # Default values
    DEFAULT_CUSTOM_CONTAINER_NAME, DEFAULT_CUSTOM_PORT, DEFAULT_ENTITY_DIR_NAME,
    # Environment variables
    ENV_GRAPHITI_LOG_LEVEL,
    # Logging
    DEFAULT_LOG_LEVEL_STR,
    # Entity template constants (these should remain local as they're specific to this module)
    DIR_AI, DIR_GRAPH, DIR_ENTITIES, FILE_GIT_KEEP, REGEX_VALID_NAME
)

# --- Entity Template Constants ---
ENTITY_CLASS_PATTERN = "class Product(BaseModel):"
ENTITY_DESC_PATTERN_PRODUCT = "A Product represents"
ENTITY_DESC_PATTERN_ABOUT_PRODUCTS = "about Products mentioned"
ENTITY_DESC_PATTERN_PRODUCT_NAMES = "product names"
ENTITY_DESC_PATTERN_PRODUCT_BELONGS = "the product belongs"
ENTITY_DESC_PATTERN_PRODUCT_DESC = "description of the product"

# --- Docker Commands ---

def docker_up(detached: bool, log_level: str):
    """
    Start all containers using Docker Compose (builds first).
    
    Args:
        detached (bool): Whether to run in detached mode
        log_level (str): Log level to use
    """
    core.ensure_docker_compose_file()
    core.ensure_dist_for_build()
    cmd = ["up", "--build", "--force-recreate"]
    core.run_docker_compose(cmd, log_level, detached)
    print(f"{core.GREEN}Docker compose up completed.{core.NC}")

def docker_down(log_level: str):
    """
    Stop and remove all containers using Docker Compose.
    
    Args:
        log_level (str): Log level to use
    """
    core.ensure_docker_compose_file()  # Needed for compose to find project
    core.run_docker_compose(["down"], log_level)
    print(f"{core.GREEN}Docker compose down completed.{core.NC}")

def docker_restart(detached: bool, log_level: str):
    """
    Restart all containers: runs 'down' then 'up'.
    
    Args:
        detached (bool): Whether to run in detached mode
        log_level (str): Log level to use
    """
    print(f"{core.BOLD}Restarting Graphiti containers: first down, then up...{core.NC}")
    core.ensure_docker_compose_file()  # Ensure docker-compose.yml exists before the restart sequence
    core.run_docker_compose(["down"], log_level)
    docker_up(detached, log_level)
    print(f"{core.GREEN}Restart sequence completed.{core.NC}")

def docker_reload(service_name: str):
    """
    Restart a specific running service container.
    
    Args:
        service_name (str): Name of the service to reload
    """
    core.ensure_docker_compose_file()
    print(f"{core.BOLD}Attempting to restart service '{core.CYAN}{service_name}{core.NC}'...{core.NC}")
    try:
        core.run_docker_compose(["restart", service_name], log_level=core.LogLevel.info.value)
        print(f"{core.GREEN}Service '{service_name}' restarted successfully.{core.NC}")
    except Exception:
        print(f"{core.RED}Failed to restart service '{service_name}'. Check service name and if stack is running.{core.NC}")
        sys.exit(1)

def docker_compose_generate():
    """
    Generate docker-compose.yml from base and project configs.
    """
    print(f"{core.BOLD}Generating docker-compose.yml from templates...{core.NC}")
    mcp_server_dir = core.get_mcp_server_dir()
    try:
        yaml_utils.generate_compose_logic(mcp_server_dir)  # Generate with default level
        # Success message printed within generate_compose_logic
    except Exception as e:
        print(f"{core.RED}Error: Failed to generate docker-compose.yml file: {e}{core.NC}")
        sys.exit(1)

# --- Project/File Management Commands ---

def init_project(project_name: str, target_dir: Path):
    """
    Initialize a new Graphiti project.
    
    Args:
        project_name (str): Name of the project
        target_dir (Path): Target directory for the project
    """
    # Basic validation
    if not re.fullmatch(REGEX_VALID_NAME, project_name):
        print(f"{core.RED}Error: Invalid PROJECT_NAME '{project_name}'. Use only letters, numbers, underscores, and hyphens.{core.NC}")
        sys.exit(1)

    print(f"Initializing Graphiti project '{core.CYAN}{project_name}{core.NC}' in '{core.CYAN}{target_dir}{core.NC}'...")

    # Create ai/graph directory structure
    graph_dir = target_dir / DIR_AI / DIR_GRAPH
    try:
        graph_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory structure: {core.CYAN}{graph_dir}{core.NC}")
    except OSError as e:
        print(f"{core.RED}Error creating directory structure {graph_dir}: {e}{core.NC}")
        sys.exit(1)

    # Create mcp-config.yaml in ai/graph directory
    config_path = graph_dir / CONFIG_FILENAME
    config_content = f"""# Configuration for project: {project_name}
{CONFIG_KEY_SERVICES}:
  - {CONFIG_KEY_ID}: {project_name}-main  # Service ID (used for default naming)
    # {CONFIG_KEY_CONTAINER_NAME}: "{DEFAULT_CUSTOM_CONTAINER_NAME}"  # Optional: Specify custom container name
    # {CONFIG_KEY_PORT_DEFAULT}: {DEFAULT_CUSTOM_PORT}             # Optional: Specify custom host port
    {CONFIG_KEY_GROUP_ID}: "{project_name}"       # Graph group ID
    {CONFIG_KEY_ENTITY_DIR}: "{DEFAULT_ENTITY_DIR_NAME}"           # Relative path to entity definitions within ai/graph
    {CONFIG_KEY_ENVIRONMENT}:                     # Optional: Add non-secret env vars here
      {ENV_GRAPHITI_LOG_LEVEL}: "{DEFAULT_LOG_LEVEL_STR}"
"""
    try:
        config_path.write_text(config_content)
        print(f"Created template {core.CYAN}{config_path}{core.NC}")
    except OSError as e:
        print(f"{core.RED}Error creating config file {config_path}: {e}{core.NC}")
        sys.exit(1)

    # Create entities directory within ai/graph
    entities_dir = graph_dir / DIR_ENTITIES
    try:
        entities_dir.mkdir(exist_ok=True)
        (entities_dir / FILE_GIT_KEEP).touch(exist_ok=True)  # Create or update timestamp
        print(f"Created entities directory: {core.CYAN}{entities_dir}{core.NC}")
    except OSError as e:
        print(f"{core.RED}Error creating entities directory {entities_dir}: {e}{core.NC}")
        sys.exit(1)

    # Set up rules
    setup_rules(project_name, target_dir)  # Call the rules setup logic

    # Update central registry
    mcp_server_dir = core.get_mcp_server_dir()
    registry_path = mcp_server_dir / "mcp-projects.yaml"
    print(f"Updating central project registry: {core.CYAN}{registry_path}{core.NC}")
    try:
        # Ensure paths are absolute before passing
        success = yaml_utils.update_registry_logic(
            registry_file=registry_path,
            project_name=project_name,
            root_dir=target_dir.resolve(),
            config_file=config_path.resolve(),
            enabled=True
        )
        if not success:
            print(f"{core.RED}Error: Failed to update project registry (see previous errors).{core.NC}")
            sys.exit(1)
    except Exception as e:
        print(f"{core.RED}Error updating project registry: {e}{core.NC}")
        sys.exit(1)

    print(f"{core.GREEN}Graphiti project '{project_name}' initialization complete.{core.NC}")
    print(f"You can now create entity definitions in: {core.CYAN}{entities_dir}{core.NC}")


def setup_rules(project_name: str, target_dir: Path):
    """
    Set up Cursor rules for a project.
    
    Args:
        project_name (str): Name of the project
        target_dir (Path): Target directory for the project
    """
    print(f"Setting up Graphiti Cursor rules for project '{core.CYAN}{project_name}{core.NC}' in {core.CYAN}{target_dir}{core.NC}")
    mcp_server_dir = core.get_mcp_server_dir()
    rules_source_dir = mcp_server_dir / "rules"
    templates_source_dir = rules_source_dir / "templates"
    cursor_rules_dir = target_dir / ".cursor" / "rules" / "graphiti"

    try:
        cursor_rules_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created/verified rules directory: {core.CYAN}{cursor_rules_dir}{core.NC}")

        core_rule_src = rules_source_dir / "graphiti-mcp-core-rules.md"
        maint_rule_src = rules_source_dir / "graphiti-knowledge-graph-maintenance.md"
        schema_template_src = templates_source_dir / "project_schema_template.md"

        core_rule_link = cursor_rules_dir / "graphiti-mcp-core-rules.mdc"
        maint_rule_link = cursor_rules_dir / "graphiti-knowledge-graph-maintenance.mdc"
        target_schema_file = cursor_rules_dir / f"graphiti-{project_name}-schema.mdc"

        # Check source files
        missing_files = []
        if not core_rule_src.is_file(): missing_files.append(core_rule_src)
        if not maint_rule_src.is_file(): missing_files.append(maint_rule_src)
        if not schema_template_src.is_file(): missing_files.append(schema_template_src)
        if missing_files:
            print(f"{core.RED}Error: Source rule/template files not found:{core.NC}")
            for f in missing_files: print(f"  - {f}")
            sys.exit(1)

        # Create/Update symlinks using relative paths for better portability
        try:
            core_rel_path = os.path.relpath(core_rule_src.resolve(), start=cursor_rules_dir.resolve())
            maint_rel_path = os.path.relpath(maint_rule_src.resolve(), start=cursor_rules_dir.resolve())
        except ValueError:
            # Handle case where paths are on different drives (Windows) - fall back to absolute
            print(f"{core.YELLOW}Warning: Cannot create relative symlink paths (different drives?). Using absolute paths.{core.NC}")
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
            print(f"Linking core rule: {core.CYAN}{core_rule_link.name}{core.NC} -> {core.CYAN}{core_rel_path}{core.NC}")
        else:
            print(f"Core rule link already exists: {core.CYAN}{core_rule_link.name}{core.NC}")

        if maint_rule_link.is_symlink():
            if maint_rule_link.readlink() != Path(maint_rel_path):
                maint_rule_link.unlink()
        elif maint_rule_link.exists():
            maint_rule_link.unlink()

        if not maint_rule_link.exists():
            maint_rule_link.symlink_to(maint_rel_path)
            print(f"Linking maintenance rule: {core.CYAN}{maint_rule_link.name}{core.NC} -> {core.CYAN}{maint_rel_path}{core.NC}")
        else:
            print(f"Maintenance rule link already exists: {core.CYAN}{maint_rule_link.name}{core.NC}")

        # Generate schema file from template
        if target_schema_file.exists():
            print(f"{core.YELLOW}Warning: Project schema file already exists, skipping template generation: {target_schema_file}{core.NC}")
        else:
            print(f"Generating template project schema file: {core.CYAN}{target_schema_file}{core.NC}")
            template_content = schema_template_src.read_text()
            schema_content = template_content.replace("__PROJECT_NAME__", project_name)
            target_schema_file.write_text(schema_content)

        print(f"{core.GREEN}Graphiti Cursor rules setup complete for project '{project_name}'.{core.NC}")

    except OSError as e:
        print(f"{core.RED}Error setting up rules: {e}{core.NC}")
        sys.exit(1)
    except Exception as e:
        print(f"{core.RED}An unexpected error occurred during rule setup: {e}{core.NC}")
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
        entity_name (str): Name for the new entity type
        target_dir (Path): Target project root directory
    """
    # Validate entity_name format
    if not re.fullmatch(REGEX_VALID_NAME, entity_name):
        print(f"{core.RED}Error: Invalid entity name '{entity_name}'. Use only letters, numbers, underscores, and hyphens.{core.NC}")
        sys.exit(1)
        
    # Load project configuration from ai/graph directory
    graph_dir = target_dir / DIR_AI / DIR_GRAPH
    config_path = graph_dir / CONFIG_FILENAME
    if not config_path.is_file():
        print(f"{core.RED}Error: Project configuration file not found: {config_path}{core.NC}")
        print(f"Make sure the project has been initialized with 'graphiti init' first.")
        sys.exit(1)
        
    project_config = yaml_utils.load_yaml_file(config_path, safe=True)
    if project_config is None:
        print(f"{core.RED}Error: Failed to load project configuration from: {config_path}{core.NC}")
        sys.exit(1)
        
    # Validate project config structure
    if CONFIG_KEY_SERVICES not in project_config or not isinstance(project_config[CONFIG_KEY_SERVICES], list) or not project_config[CONFIG_KEY_SERVICES]:
        print(f"{core.RED}Error: Invalid or missing '{CONFIG_KEY_SERVICES}' section in project configuration: {config_path}{core.NC}")
        sys.exit(1)
        
    # Extract the entity directory name from the first service entry
    entity_dir_name = project_config.get(CONFIG_KEY_SERVICES, [{}])[0].get(CONFIG_KEY_ENTITY_DIR, DEFAULT_ENTITY_DIR_NAME)
    
    # Calculate paths - entities directory directly in graph_dir
    project_entity_dir = graph_dir / entity_dir_name
    
    # Generate file name with the entity class name (without Entity suffix)
    class_name = _to_pascal_case(entity_name)
    entity_file_path = project_entity_dir / f"{class_name}{ENTITY_FILE_EXTENSION}"  # Name file after class
    
    # Check if the entity file already exists
    if entity_file_path.exists():
        print(f"{core.RED}Error: Entity file '{class_name}{ENTITY_FILE_EXTENSION}' already exists at: {entity_file_path}{core.NC}")
        sys.exit(1)
        
    # Get path to template file from mcp_server
    mcp_server_dir = core.get_mcp_server_dir()
    example_template_path = mcp_server_dir / "entity_types" / "example" / "custom_entity_example.py"
    
    try:
        # Create the project entity directory if it doesn't exist
        project_entity_dir.mkdir(parents=True, exist_ok=True)

        if not example_template_path.is_file():
            print(f"{core.YELLOW}Warning: Template file not found: {example_template_path}{core.NC}")
            print("Creating a minimal entity file instead.")
            minimal_content = f"""from pydantic import BaseModel, Field

class {class_name}(BaseModel):
    \"\"\"Entity definition for '{entity_name}'.\"\"\"

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
        
        print(f"Created entity file: {core.CYAN}{entity_file_path}{core.NC}")
        print(f"{core.GREEN}Entity '{entity_name}' successfully created.{core.NC}")
        print(f"You can now edit the entity definition in: {core.CYAN}{entity_file_path}{core.NC}")

    except OSError as e:
        print(f"{core.RED}Error creating entity '{entity_name}': {e}{core.NC}")
        sys.exit(1)
    except Exception as e:
        print(f"{core.RED}An unexpected error occurred creating entity '{entity_name}': {e}{core.NC}")
        sys.exit(1)
```

## File: graphiti_cli/core.py
```python
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
    - A mcp_server/ directory
    - Within mcp_server/: entity_types/ directory
    
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
    # Current script should be in mcp_server/graphiti_cli/core.py
    current_file = Path(__file__).resolve()
    if "mcp_server" in current_file.parts and "graphiti_cli" in current_file.parts:
        # Go up to the 'mcp_server' parent, then one more level to reach repo root
        potential_root = current_file.parents[2]  # Two levels up from core.py
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
    mcp_server_dir = path / DIR_MCP_SERVER
    entity_types_dir = mcp_server_dir / DIR_ENTITY_TYPES
    
    return mcp_server_dir.is_dir() and entity_types_dir.is_dir()

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
    Get the mcp_server directory path.
    
    Returns:
        Path: The absolute path to the mcp_server directory
    """
    return get_repo_root() / "mcp_server"

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
    mcp_server_dir = get_mcp_server_dir()
    
    # Ensure the docker-compose.yml file exists
    ensure_docker_compose_file()
    
    # Add -d flag if detached mode is requested
    if detached and subcmd[0] in ["up", "restart"]:  # Add restart for consistency
        subcmd.append("-d")
    
    # Prepare full command
    cmd = ["docker", "compose"] + subcmd
    
    print(f"Running Docker Compose from: {CYAN}{mcp_server_dir}{NC}")
    print(f"Command: {' '.join(cmd)}")
    if log_level != LogLevel.info.value:
        print(f"Log level: {CYAN}{log_level}{NC}")
    
    # Execute the command - Pass the log level as an environment variable
    env = {"GRAPHITI_LOG_LEVEL": log_level}
    run_command(cmd, check=True, env=env, cwd=mcp_server_dir)

def ensure_docker_compose_file() -> None:
    """
    Ensure that the docker-compose.yml file exists by generating it if necessary.
    """
    mcp_server_dir = get_mcp_server_dir()
    compose_file = mcp_server_dir / "docker-compose.yml"
    
    # Use our Python utility (to be implemented in yaml_utils.py) instead of the script
    # Will be implemented after yaml_utils.py is created
    from . import yaml_utils
    try:
        yaml_utils.generate_compose_logic(mcp_server_dir)  # Generate with default log level initially
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
    mcp_server_dir = get_mcp_server_dir()
    
    print(f"{BOLD}Checking build configuration...{NC}")
    
    # Check pyproject.toml to see if we're using local wheel
    pyproject_path = mcp_server_dir / FILE_PYPROJECT_TOML
    try:
        with open(pyproject_path, 'r') as f:
            pyproject_content = f.read()
            
        # Check if we're using local wheel and not published package
        using_local_wheel = PACKAGE_LOCAL_WHEEL_MARKER in pyproject_content
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
        repo_dist = repo_root / DIR_DIST
        server_dist = mcp_server_dir / DIR_DIST
        
        # Check if source dist exists
        if not repo_dist.is_dir():
            print(f"{RED}Error: dist directory not found at {repo_dist}{NC}")
            print(f"Please build the graphiti-core wheel first.")
            sys.exit(1)
        
        # Find wheel files
        wheel_files = list(repo_dist.glob("*.whl"))
        if not wheel_files:
            print(f"{RED}Error: No wheel files found in {repo_dist}{NC}")
            print(f"Please build the graphiti-core wheel first.")
            sys.exit(1)
        
        # Create target directory if needed
        server_dist.mkdir(exist_ok=True, parents=True)
        
        # Copy wheel files
        print(f"Copying wheel files from {CYAN}{repo_dist}{NC} to {CYAN}{server_dist}{NC}")
        for wheel_file in wheel_files:
            shutil.copy2(wheel_file, server_dist)
        
        print(f"{GREEN}Dist directory prepared for Docker build.{NC}")
    
    except Exception as e:
        print(f"{RED}Error checking build configuration: {e}{NC}")
        print(f"{YELLOW}Please ensure your pyproject.toml is properly configured.{NC}")
        sys.exit(1)
```

## File: graphiti_cli/main.py
```python
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
```

## File: graphiti_cli/yaml_utils.py
```python
#!/usr/bin/env python3
"""
YAML utility functions for the Graphiti CLI.
Contains functions for loading/saving YAML files, updating the registry,
and generating the Docker Compose configuration.
"""
import sys
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
import os
from typing import Optional, List, Dict, Any

from .core import get_mcp_server_dir
from constants import (
    # Colors for output
    RED, GREEN, YELLOW, CYAN, NC,
    # Docker/container constants
    CONTAINER_ENTITY_PATH, DEFAULT_PORT_START, DEFAULT_MCP_CONTAINER_PORT_VAR,
    # Directory structure
    DIR_AI, DIR_GRAPH, DIR_ENTITIES, 
    # Environment variables
    ENV_MCP_GROUP_ID, ENV_MCP_USE_CUSTOM_ENTITIES, ENV_MCP_USE_CUSTOM_ENTITIES_VALUE, ENV_MCP_ENTITY_TYPE_DIR,
    # File and path constants
    BASE_COMPOSE_FILENAME, PROJECTS_REGISTRY_FILENAME, DOCKER_COMPOSE_OUTPUT_FILENAME,
    # Project container path
    PROJECT_CONTAINER_ENTITY_PATH,
    # Registry file keys
    REGISTRY_PROJECTS_KEY, REGISTRY_ROOT_DIR_KEY, REGISTRY_CONFIG_FILE_KEY, REGISTRY_ENABLED_KEY,
    # Compose file keys
    COMPOSE_SERVICES_KEY, COMPOSE_CUSTOM_BASE_ANCHOR_KEY, COMPOSE_CONTAINER_NAME_KEY,
    COMPOSE_PORTS_KEY, COMPOSE_ENVIRONMENT_KEY, COMPOSE_VOLUMES_KEY,
    # Project config keys
    PROJECT_SERVICES_KEY, PROJECT_SERVER_ID_KEY, PROJECT_ENTITY_DIR_KEY, 
    PROJECT_CONTAINER_NAME_KEY, PROJECT_PORT_DEFAULT_KEY, PROJECT_GROUP_ID_KEY, PROJECT_ENVIRONMENT_KEY,
    # Service name constants
    SERVICE_NAME_PREFIX
)
from .core import LogLevel

# --- Project AI Graph Dirs ---
PROJECT_AI_GRAPH_DIRS = [DIR_AI, DIR_GRAPH]  # Standard subdirectory path for project entities

# --- Registry File Header Constants ---
REGISTRY_HEADER_LINES = [
    "# !! WARNING: This file is managed by the 'graphiti init' command. !!",
    "# !! Avoid manual edits unless absolutely necessary.                 !!",
    "#",
    "# Maps project names to their configuration details.",
    "# Paths should be absolute for reliability.",
]

# --- Docker Compose Header Constants ---
DOCKER_COMPOSE_HEADER_LINES = [
    "# Generated by graphiti CLI",
    "# Do not edit this file directly. Modify base-compose.yaml or project-specific mcp-config.yaml files instead.",
    "",
    "# --- Custom MCP Services Info ---"
]

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

# --- Logic from _yaml_helper.py ---
def update_registry_logic(
    registry_file: Path,
    project_name: str,
    root_dir: Path,  # Expecting resolved absolute path
    config_file: Path,  # Expecting resolved absolute path
    enabled: bool = True
) -> bool:
    """
    Updates the central project registry file (mcp-projects.yaml).
    Corresponds to the logic in the old _yaml_helper.py.
    
    Args:
        registry_file (Path): Path to the registry file
        project_name (str): Name of the project
        root_dir (Path): Absolute path to the project root directory
        config_file (Path): Absolute path to the project config file
        enabled (bool): Whether the project should be enabled
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"Updating registry '{registry_file}' for project '{project_name}'")
    if not root_dir.is_absolute() or not config_file.is_absolute():
        print("Error: Project root_dir and config_file must be absolute paths.")
        return False

    if not config_file.exists():
        print(f"Warning: Project config file '{config_file}' does not exist.")
        # Allow continuing for init scenarios

    # Create registry file with header if it doesn't exist
    if not registry_file.exists():
        print(f"Creating new registry file: {registry_file}")
        initial_data = CommentedMap({REGISTRY_PROJECTS_KEY: CommentedMap()})
        try:
            write_yaml_file(initial_data, registry_file, header=REGISTRY_HEADER_LINES)
        except Exception:
            return False  # Error handled in write_yaml_file

    # Load existing registry data using round-trip loader
    data = load_yaml_file(registry_file, safe=False)
    if data is None:
        print(f"Error: Could not load registry file {registry_file}")
        return False

    if not isinstance(data, dict) or REGISTRY_PROJECTS_KEY not in data:
        print(f"Error: Invalid registry file format in {registry_file}. Missing '{REGISTRY_PROJECTS_KEY}' key.")
        return False

    # Ensure 'projects' key exists and is a map
    if data.get(REGISTRY_PROJECTS_KEY) is None:
        data[REGISTRY_PROJECTS_KEY] = CommentedMap()
    elif not isinstance(data[REGISTRY_PROJECTS_KEY], dict):
        print(f"Error: '{REGISTRY_PROJECTS_KEY}' key in {registry_file} is not a dictionary.")
        return False

    # Add or update the project entry (convert Paths to strings for YAML)
    project_entry = CommentedMap({
        REGISTRY_ROOT_DIR_KEY: str(root_dir),
        REGISTRY_CONFIG_FILE_KEY: str(config_file),
        REGISTRY_ENABLED_KEY: enabled
    })
    data[REGISTRY_PROJECTS_KEY][project_name] = project_entry

    # Write back to the registry file
    try:
        # Preserve header by reading first few lines if necessary (complex)
        # Simpler: Assume header is managed manually or re-added if file recreated.
        # We rewrite the whole file here.
        write_yaml_file(data, registry_file)
        print(f"Successfully updated registry for project '{project_name}'")
        return True
    except Exception:
        return False  # Error handled in write_yaml_file

# --- Logic from generate_compose.py ---
def generate_compose_logic(
    mcp_server_dir: Path
):
    """
    Generates the final docker-compose.yml by merging base and project configs.
    Corresponds to the logic in the old generate_compose.py.
    
    Args:
        mcp_server_dir (Path): Path to the mcp_server directory
    """
    print("Generating docker-compose.yml...")
    base_compose_path = mcp_server_dir / BASE_COMPOSE_FILENAME
    projects_registry_path = mcp_server_dir / PROJECTS_REGISTRY_FILENAME
    output_compose_path = mcp_server_dir / DOCKER_COMPOSE_OUTPUT_FILENAME

    # Load base compose file
    compose_data = load_yaml_file(base_compose_path, safe=False)
    if compose_data is None or not isinstance(compose_data, dict):
        print(f"Error: Failed to load or parse base compose file: {base_compose_path}")
        sys.exit(1)

    if COMPOSE_SERVICES_KEY not in compose_data or not isinstance(compose_data.get(COMPOSE_SERVICES_KEY), dict):
        print(f"Error: Invalid structure in '{base_compose_path}'. Missing '{COMPOSE_SERVICES_KEY}' dictionary.")
        sys.exit(1)

    # Load project registry safely
    projects_registry = load_yaml_file(projects_registry_path, safe=True)
    if projects_registry is None:
        print(f"Warning: Project registry file '{projects_registry_path}' not found or failed to parse. No custom services will be added.")
        projects_registry = {REGISTRY_PROJECTS_KEY: {}}
    elif REGISTRY_PROJECTS_KEY not in projects_registry or not isinstance(projects_registry[REGISTRY_PROJECTS_KEY], dict):
        print(f"Warning: Invalid format or missing '{REGISTRY_PROJECTS_KEY}' key in '{projects_registry_path}'. No custom services will be added.")
        projects_registry = {REGISTRY_PROJECTS_KEY: {}}

    # --- Generate Custom Service Definitions ---
    services_map = compose_data[COMPOSE_SERVICES_KEY]  # Should be CommentedMap

    # Find the anchor object for merging
    custom_base_anchor_obj = compose_data.get(COMPOSE_CUSTOM_BASE_ANCHOR_KEY)
    if not custom_base_anchor_obj:
        print(f"{RED}Error: Could not find '{COMPOSE_CUSTOM_BASE_ANCHOR_KEY}' definition in {base_compose_path}.{NC}")
        sys.exit(1)

    overall_service_index = 0
    # Iterate through projects from the registry
    for project_name, project_data in projects_registry.get(REGISTRY_PROJECTS_KEY, {}).items():
        if not isinstance(project_data, dict) or not project_data.get(REGISTRY_ENABLED_KEY, False):
            continue  # Skip disabled or invalid projects

        project_config_path_str = project_data.get(REGISTRY_CONFIG_FILE_KEY)
        project_root_dir_str = project_data.get(REGISTRY_ROOT_DIR_KEY)

        if not project_config_path_str or not project_root_dir_str:
            print(f"Warning: Skipping project '{project_name}' due to missing '{REGISTRY_CONFIG_FILE_KEY}' or '{REGISTRY_ROOT_DIR_KEY}'.")
            continue

        project_config_path = Path(project_config_path_str)
        project_root_dir = Path(project_root_dir_str)

        # Load the project's specific mcp-config.yaml
        project_config = load_yaml_file(project_config_path, safe=True)
        if project_config is None:
            print(f"Warning: Skipping project '{project_name}' because config file '{project_config_path}' could not be loaded.")
            continue

        if PROJECT_SERVICES_KEY not in project_config or not isinstance(project_config[PROJECT_SERVICES_KEY], list):
            print(f"Warning: Skipping project '{project_name}' due to missing or invalid '{PROJECT_SERVICES_KEY}' list in '{project_config_path}'.")
            continue

        # Iterate through services defined in the project's config
        for server_conf in project_config[PROJECT_SERVICES_KEY]:
            if not isinstance(server_conf, dict):
                print(f"Warning: Skipping invalid service entry in '{project_config_path}': {server_conf}")
                continue

            server_id = server_conf.get(PROJECT_SERVER_ID_KEY)
            entity_type_dir = server_conf.get(PROJECT_ENTITY_DIR_KEY)  # Relative path within project

            if not server_id or not entity_type_dir:
                print(f"Warning: Skipping service in '{project_name}' due to missing '{PROJECT_SERVER_ID_KEY}' or '{PROJECT_ENTITY_DIR_KEY}': {server_conf}")
                continue

            # --- Determine Service Configuration ---
            service_name = f"{SERVICE_NAME_PREFIX}{server_id}"
            container_name = server_conf.get(PROJECT_CONTAINER_NAME_KEY, service_name)  # Default to service_name
            port_default = server_conf.get(PROJECT_PORT_DEFAULT_KEY, DEFAULT_PORT_START + overall_service_index + 1)
            port_mapping = f"{port_default}:${{{DEFAULT_MCP_CONTAINER_PORT_VAR}}}"  # Use f-string

            # --- Build Service Definition using CommentedMap ---
            new_service = CommentedMap()
            # Add the merge key first using the anchor object
            new_service.add_yaml_merge([(0, custom_base_anchor_obj)])  # Merge base config

            new_service[COMPOSE_CONTAINER_NAME_KEY] = container_name
            new_service[COMPOSE_PORTS_KEY] = [port_mapping]  # Ports must be a list

            # --- Environment Variables ---
            env_vars = CommentedMap()  # Use CommentedMap to preserve order if needed
            mcp_group_id = server_conf.get(PROJECT_GROUP_ID_KEY, project_name)  # Default group_id to project_name
            env_vars[ENV_MCP_GROUP_ID] = mcp_group_id
            env_vars[ENV_MCP_USE_CUSTOM_ENTITIES] = ENV_MCP_USE_CUSTOM_ENTITIES_VALUE  # Assume true if defined here

            # Calculate absolute host path for entity volume mount
            abs_host_entity_path = (project_root_dir / DIR_AI / DIR_GRAPH / entity_type_dir).resolve()
            if not abs_host_entity_path.is_dir():
                print(f"Warning: Entity directory '{abs_host_entity_path}' for service '{service_name}' does not exist. Volume mount might fail.")
                # Continue anyway, Docker will create an empty dir inside container if host path doesn't exist

            # Set container path for entity directory env var
            env_vars[ENV_MCP_ENTITY_TYPE_DIR] = PROJECT_CONTAINER_ENTITY_PATH

            # Add project-specific environment variables from mcp-config.yaml
            project_environment = server_conf.get(PROJECT_ENVIRONMENT_KEY, {})
            if isinstance(project_environment, dict):
                env_vars.update(project_environment)
            else:
                print(f"Warning: Invalid '{PROJECT_ENVIRONMENT_KEY}' section for service '{service_name}' in '{project_config_path}'. Expected a dictionary.")

            new_service[COMPOSE_ENVIRONMENT_KEY] = env_vars

            # --- Volumes ---
            # Ensure volumes list exists (might be added by anchor merge, check needed?)
            # setdefault is safer if anchor doesn't guarantee 'volumes'
            if COMPOSE_VOLUMES_KEY not in new_service:
                new_service[COMPOSE_VOLUMES_KEY] = []
            elif not isinstance(new_service[COMPOSE_VOLUMES_KEY], list):
                print(f"Warning: '{COMPOSE_VOLUMES_KEY}' merged from anchor for service '{service_name}' is not a list. Overwriting.")
                new_service[COMPOSE_VOLUMES_KEY] = []

            # Append the entity volume mount (read-only)
            new_service[COMPOSE_VOLUMES_KEY].append(f"{abs_host_entity_path}:{PROJECT_CONTAINER_ENTITY_PATH}:ro")

            # --- Add to Services Map ---
            services_map[service_name] = new_service
            overall_service_index += 1

    # --- Write Output File ---
    header = DOCKER_COMPOSE_HEADER_LINES + [
        f"# Default Ports: Assigned sequentially starting from {DEFAULT_PORT_START + 1}",
        "#              Can be overridden by specifying 'port_default' in project's mcp-config.yaml.",
    ]
    try:
        write_yaml_file(compose_data, output_compose_path, header=header)
        print(f"Successfully generated '{output_compose_path}'.")
    except Exception:
        # Error already printed by write_yaml_file
        sys.exit(1)
```

## File: rules/examples/graphiti-example-schema.md
```markdown
---
description: Use this rule when working specifically within the 'example' project context to understand its unique entities (Product, Company), relationships (PRODUCES), and extraction guidelines.
globs: mcp_server/entity_types/example/*.py
alwaysApply: false
---

# Graphiti Schema: Example Project

This document outlines the specific knowledge graph schema for the 'example' project.

**Core Rules Reference:** For general Graphiti tool usage and foundational entity extraction principles, refer to `@graphiti-mcp-core-rules.md`.

**Maintenance:** For rules on how to update *this* schema file, refer to `@graphiti-knowledge-graph-maintenance.md`.

## 1. Defined Entity Types

The following entity types are defined for this project:

*   **`Product`**: Represents a specific good or service offered.
    *   Reference: `@mcp_server/entity_types/example/custom_entity_example.py`
    *   Fields: `name` (str), `description` (str), `category` (str)
*   **`Company`**: Represents a business organization.
    *   Reference: `@mcp_server/entity_types/example/company_entity.py`
    *   Fields: `name` (str), `industry` (str | None)

## 2. Defined Relationships (Facts)

The primary relationship captured in this project is:

*   **Subject:** `Company`
*   **Predicate:** `PRODUCES`
*   **Object:** `Product`

    *Example Fact:* `(Company: 'Acme Corp') --[PRODUCES]-> (Product: 'Widget Pro')`

**Extraction Rule:** When extracting facts of this type, ensure both the Company and Product entities are identified according to their definitions.

## 3. Project-Specific Extraction Guidelines

These guidelines supplement or specialize the instructions within the entity definitions and core rules:

*   **Product Category Inference:** If a `Product`'s category is not explicitly stated but its producing `Company`'s `industry` is known, you *may* infer the category from the industry if it's a direct match (e.g., a Tech company likely produces Software/Hardware). State the inference basis in the extraction reasoning.
*   **Disambiguation:** If multiple companies could produce a mentioned product, prioritize the company most recently discussed or most closely associated with the product description in the context.

## 4. Future Evolution

This schema may be expanded to include other entities (e.g., `Customer`, `Review`) and relationships (e.g., `SELLS`, `REVIEWS`) as the project needs evolve. Follow the process in `@graphiti-knowledge-graph-maintenance.md` to propose changes.
```

## File: rules/templates/project_schema_template.md
```markdown
---
description: Use this rule when working specifically within the '__PROJECT_NAME__' project context to understand its unique entities, relationships, and extraction guidelines.
globs: # Add relevant globs for your project files, e.g., src/**/*.py
alwaysApply: false
---

# Graphiti Schema: __PROJECT_NAME__ Project

This document outlines the specific knowledge graph schema for the '__PROJECT_NAME__' project.

**Core Rules Reference:** For general Graphiti tool usage and foundational entity extraction principles, refer to `@graphiti-mcp-core-rules.mdc`.

**Maintenance:** For rules on how to update *this* schema file, refer to `@graphiti-knowledge-graph-maintenance.mdc`.

---

## 1. Defined Entity Types

*Add definitions for entities specific to the '__PROJECT_NAME__' project here.*
*Reference the entity definition files (e.g., Python classes) if applicable.*

Example:
*   **`MyEntity`**: Description of what this entity represents.
    *   Reference: `@path/to/your/entity/definition.py` (if applicable)
    *   Fields: `field1` (type), `field2` (type)

---

## 2. Defined Relationships (Facts)

*Define the key relationships (subject-predicate-object triples) specific to '__PROJECT_NAME__'.*

Example:
*   **Subject:** `MyEntity`
*   **Predicate:** `RELATED_TO`
*   **Object:** `AnotherEntity`

    *Example Fact:* `(MyEntity: 'Instance A') --[RELATED_TO]-> (AnotherEntity: 'Instance B')`
    *Extraction Rule:* Briefly describe how to identify this relationship.

---

## 3. Project-Specific Extraction Guidelines

*Add any extraction rules or nuances unique to the '__PROJECT_NAME__' project.*
*These guidelines supplement or specialize instructions in entity definitions and core rules.*

Example:
*   **Handling Ambiguity:** How to resolve conflicts when multiple potential entities match.
*   **Inference Rules:** Conditions under which properties can be inferred.

---

## 4. Future Evolution

*Briefly mention potential future directions or areas for schema expansion.*
```

## File: rules/graphiti-knowledge-graph-maintenance.md
```markdown
---
description: Use this rule when you need to propose changes (additions, modifications) to a project's specific knowledge graph schema file (`graphiti-[project-name]-schema.md`).
globs: 
alwaysApply: false
---

# Graphiti Knowledge Graph Maintenance Rules

## 1. Purpose and Scope

This document provides rules for AI agents on how to maintain and update the **project-specific knowledge graph schema file**, typically named `graphiti-[project-name]-schema.md`.

**Goal:** Ensure consistency between the defined project schema, the agent's entity extraction behavior for this project, and the actual structure of the project's knowledge graph over time.

**Key Distinctions:**
- This rule governs the *maintenance* of the project schema.
- For general rules on using Graphiti tools, refer to `@graphiti-mcp-core-rules.md`.
- For the specific entities and relationships of *this* project, refer to `graphiti-[project-name]-schema.md`.

**Scope Limitation:** These rules apply *only* to proposing changes to the project-specific `graphiti-[project-name]-schema.md` file. Do not use these rules to modify `@graphiti-mcp-core-rules.md` or this file itself.

## 2. Primacy of the Project Schema

- The `graphiti-[project-name]-schema.md` file is the **single source of truth** for this project's unique knowledge structure (entities, relationships, properties).
- Specific rules within the project schema **override or specialize** the general guidelines found in `@graphiti-mcp-core-rules.md`.

## 3. When to Consult the Project Schema

You **must** consult the relevant `graphiti-[project-name]-schema.md` file **before**:
- Defining any new entity type or relationship that appears specific to the current project.
- Extracting entities, facts, or relationships based on project-specific requirements mentioned by the user or discovered in project context.
- Answering user questions about the project's established knowledge structure, entities, or relationships.

## 4. Consistency Verification

- Before adding any new entity instance, fact, or relationship that seems specific to the project, **verify** that it conforms to the existing definitions and relationship rules documented in `graphiti-[project-name]-schema.md`.
- If the information doesn't fit the existing schema, proceed to Section 5 (Schema Evolution).

## 5. Schema Evolution and Update Process

Project knowledge schemas are expected to evolve. If you identify a need for a **new** entity type, relationship, property, or a **modification** to an existing one based on user interaction or task requirements:

1.  **Identify the Need:** Clearly determine the required change (e.g., "Need a 'SoftwareComponent' entity type," "Need to add a 'dependency' relationship between 'SoftwareComponent' entities," "Need to add a 'version' property to 'SoftwareComponent'").
2.  **Consult Existing Schema:** Double-check `graphiti-[project-name]-schema.md` to confirm the element truly doesn't exist or needs modification.
3.  **Propose Schema Update:**
    - Formulate a proposed change to the `graphiti-[project-name]-schema.md` file.
    - Define the new/modified element clearly, following the structural best practices (like those derived from the entity templates mentioned in `@graphiti-mcp-core-rules.md`).
    - Format the proposed edit for the `.md` file itself according to the guidelines in `@creating-cursor-rules.mdc`.
    - Include a justification (see Section 6).
    - Use the appropriate tool (e.g., `edit_file`) to propose this change to the `graphiti-[project-name]-schema.md` file.
4.  **Await Outcome:** Wait for the schema update proposal to be accepted or rejected.
5.  **Proceed Based on Outcome:**
    - **If Accepted:** You can now proceed with the original task (e.g., entity extraction, graph update) using the newly defined/modified schema element.
    - **If Rejected:** Do not proceed with adding graph data that violates the established schema. Inform the user if necessary, explaining that the required structure is not defined in the project schema.

## 6. Justification for Schema Changes

- When proposing any change to the `graphiti-[project-name]-schema.md`, provide a brief, clear justification.
- Link the justification directly to the user request, conversation context, or specific information encountered that necessitates the schema change. Example: "Justification: User requested tracking software components and their dependencies, which requires adding a 'SoftwareComponent' entity and a 'dependency' relationship to the project schema."

## 7. Schema Validation (Best Practice)

- Before finalizing a schema change proposal, briefly consider its potential impact:
    - Does the change conflict with existing data in the knowledge graph?
    - Does it align with the overall goals of the project as understood?
    - Does it maintain the clarity and usefulness of the schema?
- Mention any potential conflicts or considerations in your justification if significant.

**Remember:** Maintaining an accurate and consistent project schema is crucial for reliable knowledge management and effective AI assistance within the project context.
```

## File: rules/graphiti-mcp-core-rules.md
```markdown
---
description: Use this rule first for general guidance on using Graphiti MCP server tools (entity extraction, memory). It explains the overall rule structure and links to project-specific schemas and maintenance procedures.
globs: 
alwaysApply: false
---

# Graphiti MCP Tools Guide for AI Agents

## Understanding Graphiti Rule Structure

This document provides the **core, foundational guidelines** for using the Graphiti MCP server tools, including entity extraction and agent memory management via the knowledge graph. These rules apply generally across projects.

For effective project work, be aware of the three key types of Graphiti rules:

1.  **This Core Rule (`@graphiti-mcp-core-rules.md`):** Your starting point for general tool usage and best practices.
2.  **Project-Specific Schema (`graphiti-[project-name]-schema.md`):** Defines the unique entities, relationships, and extraction nuances for a *specific* project. **Always consult the relevant project schema** when working on project-specific tasks. Example: `@graphiti-example-schema.md`.
3.  **Schema Maintenance (`@graphiti-knowledge-graph-maintenance.md`):** Explains the *process* for proposing updates or changes to a project-specific schema file.

**Always prioritize rules in the project-specific schema** if they conflict with these general core rules.

## Entity Extraction Principles

- **Use structured extraction patterns:** Follow the AI persona, task, context, and instructions format in entity definitions.
- **Maintain entity type integrity:** Each entity type should have a clear, unique purpose with non-overlapping definitions.
- **Prefer explicit information:** Extract only what is explicitly or strongly implied in the text; avoid assumptions.
- **Handle ambiguity properly:** If information is missing or uncertain, acknowledge the ambiguity rather than fabricating details.
- **Follow field definitions strictly:** Respect the description and constraints defined for each field in the entity model.

## Creating New Entity Types

- **Utilize the `graphiti add-entities` command:** Create new entity type sets with proper scaffolding.
- **Follow the template pattern:** Use the comprehensive docstring format from `custom_entity_example.py` when defining new entity types.
- **Structure entity classes clearly:** Include AI persona, task definition, context explanation, detailed extraction instructions, and output format.
- **Use descriptive field definitions:** Each field should have clear descriptions using the Field annotations.
- **Document extraction logic:** Include specific instructions for identifying and extracting each required field.

## Agent Memory Management

### Before Starting Any Task

- **Always search first:** Use the `search_nodes` tool to look for relevant preferences and procedures before beginning work.
- **Search for facts too:** Use the `search_facts` tool to discover relationships and factual information that may be relevant to your task.
- **Filter by entity type:** Specify `Preference`, `Procedure`, `Requirement`, or other relevant entity types in your node search to get targeted results.
- **Review all matches:** Carefully examine any preferences, procedures, or facts that match your current task.

### Always Save New or Updated Information

- **Capture requirements and preferences immediately:** When a user expresses a requirement or preference, use `add_episode` to store it right away.
  - _Best practice:_ Split very long requirements into shorter, logical chunks.
- **Be explicit if something is an update to existing knowledge.** Only add what's changed or new to the graph.
- **Document procedures clearly:** When you discover how a user wants things done, record it as a procedure.
- **Record factual relationships:** When you learn about connections between entities, store these as facts.
- **Be specific with categories:** Label entities with clear categories for better retrieval later.

### During Your Work

- **Respect discovered preferences:** Align your work with any preferences you've found.
- **Follow procedures exactly:** If you find a procedure for your current task, follow it step by step.
- **Apply relevant facts:** Use factual information to inform your decisions and recommendations.
- **Stay consistent:** Maintain consistency with previously identified entities, preferences, procedures, and facts.

## Best Practices for Tool Usage

- **Search before suggesting:** Always check if there's established knowledge before making recommendations.
- **Combine node and fact searches:** For complex tasks, search both nodes and facts to build a complete picture.
- **Use `center_node_uuid`:** When exploring related information, center your search around a specific node.
- **Prioritize specific matches:** More specific information takes precedence over general information.
- **Be proactive:** If you notice patterns in user behavior, consider storing them as preferences or procedures.
- **Document your reasoning:** When making extraction or classification decisions, briefly note your reasoning.
- **Handle edge cases gracefully:** Plan for anomalies and develop consistent strategies for handling them.
- **Validate entity coherence:** Ensure extracted entities form a coherent, logically consistent set.
- **Understand parameter behavior:** Be aware of specific tool parameter nuances:
  - For `mcp_graphiti_core_add_episode`, avoid explicitly providing `group_id` as a string—let the system use defaults from command line configuration or generate one automatically.
  - Use episode source types appropriately: 'text' for plain content, 'json' for structured data that should automatically extract entities and relationships, and 'message' for conversation-style content.
- **Leverage advanced search capabilities:** When using search tools:
  - Use hybrid search combining vector similarity, full-text search, and graph traversal.
  - Set appropriate `max_nodes` and `max_facts` to control result volume.
  - Apply `entity` parameter when filtering for specific entity types (e.g., "Preference", "Procedure").
  - Use advanced re-ranking strategies for more contextually relevant results.

## MCP Server Codebase Organization

- **Prefer flat directory structures:** Use consolidated, shallow directory hierarchies over deeply nested ones.
- **Group similar entity types:** Place related entity types within a single directory (e.g., `entity_types/graphiti/`).
- **Follow semantic naming:** Name entity type files according to their semantic type (e.g., `ArchitecturalPattern.py`) rather than using generic names.
- **Remove redundant files:** Keep the codebase clean by removing unnecessary `__init__.py` files in auto-loaded directories.
- **Clean up after reorganization:** Systematically remove empty directories after file restructuring.
- **Maintain proper entity structure:** Ensure all entity types follow the Pydantic model pattern with well-defined fields, descriptions, and extraction instructions.

## Maintaining Context and Continuity

- **Track conversation history:** Reference relevant prior exchanges when making decisions.
- **Build knowledge incrementally:** Add to the graph progressively as new information emerges.
- **Preserve important context:** Identify and retain critical contextual information across sessions.
- **Connect related entities:** Create explicit links between related entities to build a rich knowledge graph.
- **Support iterative refinement:** Allow for progressive improvement of entity definitions and instances.

**Remember:** The knowledge graph is your memory. Use it consistently, respecting the rules outlined here and, more importantly, the specific definitions and guidelines within the relevant `graphiti-[project-name]-schema.md` file for your current project context. Entity extraction should be precise, consistent, and aligned with the structured models defined in the codebase and the project schema.

---

## Background & References

Maintaining a knowledge graph requires diligence. The goal is not just to store data, but to create a useful, accurate, and evolving representation of knowledge.

*   **Graphiti Project:** This MCP server leverages the Graphiti framework. Understanding its core concepts is beneficial.
    *   [Graphiti GitHub Repository](mdc:https:/github.com/getzep/Graphiti)
    *   [Graphiti Documentation & Guides](mdc:https:/help.getzep.com/graphiti)
    *   Graphiti powers [Zep Agent Memory](mdc:https:/www.getzep.com), detailed in the paper: [Zep: A Temporal Knowledge Graph Architecture for Agent Memory](mdc:https:/arxiv.org/abs/2501.13956).
*   **Neo4j Database:** Graphiti uses Neo4j (v5.26+) as its backend storage.
    *   [Neo4j Developer Documentation](mdc:https:/neo4j.com/docs/getting-started/current)
    *   [Neo4j Desktop](mdc:https:/neo4j.com/download) (Recommended for local development)
*   **Knowledge Graph Principles:** Building and maintaining knowledge graphs involves careful planning and iteration.
    *   **Defining Scope & Entities:** Clearly define the purpose, scope, entities, and relationships for your graph. ([Source: pageon.ai](mdc:https:/www.pageon.ai/blog/how-to-build-a-knowledge-graph), [Source: smythos.com](mdc:https:/smythos.com/ai-agents/ai-tutorials/knowledge-graph-tutorial))
    *   **Maintenance & Validation:** Regularly assess the graph's accuracy and usefulness. Ensure data validity and consistency. Schemas evolve, so plan for iteration. ([Source: stardog.com](mdc:https:/www.stardog.com/building-a-knowledge-graph))

Use the specific rules defined in `@graphiti-knowledge-graph-maintenance.md` when proposing changes to project schemas.
```

## File: .env.example
```
# Graphiti MCP Server Environment Configuration

# --- Required Secrets ---
# Neo4j Database Configuration
# These settings are used to connect to your Neo4j database
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_strong_neo4j_password_here

# OpenAI API Configuration
# Required for LLM operations
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4o

# --- Optional Configuration ---
# OpenAI Base URL (if not using the standard OpenAI API endpoint)
# OPENAI_BASE_URL=https://api.openai.com/v1

# --- Neo4j Connection Configuration ---
# Host ports - ports exposed on your local machine
NEO4J_HOST_HTTP_PORT=7474
NEO4J_HOST_BOLT_PORT=7687

# Container ports - ports used inside the container (rarely need to change)
# NEO4J_CONTAINER_HTTP_PORT=7474
# NEO4J_CONTAINER_BOLT_PORT=7687

# Neo4j Memory Settings
# NEO4J_HEAP_INITIAL=512m # Initial heap size for Neo4j
# NEO4J_HEAP_MAX=1G # Maximum heap size for Neo4j
# NEO4J_PAGECACHE=512m # Page cache size for Neo4j

# --- MCP Server Configuration ---
# Default internal port used by all MCP servers
MCP_ROOT_CONTAINER_PORT=8000

# Root MCP Server (Required)
MCP_ROOT_CONTAINER_NAME=graphiti-mcp-root
MCP_ROOT_HOST_PORT=8000

# --- Custom MCP Servers (Required if uncommented in docker-compose.yml) ---
# Civilization 7 MCP Server
CIV7_CONTAINER_NAME=mcp-civ7
CIV7_PORT=8001

# Filesystem MCP Server
FILESYSTEM_CONTAINER_NAME=mcp-filesystem
FILESYSTEM_PORT=8002

# Magic Candidates MCP Server
CANDIDATES_CONTAINER_NAME=mcp-candidates
CANDIDATES_PORT=8004

# --- Neo4j Container Name ---
NEO4J_CONTAINER_NAME=graphiti-mcp-neo4j

# --- Logging Configuration ---
GRAPHITI_LOG_LEVEL=info

# --- DANGER ZONE ---
# !!! WARNING !!! UNCOMMENTING AND SETTING THE FOLLOWING VARIABLE TO "true" WILL:
# - PERMANENTLY DELETE ALL DATA in the Neo4j database
# - Affect ALL knowledge graphs, not just a specific group
# - Cannot be undone once executed
# Only uncomment and set to "true" when you specifically need to clear all data
# Always comment out or set back to "false" immediately after use
# NEO4J_DESTROY_ENTIRE_GRAPH=true
```

## File: .repomixignore
```
# Add patterns to ignore here, one per line
# Example:
# *.log
# tmp/
```

## File: base-compose.yaml
```yaml
# base-compose.yaml
# Base structure for the Docker Compose configuration, including static services and anchors.

version: "3.8"

# --- Base Definitions (Anchors) ---
# Anchors are defined here and will be loaded by the Python script.

x-mcp-healthcheck: &mcp-healthcheck
  test:
    [
      "CMD-SHELL",
      "curl -s -I --max-time 1 http://localhost:${MCP_ROOT_CONTAINER_PORT:-8000}/sse | grep -q 'text/event-stream' || exit 1",
    ]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 5s

x-neo4j-connection: &neo4j-connection
  NEO4J_URI: "bolt://neo4j:${NEO4J_CONTAINER_BOLT_PORT:-7687}"
  NEO4J_USER: "${NEO4J_USER}"
  NEO4J_PASSWORD: "${NEO4J_PASSWORD}"

x-mcp-env: &mcp-env
  MODEL_NAME: "${MODEL_NAME:-gpt-4o}"
  OPENAI_API_KEY: ${OPENAI_API_KEY?Please set OPENAI_API_KEY in your .env file}
  OPENAI_BASE_URL: ${OPENAI_BASE_URL:-https://api.openai.com/v1}
  GRAPHITI_LOG_LEVEL: ${GRAPHITI_LOG_LEVEL:-info}
  PATH: "/app:/root/.local/bin:${PATH}"

x-graphiti-mcp-base: &graphiti-mcp-base
  build:
    context: .
    dockerfile: Dockerfile
  env_file:
    - path: .env
      required: true
  environment:
    <<: [*mcp-env, *neo4j-connection] # Aliases refer to anchors above
  healthcheck:
    <<: *mcp-healthcheck             # Alias refers to anchor above
  restart: unless-stopped

x-graphiti-mcp-custom-base: &graphiti-mcp-custom-base
  <<: *graphiti-mcp-base # Alias refers to anchor above
  depends_on:
    neo4j:
      condition: service_healthy
    graphiti-mcp-root:
      condition: service_healthy

# --- Services (Static Ones) ---
services:
  # --- Database ---
  neo4j:
    image: neo4j:5.26.0
    container_name: ${NEO4J_CONTAINER_NAME:-graphiti-mcp-neo4j}
    ports:
      - "${NEO4J_HOST_HTTP_PORT:-7474}:${NEO4J_CONTAINER_HTTP_PORT:-7474}"
      - "${NEO4J_HOST_BOLT_PORT:-7687}:${NEO4J_CONTAINER_BOLT_PORT:-7687}"
    environment:
      - NEO4J_AUTH=${NEO4J_USER?Please set NEO4J_USER in your .env file}/${NEO4J_PASSWORD?Please set NEO4J_PASSWORD in your .env file}
      - NEO4J_server_memory_heap_initial__size=${NEO4J_HEAP_INITIAL:-512m}
      - NEO4J_server_memory_heap_max__size=${NEO4J_HEAP_MAX:-1G}
      - NEO4J_server_memory_pagecache_size=${NEO4J_PAGECACHE:-512m}
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    healthcheck:
      test:
        [
          "CMD",
          "wget",
          "-O",
          "/dev/null",
          "http://localhost:${NEO4J_CONTAINER_HTTP_PORT:-7474}",
        ]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  # --- Root MCP Server (Required) ---
  graphiti-mcp-root:
    <<: *graphiti-mcp-base # Alias refers to anchor above
    container_name: ${MCP_ROOT_CONTAINER_NAME:-graphiti-mcp-root}
    depends_on:
      neo4j:
        condition: service_healthy
    ports:
      - "${MCP_ROOT_HOST_PORT:-8000}:${MCP_ROOT_CONTAINER_PORT:-8000}"
    environment:
      # Specific env vars merged with base env vars via the alias above
      MCP_GROUP_ID: "root"
      MCP_USE_CUSTOM_ENTITIES: "true"
      MCP_ENTITY_TYPE_DIR: "entity_types/base"

# --- Volumes ---
volumes:
  neo4j_data: # Persists Neo4j graph data
  neo4j_logs: # Persists Neo4j logs
```

## File: constants.py
```python
#!/usr/bin/env python3
"""
Shared constants for the Graphiti MCP server ecosystem.
This module centralizes constants used across different components.
"""
import logging

# --- Logging Constants ---
# Constants related to Graphiti's logging mechanism
DEFAULT_LOG_LEVEL_STR = "info"                 # Default logging level as a string
DEFAULT_LOG_LEVEL = logging.INFO               # Default logging level as a Python logging constant
ENV_GRAPHITI_LOG_LEVEL = "GRAPHITI_LOG_LEVEL"  # Environment variable name for configuring the logging level

# --- Directory Structure Constants ---
# Standard directories used in Graphiti project structure
DIR_AI = "ai"                  # AI-related files
DIR_GRAPH = "graph"            # Knowledge graph data
DIR_ENTITIES = "entities"      # Entity definitions
DIR_MCP_SERVER = "mcp_server"  # MCP server code
DIR_ENTITY_TYPES = "entity_types"  # Entity type definitions for knowledge graph
DIR_DIST = "dist"              # Distribution directory for built packages

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
ENV_MCP_ENTITY_TYPE_DIR = "MCP_ENTITY_TYPE_DIR"  # Directory for custom entity type definitions

# --- Container Path Constants ---
# Paths used within Docker containers for entity type mounting
CONTAINER_ENTITY_PATH = "/app/entity_types"  # Default entity types
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
ENTITY_FILE_EXTENSION = ".py"        # File extension for Python entity type definitions

# --- Configuration Key Constants ---
# Keys used in configuration files for MCP settings
CONFIG_KEY_SERVICES = "services"            # Services section
CONFIG_KEY_ID = "id"                        # Server ID
CONFIG_KEY_CONTAINER_NAME = "container_name"  # Docker container name
CONFIG_KEY_PORT_DEFAULT = "port_default"    # Default port
CONFIG_KEY_GROUP_ID = "group_id"            # Group ID for namespacing
CONFIG_KEY_ENTITY_DIR = "entity_dir"        # Entity directory path
CONFIG_KEY_ENVIRONMENT = "environment"      # Environment variables

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
PROJECT_ENTITY_DIR_KEY = "entity_dir"              # Entity directory
PROJECT_CONTAINER_NAME_KEY = "container_name"      # Container name
PROJECT_PORT_DEFAULT_KEY = "port_default"          # Default port
PROJECT_GROUP_ID_KEY = "group_id"                  # Group ID
PROJECT_ENVIRONMENT_KEY = "environment"            # Environment variables

# --- Default Value Constants ---
# Default values used when specific settings are not provided
DEFAULT_CUSTOM_CONTAINER_NAME = "custom-name"  # Default container name for custom services
DEFAULT_CUSTOM_PORT = "8001"                   # Default port for custom services
DEFAULT_ENTITY_DIR_NAME = "entities"           # Default name for entity directories

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
```

## File: docker-compose.yml
```yaml
# Generated by graphiti CLI
# Do not edit this file directly. Modify base-compose.yaml or project-specific mcp-config.yaml files instead.

# --- Custom MCP Services Info ---
# Default Ports: Assigned sequentially starting from 8001
#              Can be overridden by specifying 'port_default' in project's mcp-config.yaml.

# base-compose.yaml
# Base structure for the Docker Compose configuration, including static services and anchors.

version: "3.8"

# --- Base Definitions (Anchors) ---
# Anchors are defined here and will be loaded by the Python script.

x-mcp-healthcheck: &mcp-healthcheck
  test: ["CMD-SHELL", "curl -s -I --max-time 1 http://localhost:${MCP_ROOT_CONTAINER_PORT:-8000}/sse
        | grep -q 'text/event-stream' || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 5s

x-neo4j-connection: &neo4j-connection
  NEO4J_URI: "bolt://neo4j:${NEO4J_CONTAINER_BOLT_PORT:-7687}"
  NEO4J_USER: "${NEO4J_USER}"
  NEO4J_PASSWORD: "${NEO4J_PASSWORD}"

x-mcp-env: &mcp-env
  MODEL_NAME: "${MODEL_NAME:-gpt-4o}"
  OPENAI_API_KEY: ${OPENAI_API_KEY?Please set OPENAI_API_KEY in your .env file}
  OPENAI_BASE_URL: ${OPENAI_BASE_URL:-https://api.openai.com/v1}
  GRAPHITI_LOG_LEVEL: ${GRAPHITI_LOG_LEVEL:-info}
  PATH: "/app:/root/.local/bin:${PATH}"

x-graphiti-mcp-base: &graphiti-mcp-base
  build:
    context: .
    dockerfile: Dockerfile
  env_file:
    - path: .env
      required: true
  environment:
    <<: [*mcp-env, *neo4j-connection]
  healthcheck:
    <<: *mcp-healthcheck
                                     # Alias refers to anchor above
  restart: unless-stopped

x-graphiti-mcp-custom-base: &graphiti-mcp-custom-base
  <<: *graphiti-mcp-base
                         # Alias refers to anchor above
  depends_on:
    neo4j:
      condition: service_healthy
    graphiti-mcp-root:
      condition: service_healthy

# --- Services (Static Ones) ---
services:
  # --- Database ---
  neo4j:
    image: neo4j:5.26.0
    container_name: ${NEO4J_CONTAINER_NAME:-graphiti-mcp-neo4j}
    ports:
      - "${NEO4J_HOST_HTTP_PORT:-7474}:${NEO4J_CONTAINER_HTTP_PORT:-7474}"
      - "${NEO4J_HOST_BOLT_PORT:-7687}:${NEO4J_CONTAINER_BOLT_PORT:-7687}"
    environment:
      - NEO4J_AUTH=${NEO4J_USER?Please set NEO4J_USER in your .env file}/${NEO4J_PASSWORD?Please
        set NEO4J_PASSWORD in your .env file}
      - NEO4J_server_memory_heap_initial__size=${NEO4J_HEAP_INITIAL:-512m}
      - NEO4J_server_memory_heap_max__size=${NEO4J_HEAP_MAX:-1G}
      - NEO4J_server_memory_pagecache_size=${NEO4J_PAGECACHE:-512m}
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    healthcheck:
      test: ["CMD", "wget", "-O", "/dev/null", "http://localhost:${NEO4J_CONTAINER_HTTP_PORT:-7474}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  # --- Root MCP Server (Required) ---
  graphiti-mcp-root:
    <<: *graphiti-mcp-base
                           # Alias refers to anchor above
    container_name: ${MCP_ROOT_CONTAINER_NAME:-graphiti-mcp-root}
    depends_on:
      neo4j:
        condition: service_healthy
    ports:
      - "${MCP_ROOT_HOST_PORT:-8000}:${MCP_ROOT_CONTAINER_PORT:-8000}"
    environment:
      # Specific env vars merged with base env vars via the alias above
      MCP_GROUP_ID: "root"
      MCP_USE_CUSTOM_ENTITIES: "true"
      MCP_ENTITY_TYPE_DIR: "entity_types/base"

# --- Volumes ---
  mcp-filesystem-main:
    <<: *graphiti-mcp-custom-base
    environment:
      MCP_GROUP_ID: filesystem
      MCP_USE_CUSTOM_ENTITIES: 'true'
      MCP_ENTITY_TYPE_DIR: /app/project_entities
      GRAPHITI_LOG_LEVEL: debug
    container_name: mcp-filesystem-main
    ports:
      - 8001:${MCP_PORT}
    volumes:
      - /Users/mateicanavra/Documents/.nosync/DEV/mcp-servers/mcp-filesystem/ai/graph/entities:/app/project_entities:ro
  mcp-filesystem-meta:
    <<: *graphiti-mcp-custom-base
    environment:
      MCP_GROUP_ID: filesystem-meta
      MCP_USE_CUSTOM_ENTITIES: 'true'
      MCP_ENTITY_TYPE_DIR: /app/project_entities
    container_name: mcp-filesystem-meta
    ports:
      - 8002:${MCP_PORT}
    volumes:
      - /Users/mateicanavra/Documents/.nosync/DEV/mcp-servers/mcp-filesystem/ai/graph/entities:/app/project_entities:ro
  mcp-magic-candidates-main:
    <<: *graphiti-mcp-custom-base
    environment:
      MCP_GROUP_ID: magic-candidates
      MCP_USE_CUSTOM_ENTITIES: 'true'
      MCP_ENTITY_TYPE_DIR: /app/project_entities
      GRAPHITI_LOG_LEVEL: debug
    container_name: mcp-magic-candidates-main
    ports:
      - 8003:${MCP_PORT}
    volumes:
      - /Users/mateicanavra/Documents/.nosync/DEV/magic-apply-candidates/ai/graph/entities:/app/project_entities:ro
volumes:
  neo4j_data: # Persists Neo4j graph data
  neo4j_logs: # Persists Neo4j logs
```

## File: Dockerfile
```dockerfile
FROM --platform=$BUILDPLATFORM python:3.11-slim AS base

# Set environment variables to prevent buffering issues with logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Install curl, install uv, add its dir to the current PATH, and verify in one step
RUN apt-get update && apt-get install -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Install uv using the recommended installer script
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    # Add uv's ACTUAL installation directory to the PATH for this RUN command's shell
    && export PATH="/root/.local/bin:${PATH}" \
    # Verify uv installation within the same RUN command
    && uv --version

# Add uv's ACTUAL installation directory to the ENV PATH for subsequent stages and the final image
ENV PATH="/root/.local/bin:${PATH}"

# --- Build Stage ---
# Use a build stage to install dependencies
# This helps leverage Docker layer caching
FROM base AS builder

# Create dist directory for local wheel installation if needed
RUN mkdir -p /dist/

# Copy the dist directory contents (containing local wheels)
# This step allows installing local packages like graphiti-core
# Ensure 'dist' exists in your project root and contains necessary wheels before building
COPY dist/* /dist/

# Copy project configuration
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv sync (faster than pip install)
# This installs dependencies specified in pyproject.toml based on uv.lock
# Add --system to allow installation into the container's Python environment
RUN uv pip sync uv.lock --system

# If you want to install the project itself (mcp-server), uncomment the line below
# This makes 'constants.py', 'graphiti_mcp_server.py', etc., available as installed modules
# RUN uv pip install . --no-deps --system


# --- Final Stage ---
# Start from the base image again for a cleaner final image
FROM base

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# Also copy binaries installed by dependencies (like uv itself if installed via pip in builder)
COPY --from=builder /root/.local/bin /root/.local/bin

# Copy application code
COPY graphiti_mcp_server.py ./
COPY constants.py ./
COPY entity_types/ ./entity_types/
COPY entrypoint.sh .

# Make entrypoint script executable
RUN chmod +x ./entrypoint.sh

# Expose the default MCP port (adjust if needed)
EXPOSE 8000

# Set the entrypoint script to run when the container starts
ENTRYPOINT ["./entrypoint.sh"]

# Default command can be overridden (e.g., to specify group_id)
# Example: docker run <image> --group-id my_project
CMD ["--transport", "sse"]
```

## File: entrypoint.sh
```bash
#!/bin/sh
# docker-entrypoint.sh
# This script constructs and executes the graphiti_mcp_server command
# based on environment variables set in docker-compose.yml.

# Exit immediately if a command exits with a non-zero status.
set -e

# Base command parts
CMD_PREFIX="uv run graphiti_mcp_server.py"
CMD_ARGS="--transport sse" # Common arguments

# Append arguments based on environment variables

# --group-id (Required or has default handling in script?)
if [ -n "$MCP_GROUP_ID" ]; then
  CMD_ARGS="$CMD_ARGS --group-id \"$MCP_GROUP_ID\""
else
  echo "Warning: MCP_GROUP_ID environment variable not set."
  # Decide: exit 1? Or let the python script handle default/error?
fi

# --use-custom-entities (Boolean flag)
# Adjust check if different values like "1", "yes" are used
if [ "$MCP_USE_CUSTOM_ENTITIES" = "true" ]; then
  CMD_ARGS="$CMD_ARGS --use-custom-entities"
fi

# --entity-type-dir (Optional path)
if [ -n "$MCP_ENTITY_TYPE_DIR" ]; then
  CMD_ARGS="$CMD_ARGS --entity-type-dir $MCP_ENTITY_TYPE_DIR"
fi

# --entity-types (Optional space-separated list)
# Assumes the python script handles a space-separated list after the flag.
if [ -n "$MCP_ENTITY_TYPES" ]; then
   CMD_ARGS="$CMD_ARGS --entity-types $MCP_ENTITY_TYPES"
fi

# --log-level (Pass based on ENV var)
# Read the env var set by docker compose (from .env or compose override)
if [ -n "$GRAPHITI_LOG_LEVEL" ]; then
  CMD_ARGS="$CMD_ARGS --log-level $GRAPHITI_LOG_LEVEL"
fi

# --destroy-graph (Boolean flag)
if [ "$NEO4J_DESTROY_ENTIRE_GRAPH" = "true" ]; then
  CMD_ARGS="$CMD_ARGS --destroy-graph"
  echo "!!! DANGER !!! NEO4J_DESTROY_ENTIRE_GRAPH flag is set to 'true'."
  echo "!!! WARNING !!! This will PERMANENTLY DELETE ALL DATA in the Neo4j database, not just data for this group."
  echo "                 Set to 'false' immediately after use to prevent accidental data loss."
fi

# Add logic for any other configurable flags here...

# Combine prefix and arguments
FULL_CMD="$CMD_PREFIX $CMD_ARGS"

echo "--------------------------------------------------"
echo " Running MCP Server with Group ID: ${MCP_GROUP_ID:-<Not Set>}"
echo " Executing command: $FULL_CMD"
echo "--------------------------------------------------"

# Use 'exec' to replace the shell process with the Python process.
# "$@" passes along any arguments that might have been added via
# 'command:' in docker-compose.yml (though we aren't using them here).
exec $FULL_CMD "$@"
```

## File: graphiti_mcp_server.py
```python
#!/usr/bin/env python3
"""
Graphiti MCP Server - Exposes Graphiti functionality through the Model Context Protocol (MCP)
"""

import argparse
import asyncio
import importlib
import importlib.util
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Union, cast

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from graphiti_core import Graphiti
from graphiti_core.edges import EntityEdge
from graphiti_core.llm_client import LLMClient
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_client import OpenAIClient
from graphiti_core.nodes import EpisodeType, EpisodicNode
from graphiti_core.search.search_config_recipes import (
    NODE_HYBRID_SEARCH_NODE_DISTANCE,
    NODE_HYBRID_SEARCH_RRF,
)
from graphiti_core.search.search_filters import SearchFilters
from graphiti_core.utils.maintenance.graph_data_operations import clear_data
from entity_types import get_entity_types, get_entity_type_subset, register_entity_type
from constants import DEFAULT_LOG_LEVEL, DEFAULT_LLM_MODEL, ENV_GRAPHITI_LOG_LEVEL

load_dotenv()

# The ENTITY_TYPES dictionary is managed by the registry in mcp_server.entity_types
# NOTE: This global reference is only used for predefined entity subsets below.
# For the latest entity types, always use get_entity_types() directly.
ENTITY_TYPES = get_entity_types()

# Predefined entity type sets for different use cases
REQUIREMENT_ONLY_ENTITY_TYPES = get_entity_type_subset(['Requirement'])
PREFERENCE_ONLY_ENTITY_TYPES = get_entity_type_subset(['Preference'])
PROCEDURE_ONLY_ENTITY_TYPES = get_entity_type_subset(['Procedure'])


# Type definitions for API responses
class ErrorResponse(TypedDict):
    error: str


class SuccessResponse(TypedDict):
    message: str


class NodeResult(TypedDict):
    uuid: str
    name: str
    summary: str
    labels: list[str]
    group_id: str
    created_at: str
    attributes: dict[str, Any]


class NodeSearchResponse(TypedDict):
    message: str
    nodes: list[NodeResult]


class FactSearchResponse(TypedDict):
    message: str
    facts: list[dict[str, Any]]


class EpisodeSearchResponse(TypedDict):
    message: str
    episodes: list[dict[str, Any]]


class StatusResponse(TypedDict):
    status: str
    message: str


# Server configuration classes
class GraphitiConfig(BaseModel):
    """Configuration for Graphiti client.

    Centralizes all configuration parameters for the Graphiti client,
    including database connection details and LLM settings.
    """

    # neo4j_uri: str = 'bolt://localhost:7687'
    neo4j_uri: str = 'bolt://neo4j:7687'
    neo4j_user: str = 'neo4j'
    neo4j_password: str = 'password'
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    model_name: Optional[str] = None
    group_id: Optional[str] = None
    use_custom_entities: bool = False
    entity_type_subset: Optional[list[str]] = None

    @classmethod
    def from_env(cls) -> 'GraphitiConfig':
        """Create a configuration instance from environment variables."""
        return cls(
            # neo4j_uri=os.environ.get('NEO4J_URI', 'bolt://localhost:7687'),
            neo4j_uri=os.environ.get('NEO4J_URI', 'bolt://neo4j:7687'),
            neo4j_user=os.environ.get('NEO4J_USER', 'neo4j'),
            neo4j_password=os.environ.get('NEO4J_PASSWORD', 'password'),
            openai_api_key=os.environ.get('OPENAI_API_KEY'),
            openai_base_url=os.environ.get('OPENAI_BASE_URL'),
            model_name=os.environ.get('MODEL_NAME'),
        )


class MCPConfig(BaseModel):
    """Configuration for MCP server."""

    transport: str


# Configure logging
log_level_str = os.environ.get(ENV_GRAPHITI_LOG_LEVEL, 'info').upper()
log_level = getattr(logging, log_level_str, DEFAULT_LOG_LEVEL)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)
logger.info(f'Initial logging configured with level: {logging.getLevelName(log_level)}')

# Function to reconfigure logging level based on final decision
def configure_logging(level_name: str):
    """
    Configure or reconfigure the logging level based on a string level name.
    
    Args:
        level_name: A string representation of the logging level ('debug', 'info', etc.)
    """
    global logger, log_level
    level_name_upper = level_name.upper()
    new_level = getattr(logging, level_name_upper, DEFAULT_LOG_LEVEL)
    if new_level != log_level:  # Only reconfigure if level changes
        log_level = new_level
        logging.getLogger().setLevel(log_level)  # Set level on root logger
        # Re-get logger instance for safety
        logger = logging.getLogger(__name__)
        logger.info(f"Logging level reconfigured to: {logging.getLevelName(log_level)}")
    else:
        logger.info(f"Logging level remains at: {logging.getLevelName(log_level)}")

# Create global config instance
config = GraphitiConfig.from_env()

# MCP server instructions
GRAPHITI_MCP_INSTRUCTIONS = """
Welcome to Graphiti MCP - a memory service for AI agents built on a knowledge graph. Graphiti performs well
with dynamic data such as user interactions, changing enterprise data, and external information.

Graphiti transforms information into a richly connected knowledge network, allowing you to 
capture relationships between concepts, entities, and information. The system organizes data as episodes 
(content snippets), nodes (entities), and facts (relationships between entities), creating a dynamic, 
queryable memory store that evolves with new information. Graphiti supports multiple data formats, including 
structured JSON data, enabling seamless integration with existing data pipelines and systems.

Facts contain temporal metadata, allowing you to track the time of creation and whether a fact is invalid 
(superseded by new information).

Key capabilities:
1. Add episodes (text, messages, or JSON) to the knowledge graph with the add_episode tool
2. Search for nodes (entities) in the graph using natural language queries with search_nodes
3. Find relevant facts (relationships between entities) with search_facts
4. Retrieve specific entity edges or episodes by UUID
5. Manage the knowledge graph with tools like delete_episode, delete_entity_edge, and clear_graph

The server connects to a database for persistent storage and uses language models for certain operations. 
Each piece of information is organized by group_id, allowing you to maintain separate knowledge domains.

When adding information, provide descriptive names and detailed content to improve search quality. 
When searching, use specific queries and consider filtering by group_id for more relevant results.

For optimal performance, ensure the database is properly configured and accessible, and valid 
API keys are provided for any language model operations.
"""


# MCP server instance
mcp = FastMCP(
    'graphiti',
    instructions=GRAPHITI_MCP_INSTRUCTIONS,
)


# Initialize Graphiti client
graphiti_client: Optional[Graphiti] = None


async def initialize_graphiti(llm_client: Optional[LLMClient] = None, destroy_graph: bool = False):
    """Initialize the Graphiti client with the provided settings.

    Args:
        llm_client: Optional LLMClient instance to use for LLM operations
        destroy_graph: Optional boolean to destroy all Graphiti graphs
    """
    global graphiti_client

    # If no client is provided, create a default OpenAI client
    if not llm_client:
        if config.openai_api_key:
            llm_config = LLMConfig(api_key=config.openai_api_key)
            if config.openai_base_url:
                llm_config.base_url = config.openai_base_url
            if config.model_name:
                llm_config.model = config.model_name
            llm_client = OpenAIClient(config=llm_config)
        else:
            raise ValueError('OPENAI_API_KEY must be set when not using a custom LLM client')

    if not config.neo4j_uri or not config.neo4j_user or not config.neo4j_password:
        raise ValueError('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set')

    graphiti_client = Graphiti(
        uri=config.neo4j_uri,
        user=config.neo4j_user,
        password=config.neo4j_password,
        llm_client=llm_client,
    )

    if destroy_graph:
        logger.info('Destroying graph...')
        await clear_data(graphiti_client.driver)

    # Initialize the graph database with Graphiti's indices
    await graphiti_client.build_indices_and_constraints()
    logger.info('Graphiti client initialized successfully')


def format_fact_result(edge: EntityEdge) -> dict[str, Any]:
    """Format an entity edge into a readable result.

    Since EntityEdge is a Pydantic BaseModel, we can use its built-in serialization capabilities.

    Args:
        edge: The EntityEdge to format

    Returns:
        A dictionary representation of the edge with serialized dates and excluded embeddings
    """
    return edge.model_dump(
        mode='json',
        exclude={
            'fact_embedding',
        },
    )


# Dictionary to store queues for each group_id
# Each queue is a list of tasks to be processed sequentially
episode_queues: dict[str, asyncio.Queue] = {}
# Dictionary to track if a worker is running for each group_id
queue_workers: dict[str, bool] = {}


async def process_episode_queue(group_id: str):
    """Process episodes for a specific group_id sequentially.

    This function runs as a long-lived task that processes episodes
    from the queue one at a time.
    """
    global queue_workers

    logger.info(f'Starting episode queue worker for group_id: {group_id}')
    queue_workers[group_id] = True

    try:
        while True:
            # Get the next episode processing function from the queue
            # This will wait if the queue is empty
            process_func = await episode_queues[group_id].get()

            try:
                # Process the episode
                await process_func()
            except Exception as e:
                logger.error(f'Error processing queued episode for group_id {group_id}: {str(e)}')
            finally:
                # Mark the task as done regardless of success/failure
                episode_queues[group_id].task_done()
    except asyncio.CancelledError:
        logger.info(f'Episode queue worker for group_id {group_id} was cancelled')
    except Exception as e:
        logger.error(f'Unexpected error in queue worker for group_id {group_id}: {str(e)}')
    finally:
        queue_workers[group_id] = False
        logger.info(f'Stopped episode queue worker for group_id: {group_id}')


@mcp.tool()
async def add_episode(
    name: str,
    episode_body: Union[str, Dict[str, Any], List[Any]],
    group_id: Optional[str] = None,
    source: str = 'text',
    source_description: str = '',
    uuid: Optional[str] = None,
    entity_type_subset: Optional[list[str]] = None,
) -> Union[SuccessResponse, ErrorResponse]:
    """Add an episode to the Graphiti knowledge graph. This is the primary way to add information to the graph.

    This function returns immediately and processes the episode addition in the background.
    Episodes for the same group_id are processed sequentially to avoid race conditions.

    Args:
        name (str): Name of the episode
        episode_body (Union[str, Dict[str, Any], List[Any]]): The content of the episode.
                           When source='json', this can be either:
                           - A Python dictionary or list that will be automatically serialized, or
                           - A properly escaped JSON string.
                           The JSON data will be automatically processed to extract entities and relationships.
                           For other source types, this must be a string.
        group_id (str, optional): A unique ID for this graph. If not provided, uses the default group_id from CLI
                                 or a generated one.
        source (str, optional): Source type, must be one of:
                               - 'text': For plain text content (default)
                               - 'json': For structured data
                               - 'message': For conversation-style content
        source_description (str, optional): Description of the source
        uuid (str, optional): Optional UUID for the episode
        entity_type_subset (list[str], optional): Optional list of entity type names to use for this episode.
                                                If not provided, uses all entity types if enabled.

    Examples:
        # Adding plain text content
        add_episode(
            name="Company News",
            episode_body="Acme Corp announced a new product line today.",
            source="text",
            source_description="news article",
            group_id="some_arbitrary_string"
        )

        # Adding structured JSON data as a Python dictionary (preferred method)
        add_episode(
            name="Customer Profile",
            episode_body={"company": {"name": "Acme Technologies"}, "products": [{"id": "P001", "name": "CloudSync"}, {"id": "P002", "name": "DataMiner"}]},
            source="json",
            source_description="CRM data"
        )
        
        # Adding structured JSON data as a pre-serialized string (alternative method)
        add_episode(
            name="Customer Profile",
            episode_body="{\\\"company\\\": {\\\"name\\\": \\\"Acme Technologies\\\"}, \\\"products\\\": [{\\\"id\\\": \\\"P001\\\", \\\"name\\\": \\\"CloudSync\\\"}, {\\\"id\\\": \\\"P002\\\", \\\"name\\\": \\\"DataMiner\\\"}]}",
            source="json",
            source_description="CRM data"
        )

        # Adding message-style content
        add_episode(
            name="Customer Conversation",
            episode_body="user: What's your return policy?\nassistant: You can return items within 30 days.",
            source="message",
            source_description="chat transcript",
            group_id="some_arbitrary_string"
        )

        # Using a specific subset of entity types
        add_episode(
            name="Project Requirements",
            episode_body="We need to implement user authentication with SSO.",
            entity_type_subset=["Requirement"],
            source="text",
            source_description="meeting notes"
        )

    Notes:
        When using source='json':
        - For convenience, you can provide a Python dictionary or list directly (recommended method)
        - Alternatively, you can provide a properly escaped JSON string
        - The JSON will be automatically processed to extract entities and relationships
        - Complex nested structures are supported (arrays, nested objects, mixed data types), but keep nesting to a minimum
        - Entities will be created from appropriate JSON properties
        - Relationships between entities will be established based on the JSON structure
        
        For source='text' and source='message', only string inputs are accepted.
    """
    global graphiti_client, episode_queues, queue_workers

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # Map string source to EpisodeType enum
        source_type = EpisodeType.text
        if source.lower() == 'message':
            source_type = EpisodeType.message
        elif source.lower() == 'json':
            source_type = EpisodeType.json

        # Use the provided group_id or fall back to the default from config
        effective_group_id = group_id if group_id is not None else config.group_id

        # Cast group_id to str to satisfy type checker
        # The Graphiti client expects a str for group_id, not Optional[str]
        group_id_str = str(effective_group_id) if effective_group_id is not None else ''

        # We've already checked that graphiti_client is not None above
        # This assert statement helps type checkers understand that graphiti_client is defined
        assert graphiti_client is not None, 'graphiti_client should not be None here'

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)
        
        # Input validation and preparation
        episode_body_str = ""
        if source_type == EpisodeType.json:
            # For JSON source, we accept both dictionaries/lists and pre-serialized strings
            if isinstance(episode_body, (dict, list)):
                try:
                    episode_body_str = json.dumps(episode_body)
                    logger.debug(f"Successfully serialized dictionary/list to JSON string")
                except TypeError as e:
                    error_msg = f"Failed to serialize episode_body to JSON: {str(e)}"
                    logger.error(error_msg)
                    return {'error': error_msg}
            elif isinstance(episode_body, str):
                # Optionally validate the JSON string
                try:
                    json.loads(episode_body)  # Just for validation
                    episode_body_str = episode_body
                    logger.debug(f"Verified episode_body is a valid JSON string")
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON string provided for episode_body: {str(e)}"
                    logger.error(error_msg)
                    return {'error': error_msg}
            else:
                error_msg = f"Invalid episode_body type for source='json': {type(episode_body)}. Expected dict, list, or string."
                logger.error(error_msg)
                return {'error': error_msg}
        else:
            # For text and message sources, we only accept strings
            if isinstance(episode_body, str):
                episode_body_str = episode_body
            else:
                error_msg = f"Invalid episode_body type for source='{source}': {type(episode_body)}. Expected string."
                logger.error(error_msg)
                return {'error': error_msg}

        # Define the episode processing function
        async def process_episode():
            try:
                logger.info(f"Processing queued episode '{name}' for group_id: {group_id_str}")
                
                # Import here to ensure we get the most up-to-date entity registry
                from entity_types import get_entity_types, get_entity_type_subset
                
                # Determine which entity types to use based on configuration and parameters
                logger.info(f"Configuration settings - use_custom_entities: {config.use_custom_entities}, "
                           f"entity_type_subset param: {entity_type_subset}, "
                           f"config.entity_type_subset: {config.entity_type_subset}")
                
                if not config.use_custom_entities:
                    # If custom entities are disabled, use empty dict
                    entity_types_to_use = {}
                    logger.info("Custom entities disabled, using empty entity type dictionary")
                elif entity_type_subset:
                    # If a subset is specified in function call, it takes highest precedence
                    entity_types_to_use = get_entity_type_subset(entity_type_subset)
                    logger.info(f"Using function parameter entity subset: {entity_type_subset}")
                elif config.entity_type_subset:
                    # If subset is specified via command line, use that
                    entity_types_to_use = get_entity_type_subset(config.entity_type_subset)
                    logger.info(f"Using command-line entity subset: {config.entity_type_subset}")
                else:
                    # Otherwise use all registered entity types - get fresh reference here
                    entity_types_to_use = get_entity_types()
                    logger.info(f"Using all registered entity types: {list(entity_types_to_use.keys())}")
                
                logger.info(f"Final entity types being used: {list(entity_types_to_use.keys())}")

                await client.add_episode(
                    name=name,
                    episode_body=episode_body_str,
                    source=source_type,
                    source_description=source_description,
                    group_id=group_id_str,  # Using the string version of group_id
                    uuid=uuid,
                    reference_time=datetime.now(timezone.utc),
                    entity_types=entity_types_to_use,
                )
                logger.info(f"Episode '{name}' added successfully")

                logger.info(f"Building communities after episode '{name}'")
                await client.build_communities()

                logger.info(f"Episode '{name}' processed successfully")
            except Exception as e:
                error_msg = str(e)
                logger.error(
                    f"Error processing episode '{name}' for group_id {group_id_str}: {error_msg}"
                )

        # Initialize queue for this group_id if it doesn't exist
        if group_id_str not in episode_queues:
            episode_queues[group_id_str] = asyncio.Queue()

        # Add the episode processing function to the queue
        await episode_queues[group_id_str].put(process_episode)

        # Start a worker for this queue if one isn't already running
        if not queue_workers.get(group_id_str, False):
            asyncio.create_task(process_episode_queue(group_id_str))

        # Return immediately with a success message
        return {
            'message': f"Episode '{name}' queued for processing (position: {episode_queues[group_id_str].qsize()})"
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error queuing episode task: {error_msg}')
        return {'error': f'Error queuing episode task: {error_msg}'}


@mcp.tool()
async def search_nodes(
    query: str,
    group_ids: Optional[list[str]] = None,
    max_nodes: int = 10,
    center_node_uuid: Optional[str] = None,
    entity: str = '',  # cursor seems to break with None
) -> Union[NodeSearchResponse, ErrorResponse]:
    """Search the Graphiti knowledge graph for relevant node summaries.
    These contain a summary of all of a node's relationships with other nodes.

    Note: entity is a single entity type to filter results (permitted: "Preference", "Procedure").

    Args:
        query: The search query
        group_ids: Optional list of group IDs to filter results
        max_nodes: Maximum number of nodes to return (default: 10)
        center_node_uuid: Optional UUID of a node to center the search around
        entity: Optional single entity type to filter results (permitted: "Preference", "Procedure")
    """
    global graphiti_client

    if graphiti_client is None:
        return ErrorResponse(error='Graphiti client not initialized')

    try:
        # Use the provided group_ids or fall back to the default from config if none provided
        effective_group_ids = (
            group_ids if group_ids is not None else [config.group_id] if config.group_id else []
        )

        # Configure the search
        if center_node_uuid is not None:
            search_config = NODE_HYBRID_SEARCH_NODE_DISTANCE.model_copy(deep=True)
        else:
            search_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        search_config.limit = max_nodes

        filters = SearchFilters()
        if entity != '':
            filters.node_labels = [entity]

        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        # Perform the search using the _search method
        search_results = await client._search(
            query=query,
            config=search_config,
            group_ids=effective_group_ids,
            center_node_uuid=center_node_uuid,
            search_filter=filters,
        )

        if not search_results.nodes:
            return NodeSearchResponse(message='No relevant nodes found', nodes=[])

        # Format the node results
        formatted_nodes: list[NodeResult] = [
            {
                'uuid': node.uuid,
                'name': node.name,
                'summary': node.summary if hasattr(node, 'summary') else '',
                'labels': node.labels if hasattr(node, 'labels') else [],
                'group_id': node.group_id,
                'created_at': node.created_at.isoformat(),
                'attributes': node.attributes if hasattr(node, 'attributes') else {},
            }
            for node in search_results.nodes
        ]

        return NodeSearchResponse(message='Nodes retrieved successfully', nodes=formatted_nodes)
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error searching nodes: {error_msg}')
        return ErrorResponse(error=f'Error searching nodes: {error_msg}')


@mcp.tool()
async def search_facts(
    query: str,
    group_ids: Optional[list[str]] = None,
    max_facts: int = 10,
    center_node_uuid: Optional[str] = None,
) -> Union[FactSearchResponse, ErrorResponse]:
    """Search the Graphiti knowledge graph for relevant facts.

    Args:
        query: The search query
        group_ids: Optional list of group IDs to filter results
        max_facts: Maximum number of facts to return (default: 10)
        center_node_uuid: Optional UUID of a node to center the search around
    """
    global graphiti_client

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # Use the provided group_ids or fall back to the default from config if none provided
        effective_group_ids = (
            group_ids if group_ids is not None else [config.group_id] if config.group_id else []
        )

        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        relevant_edges = await client.search(
            group_ids=effective_group_ids,
            query=query,
            num_results=max_facts,
            center_node_uuid=center_node_uuid,
        )

        if not relevant_edges:
            return {'message': 'No relevant facts found', 'facts': []}

        facts = [format_fact_result(edge) for edge in relevant_edges]
        return {'message': 'Facts retrieved successfully', 'facts': facts}
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error searching facts: {error_msg}')
        return {'error': f'Error searching facts: {error_msg}'}


@mcp.tool()
async def delete_entity_edge(uuid: str) -> Union[SuccessResponse, ErrorResponse]:
    """Delete an entity edge from the Graphiti knowledge graph.

    Args:
        uuid: UUID of the entity edge to delete
    """
    global graphiti_client

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        # Get the entity edge by UUID
        entity_edge = await EntityEdge.get_by_uuid(client.driver, uuid)
        # Delete the edge using its delete method
        await entity_edge.delete(client.driver)
        return {'message': f'Entity edge with UUID {uuid} deleted successfully'}
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error deleting entity edge: {error_msg}')
        return {'error': f'Error deleting entity edge: {error_msg}'}


@mcp.tool()
async def delete_episode(uuid: str) -> Union[SuccessResponse, ErrorResponse]:
    """Delete an episode from the Graphiti knowledge graph.

    Args:
        uuid: UUID of the episode to delete
    """
    global graphiti_client

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        # Get the episodic node by UUID - EpisodicNode is already imported at the top
        episodic_node = await EpisodicNode.get_by_uuid(client.driver, uuid)
        # Delete the node using its delete method
        await episodic_node.delete(client.driver)
        return {'message': f'Episode with UUID {uuid} deleted successfully'}
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error deleting episode: {error_msg}')
        return {'error': f'Error deleting episode: {error_msg}'}


@mcp.tool()
async def get_entity_edge(uuid: str) -> Union[dict[str, Any], ErrorResponse]:
    """Get an entity edge from the Graphiti knowledge graph by its UUID.

    Args:
        uuid: UUID of the entity edge to retrieve
    """
    global graphiti_client

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        # Get the entity edge directly using the EntityEdge class method
        entity_edge = await EntityEdge.get_by_uuid(client.driver, uuid)

        # Use the format_fact_result function to serialize the edge
        # Return the Python dict directly - MCP will handle serialization
        return format_fact_result(entity_edge)
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error getting entity edge: {error_msg}')
        return {'error': f'Error getting entity edge: {error_msg}'}


@mcp.tool()
async def get_episodes(
    group_id: Optional[str] = None, last_n: int = 10
) -> Union[list[dict[str, Any]], EpisodeSearchResponse, ErrorResponse]:
    """Get the most recent episodes for a specific group.

    Args:
        group_id: ID of the group to retrieve episodes from. If not provided, uses the default group_id.
        last_n: Number of most recent episodes to retrieve (default: 10)
    """
    global graphiti_client

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # Use the provided group_id or fall back to the default from config
        effective_group_id = group_id if group_id is not None else config.group_id

        if not isinstance(effective_group_id, str):
            return {'error': 'Group ID must be a string'}

        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        episodes = await client.retrieve_episodes(
            group_ids=[effective_group_id], last_n=last_n, reference_time=datetime.now(timezone.utc)
        )

        if not episodes:
            return {'message': f'No episodes found for group {effective_group_id}', 'episodes': []}

        # Use Pydantic's model_dump method for EpisodicNode serialization
        formatted_episodes = [
            # Use mode='json' to handle datetime serialization
            episode.model_dump(mode='json')
            for episode in episodes
        ]

        # Return the Python list directly - MCP will handle serialization
        return formatted_episodes
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error getting episodes: {error_msg}')
        return {'error': f'Error getting episodes: {error_msg}'}


@mcp.tool()
async def clear_graph() -> Union[SuccessResponse, ErrorResponse]:
    """Clear all data from the Graphiti knowledge graph and rebuild indices."""
    global graphiti_client

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        # clear_data is already imported at the top
        await clear_data(client.driver)
        await client.build_indices_and_constraints()
        return {'message': 'Graph cleared successfully and indices rebuilt'}
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error clearing graph: {error_msg}')
        return {'error': f'Error clearing graph: {error_msg}'}


@mcp.resource('http://graphiti/status')
async def get_status() -> StatusResponse:
    """Get the status of the Graphiti MCP server and Neo4j connection."""
    global graphiti_client

    if graphiti_client is None:
        return {'status': 'error', 'message': 'Graphiti client not initialized'}

    try:
        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        # Test Neo4j connection
        await client.driver.verify_connectivity()
        return {'status': 'ok', 'message': 'Graphiti MCP server is running and connected to Neo4j'}
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error checking Neo4j connection: {error_msg}')
        return {
            'status': 'error',
            'message': f'Graphiti MCP server is running but Neo4j connection failed: {error_msg}',
        }


def create_llm_client(api_key: Optional[str] = None, model: Optional[str] = None) -> LLMClient:
    """Create an OpenAI LLM client.

    Args:
        api_key: API key for the OpenAI service
        model: Model name to use

    Returns:
        An instance of the OpenAI LLM client
    """
    # Create config with provided API key and model
    llm_config = LLMConfig(api_key=api_key)

    # Set model if provided
    if model:
        llm_config.model = model

    # Create and return the client
    return OpenAIClient(config=llm_config)


async def initialize_server() -> MCPConfig:
    """Initialize the Graphiti server with the specified LLM client."""
    global config

    parser = argparse.ArgumentParser(
        description='Run the Graphiti MCP server with optional LLM client'
    )
    parser.add_argument(
        '--group-id',
        help='Namespace for the graph. This is an arbitrary string used to organize related data. '
        'If not provided, a random UUID will be generated.',
    )
    parser.add_argument(
        '--transport',
        choices=['sse', 'stdio'],
        default='sse',
        help='Transport to use for communication with the client. (default: sse)',
    )
    # OpenAI is the only supported LLM client
    parser.add_argument('--model', help='Model name to use with the LLM client')
    parser.add_argument('--destroy-graph', action='store_true', help='Destroy all Graphiti graphs')
    parser.add_argument(
        '--use-custom-entities',
        action='store_true',
        help='Enable entity extraction using the predefined ENTITY_TYPES',
    )
    # Add argument for specifying entity types
    parser.add_argument(
        '--entity-types',
        nargs='+',
        help='Specify which entity types to use (e.g., --entity-types Requirement Preference). '
        'If not provided but --use-custom-entities is set, all registered entity types will be used.',
    )
    # Add argument for custom entity type directory
    parser.add_argument(
        '--entity-type-dir',
        help='Directory containing custom entity type modules to load'
    )
    # Add argument for log level
    parser.add_argument(
        '--log-level',
        choices=['debug', 'info', 'warn', 'error', 'fatal'],
        default=os.environ.get('GRAPHITI_LOG_LEVEL', 'info').lower(),  # Default to ENV or 'info'
        help='Set the logging level.'
    )

    args = parser.parse_args()

    # Reconfigure logging based on final argument
    configure_logging(args.log_level)
    logger.info(f"Final effective logging level: {logging.getLevelName(log_level)}")

    # Set the group_id from CLI argument or generate a random one
    if args.group_id:
        config.group_id = args.group_id
        logger.info(f'Using provided group_id: {config.group_id}')
    else:
        config.group_id = f'graph_{uuid.uuid4().hex[:8]}'
        logger.info(f'Generated random group_id: {config.group_id}')

    # Define the expected path for base entity types within the container
    container_base_entity_dir = "/app/entity_types/base"
    
    # Always load base entity types first
    if os.path.exists(container_base_entity_dir) and os.path.isdir(container_base_entity_dir):
        logger.info(f'Loading base entity types from: {container_base_entity_dir}')
        load_entity_types_from_directory(container_base_entity_dir)
    else:
        logger.warning(f"Base entity types directory not found at: {container_base_entity_dir}")
    
    # Load project-specific entity types if directory is specified and different from base
    if args.entity_type_dir:
        # Resolve paths to handle potential symlinks or relative paths inside container
        abs_project_dir = os.path.abspath(args.entity_type_dir)
        abs_base_dir = os.path.abspath(container_base_entity_dir)
        
        if abs_project_dir != abs_base_dir:
            if os.path.exists(abs_project_dir) and os.path.isdir(abs_project_dir):
                logger.info(f'Loading project-specific entity types from: {abs_project_dir}')
                load_entity_types_from_directory(abs_project_dir)
            else:
                logger.warning(f"Project entity types directory not found or not a directory: {abs_project_dir}")
        else:
            logger.info(f"Project entity directory '{args.entity_type_dir}' is the same as base, skipping redundant load.")

    # Set use_custom_entities flag if specified
    if args.use_custom_entities:
        config.use_custom_entities = True
        logger.info('Entity extraction enabled using predefined ENTITY_TYPES')
    else:
        logger.info('Entity extraction disabled (no custom entities will be used)')
        
    # Store the entity types to use if specified
    if args.entity_types:
        config.entity_type_subset = args.entity_types
        logger.info(f'Using entity types: {", ".join(args.entity_types)}')
    else:
        config.entity_type_subset = None
        if config.use_custom_entities:
            logger.info('Using all registered entity types')
        
    # Log all registered entity types after initialization
    logger.info(f"All registered entity types after initialization: {len(get_entity_types())}")
    for entity_name in get_entity_types().keys():
        logger.info(f"  - Available entity: {entity_name}")

    llm_client = None

    # Create OpenAI client if model is specified or if OPENAI_API_KEY is available
    if args.model or config.openai_api_key:
        # Override model from command line if specified

        config.model_name = args.model or DEFAULT_LLM_MODEL

        # Create the OpenAI client
        llm_client = create_llm_client(api_key=config.openai_api_key, model=config.model_name)

    # Initialize Graphiti with the specified LLM client
    await initialize_graphiti(llm_client, destroy_graph=args.destroy_graph)

    return MCPConfig(transport=args.transport)


async def run_mcp_server():
    """Run the MCP server in the current event loop."""
    # Initialize the server
    mcp_config = await initialize_server()

    # Run the server with stdio transport for MCP in the same event loop
    logger.info(f'Starting MCP server with transport: {mcp_config.transport}')
    if mcp_config.transport == 'stdio':
        await mcp.run_stdio_async()
    elif mcp_config.transport == 'sse':
        logger.info(
            f'Running MCP server with SSE transport on {mcp.settings.host}:{mcp.settings.port}'
        )
        await mcp.run_sse_async()


def main():
    """Main function to run the Graphiti MCP server."""
    try:
        # Run everything in a single event loop
        asyncio.run(run_mcp_server())
    except Exception as e:
        logger.error(f'Error initializing Graphiti MCP server: {str(e)}')
        raise


def load_entity_types_from_directory(directory_path: str) -> None:
    """Load all Python modules in the specified directory as entity types.
    
    This function dynamically imports all Python files in the specified directory,
    and automatically registers any Pydantic BaseModel classes that have docstrings.
    No explicit imports or registration calls are needed in the entity type files.
    
    Args:
        directory_path: Path to the directory containing entity type modules
    """
    logger.info(f"Attempting to load entities from directory: {directory_path}")
    directory = Path(directory_path)
    if not directory.exists() or not directory.is_dir():
        logger.warning(f"Entity types directory {directory_path} does not exist or is not a directory")
        return
        
    # Find all Python files in the directory
    python_files = list(directory.glob('*.py'))
    logger.info(f"Found {len(python_files)} Python files in {directory_path}")
    
    for file_path in python_files:
        if file_path.name.startswith('__'):
            continue  # Skip __init__.py and similar files
            
        module_name = file_path.stem
        full_module_path = str(file_path.absolute())
        
        try:
            # Dynamically import the module
            spec = importlib.util.spec_from_file_location(module_name, full_module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Track how many entities were registered from this file
                entities_registered = 0
                
                # Look for BaseModel classes in the module
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    
                    # Check if it's a class and a subclass of BaseModel
                    if (isinstance(attribute, type) and 
                        issubclass(attribute, BaseModel) and 
                        attribute != BaseModel and
                        attribute.__doc__):  # Only consider classes with docstrings
                        
                        # Register the entity type
                        register_entity_type(attribute_name, attribute)
                        entities_registered += 1
                        logger.info(f"Auto-registered entity type: {attribute_name}")
                
                logger.info(f"Successfully loaded entity type module: {module_name} (registered {entities_registered} entities)")
        except Exception as e:
            logger.error(f"Error loading entity type module {module_name}: {str(e)}")
    
    # Log total registered entity types after loading this directory
    logger.info(f"Total registered entity types after loading {directory_path}: {len(get_entity_types())}")
    for entity_name in get_entity_types().keys():
        logger.info(f"  - Registered entity: {entity_name}")


if __name__ == '__main__':
    main()
```

## File: mcp_config_sse_example.json
```json
{
    "mcpServers": {
        "graphiti": {
            "transport": "sse",
            "url": "http://localhost:8000/sse"
        }
    }
}
```

## File: mcp_config_stdio_example.json
```json
{
    "mcpServers": {
        "graphiti": {
            "transport": "stdio",
            "command": "uv",
            "args": [
                "run",
                "/ABSOLUTE/PATH/TO/graphiti_mcp_server.py",
                "--transport",
                "stdio"
            ],
            "env": {
                "NEO4J_URI": "bolt://localhost:7687",
                "NEO4J_USER": "neo4j",
                "NEO4J_PASSWORD": "demodemo",
                "OPENAI_API_KEY": "${OPENAI_API_KEY}",
                "MODEL_NAME": "gpt-4o"
            }
        }
    }
}
```

## File: mcp-projects.yaml
```yaml
# !! WARNING: This file is managed by the 'graphiti init' command. !!
# !! Avoid manual edits unless absolutely necessary.                 !!
#
# Maps project names to their configuration details.
# Paths should be absolute for reliability.
projects:
# Example Entry (will be added by 'graphiti init'):
# alpha:
#   config_file: /abs/path/to/project-alpha/mcp-config.yaml
#   root_dir: /abs/path/to/project-alpha
#   enabled: true 
  filesystem:
    root_dir: /Users/mateicanavra/Documents/.nosync/DEV/mcp-servers/mcp-filesystem
    config_file: 
      /Users/mateicanavra/Documents/.nosync/DEV/mcp-servers/mcp-filesystem/ai/graph/mcp-config.yaml
    enabled: true
  magic-candidates:
    root_dir: /Users/mateicanavra/Documents/.nosync/DEV/magic-apply-candidates
    config_file: 
      /Users/mateicanavra/Documents/.nosync/DEV/magic-apply-candidates/ai/graph/mcp-config.yaml
    enabled: true
```

## File: pyproject.toml
```toml
[project]
name = "mcp-server"
version = "0.1.0"
description = "Graphiti MCP Server"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.5.0",
    "openai>=1.68.2",
    # For local development with local graphiti-core wheel:
    # "graphiti-core @ file:///dist/graphiti_core-0.8.5-py3-none-any.whl",
    # For production/normal use (uncomment this and comment out the above):
    "graphiti-core>=0.8.5",
    "ruamel.yaml>=0.17.21",
    "typer[all]>=0.9.0",
    "python-dotenv>=1.0.0",
]

[project.scripts]
graphiti = "graphiti_cli.main:app"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

# Explicitly specify packages to include
[tool.setuptools.packages.find]
where = ["."]  # Look in the current directory (mcp_server)
include = ["graphiti_cli"]  # Only include the CLI package

# Add py_modules to include individual Python files (like constants.py)
[tool.setuptools]
py-modules = ["constants"]
```

## File: repomix.config.json
```json
{
  "output": {
    "filePath": "graphiti-mcp-repo.md",
    "style": "markdown",
    "parsableStyle": false,
    "fileSummary": true,
    "directoryStructure": true,
    "removeComments": false,
    "removeEmptyLines": false,
    "compress": false,
    "topFilesLength": 5,
    "showLineNumbers": false,
    "copyToClipboard": false,
    "git": {
      "sortByChanges": true,
      "sortByChangesMaxCommits": 100
    }
  },
  "include": [],
  "ignore": {
    "useGitignore": true,
    "useDefaultPatterns": true,
    "customPatterns": [
      ".venv/**",
      "uv.lock",
      "dist/**",
      ".ai/**",
      "llm_cache/**",
      "scripts/README.md",
      "README.md",
      "docs/**",
      "*.egg-info/**",
      "__pycache__/**",
      "*.pyc",
      "*.pyo",
      ".python-version",
      ".env",
      "*.log"
    ]
  },
  "security": {
    "enableSecurityCheck": true
  },
  "tokenCount": {
    "encoding": "o200k_base"
  }
}
```
