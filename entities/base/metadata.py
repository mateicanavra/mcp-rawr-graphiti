# entities/base/metadata.py
from pydantic import BaseModel, ConfigDict

class BaseMetadata(BaseModel):
    """
    Base model for metadata fields to ensure strict schema validation
    (no additional properties allowed), compatible with OpenAI's JSON mode.
    Add specific common metadata fields here if needed in the future.
    """
    model_config = ConfigDict(extra='forbid')