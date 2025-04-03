"""
Unit tests for the Docker command operations in the graphiti_cli.
"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

from graphiti_cli.commands import docker
from constants import LogLevel

class TestDockerComposeFile:
    """Tests related to docker-compose.yml file generation and management."""

    def test_ensure_docker_compose_file_exists(self, mock_repo_root):
        """Test that ensure_docker_compose_file skips generation when file exists."""
        with patch('pathlib.Path.is_file', return_value=True):
            with patch('graphiti_cli.logic.compose_generator.generate_compose_logic') as mock_gen:
                docker.ensure_docker_compose_file()
                
                # Should not try to generate the file if it exists
                mock_gen.assert_not_called()

    def test_ensure_docker_compose_file_missing(self, mock_repo_root):
        """Test that ensure_docker_compose_file generates when file is missing."""
        with patch('pathlib.Path.is_file', return_value=False):
            with patch('graphiti_cli.logic.compose_generator.generate_compose_logic') as mock_gen:
                docker.ensure_docker_compose_file()
                
                # Should generate the file when missing
                mock_gen.assert_called_once_with(mock_repo_root)
    
    def test_ensure_docker_compose_file_error(self, mock_repo_root):
        """Test that ensure_docker_compose_file handles errors appropriately."""
        with patch('pathlib.Path.is_file', return_value=False):
            with patch('graphiti_cli.logic.compose_generator.generate_compose_logic') as mock_gen:
                mock_gen.side_effect = Exception("Test error")
                
                # Should exit on error
                with pytest.raises(SystemExit):
                    docker.ensure_docker_compose_file()

class TestDockerCommands:
    """Tests for the Docker command functions."""
    
    def test_docker_up_regenerates_compose_file(self, mock_repo_root):
        """Test that docker_up always regenerates compose file."""
        with patch('graphiti_cli.commands.docker.ensure_dist_for_build') as mock_ensure:
            with patch('graphiti_cli.commands.docker.compose_generator.generate_compose_logic') as mock_gen:
                with patch('graphiti_cli.commands.docker.run_docker_compose') as mock_run:
                    docker.docker_up(detached=True, log_level=LogLevel.info.value)
                    
                    # Verify compose file was regenerated
                    mock_gen.assert_called_once_with(mock_repo_root)
                    # Verify docker compose was called
                    mock_run.assert_called_once()
    
    def test_docker_down(self, mock_repo_root):
        """Test that docker_down calls run_docker_compose with correct args."""
        with patch('graphiti_cli.commands.docker.ensure_docker_compose_file') as mock_ensure:
            with patch('graphiti_cli.commands.docker.run_docker_compose') as mock_run:
                docker.docker_down(log_level=LogLevel.info.value)
                
                # Should call ensure_docker_compose_file
                mock_ensure.assert_called_once()
                # Should call run_docker_compose with ["down"]
                mock_run.assert_called_once_with(["down"], LogLevel.info.value)
    
    def test_docker_restart(self, mock_repo_root):
        """Test that docker_restart calls docker_down then docker_up."""
        with patch('graphiti_cli.commands.docker.run_docker_compose') as mock_run:
            with patch('graphiti_cli.commands.docker.docker_up') as mock_up:
                docker.docker_restart(detached=True, log_level=LogLevel.info.value)
                
                # Should call run_docker_compose with ["down"]
                mock_run.assert_called_once_with(["down"], LogLevel.info.value)
                # Should call docker_up with detached and log_level
                mock_up.assert_called_once_with(True, LogLevel.info.value)
    
    @pytest.mark.parametrize("detached", [True, False])
    def test_docker_up_command_formatting(self, mock_repo_root, detached):
        """Test that docker_up generates proper command with/without detached flag."""
        with patch('graphiti_cli.commands.docker.ensure_dist_for_build'):
            with patch('graphiti_cli.commands.docker.compose_generator.generate_compose_logic'):
                with patch('graphiti_cli.utils.process.run_command') as mock_run:
                    docker.docker_up(detached=detached, log_level=LogLevel.info.value)
                    
                    # Check that run_command was called at all
                    mock_run.assert_called()
                    
                    # With our current mocking strategy, we can't easily check
                    # the precise command arguments. We'd need to refactor run_docker_compose
                    # to return the command rather than execute it, or use a more sophisticated
                    # mocking approach to capture the arguments to run_command.
    
    def test_docker_reload(self, mock_repo_root):
        """Test that docker_reload regenerates compose file and restarts service."""
        service_name = "test-service"
        
        with patch('graphiti_cli.commands.docker.ensure_docker_compose_file') as mock_ensure:
            with patch('graphiti_cli.commands.docker.compose_generator.generate_compose_logic') as mock_gen:
                with patch('graphiti_cli.commands.docker.run_docker_compose') as mock_run:
                    docker.docker_reload(service_name)
                    
                    # Should ensure docker-compose file exists
                    mock_ensure.assert_called_once()
                    # Should regenerate compose file
                    mock_gen.assert_called_once_with(mock_repo_root)
                    # Should call run_docker_compose with ["restart", service_name]
                    mock_run.assert_called_once()
                    assert mock_run.call_args[0][0] == ["restart", service_name] 