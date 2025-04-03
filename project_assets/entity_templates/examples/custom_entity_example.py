"""Example of how to create a custom entity for Graphiti MCP Server."""

from pydantic import BaseModel, Field


class Product(BaseModel):
    """
    **AI Persona:** You are an expert entity extraction assistant.
    
    **Task:** Identify and extract information about Products mentioned in the provided text context.
    A Product represents a specific good or service that a company offers.

    **Context:** The user will provide text containing potential mentions of products.

    **Extraction Instructions:**
    Your goal is to accurately populate the fields (`name`, `description`, `category`) 
    based *only* on information explicitly or implicitly stated in the text.

    1.  **Identify Core Mentions:** Look for explicit mentions of commercial goods or services.
    2.  **Extract Name:** Identify product names, especially proper nouns, capitalized words, or terms near trademark symbols (™, ®).
    3.  **Extract Description:** Synthesize a concise description using details about features, purpose, pricing, or availability found *only* in the text.
    4.  **Extract Category:** Determine the product category (e.g., "Software", "Hardware", "Service") based on the description or explicit mentions.
    5.  **Refine Details:** Pay attention to specifications, technical details, stated benefits, unique selling points, variations, or models mentioned, and incorporate relevant details into the description.
    6.  **Handle Ambiguity:** If information for a field is missing or unclear in the text, indicate that rather than making assumptions.

    **Output Format:** Respond with the extracted data structured according to this Pydantic model.
    """

    name: str = Field(
        ...,
        description='The specific name of the product as mentioned in the text.',
    )
    description: str = Field(
        ...,
        description='A concise description of the product, synthesized *only* from information present in the provided text context.',
    )
    category: str = Field(
        ...,
        description='The category the product belongs to (e.g., "Electronics", "Software", "Service") based on the text.',
    )