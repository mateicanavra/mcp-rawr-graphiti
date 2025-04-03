"""Procedure entity for Graphiti MCP Server.

This module defines the Procedure entity, which represents actionable steps or procedures to be executed.
"""

from pydantic import BaseModel, Field, ConfigDict


class Procedure(BaseModel):
    """Defines actionable steps or procedures to be executed.

    Instructions for identifying and extracting procedures:
    1. Look for clearly defined steps or instructions.
    2. Ensure each step logically follows from the previous one.
    3. Capture explicit descriptions of each step.
    """

    model_config = ConfigDict(extra='forbid')

    name: str = Field(..., description="Name of the procedure.")
    description: str = Field(..., description="Detailed steps or actions to perform.") 