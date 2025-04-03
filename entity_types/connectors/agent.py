"""Agent entity type for Graphiti MCP Server.

This module defines the Agent entity type, which represents an AI agent persona or role.
"""

from pydantic import BaseModel, Field


class Agent(BaseModel):
    """Represents an AI agent persona or role.

    Instructions for identifying and extracting agents:
    1. Explicitly named roles or personas.
    2. Clearly stated skills, expertise, or responsibilities.
    """

    name: str = Field(..., description="Agent's name.")
    description: str = Field(..., description="Summary of agent's role and skills.") 