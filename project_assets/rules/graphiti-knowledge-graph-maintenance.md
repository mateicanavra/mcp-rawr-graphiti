---
description: Use this rule when you need to propose changes (additions, modifications) to a project's specific knowledge graph schema file (`graphiti-[project-name]-schema.md`).
globs: 
alwaysApply: false
---

# Graphiti Knowledge Graph Maintenance Rules

## 1. Purpose and Scope

This document provides rules for AI agents on how to maintain and update the **project-specific knowledge graph schema file**, typically named `graphiti-[project-name]-schema.md`.

**Goal:** Ensure consistency between the defined project schema, the agent's entity extraction behavior for this project, and the actual structure of the project's knowledge graph over time.

**Key Distinctions:**
- This rule governs the *maintenance* of the project schema.
- For general rules on using Graphiti tools, refer to `@graphiti-mcp-core-rules.md`.
- For the specific entities and relationships of *this* project, refer to `graphiti-[project-name]-schema.md`.

**Scope Limitation:** These rules apply *only* to proposing changes to the project-specific `graphiti-[project-name]-schema.md` file. Do not use these rules to modify `@graphiti-mcp-core-rules.md` or this file itself.

## 2. Primacy of the Project Schema

- The `graphiti-[project-name]-schema.md` file is the **single source of truth** for this project's unique knowledge structure (entities, relationships, properties).
- Specific rules within the project schema **override or specialize** the general guidelines found in `@graphiti-mcp-core-rules.md`.

## 3. When to Consult the Project Schema

You **must** consult the relevant `graphiti-[project-name]-schema.md` file **before**:
- Defining any new entity type or relationship that appears specific to the current project.
- Extracting entities, facts, or relationships based on project-specific requirements mentioned by the user or discovered in project context.
- Answering user questions about the project's established knowledge structure, entities, or relationships.

## 4. Consistency Verification

- Before adding any new entity instance, fact, or relationship that seems specific to the project, **verify** that it conforms to the existing definitions and relationship rules documented in `graphiti-[project-name]-schema.md`.
- If the information doesn't fit the existing schema, proceed to Section 5 (Schema Evolution).

## 5. Schema Evolution and Update Process

Project knowledge schemas are expected to evolve. If you identify a need for a **new** entity type, relationship, property, or a **modification** to an existing one based on user interaction or task requirements:

1.  **Identify the Need:** Clearly determine the required change (e.g., "Need a 'SoftwareComponent' entity type," "Need to add a 'dependency' relationship between 'SoftwareComponent' entities," "Need to add a 'version' property to 'SoftwareComponent'").
2.  **Consult Existing Schema:** Double-check `graphiti-[project-name]-schema.md` to confirm the element truly doesn't exist or needs modification.
3.  **Propose Schema Update:**
    - Formulate a proposed change to the `graphiti-[project-name]-schema.md` file.
    - Define the new/modified element clearly, following the structural best practices (like those derived from the entity templates mentioned in `@graphiti-mcp-core-rules.md`).
    - Format the proposed edit for the `.md` file itself according to the guidelines in `@creating-cursor-rules.mdc`.
    - Include a justification (see Section 6).
    - Use the appropriate tool (e.g., `edit_file`) to propose this change to the `graphiti-[project-name]-schema.md` file.
4.  **Await Outcome:** Wait for the schema update proposal to be accepted or rejected.
5.  **Proceed Based on Outcome:**
    - **If Accepted:** You can now proceed with the original task (e.g., entity extraction, graph update) using the newly defined/modified schema element.
    - **If Rejected:** Do not proceed with adding graph data that violates the established schema. Inform the user if necessary, explaining that the required structure is not defined in the project schema.

## 6. Justification for Schema Changes

- When proposing any change to the `graphiti-[project-name]-schema.md`, provide a brief, clear justification.
- Link the justification directly to the user request, conversation context, or specific information encountered that necessitates the schema change. Example: "Justification: User requested tracking software components and their dependencies, which requires adding a 'SoftwareComponent' entity and a 'dependency' relationship to the project schema."

## 7. Schema Validation (Best Practice)

- Before finalizing a schema change proposal, briefly consider its potential impact:
    - Does the change conflict with existing data in the knowledge graph?
    - Does it align with the overall goals of the project as understood?
    - Does it maintain the clarity and usefulness of the schema?
- Mention any potential conflicts or considerations in your justification if significant.

**Remember:** Maintaining an accurate and consistent project schema is crucial for reliable knowledge management and effective AI assistance within the project context. 