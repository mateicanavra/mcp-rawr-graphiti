"""Project entity type for Graphiti MCP Server.

This module defines the Project entity type, which represents a project or initiative.
"""

from pydantic import BaseModel, Field


class Project(BaseModel):
    """Represents a project or initiative.

    Instructions for identifying and extracting projects:
    1. Named initiatives with clear scope and objectives.
    """

    name: str = Field(..., description="Project name.")
    description: str = Field(..., description="Project scope and objectives.") 