#!/usr/bin/env python3
"""
Graphiti MCP Server - Exposes Graphiti functionality through the Model Context Protocol (MCP)
"""

import argparse
import asyncio
import importlib
import importlib.util
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Union, cast

import traceback  # Added for detailed error logging
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError  # Added for specific error handling
from pydantic import BaseModel, Field

from graphiti_core import Graphiti
from graphiti_core.edges import EntityEdge
from graphiti_core.llm_client import LLMClient
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient as OpenAIClient
from graphiti_core.nodes import EpisodeType, EpisodicNode
from graphiti_core.search.search_config_recipes import (
    NODE_HYBRID_SEARCH_NODE_DISTANCE,
    NODE_HYBRID_SEARCH_RRF,
)
from graphiti_core.search.search_filters import SearchFilters
from graphiti_core.utils.maintenance.graph_data_operations import clear_data
from entities import get_entities, get_entity_subset, register_entity
from constants import DEFAULT_LOG_LEVEL, DEFAULT_LLM_MODEL, ENV_GRAPHITI_LOG_LEVEL
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

load_dotenv()

# The ENTITIES dictionary is managed by the registry in mcp_server.entities
# NOTE: This global reference is only used for predefined entity subsets below.
# For the latest entities, always use get_entities() directly.
ENTITIES = get_entities()

# Predefined entity sets for different use cases
REQUIREMENT_ONLY_ENTITIES = get_entity_subset(['Requirement'])
PREFERENCE_ONLY_ENTITIES = get_entity_subset(['Preference'])
PROCEDURE_ONLY_ENTITIES = get_entity_subset(['Procedure'])


# Type definitions for API responses
class ErrorResponse(TypedDict):
    error: str


class SuccessResponse(TypedDict):
    message: str


class NodeResult(TypedDict):
    uuid: str
    name: str
    summary: str
    labels: list[str]
    group_id: str
    created_at: str
    attributes: dict[str, Any]


class NodeSearchResponse(TypedDict):
    message: str
    nodes: list[NodeResult]


class FactSearchResponse(TypedDict):
    message: str
    facts: list[dict[str, Any]]


class EpisodeSearchResponse(TypedDict):
    message: str
    episodes: list[dict[str, Any]]


class StatusResponse(TypedDict):
    status: str
    message: str


# Server configuration classes
class GraphitiConfig(BaseModel):
    """Configuration for Graphiti client.

    Centralizes all configuration parameters for the Graphiti client,
    including database connection details and LLM settings.
    """

    # neo4j_uri: str = 'bolt://localhost:7687'
    neo4j_uri: str = 'bolt://neo4j:7687'
    neo4j_user: str = 'neo4j'
    neo4j_password: str = 'password'
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    model_name: Optional[str] = None
    group_id: Optional[str] = None
    use_custom_entities: bool = False
    # entity_subset: Optional[list[str]] = None # REMOVED: This is now controlled by loading mechanism via --entities arg

    @classmethod
    def from_env(cls) -> 'GraphitiConfig':
        """Create a configuration instance from environment variables."""
        neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
        neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
        neo4j_password = os.environ.get('NEO4J_PASSWORD', 'password')
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        openai_base_url = os.environ.get('OPENAI_BASE_URL')
        model_name = os.environ.get('MODEL_NAME')

        # Environment context check for password hardening
        # Use GRAPHITI_ENV if set, else treat as non-dev
        env_context = os.environ.get('GRAPHITI_ENV', '').lower()
        if (
            neo4j_password == 'password'
            and env_context not in ('dev', 'development')
        ):
            raise ValueError(
                "Default Neo4j password 'password' is insecure and not allowed in non-development environments. "
                "Set a strong NEO4J_PASSWORD."
            )

        return cls(
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password,
            openai_api_key=openai_api_key,
            openai_base_url=openai_base_url,
            model_name=model_name,
        )


class MCPConfig(BaseModel):
    """Configuration for MCP server."""

    transport: str


# Configure logging
log_level_str = os.environ.get(ENV_GRAPHITI_LOG_LEVEL, 'info').upper()
log_level = getattr(logging, log_level_str, DEFAULT_LOG_LEVEL)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)
logger.info(f'Initial logging configured with level: {logging.getLevelName(log_level)}')

# Function to reconfigure logging level based on final decision
def configure_logging(level_name: str):
    """
    Configure or reconfigure the logging level based on a string level name.
    
    Args:
        level_name: A string representation of the logging level ('debug', 'info', etc.)
    """
    global logger, log_level
    level_name_upper = level_name.upper()
    new_level = getattr(logging, level_name_upper, DEFAULT_LOG_LEVEL)
    if new_level != log_level:  # Only reconfigure if level changes
        log_level = new_level
        logging.getLogger().setLevel(log_level)  # Set level on root logger
        # Re-get logger instance for safety
        logger = logging.getLogger(__name__)
        logger.info(f"Logging level reconfigured to: {logging.getLevelName(log_level)}")
    else:
        logger.info(f"Logging level remains at: {logging.getLevelName(log_level)}")

