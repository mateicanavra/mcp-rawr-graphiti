"""Goal entity for Graphiti MCP Server.

This module defines the Goal entity, which represents clearly stated objectives or goals.
"""

from pydantic import BaseModel, Field


class Goal(BaseModel):
    """Clearly stated objectives or goals.

    Instructions for identifying and extracting goals:
    1. Explicit statements of objectives or desired outcomes.
    2. Success indicators or measurable outcomes explicitly mentioned.
    3. Clearly track status, definition, and success criteria changes over time.
    """

    goal_id: str = Field(..., description="Unique identifier for the goal.")
    description: str = Field(..., description="Detailed description of the goal.")
    status: str = Field(..., description="Current status of the goal.")
    statement: str = Field(..., description="Clear statement of goal or objective.")
    success_indicators: str = Field(..., description="Indicators of successful achievement.") 
    start_date: str = Field(..., description="Start date of the goal.")
    end_date: str = Field(..., description="End date of the goal.")
    desired_outcome: str = Field(..., description="Desired outcome of the goal.")
    resources: list[str] = Field(default_factory=list, description="List of resources associated with the goal.")
    