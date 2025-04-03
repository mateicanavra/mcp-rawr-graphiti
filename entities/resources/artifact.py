"""Artifact entity type for Graphiti MCP Server.

This module defines the Artifact entity type, which represents outputs or artifacts from work activities.
"""

from pydantic import BaseModel, Field


class Artifact(BaseModel):
    """
    ## AI Persona
    You are an artifact extraction specialist responsible for identifying and structuring information about artifacts referenced or utilized within the system.

    ## Task Definition
    Extract structured information about artifacts, including unique identifiers, names, types, and locations or references.

    ## Context
    This entity represents tangible or intangible artifacts (e.g., files, datasets, models) that agents or users interact with or reference during tasks or projects.

    ## Instructions
    1. Extract the unique identifier (`artifact_id`) explicitly stated in the source.
    2. Clearly capture the name of the artifact exactly as provided.
    3. Extract the explicit type or category of the artifact.
    4. Identify and extract the explicit location or reference to the artifact.
    5. Do not infer or fabricate any information not explicitly stated.

    ## Output Format
    An Artifact entity with fields populated according to explicitly available information.
    """

    name: str = Field(..., description="Name of the artifact.")
    type: str = Field(..., description="Type or category of the artifact.")
    location: str = Field(..., description="Location or reference to the artifact.") 