"""Requirement entity for Graphiti MCP Server.

This module defines the Requirement entity, which represents constraints, conditions, or requirements that must be satisfied.
"""

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    """Defines constraints, conditions, or requirements that must be satisfied.

    Instructions for identifying and extracting requirements:
    1. Identify clearly stated constraints or prerequisites.
    2. Include rationale or importance if explicitly mentioned.
    """

    name: str = Field(..., description="Requirement identifier.")
    description: str = Field(..., description="Description of the requirement or constraint.") 