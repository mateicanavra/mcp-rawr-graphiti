"""Tool entity type for Graphiti MCP Server.

This module defines the Tool entity type, which represents tools used by agents or developers.
"""

from pydantic import BaseModel, Field


class Tool(BaseModel):
    """Tools used by agents or developers.

    Instructions for identifying and extracting tools:
    1. Explicit mentions of specific tools used.
    2. Clearly described functionality or usage contexts.
    """

    name: str = Field(..., description="Tool name.")
    description: str = Field(..., description="Tool usage context and purpose.") 