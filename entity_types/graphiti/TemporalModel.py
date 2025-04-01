"""Definition of the TemporalModel entity type for Graphiti."""

from pydantic import BaseModel, Field
from typing import List, Optional


class TemporalModelEntity(BaseModel):
    """
    **AI Persona:** You are an expert in temporal data modeling and time-aware databases.
    
    **Task:** Identify and extract information about temporal data models used in the Graphiti framework.
    TemporalModelEntity represents an approach to modeling data that incorporates time dimensions.

    **Context:** The text will contain descriptions of how time is represented, tracked, and queried in the system.

    **Extraction Instructions:**
    Your goal is to accurately populate the fields about temporal data models based *only* on information explicitly or implicitly stated in the text.

    1.  **Identify Temporal Model Mentions:** Look for descriptions of how time is represented in data structures.
    2.  **Extract Name:** Identify the specific temporal model approach (e.g., "Bi-temporal Model", "Valid-time Tracking").
    3.  **Extract Description:** Synthesize a concise description of how the temporal model works and what problem it solves.
    4.  **Extract Time Dimensions:** Identify which dimensions of time are captured (e.g., system time, valid time, transaction time).
    5.  **Extract Query Capabilities:** Note any information about how temporal data can be queried or retrieved.
    6.  **Extract Implementation:** Capture details about how the temporal model is implemented in the database.
    7.  **Extract Use Cases:** Identify specific use cases or scenarios where this temporal model provides value.
    8.  **Handle Ambiguity:** If information for a field is missing or unclear in the text, leave the optional fields empty.

    **Output Format:** Respond with the extracted data structured according to this Pydantic model.
    """

    name: str = Field(
        ...,
        description='The specific name or type of the temporal model (e.g., "Bi-temporal Model", "Valid-time Tracking").',
    )
    description: str = Field(
        ...,
        description='A concise description of how the temporal model works and what problem it solves.',
    )
    time_dimensions: Optional[List[str]] = Field(
        None,
        description='The dimensions of time that are captured (e.g., "system time", "valid time", "transaction time").',
    )
    query_capabilities: Optional[str] = Field(
        None,
        description='How temporal data can be queried or retrieved, including any special query features.',
    )
    implementation: Optional[str] = Field(
        None,
        description='How the temporal model is implemented in the database or data structures.',
    )
    use_cases: Optional[List[str]] = Field(
        None,
        description='Specific use cases or scenarios where this temporal model provides value.',
    ) 