# Create global config instance
config = GraphitiConfig.from_env()

# MCP server instructions
GRAPHITI_MCP_INSTRUCTIONS = """
Welcome to Graphiti MCP - a memory service for AI agents built on a knowledge graph. Graphiti performs well
with dynamic data such as user interactions, changing enterprise data, and external information.

Graphiti transforms information into a richly connected knowledge network, allowing you to 
capture relationships between concepts, entities, and information. The system organizes data as episodes 
(content snippets), nodes (entities), and facts (relationships between entities), creating a dynamic, 
queryable memory store that evolves with new information. Graphiti supports multiple data formats, including 
structured JSON data, enabling seamless integration with existing data pipelines and systems.

Facts contain temporal metadata, allowing you to track the time of creation and whether a fact is invalid 
(superseded by new information).

Key capabilities:
1. Add episodes (text, messages, or JSON) to the knowledge graph with the add_episode tool
2. Search for nodes (entities) in the graph using natural language queries with search_nodes
3. Find relevant facts (relationships between entities) with search_facts
4. Retrieve specific entity edges or episodes by UUID
5. Manage the knowledge graph with tools like delete_episode, delete_entity_edge, and clear_graph

The server connects to a database for persistent storage and uses language models for certain operations. 
Each piece of information is organized by group_id, allowing you to maintain separate knowledge domains.

When adding information, provide descriptive names and detailed content to improve search quality. 
When searching, use specific queries and consider filtering by group_id for more relevant results.

For optimal performance, ensure the database is properly configured and accessible, and valid 
API keys are provided for any language model operations.
"""


# MCP server instance
mcp = FastMCP(
    'graphiti',
    instructions=GRAPHITI_MCP_INSTRUCTIONS,
)


# Initialize Graphiti client
graphiti_client: Optional[Graphiti] = None


async def initialize_graphiti(llm_client: Optional[LLMClient] = None, destroy_graph: bool = False):
    """Initialize the Graphiti client with the provided settings.

    Args:
        llm_client: Optional LLMClient instance to use for LLM operations
        destroy_graph: Optional boolean to destroy all Graphiti graphs
    """
    global graphiti_client

    # If no client is provided, create a default OpenAI client
    if not llm_client:
        if config.openai_api_key:
            llm_config = LLMConfig(api_key=config.openai_api_key)
            if config.openai_base_url:
                llm_config.base_url = config.openai_base_url
            if config.model_name:
                llm_config.model = config.model_name
            llm_client = OpenAIClient(config=llm_config)
        else:
            raise ValueError('OPENAI_API_KEY must be set when not using a custom LLM client')

    if not config.neo4j_uri or not config.neo4j_user or not config.neo4j_password:
        raise ValueError('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set')

    graphiti_client = Graphiti(
        uri=config.neo4j_uri,
        user=config.neo4j_user,
        password=config.neo4j_password,
        llm_client=llm_client,
    )

    if destroy_graph:
        logger.info('Destroying graph...')
        await clear_data(graphiti_client.driver)

    # Initialize the graph database with Graphiti's indices
    await graphiti_client.build_indices_and_constraints()
    logger.info('Graphiti client initialized successfully')


def format_fact_result(edge: EntityEdge) -> dict[str, Any]:
    """Format an entity edge into a readable result.

    Since EntityEdge is a Pydantic BaseModel, we can use its built-in serialization capabilities.

    Args:
        edge: The EntityEdge to format

    Returns:
        A dictionary representation of the edge with serialized dates and excluded embeddings
    """
    return edge.model_dump(
        mode='json',
        exclude={
            'fact_embedding',
        },
    )


# Dictionary to store queues for each group_id
# Each queue is a list of tasks to be processed sequentially
episode_queues: dict[str, asyncio.Queue] = {}
# Dictionary to track if a worker is running for each group_id
queue_workers: dict[str, bool] = {}


async def process_episode_queue(group_id: str):
    """Process episodes for a specific group_id sequentially.

    This function runs as a long-lived task that processes episodes
    from the queue one at a time.
    """
    global queue_workers

    logger.info(f'Starting episode queue worker for group_id: {group_id}')
    queue_workers[group_id] = True

    try:
        while True:
            # Get the next episode processing function from the queue
            # This will wait if the queue is empty
            process_func = await episode_queues[group_id].get()

            try:
                # Process the episode
                await process_func()
            except Exception as e:
                logger.error(f'Error processing queued episode for group_id {group_id}: {str(e)}')
            finally:
                # Mark the task as done regardless of success/failure
                episode_queues[group_id].task_done()
    except asyncio.CancelledError:
        logger.info(f'Episode queue worker for group_id {group_id} was cancelled')
    except Exception as e:
        logger.error(f'Unexpected error in queue worker for group_id {group_id}: {str(e)}')
    finally:
        queue_workers[group_id] = False
        logger.info(f'Stopped episode queue worker for group_id: {group_id}')


