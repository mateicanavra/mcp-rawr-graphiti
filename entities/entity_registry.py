"""Entities Registry for Graphiti MCP Server.

This module provides a registry to manage entities in a modular way.
"""

from typing import Dict, Type

from pydantic import BaseModel, ConfigDict

# Global registry to store entities
_ENTITY_REGISTRY: Dict[str, Type[BaseModel]] = {}


def register_entity(name: str, entity_class: Type[BaseModel]) -> None:
    """Register an entity with the registry.

    Args:
        name: The name of the entity
        entity_class: The Pydantic model class for the entity
    """
    _ENTITY_REGISTRY[name] = entity_class


def get_entities() -> Dict[str, Type[BaseModel]]:
    """Get all registered entities.

    Returns:
        A dictionary mapping entity names to their Pydantic model classes
    """
    # Return the actual registry reference, not a copy
    return _ENTITY_REGISTRY


def get_entity_subset(names: list[str]) -> Dict[str, Type[BaseModel]]:
    """Get a subset of registered entities.

    Args:
        names: List of entity names to include

    Returns:
        A dictionary containing only the specified entities
    """
    return {name: _ENTITY_REGISTRY[name] for name in names if name in _ENTITY_REGISTRY} 