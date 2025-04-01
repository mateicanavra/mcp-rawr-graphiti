"""Definition of the DataPipeline entity type for Graphiti."""

from pydantic import BaseModel, Field
from typing import List, Optional


class DataPipelineEntity(BaseModel):
    """
    **AI Persona:** You are an expert data engineer and systems analyst.
    
    **Task:** Identify and extract information about data processing pipelines in the Graphiti framework.
    DataPipelineEntity represents a workflow or sequence of operations that transform, process, or move data within the system.

    **Context:** The text will contain descriptions of data flows, ETL processes, or information processing sequences.

    **Extraction Instructions:**
    Your goal is to accurately populate the fields about data pipelines based *only* on information explicitly or implicitly stated in the text.

    1.  **Identify Pipeline Mentions:** Look for descriptions of sequential data processing, transformations, or workflows.
    2.  **Extract Name:** Identify the specific pipeline name or purpose (e.g., "Entity Extraction Pipeline", "Knowledge Graph Update Pipeline").
    3.  **Extract Description:** Synthesize a concise description of the pipeline's overall purpose and function.
    4.  **Extract Stages:** Identify the discrete steps or stages in the pipeline process.
    5.  **Extract Input/Output:** Determine what data enters the pipeline and what results from it.
    6.  **Extract Components:** Note which system components are involved in implementing this pipeline.
    7.  **Handle Ambiguity:** If information for a field is missing or unclear in the text, leave the optional fields empty.

    **Output Format:** Respond with the extracted data structured according to this Pydantic model.
    """

    name: str = Field(
        ...,
        description='The specific name or purpose of the data pipeline (e.g., "Entity Extraction Pipeline").',
    )
    description: str = Field(
        ...,
        description='A concise description of the pipeline\'s overall purpose and function in the system.',
    )
    stages: Optional[List[str]] = Field(
        None,
        description='The discrete steps or stages in the pipeline process, in sequential order.',
    )
    input_data: Optional[str] = Field(
        None,
        description='The type or source of data that enters the pipeline for processing.',
    )
    output_data: Optional[str] = Field(
        None,
        description='The resulting data or artifacts produced by the pipeline.',
    )
    components: Optional[List[str]] = Field(
        None,
        description='System components or modules involved in implementing this pipeline.',
    ) 