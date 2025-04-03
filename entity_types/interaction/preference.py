"""Preference entity type for Graphiti MCP Server.

This module defines the Preference entity type, which represents a user's expressed likes, dislikes, or preferences.
"""

from pydantic import BaseModel, Field


class Preference(BaseModel):
    """A user's expressed likes, dislikes, or preferences.

    Instructions for identifying and extracting preferences:
    1. Explicit statements of preference.
    2. Comparative statements ("I prefer X over Y").
    3. Clearly categorize by domain (e.g., food, music).
    """

    category: str = Field(..., description="The category of the preference.")
    description: str = Field(..., description="Brief description based only on provided context.") 