@mcp.tool()
async def add_episode(
    name: str,
    # MODIFIED: Always expect a string now
    episode_body: str,
    group_id: Optional[str] = None,
    # MODIFIED: Replaced 'source' with 'format'
    format: str = 'text', # 'text', 'json', or 'message'
    source_description: str = '',
    uuid: Optional[str] = None,
    entity_subset: Optional[list[str]] = None,
) -> Union[SuccessResponse, ErrorResponse]:
    """(Revised Input) Add an episode to the Graphiti knowledge graph.

    Processes the episode addition asynchronously in the background.
    Episodes for the same group_id are processed sequentially.

    Args:
        name (str): Name of the episode
        episode_body (str): Supply the episode as **one stringified JSON blob**.
                           • Triple‑escape all quotes so the inner JSON is valid inside the outer JSON args.
                           • If format='json' → string must contain valid JSON.
                           • If format='text' | 'message' → string is treated as raw text.
        group_id (str, optional): A unique ID for this graph. Defaults to config.
        format (str, optional): How to interpret the `episode_body` string ('text', 'json', 'message'). Defaults to 'text'.
        source_description (str, optional): Description of the source.
        uuid (str, optional): Optional UUID for the episode.
        entity_subset (list[str], optional): Optional list of entity names to use.
    """
    # ---> Logging <---
    logger.debug(f"Entered add_episode for '{name}' with format '{format}'")
    global graphiti_client, episode_queues, queue_workers

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # Map string format to EpisodeType enum - Default to text
        source_type = EpisodeType.text
        if format.lower() == 'message':
            source_type = EpisodeType.message
        elif format.lower() == 'json':
            source_type = EpisodeType.json
        # ---> Logging <---
        logger.debug(f"Determined source_type: {source_type} based on format: {format}")

        # Use the provided group_id or fall back to the default from config
        effective_group_id = group_id if group_id is not None else config.group_id
        group_id_str = str(effective_group_id) if effective_group_id is not None else ''
        logger.debug(f"Effective group_id: {group_id_str}")

        assert graphiti_client is not None, 'graphiti_client should not be None here'
        client = cast(Graphiti, graphiti_client)

        # Directly use the input string - Parsing happens in the background task
        episode_body_str = episode_body
        logger.debug(f"Using provided episode_body string (length: {len(episode_body_str)})")

        # Define the episode processing function (captures current variables)
        async def process_episode():
            # ---> Logging <---
            logger.info(f"[BG Task - {group_id_str}] Starting processing for episode '{name}' (format: {format})")
            processed_body: Union[str, Dict, List] = episode_body_str # Default to string
            
            try:
                # Attempt JSON parsing ONLY if format is json, INSIDE the background task
                if source_type == EpisodeType.json:
                    try:
                        logger.debug(f"[BG Task - {group_id_str}] Attempting to parse episode_body as JSON")
                        processed_body = json.loads(episode_body_str)
                        logger.debug(f"[BG Task - {group_id_str}] Successfully parsed JSON.")
                        # NOTE: We pass the original string to client.add_episode,
                        # as the core library currently expects a string even for JSON source.
                        # If the core library is updated to accept dict/list, change `episode_body=episode_body_str` below.
                    except json.JSONDecodeError as json_err:
                        logger.error(f"[BG Task - {group_id_str}] Invalid JSON in episode_body for episode '{name}': {json_err}. Processing as text.")
                        # Fallback: Process as text if JSON parsing fails? Or raise error?
                        # For now, let's proceed but log the error. The core library might handle it gracefully or fail.
                        # Alternatively, uncomment the next line to stop processing on bad JSON:
                        # raise ValueError(f"Invalid JSON provided for format='json': {json_err}") from json_err
                
                # --- MODIFIED: Always use all currently loaded/registered entities ---
                # The decision of which entities are available is made at server startup
                # based on the --entities argument and loaded modules.
                from entities import get_entities
                entities_to_use = get_entities()
                logger.info(f"Using all currently registered entities for episode processing: {list(entities_to_use.keys())}")
                # --- End Modification ---

                # Call the core library function
                # IMPORTANT: Pass episode_body_str for now, even if format='json',
                # as graphiti-core expects a string.
                await client.add_episode(
                    name=name,
                    episode_body=episode_body_str,
                    source=source_type,
                    source_description=source_description,
                    group_id=group_id_str,
                    uuid=uuid,
                    reference_time=datetime.now(timezone.utc),
                    entity_types=entities_to_use,
                )
                logger.info(f"Episode '{name}' added successfully to graph")

                logger.info(f"Building communities after episode '{name}'")
                await client.build_communities()

                logger.info(f"[BG Task - {group_id_str}] Successfully processed episode '{name}'")
            except ValidationError as ve:
                # Format Pydantic validation errors for better readability
                error_details = []
                for error in ve.errors():
                    loc = " -> ".join(map(str, error["loc"]))
                    msg = error["msg"]
                    inp = error.get("input", "N/A") # Get input if available
                    error_details.append(f"  Field: '{loc}', Input: {inp!r}, Error: {msg}")
                formatted_errors = "\n".join(error_details)
                logger.error(
                    f"[BG Task - {group_id_str}] Pydantic Validation Error processing episode '{name}':\n{formatted_errors}\n--- Traceback ---\n{traceback.format_exc()}"
                )
            except Exception as e:
                # Catch other exceptions
                logger.error(
                    f"[BG Task - {group_id_str}] Unexpected Error processing episode '{name}': {e}\n--- Traceback ---\n{traceback.format_exc()}"
                )
                # Optionally, you could implement a way to notify the client of background errors

        # --- ASYNC QUEUEING LOGIC (Restored) ---
        logger.debug(f"Checking/Initializing queue for group_id: {group_id_str}")
        if group_id_str not in episode_queues:
            episode_queues[group_id_str] = asyncio.Queue()

        logger.debug(f"Adding process_episode to queue for group_id: {group_id_str}")
        await episode_queues[group_id_str].put(process_episode)

        logger.debug(f"Ensuring worker task exists for group_id: {group_id_str}")
        if not queue_workers.get(group_id_str, False):
            asyncio.create_task(process_episode_queue(group_id_str))

        logger.debug(f"Returning immediate 'queued' response for episode '{name}'")
        return {
            'message': f"Episode '{name}' queued for processing (position: {episode_queues[group_id_str].qsize()})"
        }
        # --- END ASYNC QUEUEING LOGIC ---

    except Exception as e:
        # This catches errors during the *initial* part (before queueing)
        error_msg = str(e)
        logger.error(f'Error queuing episode task for "{name}": {error_msg}')
        return {'error': f'Error queuing episode task: {error_msg}'}




