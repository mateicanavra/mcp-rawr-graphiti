"""Definition of the IntegrationPattern entity type for Graphiti."""

from pydantic import BaseModel, Field
from typing import List, Optional


class IntegrationPatternEntity(BaseModel):
    """
    **AI Persona:** You are an expert in systems integration and API design.
    
    **Task:** Identify and extract information about integration patterns used in the Graphiti framework.
    IntegrationPatternEntity represents an approach or technique for connecting Graphiti with external systems, databases, or services.

    **Context:** The text will contain descriptions of how Graphiti interfaces with external components, APIs, or data sources.

    **Extraction Instructions:**
    Your goal is to accurately populate the fields about integration patterns based *only* on information explicitly or implicitly stated in the text.

    1.  **Identify Integration Pattern Mentions:** Look for descriptions of how Graphiti connects to external systems or services.
    2.  **Extract Name:** Identify the specific integration pattern name (e.g., "Plugin Architecture", "API Abstraction Layer").
    3.  **Extract Description:** Synthesize a concise description of how the integration pattern works and what integration need it addresses.
    4.  **Extract Interfaces:** Identify the specific interfaces, APIs, or protocols used by this integration pattern.
    5.  **Extract External Systems:** Note which external systems, services, or databases are integrated using this pattern.
    6.  **Extract Implementation Details:** Capture how the integration is technically implemented in the codebase.
    7.  **Extract Benefits:** Identify the benefits or advantages this integration pattern provides.
    8.  **Handle Ambiguity:** If information for a field is missing or unclear in the text, leave the optional fields empty.

    **Output Format:** Respond with the extracted data structured according to this Pydantic model.
    """

    name: str = Field(
        ...,
        description='The specific name of the integration pattern (e.g., "Plugin Architecture", "API Abstraction Layer").',
    )
    description: str = Field(
        ...,
        description='A concise description of how the integration pattern works and what integration need it addresses.',
    )
    interfaces: Optional[List[str]] = Field(
        None,
        description='The specific interfaces, APIs, or protocols used by this integration pattern.',
    )
    external_systems: Optional[List[str]] = Field(
        None,
        description='External systems, services, or databases that are integrated using this pattern.',
    )
    implementation_details: Optional[str] = Field(
        None,
        description='How the integration is technically implemented in the codebase.',
    )
    benefits: Optional[List[str]] = Field(
        None,
        description='The benefits or advantages this integration pattern provides.',
    ) 