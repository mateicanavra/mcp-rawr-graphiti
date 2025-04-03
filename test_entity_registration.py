#!/usr/bin/env python
"""Test script to verify entity registration.

This script imports the entity_types package and checks that all entities are properly registered.
"""

import entity_types
from entity_types import get_entity_types

if __name__ == "__main__":
    # Get all registered entity types
    registered_entities = get_entity_types()
    
    # Expected entity names
    expected_entities = [
        "Procedure",
        "Requirement",
        "InteractionModel",
        "Preference",
        "Feedback",
        "Agent",
        "Project",
        "Resource",
        "Goal",
        "Developer",
        "ContextBundle",
        "Documentation",
        "Artifact",
        "Tool"
    ]
    
    # Check if all expected entities are registered
    all_registered = True
    for entity_name in expected_entities:
        if entity_name in registered_entities:
            print(f"✅ Entity registered: {entity_name}")
        else:
            print(f"❌ Entity NOT registered: {entity_name}")
            all_registered = False
    
    # Print summary
    if all_registered:
        print("\n🎉 Success! All entities are registered correctly.")
    else:
        print("\n❌ Error: Some entities are not registered correctly.")
    
    # Print total number of registered entities
    print(f"\nTotal registered entities: {len(registered_entities)}")
    
    # Print all registered entity names
    print("\nAll registered entity names:")
    for name in sorted(registered_entities.keys()):
        print(f"- {name}") 