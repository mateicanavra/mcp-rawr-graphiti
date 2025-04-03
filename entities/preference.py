"""Preference entity for Graphiti MCP Server.

This module defines the Preference entity, which represents a user's expressed likes, dislikes, or preferences.
"""

from pydantic import BaseModel, Field


class Preference(BaseModel):
    """
    ## AI Persona
    You are a preference extraction specialist responsible for identifying and structuring user or agent preferences from provided data.

    ## Task Definition
    Extract structured information about preferences, including unique identifiers, descriptions, and their corresponding values or settings.

    ## Context
    This entity captures explicit preferences set by users or agents, influencing system behavior or interaction patterns.

    ## Instructions
    1. Extract the unique identifier (`preference_id`) explicitly stated in the source.
    2. Clearly capture the description of the preference.
    3. Extract the explicit value or setting associated with the preference.
    4. Do not infer or fabricate any information not explicitly stated.

    ## Output Format
    A Preference entity with fields populated according to explicitly available information.
    """

    description: str = Field(..., description="Description of the preference.")
    value: str = Field(..., description="Value or setting of the preference.")
    category: str = Field(..., description="The category of the preference.")
    description: str = Field(..., description="Brief description based only on provided context.") 