@mcp.tool()
async def search_nodes(
    query: str,
    group_ids: Optional[list[str]] = None,
    max_nodes: int = 10,
    center_node_uuid: Optional[str] = None,
    entity: str = '',  # cursor seems to break with None
) -> Union[NodeSearchResponse, ErrorResponse]:
    """Search the Graphiti knowledge graph for relevant node summaries.
    These contain a summary of all of a node's relationships with other nodes.

    Note: entity is a single entity to filter results (permitted: "Preference", "Procedure").

    Args:
        query: The search query
        group_ids: Optional list of group IDs to filter results
        max_nodes: Maximum number of nodes to return (default: 10)
        center_node_uuid: Optional UUID of a node to center the search around
        entity: Optional single entity to filter results (permitted: "Preference", "Procedure")
    """
    global graphiti_client

    if graphiti_client is None:
        return ErrorResponse(error='Graphiti client not initialized')

    try:
        # Use the provided group_ids or fall back to the default from config if none provided
        effective_group_ids = (
            group_ids if group_ids is not None else [config.group_id] if config.group_id else []
        )

        # Configure the search
        if center_node_uuid is not None:
            search_config = NODE_HYBRID_SEARCH_NODE_DISTANCE.model_copy(deep=True)
        else:
            search_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        search_config.limit = max_nodes

        filters = SearchFilters()
        if entity != '':
            filters.node_labels = [entity]

        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        # Perform the search using the _search method
        search_results = await client._search(
            query=query,
            config=search_config,
            group_ids=effective_group_ids,
            center_node_uuid=center_node_uuid,
            search_filter=filters,
        )

        if not search_results.nodes:
            return NodeSearchResponse(message='No relevant nodes found', nodes=[])

        # Format the node results
        formatted_nodes: list[NodeResult] = [
            {
                'uuid': node.uuid,
                'name': node.name,
                'summary': node.summary if hasattr(node, 'summary') else '',
                'labels': node.labels if hasattr(node, 'labels') else [],
                'group_id': node.group_id,
                'created_at': node.created_at.isoformat(),
                'attributes': node.attributes if hasattr(node, 'attributes') else {},
            }
            for node in search_results.nodes
        ]

        return NodeSearchResponse(message='Nodes retrieved successfully', nodes=formatted_nodes)
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error searching nodes: {error_msg}')
        return ErrorResponse(error=f'Error searching nodes: {error_msg}')


@mcp.tool()
async def search_facts(
    query: str,
    group_ids: Optional[list[str]] = None,
    max_facts: int = 10,
    center_node_uuid: Optional[str] = None,
) -> Union[FactSearchResponse, ErrorResponse]:
    """Search the Graphiti knowledge graph for relevant facts.

    Args:
        query: The search query
        group_ids: Optional list of group IDs to filter results
        max_facts: Maximum number of facts to return (default: 10)
        center_node_uuid: Optional UUID of a node to center the search around
    """
    global graphiti_client

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # Use the provided group_ids or fall back to the default from config if none provided
        effective_group_ids = (
            group_ids if group_ids is not None else [config.group_id] if config.group_id else []
        )

        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        relevant_edges = await client.search(
            group_ids=effective_group_ids,
            query=query,
            num_results=max_facts,
            center_node_uuid=center_node_uuid,
        )

        if not relevant_edges:
            return {'message': 'No relevant facts found', 'facts': []}

        facts = [format_fact_result(edge) for edge in relevant_edges]
        return {'message': 'Facts retrieved successfully', 'facts': facts}
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error searching facts: {error_msg}')
        return {'error': f'Error searching facts: {error_msg}'}


