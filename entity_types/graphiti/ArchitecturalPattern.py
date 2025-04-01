"""Definition of the ArchitecturalPattern entity type for Graphiti."""

from pydantic import BaseModel, Field
from typing import List, Optional


class ArchitecturalPatternEntity(BaseModel):
    """
    **AI Persona:** You are an expert software architecture analyst.
    
    **Task:** Identify and extract information about architectural patterns used in the Graphiti framework.
    ArchitecturalPatternEntity represents a high-level design pattern, principle, or architectural approach used in the system.

    **Context:** The text will contain descriptions of system architecture, code organization, or design principles.

    **Extraction Instructions:**
    Your goal is to accurately populate the fields about architectural patterns based *only* on information explicitly or implicitly stated in the text.

    1.  **Identify Pattern Mentions:** Look for explicit references to design patterns, architectural styles, or structural organization approaches.
    2.  **Extract Name:** Identify the specific pattern name (e.g., "Dependency Inversion", "Plugin Architecture", "Modular Design").
    3.  **Extract Description:** Synthesize a concise description explaining what the pattern is and how it's used in Graphiti.
    4.  **Extract Benefits:** Note any explicit or implicit benefits mentioned about why this pattern was chosen.
    5.  **Extract Implementation Details:** Capture how the pattern is implemented in the codebase, including key classes or components.
    6.  **Extract Related Components:** Identify which system components or modules implement or are affected by this pattern.
    7.  **Handle Ambiguity:** If information for a field is missing or unclear in the text, leave the optional fields empty.

    **Output Format:** Respond with the extracted data structured according to this Pydantic model.
    """

    name: str = Field(
        ...,
        description='The specific name of the architectural pattern (e.g., "Dependency Inversion", "Plugin Architecture").',
    )
    description: str = Field(
        ...,
        description='A concise description of what the pattern is and how it functions in the system architecture.',
    )
    benefits: Optional[List[str]] = Field(
        None,
        description='The advantages or benefits this pattern provides to the system (e.g., "extensibility", "maintainability").',
    )
    implementation_details: Optional[str] = Field(
        None,
        description='How the pattern is implemented in the codebase, including key classes, interfaces, or components.',
    )
    related_components: Optional[List[str]] = Field(
        None,
        description='System components or modules that implement or are directly affected by this pattern.',
    ) 