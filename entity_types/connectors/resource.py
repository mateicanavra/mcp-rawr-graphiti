"""Resource entity type for Graphiti MCP Server.

This module defines the Resource entity type, which represents assets or resources utilized by agents or projects.
"""

from pydantic import BaseModel, Field


class Resource(BaseModel):
    """Assets or resources utilized by agents or projects.

    Instructions for identifying and extracting resources:
    1. Specific tools, datasets, or other assets mentioned explicitly.
    """

    name: str = Field(..., description="Resource name.")
    description: str = Field(..., description="Description of the resource.") 