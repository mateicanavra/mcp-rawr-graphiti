"""Goal entity type for Graphiti MCP Server.

This module defines the Goal entity type, which represents clearly stated objectives or goals.
"""

from pydantic import BaseModel, Field


class Goal(BaseModel):
    """Clearly stated objectives or goals.

    Instructions for identifying and extracting goals:
    1. Explicit statements of objectives or desired outcomes.
    2. Success indicators or measurable outcomes explicitly mentioned.
    """

    statement: str = Field(..., description="Clear statement of goal or objective.")
    success_indicators: str = Field(..., description="Indicators of successful achievement.") 