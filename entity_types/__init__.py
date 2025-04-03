"""Entity Types package.

This package contains entity type definitions for Graphiti MCP Server.
"""

# Import registration utilities
from entity_types.entity_registry import (
    register_entity_type,
    get_entity_types,
    get_entity_type_subset,
)

# Import entity models from actions
from entity_types.actions.procedure import Procedure

# Import entity models from constraints
from entity_types.constraints.requirement import Requirement

# Import entity models from interaction
from entity_types.interaction.interaction_model import InteractionModel
from entity_types.interaction.preference import Preference
from entity_types.interaction.feedback import Feedback

# Import entity models from connectors
from entity_types.connectors.agent import Agent
from entity_types.connectors.project import Project
from entity_types.connectors.resource import Resource
from entity_types.connectors.goal import Goal
from entity_types.connectors.developer import Developer
from entity_types.connectors.context_bundle import ContextBundle

# Import entity models from resources
from entity_types.resources.documentation import Documentation
from entity_types.resources.artifact import Artifact
from entity_types.resources.tool import Tool

# Register all entity models
register_entity_type(Procedure.__name__, Procedure)
register_entity_type(Requirement.__name__, Requirement)
register_entity_type(InteractionModel.__name__, InteractionModel)
register_entity_type(Preference.__name__, Preference)
register_entity_type(Feedback.__name__, Feedback)
register_entity_type(Agent.__name__, Agent)
register_entity_type(Project.__name__, Project)
register_entity_type(Resource.__name__, Resource)
register_entity_type(Goal.__name__, Goal)
register_entity_type(Developer.__name__, Developer)
register_entity_type(ContextBundle.__name__, ContextBundle)
register_entity_type(Documentation.__name__, Documentation)
register_entity_type(Artifact.__name__, Artifact)
register_entity_type(Tool.__name__, Tool)