@mcp.tool()
async def delete_entity_edge(uuid: str) -> Union[SuccessResponse, ErrorResponse]:
    """Delete an entity edge from the Graphiti knowledge graph.

    Args:
        uuid: UUID of the entity edge to delete
    """
    global graphiti_client

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        # Get the entity edge by UUID
        entity_edge = await EntityEdge.get_by_uuid(client.driver, uuid)
        # Delete the edge using its delete method
        await entity_edge.delete(client.driver)
        return {'message': f'Entity edge with UUID {uuid} deleted successfully'}
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error deleting entity edge: {error_msg}')
        return {'error': f'Error deleting entity edge: {error_msg}'}


@mcp.tool()
async def delete_episode(uuid: str) -> Union[SuccessResponse, ErrorResponse]:
    """Delete an episode from the Graphiti knowledge graph.

    Args:
        uuid: UUID of the episode to delete
    """
    global graphiti_client

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        # Get the episodic node by UUID - EpisodicNode is already imported at the top
        episodic_node = await EpisodicNode.get_by_uuid(client.driver, uuid)
        # Delete the node using its delete method
        await episodic_node.delete(client.driver)
        return {'message': f'Episode with UUID {uuid} deleted successfully'}
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error deleting episode: {error_msg}')
        return {'error': f'Error deleting episode: {error_msg}'}


@mcp.tool()
async def get_entity_edge(uuid: str) -> Union[dict[str, Any], ErrorResponse]:
    """Get an entity edge from the Graphiti knowledge graph by its UUID.

    Args:
        uuid: UUID of the entity edge to retrieve
    """
    global graphiti_client

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        # Get the entity edge directly using the EntityEdge class method
        entity_edge = await EntityEdge.get_by_uuid(client.driver, uuid)

        # Use the format_fact_result function to serialize the edge
        # Return the Python dict directly - MCP will handle serialization
        return format_fact_result(entity_edge)
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error getting entity edge: {error_msg}')
        return {'error': f'Error getting entity edge: {error_msg}'}


@mcp.tool()
async def get_episodes(
    group_id: Optional[str] = None, last_n: int = 10
) -> Union[list[dict[str, Any]], EpisodeSearchResponse, ErrorResponse]:
    """Get the most recent episodes for a specific group.

    Args:
        group_id: ID of the group to retrieve episodes from. If not provided, uses the default group_id.
        last_n: Number of most recent episodes to retrieve (default: 10)
    """
    global graphiti_client

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # Use the provided group_id or fall back to the default from config
        effective_group_id = group_id if group_id is not None else config.group_id

        if not isinstance(effective_group_id, str):
            return {'error': 'Group ID must be a string'}

        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        episodes = await client.retrieve_episodes(
            group_ids=[effective_group_id], last_n=last_n, reference_time=datetime.now(timezone.utc)
        )

        if not episodes:
            return {'message': f'No episodes found for group {effective_group_id}', 'episodes': []}

        # Use Pydantic's model_dump method for EpisodicNode serialization
        formatted_episodes = [
            # Use mode='json' to handle datetime serialization
            episode.model_dump(mode='json')
            for episode in episodes
        ]

        # Return the Python list directly - MCP will handle serialization
        return formatted_episodes
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error getting episodes: {error_msg}')
        return {'error': f'Error getting episodes: {error_msg}'}


# Global variable to store the unique code for the current session
graph_clear_auth_code = str(uuid.uuid4())[:8]

