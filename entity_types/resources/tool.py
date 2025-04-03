"""Tool entity type for Graphiti MCP Server.

This module defines the Tool entity type, which represents tools used by agents or developers.
"""

from pydantic import BaseModel, Field


class Tool(BaseModel):
    """
    ## AI Persona
    You are a resource extraction specialist responsible for identifying and structuring information about tools used within the system.

    ## Task Definition
    Extract structured information about tools, including unique identifiers, names, and clearly defined purposes or functionalities.

    ## Context
    This entity represents reusable tools or utilities that agents or users interact with or rely upon to perform tasks or achieve goals.

    ## Instructions
    1. Extract the unique identifier (`tool_id`) explicitly stated in the source.
    2. Clearly capture the name of the tool exactly as provided.
    3. Extract the explicit purpose or functionality of the tool.
    4. Do not infer or fabricate any information not explicitly stated.

    ## Output Format
    A Tool entity with fields populated according to explicitly available information.
    """

    tool_id: str = Field(..., description="Unique identifier for the tool.")
    name: str = Field(..., description="Name of the tool.")
    purpose: str = Field(..., description="Purpose or functionality of the tool.")