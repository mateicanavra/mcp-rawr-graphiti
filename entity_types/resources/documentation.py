"""Documentation entity type for Graphiti MCP Server.

This module defines the Documentation entity type, which represents reference materials or documentation resources.
"""

from pydantic import BaseModel, Field


class Documentation(BaseModel):
    """Reference materials or documentation resources.

    Instructions for identifying and extracting documentation:
    1. Explicit titles or references to documentation.
    """

    title: str = Field(..., description="Title of documentation.")
    link: str = Field(..., description="Link to documentation.") 