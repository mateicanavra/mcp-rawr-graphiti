---
description: Use this rule when working specifically within the 'example' project context to understand its unique entities (Product, Company), relationships (PRODUCES), and extraction guidelines.
globs: mcp_server/entity_types/example/*.py
alwaysApply: false
---

# Graphiti Schema: Example Project

This document outlines the specific knowledge graph schema for the 'example' project.

**Core Rules Reference:** For general Graphiti tool usage and foundational entity extraction principles, refer to `@graphiti-mcp-core-rules.md`.

**Maintenance:** For rules on how to update *this* schema file, refer to `@graphiti-knowledge-graph-maintenance.md`.

## 1. Defined Entity Types

The following entity types are defined for this project:

*   **`Product`**: Represents a specific good or service offered.
    *   Reference: `@mcp_server/entity_types/example/custom_entity_example.py`
    *   Fields: `name` (str), `description` (str), `category` (str)
*   **`Company`**: Represents a business organization.
    *   Reference: `@mcp_server/entity_types/example/company_entity.py`
    *   Fields: `name` (str), `industry` (str | None)

## 2. Defined Relationships (Facts)

The primary relationship captured in this project is:

*   **Subject:** `Company`
*   **Predicate:** `PRODUCES`
*   **Object:** `Product`

    *Example Fact:* `(Company: 'Acme Corp') --[PRODUCES]-> (Product: 'Widget Pro')`

**Extraction Rule:** When extracting facts of this type, ensure both the Company and Product entities are identified according to their definitions.

## 3. Project-Specific Extraction Guidelines

These guidelines supplement or specialize the instructions within the entity definitions and core rules:

*   **Product Category Inference:** If a `Product`'s category is not explicitly stated but its producing `Company`'s `industry` is known, you *may* infer the category from the industry if it's a direct match (e.g., a Tech company likely produces Software/Hardware). State the inference basis in the extraction reasoning.
*   **Disambiguation:** If multiple companies could produce a mentioned product, prioritize the company most recently discussed or most closely associated with the product description in the context.

## 4. Future Evolution

This schema may be expanded to include other entities (e.g., `Customer`, `Review`) and relationships (e.g., `SELLS`, `REVIEWS`) as the project needs evolve. Follow the process in `@graphiti-knowledge-graph-maintenance.md` to propose changes. 