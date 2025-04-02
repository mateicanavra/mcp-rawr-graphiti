---
description: Use this rule first for general guidance on using Graphiti MCP server tools (entity extraction, memory). It explains the overall rule structure and links to project-specific schemas and maintenance procedures.
globs: 
alwaysApply: false
---

# Graphiti MCP Tools Guide for AI Agents

## Understanding Graphiti Rule Structure

This document provides the **core, foundational guidelines** for using the Graphiti MCP server tools, including entity extraction and agent memory management via the knowledge graph. These rules apply generally across projects.

For effective project work, be aware of the three key types of Graphiti rules:

1.  **This Core Rule (`@graphiti-mcp-core-rules.md`):** Your starting point for general tool usage and best practices.
2.  **Project-Specific Schema (`graphiti-[project-name]-schema.md`):** Defines the unique entities, relationships, and extraction nuances for a *specific* project. **Always consult the relevant project schema** when working on project-specific tasks. Example: `@graphiti-example-schema.md`.
3.  **Schema Maintenance (`@graphiti-knowledge-graph-maintenance.md`):** Explains the *process* for proposing updates or changes to a project-specific schema file.

**Always prioritize rules in the project-specific schema** if they conflict with these general core rules.

## Entity Extraction Principles

- **Use structured extraction patterns:** Follow the AI persona, task, context, and instructions format in entity definitions.
- **Maintain entity type integrity:** Each entity type should have a clear, unique purpose with non-overlapping definitions.
- **Prefer explicit information:** Extract only what is explicitly or strongly implied in the text; avoid assumptions.
- **Handle ambiguity properly:** If information is missing or uncertain, acknowledge the ambiguity rather than fabricating details.
- **Follow field definitions strictly:** Respect the description and constraints defined for each field in the entity model.

## Creating New Entity Types

- **Utilize the `graphiti add-entities` command:** Create new entity type sets with proper scaffolding.
- **Follow the template pattern:** Use the comprehensive docstring format from `custom_entity_example.py` when defining new entity types.
- **Structure entity classes clearly:** Include AI persona, task definition, context explanation, detailed extraction instructions, and output format.
- **Use descriptive field definitions:** Each field should have clear descriptions using the Field annotations.
- **Document extraction logic:** Include specific instructions for identifying and extracting each required field.

## Agent Memory Management

### Before Starting Any Task

- **Always search first:** Use the `search_nodes` tool to look for relevant preferences and procedures before beginning work.
- **Search for facts too:** Use the `search_facts` tool to discover relationships and factual information that may be relevant to your task.
- **Filter by entity type:** Specify `Preference`, `Procedure`, `Requirement`, or other relevant entity types in your node search to get targeted results.
- **Review all matches:** Carefully examine any preferences, procedures, or facts that match your current task.

### Always Save New or Updated Information

- **Capture requirements and preferences immediately:** When a user expresses a requirement or preference, use `add_episode` to store it right away.
  - _Best practice:_ Split very long requirements into shorter, logical chunks.
- **Be explicit if something is an update to existing knowledge.** Only add what's changed or new to the graph.
- **Document procedures clearly:** When you discover how a user wants things done, record it as a procedure.
- **Record factual relationships:** When you learn about connections between entities, store these as facts.
- **Be specific with categories:** Label entities with clear categories for better retrieval later.

### During Your Work

- **Respect discovered preferences:** Align your work with any preferences you've found.
- **Follow procedures exactly:** If you find a procedure for your current task, follow it step by step.
- **Apply relevant facts:** Use factual information to inform your decisions and recommendations.
- **Stay consistent:** Maintain consistency with previously identified entities, preferences, procedures, and facts.

## Best Practices for Tool Usage

- **Search before suggesting:** Always check if there's established knowledge before making recommendations.
- **Combine node and fact searches:** For complex tasks, search both nodes and facts to build a complete picture.
- **Use `center_node_uuid`:** When exploring related information, center your search around a specific node.
- **Prioritize specific matches:** More specific information takes precedence over general information.
- **Be proactive:** If you notice patterns in user behavior, consider storing them as preferences or procedures.
- **Document your reasoning:** When making extraction or classification decisions, briefly note your reasoning.
- **Handle edge cases gracefully:** Plan for anomalies and develop consistent strategies for handling them.
- **Validate entity coherence:** Ensure extracted entities form a coherent, logically consistent set.
- **Understand parameter behavior:** Be aware of specific tool parameter nuances:
  - For `mcp_graphiti_core_add_episode`, avoid explicitly providing `group_id` as a string—let the system use defaults from command line configuration or generate one automatically.
  - Use episode source types appropriately: 'text' for plain content, 'json' for structured data that should automatically extract entities and relationships, and 'message' for conversation-style content.
