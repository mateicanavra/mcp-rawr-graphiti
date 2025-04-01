# Graphiti MCP Tools Usage Guide

This document provides guidance on using the Graphiti Model Context Protocol (MCP) tools, including known issues, parameter handling, and best practices.

## Table of Contents

- [Available MCP Tools](#available-mcp-tools)
- [Known Issues and Solutions](#known-issues-and-solutions)
- [Best Practices](#best-practices)
- [Usage Examples](#usage-examples)

## Available MCP Tools

The Graphiti MCP server exposes the following tools:

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `mcp_graphiti_core_add_episode` | Add an episode to the knowledge graph | `name`, `episode_body`, `source` |
| `mcp_graphiti_core_search_nodes` | Search for node summaries | `query`, `max_nodes`, `center_node_uuid` |
| `mcp_graphiti_core_search_facts` | Search for facts (edges) | `query`, `max_facts`, `center_node_uuid` |
| `mcp_graphiti_core_delete_entity_edge` | Delete an entity edge | `uuid` |
| `mcp_graphiti_core_delete_episode` | Delete an episode | `uuid` |
| `mcp_graphiti_core_get_entity_edge` | Get an entity edge details | `uuid` |
| `mcp_graphiti_core_get_episodes` | Get recent episodes | `last_n` |
| `mcp_graphiti_core_clear_graph` | Clear all graph data | `random_string` (dummy parameter) |

## Known Issues and Solutions

### 1. `group_id` Parameter Handling

**Issue**: When using the `mcp_graphiti_core_add_episode` tool, explicitly providing a `group_id` parameter as a string causes an error: `Parameter 'group_id' must be of type undefined, got string`.

**Solution**: Omit the `group_id` parameter completely when calling the tool. The system will use a default group_id from the command line configuration or generate one.

```python
# Incorrect usage
mcp_graphiti_core_add_episode(
    name="Episode Name",
    episode_body="Content...",
    group_id="graphiti-source"  # This causes an error
)

# Correct usage
mcp_graphiti_core_add_episode(
    name="Episode Name",
    episode_body="Content..."
    # Let the system use the default group_id
)
```

**Background**: While the API documentation suggests that `group_id` is an optional string parameter, the MCP tool implementation expects this parameter to be either undefined or null, not an explicit string. This behavior may be specific to the MCP tool implementation rather than the underlying Graphiti API itself.

## Best Practices

### 1. Working with Knowledge Graph Search

Graphiti's knowledge graph uses a sophisticated hybrid search approach that combines:

- **Vector Similarity Search**: For semantic understanding
- **Full-text Search**: For keyword/text matching  
- **Graph Traversal**: Finding related nodes via BFS (Breadth-First Search)
- **Advanced Re-ranking**: Using techniques like MMR, Cross-encoder, RRF, etc.

When formulating search queries:
- Use natural language for semantic searches
- Include key terms for better results
- Be specific when searching for exact facts

### 2. Adding Episodes with Structured Data

When adding JSON data, ensure the JSON is properly escaped:

```python
mcp_graphiti_core_add_episode(
    name="Customer Profile",
    episode_body="{\"company\": {\"name\": \"Acme Technologies\"}, \"products\": [{\"id\": \"P001\", \"name\": \"CloudSync\"}]}",
    source="json",
    source_description="CRM data"
)
```

### 3. Context-Aware Searching

Use the `center_node_uuid` parameter when you want to prioritize search results that are closely related to a specific entity in the graph:

```python
mcp_graphiti_core_search_facts(
    query="product features",
    center_node_uuid="uuid-of-company-node"
)
```

## Usage Examples

### Adding a Text Episode

```python
mcp_graphiti_core_add_episode(
    name="Project Requirements",
    episode_body="The system must support real-time updates and maintain historical data integrity.",
    source="text",
    source_description="requirements document"
)
```

### Searching for Facts

```python
mcp_graphiti_core_search_facts(
    query="What are the system requirements?",
    max_facts=5
)
```

### Adding Conversation Data

```python
mcp_graphiti_core_add_episode(
    name="Client Meeting Discussion",
    episode_body="user: What's your timeline for deployment?\nassistant: We're planning to deploy the first phase by Q2 2025.",
    source="message",
    source_description="client meeting transcript"
)
```

### Retrieving Recent Episodes

```python
mcp_graphiti_core_get_episodes(
    last_n=5
)
```

## Search Mechanism Details

Graphiti's knowledge graph leverages a sophisticated hybrid search approach that combines multiple search methods:

1. **Vector Similarity Search**: The system creates embeddings for queries using an EmbedderClient. When a search is performed, the query text is converted to a vector representation with `query_vector = await embedder.create(input_data=[query])`. Functions like `node_similarity_search` and `edge_similarity_search` use this vector similarity to find semantically relevant content.

2. **Full-text Search**: Traditional keyword/text matching is implemented through `node_fulltext_search` and `edge_fulltext_search` functions for finding literal text matches.

3. **Graph Traversal**: BFS (Breadth-First Search) is used to find related nodes and edges with `node_bfs_search` and `edge_bfs_search`, leveraging the graph structure to discover connected information.

4. **Advanced Re-ranking**: Multiple sophisticated re-ranking strategies are applied after initial search:
   - MMR (Maximal Marginal Relevance) for diversity in results
   - Cross-encoder neural re-ranking for improved relevance
   - RRF (Reciprocal Rank Fusion) to combine multiple search methods
   - Node distance and episode mentions re-ranking for contextual relevance

The system executes these different search methods in parallel and then combines the results using the configured re-ranking strategy. 