@mcp.tool()
async def clear_graph(auth: str = None) -> Union[SuccessResponse, ErrorResponse]:
    """Clear all data from the Graphiti knowledge graph and rebuild indices.
    
    CAUTION: This is a destructive operation that will permanently delete ALL data in the graph.
    Before using this tool, you MUST first ask the user for explicit permission and authenticate.
    
    To authorize this action:
    1. First call this function without the auth parameter to get the unique authorization code
    2. Ask the user to explicitly confirm they want to delete ALL graph data
    3. Call the function again with the auth parameter set to BOTH the authorization code AND "DELETE_THIS_GRAPH"
       (Example: if code is "a1b2c3d4", auth should be "a1b2c3d4_DELETE_THIS_GRAPH")
    
    Args:
        auth: Authentication string that must include the unique code plus "_DELETE_THIS_GRAPH"
    """
    global graphiti_client, graph_clear_auth_code
    
    # Check if the current group ID is the root group ID
    root_group_id = os.environ.get('MCP_ROOT_GROUP_ID', 'root')
    current_group_id = config.group_id
    
    if current_group_id != root_group_id:
        return {
            'error': f"PERMISSION DENIED: Graph clearing operations are restricted to the root group ID. "
                    f"Current group ID: '{current_group_id}', required root group ID: '{root_group_id}'."
        }
    
    # Step 1: If no auth provided, return error with the current auth code
    if auth is None:
        return {
            'error': f"AUTHENTICATION REQUIRED: To clear the graph, you must first request permission from the user. "
                    f"Then call this function again with auth parameter set to '{graph_clear_auth_code}_DELETE_THIS_GRAPH'."
        }

    # Step 2: Validate the provided auth string
    expected_auth = f"{graph_clear_auth_code}_DELETE_THIS_GRAPH"
    if auth != expected_auth:
        # Generate a new code for security (prevents brute force attempts)
        graph_clear_auth_code = str(uuid.uuid4())[:8]
        return {
            'error': f"INVALID AUTHENTICATION: Authorization failed. A new authorization code has been generated. "
                    f"To clear the graph, first request permission from the user, then call this function again "
                    f"with auth parameter set to '{graph_clear_auth_code}_DELETE_THIS_GRAPH'."
        }

    # If we get here, authentication was successful
    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        # Log the authorized graph clear operation
        logger.warning(f"AUTHORIZED GRAPH CLEAR: Clearing all data from the graph with authorization '{auth}'")
        
        # clear_data is already imported at the top
        await clear_data(client.driver)
        await client.build_indices_and_constraints()
        
        # Generate a new code after successful operation for future security
        graph_clear_auth_code = str(uuid.uuid4())[:8]
        
        return {'message': 'Graph cleared successfully and indices rebuilt. All data has been deleted.'}
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error clearing graph: {error_msg}')
        return {'error': f'Error clearing graph: {error_msg}'}


@mcp.resource('http://graphiti/status')
async def get_status() -> StatusResponse:
    """Get the status of the Graphiti MCP server and Neo4j connection."""
    global graphiti_client

    if graphiti_client is None:
        return {'status': 'error', 'message': 'Graphiti client not initialized'}

    try:
        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        # Test Neo4j connection
        await client.driver.verify_connectivity()
        return {'status': 'ok', 'message': 'Graphiti MCP server is running and connected to Neo4j'}
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error checking Neo4j connection: {error_msg}')
        return {
            'status': 'error',
            'message': f'Graphiti MCP server is running but Neo4j connection failed: {error_msg}',
        }


def create_llm_client(api_key: Optional[str] = None, model: Optional[str] = None) -> LLMClient:
    """Create an OpenAI LLM client.

    Args:
        api_key: API key for the OpenAI service
        model: Model name to use

    Returns:
        An instance of the OpenAI LLM client
    """
    # Create config with provided API key and model
    llm_config = LLMConfig(api_key=api_key)

    # Set model if provided
    if model:
        llm_config.model = model

    # Create and return the client
    return OpenAIClient(config=llm_config)


