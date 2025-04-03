"""Resource entity for Graphiti MCP Server.

This module defines the Resource entity, which represents assets or resources utilized by agents or projects.
"""

from pydantic import BaseModel, Field


class Resource(BaseModel):
    """Assets or resources utilized by agents or projects.

    Instructions for identifying and extracting resources:
    1. Specific tools, datasets, or other assets mentioned explicitly.
    """

    id: str = Field(..., description="Resource ID (unique readable identifier).")
    name: str = Field(..., description="Resource name.")
    description: str = Field(..., description="Description of the resource.") 
    type: str = Field(..., description="Type of the resource (reference, guide, article, etc.)")
    location: str = Field(..., description="Location of the resource (URL, file path, etc.)")
    author: str = Field(..., description="Author of the resource.")
    related_resources: list[str] = Field(default_factory=list, description="List of related resources")
    