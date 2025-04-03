"""Feedback entity type for Graphiti MCP Server.

This module defines the Feedback entity type, which represents user feedback on actions or recommendations.
"""

from pydantic import BaseModel, Field


class Feedback(BaseModel):
    """User feedback on actions or recommendations.

    Instructions for identifying and extracting feedback:
    1. Explicit responses or evaluations provided by users.
    2. Include context or specific details from the feedback.
    """

    context: str = Field(..., description="Context or action the feedback relates to.")
    response: str = Field(..., description="Detail of user's feedback.") 