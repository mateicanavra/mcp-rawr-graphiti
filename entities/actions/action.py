"""Action entity type for Graphiti Meta KG."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Action(BaseModel):
    """
    ## AI Persona
    You are a process and capability analyst specializing in identifying and defining discrete, performable actions from tool descriptions and procedural documentation.

    ## Task Definition
    Extract distinct performable actions and detail their properties like parameters, preconditions, potential side effects, and boundaries.

    ## Context
    This entity represents a single, discrete, performable action, like 'read_file', 'create_issue', 'validate_input', or 'search_nodes'. Actions are the fundamental units of operation invoked by agents or tools, or sequenced in procedures. Understanding actions helps define operational semantics, constraints, and procedural logic. This entity defines *what* the action is; how it's provided (e.g., by a Tool) or used (e.g., in a Procedure) is defined by graph relationships.

    ## Instructions
    1.  Identify distinct performable actions mentioned (e.g., specific tool functions/commands, verbs describing process steps).
    2.  Determine the unique, machine-friendly `id` for the action (e.g., 'read_file', 'search_nodes', 'validate_user_credentials'). Use a consistent naming convention (e.g., snake_case).
    3.  Define a short `label` (2-3 words max) suitable for display (e.g., "Read File", "Search Nodes", "Validate Creds").
    4.  Provide a clear, human-readable `name` for the action (e.g., 'Read File Contents', 'Search Knowledge Graph Nodes', 'Validate User Credentials').
    5.  Write a detailed `description` of what the action does and its intended outcome.
    6.  If the action takes parameters, describe the expected input structure in `parameter_schema`. This could be a JSON schema (as a dict or string) or a textual description.
    7.  List any `preconditions` necessary for the action to be performed (e.g., 'User must be authenticated', 'Input file must exist').
    8.  List any potential `side_effects` or warnings associated with the action (e.g., 'May overwrite existing file', 'Can consume significant API quota', 'Requires elevated privileges').
    9.  Define the `boundary` conditions for the action's applicability (e.g., 'Applies only to text files', 'Relevant only within the project management domain', 'Requires specific API version'). This helps prevent semantic leakage.
    10. Create a separate Action entity for each distinct action identified.
    11. If information for optional fields (`parameter_schema`, `preconditions`, `side_effects`, `boundary`) is not present, leave them as None.

    ## Output Format
    An Action entity with `id`, `label`, `name`, `description`, and other available attributes populated based on the information identified.
    """

    id: str = Field(
        ...,
        description="Unique, machine-friendly identifier for the action (e.g., 'read_file', 'search_nodes'). Serves as the primary key."
    )

    label: str = Field(
        ...,
        description="A very short (2-3 words max) display label for the action (e.g., 'Read File', 'Search Nodes')."
    )

    name: str = Field(
        ...,
        description="Human-readable name for the action (e.g., 'Read File Contents', 'Search Knowledge Graph Nodes')."
    )

    description: str = Field(
        ...,
        description="A clear, human-readable explanation of what the action does, its purpose, and expected outcome."
    )

    parameter_schema: Optional[Dict[str, Any] | str] = Field(
        default=None,
        description="Describes the input parameters required by the action. Can be a JSON schema object/string or a textual description."
    )

    preconditions: Optional[List[str]] = Field(
        default=None,
        description="A list of conditions that must be met before the action can be successfully executed."
    )

    side_effects: Optional[List[str]] = Field(
        default=None,
        description="A list of potential side effects, risks, or warnings associated with executing the action."
    )

    boundary: Optional[List[str]] = Field(
        default=None,
        description="A list of boundary conditions defining the scope or context where the action is applicable/valid."
    )

# Auto-registration assumed