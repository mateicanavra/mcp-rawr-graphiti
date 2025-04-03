"""Feedback entity for Graphiti MCP Server.

This module defines the Feedback entity, which represents user feedback on actions or recommendations.
"""

from pydantic import BaseModel, Field, ConfigDict


class Feedback(BaseModel):
    """
    ## AI Persona
    You are a feedback extraction specialist responsible for identifying and structuring feedback provided by users, agents, or external systems.

    ## Task Definition
    Extract structured information about feedback, including unique identifiers, content, and the source or origin of the feedback.

    ## Context
    This entity captures explicit feedback provided to the system, used for iterative improvement, monitoring, and interaction refinement.

    ## Instructions
    1. Extract the unique identifier (`feedback_id`) explicitly stated in the source.
    2. Clearly capture the content of the feedback exactly as provided.
    3. Identify and extract the explicit source or origin of the feedback.
    4. Do not infer or fabricate any information not explicitly stated.

    ## Output Format
    A Feedback entity with fields populated according to explicitly available information.
    """

    model_config = ConfigDict(extra='forbid')

    content: str = Field(..., description="Content of the feedback provided.")
    source: str = Field(..., description="Source or origin of the feedback.")