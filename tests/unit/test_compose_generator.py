"""
Unit tests for the compose_generator module.
Tests the Docker Compose file generation functionality.
"""
import os
import sys
import pytest
from pathlib import Path
import tempfile
from unittest.mock import patch, MagicMock, mock_open
import json

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap

from graphiti_cli.logic import compose_generator
from constants import (
    BASE_COMPOSE_FILENAME,
    PROJECTS_REGISTRY_FILENAME,
    DOCKER_COMPOSE_OUTPUT_FILENAME,
    COMPOSE_SERVICES_KEY,
    COMPOSE_CUSTOM_BASE_ANCHOR_KEY,
    COMPOSE_VOLUMES_KEY
)

# Sample YAML for testing
BASE_COMPOSE_YAML = """
version: '3.8'
x-graphiti-mcp-custom-base: &graphiti-mcp-custom-base
  image: some-registry/graphiti-mcp:latest
  environment:
    MCP_PORT: 3000
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:3000/health"]

services:
  mcp-root:
    <<: *graphiti-mcp-custom-base
    container_name: graphiti-mcp-root
    ports:
      - "8000:${MCP_PORT}"
    volumes:
      - ./entity_types:/app/entity_types:ro
"""

PROJECTS_REGISTRY_YAML = """
projects:
  test-project:
    enabled: true
    root_dir: /mock/project/dir
path/to/your/project/ai/graph/mcp-config.yaml
"""

PROJECT_CONFIG_YAML = """
services:
  - id: test-project-1-main
    entity_dir: entities
    port_default: 8001
    group_id: test-project-1-graph
    environment:
      TEST_ENV_VAR: "test-value"
"""