- **Leverage JSON for structured data:** When adding structured information with `add_episode`:
  - **Preferred method:** Pass a Python dictionary or list directly: `episode_body={"company": {"name": "Acme Corp"}, "products": [{"id": "P001", "name": "CloudSync"}]}`
  - **Alternative method:** Use a properly escaped JSON string if necessary
  - Structure your JSON with logical entity hierarchies to enable automatic entity and relationship extraction
  - Keep nesting to a reasonable depth for optimal processing
  - Properties in your JSON structure will be converted to entities, with relationships established based on the structure
  - Include clear identifiers and descriptive properties to improve entity recognition
- **Leverage advanced search capabilities:** When using search tools:
  - Use hybrid search combining vector similarity, full-text search, and graph traversal.
  - Set appropriate `max_nodes` and `max_facts` to control result volume.
  - Apply `entity` parameter when filtering for specific entity types (e.g., "Preference", "Procedure").
  - Use advanced re-ranking strategies for more contextually relevant results.

## MCP Server Codebase Organization

- **Prefer flat directory structures:** Use consolidated, shallow directory hierarchies over deeply nested ones.
- **Group similar entity types:** Place related entity types within a single directory (e.g., `entity_types/graphiti/`).
- **Follow semantic naming:** Name entity type files according to their semantic type (e.g., `ArchitecturalPattern.py`) rather than using generic names.
- **Remove redundant files:** Keep the codebase clean by removing unnecessary `__init__.py` files in auto-loaded directories.
- **Clean up after reorganization:** Systematically remove empty directories after file restructuring.
- **Maintain proper entity structure:** Ensure all entity types follow the Pydantic model pattern with well-defined fields, descriptions, and extraction instructions.

## Maintaining Context and Continuity

- **Track conversation history:** Reference relevant prior exchanges when making decisions.
- **Build knowledge incrementally:** Add to the graph progressively as new information emerges.
- **Preserve important context:** Identify and retain critical contextual information across sessions.
- **Connect related entities:** Create explicit links between related entities to build a rich knowledge graph.
- **Support iterative refinement:** Allow for progressive improvement of entity definitions and instances.

**Remember:** The knowledge graph is your memory. Use it consistently, respecting the rules outlined here and, more importantly, the specific definitions and guidelines within the relevant `graphiti-[project-name]-schema.md` file for your current project context. Entity extraction should be precise, consistent, and aligned with the structured models defined in the codebase and the project schema.

---

## Background & References

Maintaining a knowledge graph requires diligence. The goal is not just to store data, but to create a useful, accurate, and evolving representation of knowledge.

*   **Graphiti Project:** This MCP server leverages the Graphiti framework. Understanding its core concepts is beneficial.
    *   [Graphiti GitHub Repository](mdc:https:/github.com/getzep/Graphiti)
    *   [Graphiti Documentation & Guides](mdc:https:/help.getzep.com/graphiti)
    *   Graphiti powers [Zep Agent Memory](mdc:https:/www.getzep.com), detailed in the paper: [Zep: A Temporal Knowledge Graph Architecture for Agent Memory](mdc:https:/arxiv.org/abs/2501.13956).
*   **Neo4j Database:** Graphiti uses Neo4j (v5.26+) as its backend storage.
    *   [Neo4j Developer Documentation](mdc:https:/neo4j.com/docs/getting-started/current)
    *   [Neo4j Desktop](mdc:https:/neo4j.com/download) (Recommended for local development)
*   **Knowledge Graph Principles:** Building and maintaining knowledge graphs involves careful planning and iteration.
    *   **Defining Scope & Entities:** Clearly define the purpose, scope, entities, and relationships for your graph. ([Source: pageon.ai](mdc:https:/www.pageon.ai/blog/how-to-build-a-knowledge-graph), [Source: smythos.com](mdc:https:/smythos.com/ai-agents/ai-tutorials/knowledge-graph-tutorial))
    *   **Maintenance & Validation:** Regularly assess the graph's accuracy and usefulness. Ensure data validity and consistency. Schemas evolve, so plan for iteration. ([Source: stardog.com](mdc:https:/www.stardog.com/building-a-knowledge-graph))

Use the specific rules defined in `@graphiti-knowledge-graph-maintenance.md` when proposing changes to project schemas.
