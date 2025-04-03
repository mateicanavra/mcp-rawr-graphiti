"""Artifact entity type for Graphiti MCP Server.

This module defines the Artifact entity type, which represents outputs or artifacts from work activities.
"""

from pydantic import BaseModel, Field


class Artifact(BaseModel):
    """Outputs or artifacts from work activities.

    Instructions for identifying and extracting artifacts:
    1. Explicit mentions of created outputs or artifacts.
    2. Include type and location clearly mentioned.
    """

    name: str = Field(..., description="Artifact name.")
    type: str = Field(..., description="Artifact type.")
    location: str = Field(..., description="Artifact location.") 