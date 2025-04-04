"""Tool entity for Graphiti MCP Server.

This module defines the Tool entity, which represents tools used by agents or developers.
"""

from typing import List, Optional  # Added List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Tool(BaseModel):
    """
    ## AI Persona
    You are a resource extraction specialist responsible for identifying and structuring information about tools used within the system.

    ## Task Definition
    Extract structured information about tools, including unique identifiers (id), human-readable names, display labels, purposes, and the specific actions they provide.

    ## Context
    This entity represents reusable tools or utilities (like MCP Servers, libraries, APIs) that agents or users interact with or rely upon to perform tasks. Tools are non-agentic providers of capabilities, enabling specific Actions.

    ## Instructions
    1. Extract the unique identifier (`id`) explicitly stated (e.g., MCP server name, library name, command name). This should be a machine-friendly key.
    2. Extract the human-readable `name` of the tool (e.g., "Filesystem MCP Server", "GitHub Search").
    3. Define a short `label` (2-3 words max) suitable for display (e.g., "FS Server", "GH Search").
    4. Extract the explicit `purpose` or overall functionality of the tool.
    5. Identify the specific `Action`(s) this tool makes available or invokes. List their IDs (corresponding to the `id` field of Action entities) in `provided_actions`.
    6. Do not infer or fabricate any information not explicitly stated.

    ## Output Format
    A Tool entity with fields populated according to explicitly available information.
    """

    model_config = ConfigDict(extra='forbid')

    id: str = Field(..., description="Unique, machine-friendly identifier for the tool (e.g., 'filesystem_mcp', 'github_search'). Serves as the primary key.")
    label: str = Field(..., description="A very short (2-3 words max) display label for the tool (e.g., 'FS Server', 'GH Search').")
    name: str = Field(..., description="Human-readable name for the tool (e.g., 'Filesystem MCP Server', 'GitHub Repository Search').")
    purpose: str = Field(..., description="Overall purpose or high-level functionality of the tool.")
    provided_actions: Optional[List[str]] = Field(
        default=None,
        description="List of IDs of the specific Action entities this tool provides or enables."
    )