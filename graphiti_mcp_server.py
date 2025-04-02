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

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from graphiti_core import Graphiti
from graphiti_core.edges import EntityEdge
from graphiti_core.llm_client import LLMClient
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_client import OpenAIClient
from graphiti_core.nodes import EpisodeType, EpisodicNode
from graphiti_core.search.search_config_recipes import (
    NODE_HYBRID_SEARCH_NODE_DISTANCE,
    NODE_HYBRID_SEARCH_RRF,
)
from graphiti_core.search.search_filters import SearchFilters
from graphiti_core.utils.maintenance.graph_data_operations import clear_data
from entity_types import get_entity_types, get_entity_type_subset, register_entity_type
from constants import DEFAULT_LOG_LEVEL, DEFAULT_LLM_MODEL, ENV_GRAPHITI_LOG_LEVEL

load_dotenv()

# The ENTITY_TYPES dictionary is managed by the registry in mcp_server.entity_types
# NOTE: This global reference is only used for predefined entity subsets below.
# For the latest entity types, always use get_entity_types() directly.
ENTITY_TYPES = get_entity_types()

# Predefined entity type sets for different use cases
REQUIREMENT_ONLY_ENTITY_TYPES = get_entity_type_subset(['Requirement'])
PREFERENCE_ONLY_ENTITY_TYPES = get_entity_type_subset(['Preference'])
PROCEDURE_ONLY_ENTITY_TYPES = get_entity_type_subset(['Procedure'])


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
    entity_type_subset: Optional[list[str]] = None

    @classmethod
    def from_env(cls) -> 'GraphitiConfig':
        """Create a configuration instance from environment variables."""
        return cls(
            # neo4j_uri=os.environ.get('NEO4J_URI', 'bolt://localhost:7687'),
            neo4j_uri=os.environ.get('NEO4J_URI', 'bolt://neo4j:7687'),
            neo4j_user=os.environ.get('NEO4J_USER', 'neo4j'),
            neo4j_password=os.environ.get('NEO4J_PASSWORD', 'password'),
            openai_api_key=os.environ.get('OPENAI_API_KEY'),
            openai_base_url=os.environ.get('OPENAI_BASE_URL'),
            model_name=os.environ.get('MODEL_NAME'),
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
    entity_type_subset: Optional[list[str]] = None,
) -> Union[SuccessResponse, ErrorResponse]:
    """(Revised Input) Add an episode to the Graphiti knowledge graph.

    Processes the episode addition asynchronously in the background.
    Episodes for the same group_id are processed sequentially.

    Args:
        name (str): Name of the episode
        episode_body (str): The content of the episode, always provided as a string.
                           If format='json', this string must be valid JSON.
        group_id (str, optional): A unique ID for this graph. Defaults to config.
        format (str, optional): How to interpret episode_body ('text', 'json', 'message'). Defaults to 'text'.
        source_description (str, optional): Description of the source.
        uuid (str, optional): Optional UUID for the episode.
        entity_type_subset (list[str], optional): Optional list of entity type names to use.
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
                
                # (Entity type determination logic remains the same as previous version)
                # Import here to ensure we get the most up-to-date entity registry
                from entity_types import get_entity_types, get_entity_type_subset
                
                logger.info(f"Configuration settings - use_custom_entities: {config.use_custom_entities}, "
                           f"entity_type_subset param: {entity_type_subset}, "
                           f"config.entity_type_subset: {config.entity_type_subset}")
                
                if not config.use_custom_entities:
                    entity_types_to_use = {}
                    logger.info("Custom entities disabled, using empty entity type dictionary")
                elif entity_type_subset:
                    entity_types_to_use = get_entity_type_subset(entity_type_subset)
                    logger.info(f"Using function parameter entity subset: {entity_type_subset}")
                elif config.entity_type_subset:
                    entity_types_to_use = get_entity_type_subset(config.entity_type_subset)
                    logger.info(f"Using command-line entity subset: {config.entity_type_subset}")
                else:
                    entity_types_to_use = get_entity_types()
                    logger.info(f"Using all registered entity types: {list(entity_types_to_use.keys())}")
                
                logger.info(f"Final entity types being used: {list(entity_types_to_use.keys())}")

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
                    entity_types=entity_types_to_use,
                )
                logger.info(f"Episode '{name}' added successfully to graph")

                logger.info(f"Building communities after episode '{name}'")
                await client.build_communities()

                logger.info(f"[BG Task - {group_id_str}] Successfully processed episode '{name}'")
            except Exception as e:
                error_msg = str(e)
                logger.error(
                    f"[BG Task - {group_id_str}] Error processing episode '{name}': {error_msg}"
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
async def add_episode_test(
    name: str,
    episode_body: str,
    group_id: Optional[str] = None,
    source_description: str = '',
    uuid: Optional[str] = None,
) -> Union[SuccessResponse, ErrorResponse]:
    """(Simplified for Testing) Add an episode to the Graphiti knowledge graph.

    This version processes the episode synchronously for debugging.

    Args:
        name (str): Name of the episode
        episode_body (str): The text content of the episode.
        group_id (str, optional): A unique ID for this graph. If not provided, uses the default group_id from CLI
                                 or a generated one.
        source_description (str, optional): Description of the source
        uuid (str, optional): Optional UUID for the episode
    """
    logger.debug(f"Entered add_episode_test (simplified) for '{name}'")
    global graphiti_client, episode_queues, queue_workers

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # Map string source to EpisodeType enum - Simplified: Assume text
        source_type = EpisodeType.text
        logger.debug(f"Using fixed source_type: {source_type}")

        # Use the provided group_id or fall back to the default from config
        effective_group_id = group_id if group_id is not None else config.group_id

        # Cast group_id to str to satisfy type checker
        group_id_str = str(effective_group_id) if effective_group_id is not None else ''
        logger.debug(f"Effective group_id: {group_id_str}")

        assert graphiti_client is not None, 'graphiti_client should not be None here'
        client = cast(Graphiti, graphiti_client)

        # Simplified: Directly use the string input
        episode_body_str = episode_body
        logger.debug(f"Using provided episode_body string (length: {len(episode_body_str)})")

        # Define the episode processing function
        async def process_episode():
            logger.info(f"[Sync Task - {group_id_str}] Starting processing for episode '{name}'") # Changed log prefix
            try:
                # Import here to ensure we get the most up-to-date entity registry
                from entity_types import get_entity_types # Keep get_entity_types import

                # SIMPLIFIED: Determine entity types based only on config flag
                if config.use_custom_entities:
                    entity_types_to_use = get_entity_types() # Use all registered types
                    logger.info(f"Using ALL registered entity types ({len(entity_types_to_use)} types)")
                else:
                    entity_types_to_use = {} # Use no custom types
                    logger.info("Custom entities disabled by config, using empty entity type dictionary")
                
                logger.info(f"Final entity types being used: {list(entity_types_to_use.keys())}")

                await client.add_episode(
                    name=name,
                    episode_body=episode_body_str, # Use the validated string
                    source=source_type, # Use simplified source type
                    source_description=source_description,
                    group_id=group_id_str,
                    uuid=uuid,
                    reference_time=datetime.now(timezone.utc),
                    entity_types=entity_types_to_use, # Pass the simplified set
                )
                logger.info(f"Episode '{name}' added successfully to graph")

                logger.info(f"Building communities after episode '{name}'")
                await client.build_communities()

                logger.info(f"[Sync Task - {group_id_str}] Successfully processed episode '{name}'") # Changed log prefix
            except Exception as e:
                error_msg = str(e)
                logger.error(
                    f"[Sync Task - {group_id_str}] Error processing episode '{name}': {error_msg}" # Changed log prefix
                )
                # Re-raise the exception so the main function catches it for the sync case
                raise

        # --- TEMPORARY SYNC EXECUTION START ---
        # Execute synchronously for debugging.
        logger.debug(f"Executing process_episode synchronously for episode '{name}'")
        await process_episode() # Direct await
        logger.debug(f"Synchronous process_episode finished for episode '{name}'")
        # Return a success message indicating synchronous completion
        return {'message': f"Episode '{name}' processed synchronously."}
        # --- TEMPORARY SYNC EXECUTION END ---

    except Exception as e:
        error_msg = str(e)
        # Log the error originating from the synchronous call or initial setup
        logger.error(f'Error in add_episode_test tool function (sync execution): {error_msg}')
        # Return an error response to the client
        return {'error': f'Error processing episode synchronously: {error_msg}'}


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

    Note: entity is a single entity type to filter results (permitted: "Preference", "Procedure").

    Args:
        query: The search query
        group_ids: Optional list of group IDs to filter results
        max_nodes: Maximum number of nodes to return (default: 10)
        center_node_uuid: Optional UUID of a node to center the search around
        entity: Optional single entity type to filter results (permitted: "Preference", "Procedure")
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


@mcp.tool()
async def clear_graph() -> Union[SuccessResponse, ErrorResponse]:
    """Clear all data from the Graphiti knowledge graph and rebuild indices."""
    global graphiti_client

    if graphiti_client is None:
        return {'error': 'Graphiti client not initialized'}

    try:
        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        # clear_data is already imported at the top
        await clear_data(client.driver)
        await client.build_indices_and_constraints()
        return {'message': 'Graph cleared successfully and indices rebuilt'}
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
        help='Enable entity extraction using the predefined ENTITY_TYPES',
    )
    # Add argument for specifying entity types
    parser.add_argument(
        '--entity-types',
        nargs='+',
        help='Specify which entity types to use (e.g., --entity-types Requirement Preference). '
        'If not provided but --use-custom-entities is set, all registered entity types will be used.',
    )
    # Add argument for custom entity type directory
    parser.add_argument(
        '--entity-type-dir',
        help='Directory containing custom entity type modules to load'
    )
    # Add argument for log level
    parser.add_argument(
        '--log-level',
        choices=['debug', 'info', 'warn', 'error', 'fatal'],
        default=os.environ.get('GRAPHITI_LOG_LEVEL', 'info').lower(),  # Default to ENV or 'info'
        help='Set the logging level.'
    )

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

    # Define the expected path for base entity types within the container
    container_base_entity_dir = "/app/entity_types/base"
    
    # Always load base entity types first
    if os.path.exists(container_base_entity_dir) and os.path.isdir(container_base_entity_dir):
        logger.info(f'Loading base entity types from: {container_base_entity_dir}')
        load_entity_types_from_directory(container_base_entity_dir)
    else:
        logger.warning(f"Base entity types directory not found at: {container_base_entity_dir}")
    
    # Load project-specific entity types if directory is specified and different from base
    if args.entity_type_dir:
        # Resolve paths to handle potential symlinks or relative paths inside container
        abs_project_dir = os.path.abspath(args.entity_type_dir)
        abs_base_dir = os.path.abspath(container_base_entity_dir)
        
        if abs_project_dir != abs_base_dir:
            if os.path.exists(abs_project_dir) and os.path.isdir(abs_project_dir):
                logger.info(f'Loading project-specific entity types from: {abs_project_dir}')
                load_entity_types_from_directory(abs_project_dir)
            else:
                logger.warning(f"Project entity types directory not found or not a directory: {abs_project_dir}")
        else:
            logger.info(f"Project entity directory '{args.entity_type_dir}' is the same as base, skipping redundant load.")

    # Set use_custom_entities flag if specified
    if args.use_custom_entities:
        config.use_custom_entities = True
        logger.info('Entity extraction enabled using predefined ENTITY_TYPES')
    else:
        logger.info('Entity extraction disabled (no custom entities will be used)')
        
    # Store the entity types to use if specified
    if args.entity_types:
        config.entity_type_subset = args.entity_types
        logger.info(f'Using entity types: {", ".join(args.entity_types)}')
    else:
        config.entity_type_subset = None
        if config.use_custom_entities:
            logger.info('Using all registered entity types')
        
    # Log all registered entity types after initialization
    logger.info(f"All registered entity types after initialization: {len(get_entity_types())}")
    for entity_name in get_entity_types().keys():
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


def load_entity_types_from_directory(directory_path: str) -> None:
    """Load all Python modules in the specified directory as entity types.
    
    This function dynamically imports all Python files in the specified directory,
    and automatically registers any Pydantic BaseModel classes that have docstrings.
    No explicit imports or registration calls are needed in the entity type files.
    
    Args:
        directory_path: Path to the directory containing entity type modules
    """
    logger.info(f"Attempting to load entities from directory: {directory_path}")
    directory = Path(directory_path)
    if not directory.exists() or not directory.is_dir():
        logger.warning(f"Entity types directory {directory_path} does not exist or is not a directory")
        return
        
    # Find all Python files in the directory
    python_files = list(directory.glob('*.py'))
    logger.info(f"Found {len(python_files)} Python files in {directory_path}")
    
    for file_path in python_files:
        if file_path.name.startswith('__'):
            continue  # Skip __init__.py and similar files
            
        module_name = file_path.stem
        full_module_path = str(file_path.absolute())
        
        try:
            # Dynamically import the module
            spec = importlib.util.spec_from_file_location(module_name, full_module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Track how many entities were registered from this file
                entities_registered = 0
                
                # Look for BaseModel classes in the module
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    
                    # Check if it's a class and a subclass of BaseModel
                    if (isinstance(attribute, type) and 
                        issubclass(attribute, BaseModel) and 
                        attribute != BaseModel and
                        attribute.__doc__):  # Only consider classes with docstrings
                        
                        # Register the entity type
                        register_entity_type(attribute_name, attribute)
                        entities_registered += 1
                        logger.info(f"Auto-registered entity type: {attribute_name}")
                
                logger.info(f"Successfully loaded entity type module: {module_name} (registered {entities_registered} entities)")
        except Exception as e:
            logger.error(f"Error loading entity type module {module_name}: {str(e)}")
    
    # Log total registered entity types after loading this directory
    logger.info(f"Total registered entity types after loading {directory_path}: {len(get_entity_types())}")
    for entity_name in get_entity_types().keys():
        logger.info(f"  - Registered entity: {entity_name}")


if __name__ == '__main__':
    main()
