"""Agent entity for Graphiti MCP Server.

This module defines the Agent entity, which represents an AI agent persona or role.
"""

from pydantic import BaseModel, Field, ConfigDict
from ..base.metadata import BaseMetadata # Import the new base metadata model


class Agent(BaseModel):
    """Represents an AI agent persona or role.

    Instructions for identifying and extracting agents:
    1. Explicitly named roles or personas.
    2. Clearly stated skills, expertise, or responsibilities.
    """

    model_config = ConfigDict(extra='forbid')

    id: str = Field(..., description="Unique identifier for the agent.")
    name: str = Field(..., description="Human-readable name of the agent.")
    role: str = Field(..., description="Role or function of the agent within the system.")
    metadata: BaseMetadata = Field(default_factory=BaseMetadata, description="Optional structured metadata for extensibility.")
    tools: list[str] = Field(default_factory=list, description="List of tools or capabilities the agent has.")
    capabilities: list[str] = Field(default_factory=list, description="List of capabilities or functions the agent can perform.")
    limitations: list[str] = Field(default_factory=list, description="List of limitations or constraints the agent has.")
    preferences: list[str] = Field(default_factory=list, description="List of preferences or preferences the agent has.")
    mandates: list[str] = Field(default_factory=list, description="List of mandates or goals the agent has.")
