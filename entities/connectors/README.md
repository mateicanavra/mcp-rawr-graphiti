# Connectors Entities

This directory contains Pydantic models for entities that, within the context of our Meta Knowledge Graph, serve as **central hubs or aggregation points**.

These entities act as conceptual anchors that link together diverse information, relationships, and contexts relevant to the Graphiti ecosystem and its operation. They often have numerous connections to other entities, effectively "connecting" various facets of knowledge within the meta-graph.

Examples include:

*   `Agent`: Represents an AI or autonomous system, aggregating its capabilities, goals, interactions, assigned projects, etc.
*   `Developer`: Represents a human contributor, linking their skills, assigned tasks, projects, code contributions, etc.
*   `Project`: Represents a specific initiative, connecting goals, tasks, resources, involved agents/developers, and outcomes.
*   `Goal`: Represents a desired outcome, linking related projects, tasks, and success metrics.
*   `Resource`: Represents a document, tool, or dataset, connecting its content, source, usage context, and related entities.

These entities serve as the primary "connection points" or interfaces between the internal knowledge graph and the outside world or other distinct operational contexts, such as:

*   Project management systems
*   External documentation or data resources
*   Human collaborators (e.g., Developers)
*   Other AI systems or Agents
*   Abstract concepts like Goals or Projects that provide context. 