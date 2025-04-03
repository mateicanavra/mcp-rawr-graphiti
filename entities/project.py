"""Project entity for Graphiti MCP Server.

This module defines the Project entity, which represents a project or initiative.
"""

from pydantic import BaseModel, Field, ConfigDict


class Project(BaseModel):
    """Represents a project or initiative.

    Instructions for identifying and extracting projects:
    1. Named initiatives with clear scope and objectives.
    2. Clearly track status, definition, and success criteria changes over time.
    3. Clearly associate related goals and resources.
    4. Clearly track team members and stakeholders.
    5. Clearly track start and end dates.
    6. Clearly track justification for the project.
    """

    model_config = ConfigDict(extra='forbid')

    project_id: str = Field(..., description="Unique identifier for the project.")
    name: str = Field(..., description="Name of the project.")
    description: str = Field(..., description="Description of the project.")
    goals: list[str] = Field(default_factory=list, description="List of goals or objectives associated with the project.")
    resources: list[str] = Field(default_factory=list, description="List of resources associated with the project.")
    justification: str = Field(..., description="Justification for the project.")
    status: str = Field(..., description="Current status of the project.")
    start_date: str = Field(..., description="Start date of the project.")
    end_date: str = Field(..., description="End date of the project.")
    team: list[str] = Field(default_factory=list, description="List of team members associated with the project.")
    