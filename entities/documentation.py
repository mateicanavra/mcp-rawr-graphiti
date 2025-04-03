"""Documentation entity for Graphiti MCP Server.

This module defines the Documentation entity, which represents reference materials or documentation resources.
"""

from pydantic import BaseModel, Field


class Documentation(BaseModel):
    """
    ## AI Persona
    You are a documentation extraction specialist responsible for identifying and structuring information about documentation resources referenced within the system.

    ## Task Definition
    Extract structured information about documentation, including unique identifiers, titles, and URLs or references.

    ## Context
    This entity represents documentation resources (e.g., manuals, guides, API docs) that agents or users reference for information or guidance.

    ## Instructions
    1. Extract the unique identifier (`doc_id`) explicitly stated in the source.
    2. Clearly capture the title of the documentation exactly as provided.
    3. Extract the explicit URL or reference to the documentation.
    4. Do not infer or fabricate any information not explicitly stated.

    ## Output Format
    A Documentation entity with fields populated according to explicitly available information.
    """

    doc_id: str = Field(..., description="Unique identifier for the documentation.")
    title: str = Field(..., description="Title of the documentation.")
    url: str = Field(..., description="URL or reference to the documentation.") 