class TestComposeGenerator:
    """Test cases for compose_generator module."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create mock files
        self.base_compose_path = self.temp_path / BASE_COMPOSE_FILENAME
        self.projects_registry_path = self.temp_path / PROJECTS_REGISTRY_FILENAME
        self.output_compose_path = self.temp_path / DOCKER_COMPOSE_OUTPUT_FILENAME
        
        # Write base compose file
        with open(self.base_compose_path, 'w') as f:
            f.write(BASE_COMPOSE_YAML)
        
        # Write projects registry file
        with open(self.projects_registry_path, 'w') as f:
            f.write(PROJECTS_REGISTRY_YAML)
    
    def teardown_method(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    @patch('graphiti_cli.logic.compose_generator.load_yaml_file')
    @patch('graphiti_cli.logic.compose_generator.write_yaml_file')
    def test_generate_compose_logic_basic(self, mock_write, mock_load):
        """Test basic compose file generation with minimal config."""
        # Setup mock data
        yaml = ruamel.yaml.YAML()
        base_compose_data = yaml.load(BASE_COMPOSE_YAML)
        
        projects_registry = {
            'projects': {}  # Empty registry for this test
        }
        
        # Configure mocks
        def mock_load_side_effect(path, safe=False):
            if str(path).endswith(BASE_COMPOSE_FILENAME):
                return base_compose_data
            elif str(path).endswith(PROJECTS_REGISTRY_FILENAME):
                return projects_registry
            return None
        
        mock_load.side_effect = mock_load_side_effect
        
        # Call the function
        compose_generator.generate_compose_logic(self.temp_path)
        
        # Verify the write_yaml_file was called
        mock_write.assert_called_once()
        
        # Verify the compose_data passed to write_yaml_file
        write_args = mock_write.call_args[0]
        compose_data = write_args[0]
        output_path = write_args[1]
        
        # Check basic structure
        assert COMPOSE_SERVICES_KEY in compose_data
        assert 'mcp-root' in compose_data[COMPOSE_SERVICES_KEY]
        assert output_path == self.temp_path / DOCKER_COMPOSE_OUTPUT_FILENAME
    
    @patch('graphiti_cli.logic.compose_generator.load_yaml_file')
    @patch('graphiti_cli.logic.compose_generator.write_yaml_file')
    @patch('graphiti_cli.logic.compose_generator.update_cursor_mcp_json')
    def test_generate_compose_with_projects(self, mock_update_cursor, mock_write, mock_load):
        """Test compose generation with projects from registry."""
        # Setup mock data
        yaml = ruamel.yaml.YAML()
        base_compose_data = yaml.load(BASE_COMPOSE_YAML)
        
        projects_registry = yaml.load(PROJECTS_REGISTRY_YAML)
        project_config = yaml.load(PROJECT_CONFIG_YAML)
        
        # Configure mocks
        def mock_load_side_effect(path, safe=False):
            path_str = str(path)
            if BASE_COMPOSE_FILENAME in path_str:
                return base_compose_data
            elif PROJECTS_REGISTRY_FILENAME in path_str:
                return projects_registry
            elif "mcp-config.yaml" in path_str:
                return project_config
            return None
        
        mock_load.side_effect = mock_load_side_effect
        
        # Create mock project directory structure
        project_dir = Path("/mock/project/dir")
        project_entities_dir = project_dir / "ai" / "graph" / "entities"
        
        with patch('pathlib.Path.is_dir', return_value=True):
            with patch('pathlib.Path.resolve', return_value=project_entities_dir):
                # Call the function
                compose_generator.generate_compose_logic(self.temp_path)
        
        # Verify update_cursor_mcp_json was called
        mock_update_cursor.assert_called_once()
        assert mock_update_cursor.call_args[0][1] == "test-project-1-main"  # server_id
        assert mock_update_cursor.call_args[0][2] == 8001  # port
        
        # Verify the write_yaml_file was called
        mock_write.assert_called_once()
        
        # Verify the compose_data passed to write_yaml_file
        write_args = mock_write.call_args[0]
        compose_data = write_args[0]
        
        # Check for project service
        assert "mcp-test-project-1-main" in compose_data[COMPOSE_SERVICES_KEY]
        
        # Check service configuration
        service = compose_data[COMPOSE_SERVICES_KEY]["mcp-test-project-1-main"]
        assert service["container_name"] == "mcp-test-project-1-main"
        assert service["ports"] == ["8001:${MCP_PORT}"]
        assert "environment" in service
        assert service["environment"]["MCP_GROUP_ID"] == "test-project-1-graph"
        assert service["environment"]["TEST_ENV_VAR"] == "test-value"
        
        # Check volumes
        assert COMPOSE_VOLUMES_KEY in service
    
    @patch('graphiti_cli.logic.compose_generator.load_yaml_file')
    def test_missing_base_compose_file(self, mock_load):
        """Test error handling when base compose file is missing."""
        mock_load.return_value = None  # Simulate missing file
        
        with pytest.raises(SystemExit):
            compose_generator.generate_compose_logic(self.temp_path)
    
    @patch('graphiti_cli.logic.compose_generator.load_yaml_file')
    def test_invalid_base_compose_structure(self, mock_load):
        """Test error handling when base compose file has invalid structure."""
        mock_load.return_value = {"wrong_key": {}}  # Missing services key
        
        with pytest.raises(SystemExit):
            compose_generator.generate_compose_logic(self.temp_path)
    
    @patch('graphiti_cli.logic.compose_generator.load_yaml_file')
    def test_missing_custom_base_anchor(self, mock_load):
        """Test error handling when custom base anchor is missing."""
        # Setup mock data without the anchor
        yaml = ruamel.yaml.YAML()
        base_compose_data = yaml.load(BASE_COMPOSE_YAML)
        del base_compose_data[COMPOSE_CUSTOM_BASE_ANCHOR_KEY]
        
        mock_load.return_value = base_compose_data
        
        with pytest.raises(SystemExit):
            compose_generator.generate_compose_logic(self.temp_path)
    
    @patch('graphiti_cli.logic.compose_generator.load_yaml_file')
    @patch('graphiti_cli.logic.compose_generator.write_yaml_file')
    def test_missing_projects_registry(self, mock_write, mock_load):
        """Test handling when projects registry file is missing."""
        # Setup mock data
        yaml = ruamel.yaml.YAML()
        base_compose_data = yaml.load(BASE_COMPOSE_YAML)
        
        # Configure mocks
        def mock_load_side_effect(path, safe=False):
            if str(path).endswith(BASE_COMPOSE_FILENAME):
                return base_compose_data
            elif str(path).endswith(PROJECTS_REGISTRY_FILENAME):
                return None  # Simulate missing registry
            return None
        
        mock_load.side_effect = mock_load_side_effect
        
        # Call should not fail when registry is missing
        compose_generator.generate_compose_logic(self.temp_path)
        
        # Verify the compose_data passed to write_yaml_file only has base services
        mock_write.assert_called_once()
        write_args = mock_write.call_args[0]
        compose_data = write_args[0]
        
        # Only base services should exist
        assert len(compose_data[COMPOSE_SERVICES_KEY]) == 1
        assert "mcp-root" in compose_data[COMPOSE_SERVICES_KEY] 