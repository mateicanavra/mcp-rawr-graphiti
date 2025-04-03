"""
Functional tests for the Graphiti CLI commands.
These tests invoke the CLI commands through the Typer CliRunner.
"""
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import typer.testing
from typing import List, Dict, Any, Callable

from graphiti_cli.main import app
from constants import LogLevel

# Create a Typer CLI test runner
runner = typer.testing.CliRunner()

class TestBasicCLI:
    """Test basic CLI functionality."""
    
    def test_help(self):
        """Test that the help command works."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        # Check that the description is present
        assert "CLI for managing Graphiti MCP Server" in result.stdout
        # Check that all commands are listed
        assert "Commands:" in result.stdout
        assert "init" in result.stdout
        assert "up" in result.stdout
        assert "down" in result.stdout
    
    def test_missing_command(self):
        """Test behavior with no command (should show help)."""
        result = runner.invoke(app)
        assert result.exit_code == 0
        assert "CLI for managing Graphiti MCP Server" in result.stdout
    
    def test_unknown_command(self):
        """Test behavior with unknown command."""
        result = runner.invoke(app, ["not-a-real-command"])
        assert result.exit_code != 0
        assert "Error: No such command" in result.stdout

class TestDockerCommands:
    """Test Docker-related CLI commands."""
    
    @patch('graphiti_cli.commands.docker_up')
    @patch('graphiti_cli.utils.config.get_repo_root')
    def test_up_command(self, mock_repo_root, mock_docker_up):
        """Test the 'up' command."""
        # Setup mock
        mock_repo_root.return_value = Path("/mock/repo/root")
        
        # Run command
        result = runner.invoke(app, ["up"])
        
        # Verify
        assert result.exit_code == 0
        mock_docker_up.assert_called_once_with(False, LogLevel.info.value)
    
    @patch('graphiti_cli.commands.docker_up')
    @patch('graphiti_cli.utils.config.get_repo_root')
    def test_up_command_with_options(self, mock_repo_root, mock_docker_up):
        """Test the 'up' command with options."""
        # Setup mock
        mock_repo_root.return_value = Path("/mock/repo/root")
        
        # Run command with options
        result = runner.invoke(app, ["up", "--detached", "--log-level", "debug"])
        
        # Verify
        assert result.exit_code == 0
        mock_docker_up.assert_called_once_with(True, LogLevel.debug.value)
    
    @patch('graphiti_cli.commands.docker_down')
    @patch('graphiti_cli.utils.config.get_repo_root')
    def test_down_command(self, mock_repo_root, mock_docker_down):
        """Test the 'down' command."""
        # Setup mock
        mock_repo_root.return_value = Path("/mock/repo/root")
        
        # Run command
        result = runner.invoke(app, ["down"])
        
        # Verify
        assert result.exit_code == 0
        mock_docker_down.assert_called_once_with(LogLevel.info.value)
    
    @patch('graphiti_cli.commands.docker_restart')
    @patch('graphiti_cli.utils.config.get_repo_root')
    def test_restart_command(self, mock_repo_root, mock_docker_restart):
        """Test the 'restart' command."""
        # Setup mock
        mock_repo_root.return_value = Path("/mock/repo/root")
        
        # Run command
        result = runner.invoke(app, ["restart"])
        
        # Verify
        assert result.exit_code == 0
        mock_docker_restart.assert_called_once_with(False, LogLevel.info.value)
    
    @patch('graphiti_cli.commands.docker_reload')
    @patch('graphiti_cli.utils.config.get_repo_root')
    def test_reload_command(self, mock_repo_root, mock_docker_reload):
        """Test the 'reload' command."""
        # Setup mock
        mock_repo_root.return_value = Path("/mock/repo/root")
        
        # Run command with service name
        service_name = "mcp-test-service"
        result = runner.invoke(app, ["reload", service_name])
        
        # Verify
        assert result.exit_code == 0
        mock_docker_reload.assert_called_once_with(service_name)
    
    @patch('graphiti_cli.commands.docker_reload')
    @patch('graphiti_cli.utils.config.get_repo_root')
    def test_reload_command_missing_arg(self, mock_repo_root, mock_docker_reload):
        """Test the 'reload' command with missing service name."""
        # Setup mock
        mock_repo_root.return_value = Path("/mock/repo/root")
        
        # Run command without service name
        result = runner.invoke(app, ["reload"])
        
        # Verify it fails
        assert result.exit_code != 0
        assert "Missing argument" in result.stdout
        mock_docker_reload.assert_not_called()
    
    @patch('graphiti_cli.commands.docker_compose_generate')
    @patch('graphiti_cli.utils.config.get_repo_root')
    def test_compose_command(self, mock_repo_root, mock_docker_compose_generate):
        """Test the 'compose' command."""
        # Setup mock
        mock_repo_root.return_value = Path("/mock/repo/root")
        
        # Run command
        result = runner.invoke(app, ["compose"])
        
        # Verify
        assert result.exit_code == 0
        mock_docker_compose_generate.assert_called_once()

class TestProjectCommands:
    """Test project-related CLI commands."""
    
    @patch('graphiti_cli.commands.init_project')
    @patch('graphiti_cli.utils.config.get_repo_root')
    def test_init_command(self, mock_repo_root, mock_init_project):
        """Test the 'init' command."""
        # Setup mocks
        mock_repo_root.return_value = Path("/mock/repo/root")
        
        # Run command
        project_name = "test-project"
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)
            result = runner.invoke(app, ["init", project_name, str(target_dir)])
            
            # Verify
            assert result.exit_code == 0
            mock_init_project.assert_called_once_with(project_name, target_dir)
    
    @patch('graphiti_cli.commands.create_entity_set')
    @patch('graphiti_cli.utils.config.get_repo_root')
    def test_entity_command(self, mock_repo_root, mock_create_entity_set):
        """Test the 'entity' command."""
        # Setup mocks
        mock_repo_root.return_value = Path("/mock/repo/root")
        
        # Run command
        entity_name = "test-entity"
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)
            # Create necessary structure for validation
            (target_dir / "ai" / "graph").mkdir(parents=True)
            
            result = runner.invoke(app, ["entity", entity_name, str(target_dir)])
            
            # Verify
            assert result.exit_code == 0
            mock_create_entity_set.assert_called_once_with(entity_name, target_dir)
    
    @patch('graphiti_cli.commands.setup_rules')
    @patch('graphiti_cli.utils.config.get_repo_root')
    def test_rules_command(self, mock_repo_root, mock_setup_rules):
        """Test the 'rules' command."""
        # Setup mocks
        mock_repo_root.return_value = Path("/mock/repo/root")
        
        # Run command
        project_name = "test-project"
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir)
            result = runner.invoke(app, ["rules", project_name, str(target_dir)])
            
            # Verify
            assert result.exit_code == 0
            mock_setup_rules.assert_called_once_with(project_name, target_dir)

class TestUtilityCommands:
    """Test utility CLI commands."""
    
    @patch('graphiti_cli.commands.check_setup')
    @patch('graphiti_cli.utils.config.get_repo_root')
    def test_check_setup_command(self, mock_repo_root, mock_check_setup):
        """Test the 'check_setup' command."""
        # Setup mock
        mock_repo_root.return_value = Path("/mock/repo/root")
        
        # Run command
        result = runner.invoke(app, ["check-setup"])
        
        # Verify
        assert result.exit_code == 0
        mock_check_setup.assert_called_once() 