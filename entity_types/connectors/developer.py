"""Developer entity type for Graphiti MCP Server.

This module defines the Developer entity type, which represents developer-specific working style and context.
"""

from pydantic import BaseModel, Field


class Developer(BaseModel):
    """Developer-specific working style and context.

    Instructions for identifying and extracting developer context:
    1. Explicit statements about developer working style or patterns.
    """

    name: str = Field(..., description="Developer's name.")
    working_style: str = Field(..., description="Developer's work patterns and habits.") 