async def initialize_server() -> MCPConfig:
    """Initialize the Graphiti server with the specified LLM client."""
    global config

    parser = argparse.ArgumentParser(
        description='Run the Graphiti MCP server with optional LLM client'
    )
    parser.add_argument(
        '--group-id',
        help='Namespace for the graph. This is an arbitrary string used to organize related data. '
        'If not provided, a random UUID will be generated.',
    )
    parser.add_argument(
        '--transport',
        choices=['sse', 'stdio'],
        default='sse',
        help='Transport to use for communication with the client. (default: sse)',
    )
    # OpenAI is the only supported LLM client
    parser.add_argument('--model', help='Model name to use with the LLM client')
    parser.add_argument('--destroy-graph', action='store_true', help='Destroy all Graphiti graphs')
    parser.add_argument(
        '--use-custom-entities',
        action='store_true',
        help='Enable entity extraction using the predefined ENTITIES',
    )
    # Add argument for specifying entities
    # --- MODIFIED: --entities now takes a comma-separated string for subdir selection ---
    parser.add_argument(
        '--entities',
        type=str,
        default="", # Default to empty string, meaning load all
        help='Comma-separated list of entity subdirectories (relative to --entities-dir) to load. '
             'If empty, all entities in --entities-dir are loaded.'
    )
    # --- End Modification ---
    # Add argument for custom entity directory
    parser.add_argument(
        '--entities-dir',
        help='Directory containing custom entity modules to load'
    )
    # Add argument for log level
    parser.add_argument(
        '--log-level',
        choices=['debug', 'info', 'warn', 'error', 'fatal'],
        default=os.environ.get('GRAPHITI_LOG_LEVEL', 'info').lower(),  # Default to ENV or 'info'
        help='Set the logging level.'
    )
    # --- NEW: Argument to control loading of root/base entities ---
    parser.add_argument(
        '--include-root-entities',
        type=str, # Read as string "true" or "false" from env var
        default="true", # Default to including root entities
        help='Set to "false" to prevent loading entities from the root /app/entities directory.'
    )
    # --- End NEW ---

    args = parser.parse_args()

    # Reconfigure logging based on final argument
    configure_logging(args.log_level)
    logger.info(f"Final effective logging level: {logging.getLevelName(log_level)}")

    # Set the group_id from CLI argument or generate a random one
    if args.group_id:
        config.group_id = args.group_id
        logger.info(f'Using provided group_id: {config.group_id}')
    else:
        config.group_id = f'graph_{uuid.uuid4().hex[:8]}'
        logger.info(f'Generated random group_id: {config.group_id}')

    # Define the expected path for base entities within the container
    container_base_entity_dir = "/app/entities"
    
    # --- MODIFIED: Conditionally load base entities based on --include-root-entities ---
    # Convert the string argument to boolean (case-insensitive comparison to "true")
    should_include_root = args.include_root_entities.lower() == "true"

    if should_include_root:
        if os.path.exists(container_base_entity_dir) and os.path.isdir(container_base_entity_dir):
            logger.info(f'Loading root entities from: {container_base_entity_dir}')
            load_entities_from_directory(container_base_entity_dir, "") # Load all from root
        else:
            logger.warning(f"Root entities directory specified but not found at: {container_base_entity_dir}")
    else:
        logger.info("Skipping loading of root entities based on --include-root-entities=false.")
    # --- End Modification ---
    
    # Load project-specific entities if directory is specified and different from base
    if args.entities_dir:
        # Resolve paths to handle potential symlinks or relative paths inside container
        abs_project_dir = os.path.abspath(args.entities_dir)
        abs_base_dir = os.path.abspath(container_base_entity_dir)
        
        if abs_project_dir != abs_base_dir:
            if os.path.exists(abs_project_dir) and os.path.isdir(abs_project_dir):
                logger.info(f'Loading project-specific entities from: {abs_project_dir}')
                # --- MODIFIED: Pass the entity selection spec from args ---
                load_entities_from_directory(abs_project_dir, args.entities)
            else:
                logger.warning(f"Project entities directory not found or not a directory: {abs_project_dir}")
        else:
            logger.info(f"Project entity directory '{args.entities_dir}' is the same as base, skipping redundant load.")

    # Set use_custom_entities flag if specified
    if args.use_custom_entities:
        config.use_custom_entities = True
        logger.info('Entity extraction enabled using predefined ENTITIES')
    else:
        logger.info('Entity extraction disabled (no custom entities will be used)')
        
    # --- REMOVED: Old logic for storing --entities list in config.entity_subset ---
    # This is now handled directly by the load_entities_from_directory function
    # based on the comma-separated string passed via args.entities.
    # --- End Removal ---

    # Log all registered entities after initialization
    logger.info(f"All registered entities after initialization: {len(get_entities())}")
    for entity_name in get_entities().keys():
        logger.info(f"  - Available entity: {entity_name}")

    llm_client = None

    # Create OpenAI client if model is specified or if OPENAI_API_KEY is available
    if args.model or config.openai_api_key:
        # Override model from command line if specified

        config.model_name = args.model or DEFAULT_LLM_MODEL

        # Create the OpenAI client
        llm_client = create_llm_client(api_key=config.openai_api_key, model=config.model_name)

    # Initialize Graphiti with the specified LLM client
    await initialize_graphiti(llm_client, destroy_graph=args.destroy_graph)

    return MCPConfig(transport=args.transport)


async def run_mcp_server():
    """Run the MCP server in the current event loop."""
    # Initialize the server
    mcp_config = await initialize_server()

    # Run the server with stdio transport for MCP in the same event loop
    logger.info(f'Starting MCP server with transport: {mcp_config.transport}')
    if mcp_config.transport == 'stdio':
        await mcp.run_stdio_async()
    elif mcp_config.transport == 'sse':
        logger.info(
            f'Running MCP server with SSE transport on {mcp.settings.host}:{mcp.settings.port}'
        )
        await mcp.run_sse_async()


def main():
    """Main function to run the Graphiti MCP server."""
    try:
        # Run everything in a single event loop
        asyncio.run(run_mcp_server())
    except Exception as e:
        logger.error(f'Error initializing Graphiti MCP server: {str(e)}')
        raise


