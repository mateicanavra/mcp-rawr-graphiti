"""InteractionModel entity for Graphiti MCP Server.

This module defines the InteractionModel entity, which describes structured interaction patterns.
"""

from pydantic import BaseModel, Field, ConfigDict


class InteractionModel(BaseModel):
    """Describes structured interaction patterns.

    Instructions for identifying and extracting interaction models:
    1. Look for explicit guidelines on interaction sequences.
    2. Include steps or patterns explicitly mentioned.
    """

    model_config = ConfigDict(extra='forbid')

    name: str = Field(..., description="Name of interaction pattern or model.")
    description: str = Field(..., description="How interactions typically occur.") 