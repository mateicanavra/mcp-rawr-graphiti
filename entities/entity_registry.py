"""Entity Types Registry for Graphiti MCP Server.

This module provides a registry to manage entity types in a modular way.
"""

from typing import Dict, Type

from pydantic import BaseModel

# Global registry to store entity types
_ENTITY_REGISTRY: Dict[str, Type[BaseModel]] = {}


def register_entity_type(name: str, entity_class: Type[BaseModel]) -> None:
    """Register an entity type with the registry.

    Args:
        name: The name of the entity type
        entity_class: The Pydantic model class for the entity type
    """
    _ENTITY_REGISTRY[name] = entity_class


def get_entity_types() -> Dict[str, Type[BaseModel]]:
    """Get all registered entity types.

    Returns:
        A dictionary mapping entity type names to their Pydantic model classes
    """
    # Return the actual registry reference, not a copy
    return _ENTITY_REGISTRY


def get_entity_type_subset(names: list[str]) -> Dict[str, Type[BaseModel]]:
    """Get a subset of registered entity types.

    Args:
        names: List of entity type names to include

    Returns:
        A dictionary containing only the specified entity types
    """
    return {name: _ENTITY_REGISTRY[name] for name in names if name in _ENTITY_REGISTRY} 