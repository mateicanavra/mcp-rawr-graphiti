"""Definition of the RetrievalMethod entity type for Graphiti."""

from pydantic import BaseModel, Field
from typing import List, Optional


class RetrievalMethodEntity(BaseModel):
    """
    **AI Persona:** You are an expert in information retrieval and search systems.
    
    **Task:** Identify and extract information about data retrieval methods used in the Graphiti framework.
    RetrievalMethodEntity represents an approach or technique for finding and retrieving information from the knowledge graph.

    **Context:** The text will contain descriptions of search mechanisms, query approaches, or information access methods.

    **Extraction Instructions:**
    Your goal is to accurately populate the fields about retrieval methods based *only* on information explicitly or implicitly stated in the text.

    1.  **Identify Retrieval Method Mentions:** Look for descriptions of search algorithms, querying approaches, or information access techniques.
    2.  **Extract Name:** Identify the specific retrieval method name (e.g., "Semantic Search", "Graph Traversal", "Keyword Matching").
    3.  **Extract Description:** Synthesize a concise description of how the retrieval method works and what problem it solves.
    4.  **Extract Algorithms:** Identify the specific algorithms or techniques employed by this retrieval method.
    5.  **Extract Strengths:** Note any stated advantages or strengths of this retrieval approach.
    6.  **Extract Limitations:** Capture any described limitations or constraints of this method.
    7.  **Extract Use Cases:** Identify specific use cases where this retrieval method is particularly effective.
    8.  **Handle Ambiguity:** If information for a field is missing or unclear in the text, leave the optional fields empty.

    **Output Format:** Respond with the extracted data structured according to this Pydantic model.
    """

    name: str = Field(
        ...,
        description='The specific name of the retrieval method (e.g., "Semantic Search", "Graph Traversal").',
    )
    description: str = Field(
        ...,
        description='A concise description of how the retrieval method works and what information access need it addresses.',
    )
    algorithms: Optional[List[str]] = Field(
        None,
        description='The specific algorithms or techniques employed by this retrieval method.',
    )
    strengths: Optional[List[str]] = Field(
        None,
        description='The advantages or strengths of this retrieval approach.',
    )
    limitations: Optional[List[str]] = Field(
        None,
        description='The limitations or constraints of this retrieval method.',
    )
    use_cases: Optional[List[str]] = Field(
        None,
        description='Specific scenarios or use cases where this retrieval method is particularly effective.',
    ) 