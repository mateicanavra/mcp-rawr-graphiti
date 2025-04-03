"""Definition for a Company entity."""

from pydantic import BaseModel, Field


class Company(BaseModel):
    """
    **AI Persona:** You are an expert entity extraction assistant.
    
    **Task:** Identify and extract information about Companies mentioned in the provided text context.
    A Company represents a business organization.

    **Context:** The user will provide text containing potential mentions of companies.

    **Extraction Instructions:**
    Your goal is to accurately populate the fields (`name`, `industry`) 
    based *only* on information explicitly or implicitly stated in the text.

    1.  **Identify Core Mentions:** Look for explicit mentions of business organizations, corporations, startups, etc.
    2.  **Extract Name:** Identify company names, often proper nouns or capitalized sequences.
    3.  **Extract Industry:** Determine the company's industry (e.g., "Technology", "Retail", "Finance") based on context or explicit mentions.
    4.  **Handle Ambiguity:** If information for a field is missing or unclear, indicate that.

    **Output Format:** Respond with the extracted data structured according to this Pydantic model.
    """

    name: str = Field(
        ...,
        description='The specific name of the company as mentioned in the text.',
    )
    industry: str | None = Field(
        default=None,
        description='The industry the company operates in (e.g., "Technology", "Finance"), if mentioned.',
    ) 