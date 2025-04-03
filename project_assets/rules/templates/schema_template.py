---
description: Use this rule when working specifically within the '__PROJECT_NAME__' project context to understand its unique entities, relationships, and extraction guidelines.
globs: # Add relevant globs for your project files, e.g., src/**/*.py
alwaysApply: false
---

# Graphiti Schema: __PROJECT_NAME__ Project

This document outlines the specific knowledge graph schema for the '__PROJECT_NAME__' project.

**Core Rules Reference:** For general Graphiti tool usage and foundational entity extraction principles, refer to `@graphiti-mcp-core-rules.mdc`.

**Maintenance:** For rules on how to update *this* schema file, refer to `@graphiti-knowledge-graph-maintenance.mdc`.

---

## 1. Defined Entities

*Add definitions for entities specific to the '__PROJECT_NAME__' project here.*
*Reference the entity definition files (e.g., Python classes) if applicable.*

Example:
*   **`MyEntity`**: Description of what this entity represents.
    *   Reference: `@path/to/your/entity/definition.py` (if applicable)
    *   Fields: `field1` (type), `field2` (type)

---

## 2. Defined Relationships (Facts)

*Define the key relationships (subject-predicate-object triples) specific to '__PROJECT_NAME__'.*

Example:
*   **Subject:** `MyEntity`
*   **Predicate:** `RELATED_TO`
*   **Object:** `AnotherEntity`

    *Example Fact:* `(MyEntity: 'Instance A') --[RELATED_TO]-> (AnotherEntity: 'Instance B')`
    *Extraction Rule:* Briefly describe how to identify this relationship.

---

## 3. Project-Specific Extraction Guidelines

*Add any extraction rules or nuances unique to the '__PROJECT_NAME__' project.*
*These guidelines supplement or specialize instructions in entity definitions and core rules.*

Example:
*   **Handling Ambiguity:** How to resolve conflicts when multiple potential entities match.
*   **Inference Rules:** Conditions under which properties can be inferred.

---

## 4. Future Evolution

*Briefly mention potential future directions or areas for schema expansion.* 