# --- NEW: Helper function for robust module loading ---
def _load_and_register_entity_module(file_path: Path) -> None:
    """Loads a single Python file, finds, and registers entity classes."""
    module_name = file_path.stem
    full_module_path = str(file_path.absolute())
    
    try:
        # Dynamically import the module
        spec = importlib.util.spec_from_file_location(module_name, full_module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            # Add module to sys.modules BEFORE exec_module to handle circular imports if any
            # sys.modules[module_name] = module # Consider if needed, might complicate things
            spec.loader.exec_module(module)
            
            entities_registered = 0
            # Look for BaseModel classes in the module
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                
                # Check if it's a class, a subclass of BaseModel, not BaseModel itself, and has a docstring
                if (isinstance(attribute, type) and
                    issubclass(attribute, BaseModel) and
                    attribute != BaseModel and
                    attribute.__doc__):
                    
                    # Register the entity
                    register_entity(attribute_name, attribute)
                    entities_registered += 1
                    logger.debug(f"Auto-registered entity: {attribute_name} from {file_path.name}")
            
            if entities_registered > 0:
                 logger.info(f"Successfully loaded module: {file_path.name} (registered {entities_registered} entities)")
            # else:
            #      logger.debug(f"Loaded module {file_path.name}, but found no entities to register.")

    except Exception as e:
        logger.error(f"Error loading entity module {file_path.name} ({full_module_path}): {str(e)}", exc_info=True)
        # Continue loading other modules

# --- NEW: Helper function for recursive loading ---
def _load_modules_recursive(base_dir: Path) -> None:
    """Recursively finds and loads Python entity modules from a base directory."""
    logger.info(f"Recursively loading entities from: {base_dir}")
    python_files_found = 0
    for file_path in base_dir.rglob('*.py'):
        if file_path.name.startswith('__'):
            continue  # Skip __init__.py etc.
        python_files_found += 1
        _load_and_register_entity_module(file_path)
    if python_files_found == 0:
        logger.warning(f"No Python files found for entity loading in {base_dir}")


# --- MODIFIED: Main loading function now handles selection spec ---
def load_entities_from_directory(directory_path: str, subdir_selection_spec: str = "") -> None:
    """Load Python entity modules from a directory, optionally filtering by subdirectories.

    If subdir_selection_spec is empty, loads all entities recursively from directory_path.
    If subdir_selection_spec is provided (comma-separated subdir names), loads entities
    recursively only from those specific subdirectories within directory_path.

    Args:
        directory_path: Base path to the directory containing entity modules/subdirectories.
        subdir_selection_spec: Comma-separated string of subdirectory names to load, or empty to load all.
    """
    logger.info(f"Loading entities from base directory: {directory_path} with selection spec: '{subdir_selection_spec or 'ALL'}'")
    base_directory = Path(directory_path)
    if not base_directory.exists() or not base_directory.is_dir():
        logger.warning(f"Base entities directory '{directory_path}' does not exist or is not a directory. Skipping load.")
        return

    if not subdir_selection_spec:
        # Load all recursively from the base directory
        _load_modules_recursive(base_directory)
    else:
        # Load only specified subdirectories
        selected_subdirs = [subdir.strip() for subdir in subdir_selection_spec.split(',') if subdir.strip()]
        logger.info(f"Selectively loading entities from subdirectories: {selected_subdirs}")

        if not selected_subdirs:
             logger.warning(f"Empty or invalid subdir selection spec provided: '{subdir_selection_spec}'. No specific subdirectories will be loaded.")
             return

        for subdir_name in selected_subdirs:
            target_dir = base_directory / subdir_name
            if target_dir.exists() and target_dir.is_dir():
                _load_modules_recursive(target_dir)
            else:
                logger.warning(f"Specified entity subdirectory '{target_dir}' does not exist or is not a directory. Skipping.")
            # --- Commented out: Logic for loading specific files ---
            # elif target_dir.exists() and target_dir.is_file() and target_dir.suffix == '.py':
            #     logger.info(f"Loading specific entity file: {target_dir}")
            #     _load_and_register_entity_module(target_dir)
            # else:
            #     logger.warning(f"Specified entity path '{target_dir}' is not a directory or a Python file. Skipping.")
            # --- End Comment ---

    # Log total registered entities after attempting load for this directory path
    final_count = len(get_entities())
    logger.info(f"Finished loading entities for path '{directory_path}'. Total registered entities: {final_count}")
    if final_count > 0:
        logger.debug(f"Currently registered entities: {list(get_entities().keys())}")


def ask_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            "http://192.168.100.20:11434/api/generate",
            json={"model": "llama3.2:3b", "prompt": prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("response", "Sin respuesta")
    except requests.RequestException as e:
        return f"Error al llamar a Ollama: {str(e)}"


@app.post("/invoke")
async def invoke_handler(request: Request):
    data = await request.json()
    question = data.get("input", {}).get("question", "Sin pregunta")

    # Por ahora, respuesta mock
    return JSONResponse({"answer": f"Recibido: {question}"})


@app.post("/test-ollama")
async def test_ollama_endpoint(request: Request):
    """Endpoint de prueba para integrar Ollama con Graphiti"""
    try:
        data = await request.json()
        prompt = data.get("prompt", "¿Qué sabes sobre Graphiti?")
        
        # Hacer pregunta a Ollama
        ollama_response = ask_ollama(prompt)
        
        # Crear un episodio en Graphiti con la respuesta
        if graphiti_client is not None:
            episode_name = f"Ollama Response - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            episode_content = f"Pregunta: {prompt}\n\nRespuesta de Ollama: {ollama_response}"
            
            # Usar add_episode para guardar en Graphiti
            result = await add_episode(
                name=episode_name,
                episode_body=episode_content,
                group_id="ollama_test",
                format="text",
                source_description="Respuesta de Ollama guardada en Graphiti"
            )
            
            return JSONResponse({
                "success": True,
                "prompt": prompt,
                "ollama_response": ollama_response,
                "graphiti_result": result,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return JSONResponse({
                "success": False,
                "error": "Graphiti client not initialized",
                "ollama_response": ollama_response
            })
            
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })



if __name__ == '__main__':
    main()
