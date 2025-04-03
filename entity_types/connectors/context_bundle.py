"""ContextBundle entity type for Graphiti MCP Server.

This module defines the ContextBundle entity type, which aggregates contextual information or episodes.
"""

from pydantic import BaseModel, Field


class ContextBundle(BaseModel):
    """Aggregates contextual information or episodes.

    Instructions for identifying and extracting context bundles:
    1. Explicit bundles of historical context or related information.
    """

    name: str = Field(..., description="Context bundle name.")
    description: str = Field(..., description="Overview of contextual information.") 