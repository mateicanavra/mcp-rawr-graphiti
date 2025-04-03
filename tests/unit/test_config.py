"""
Unit tests for the config module functionality.
Tests the repository root detection and configuration handling.
"""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from graphiti_cli.utils import config
from constants import (
    ENV_REPO_PATH,
    FILE_PYPROJECT_TOML,
    DIR_ENTITIES,
)

class TestConfigPaths:
    """Tests for configuration path handling."""
    
    def test_get_config_path(self):
        """Test that get_config_path returns the correct path."""
        with patch('pathlib.Path.home', return_value=Path('/mock/home')):
            config_path = config.get_config_path()
            assert config_path == Path('/mock/home/.config/graphiti/repo_path.txt')

class TestConfigOperations:
    """Tests for config file operations."""
    
    def test_load_config_exists(self):
        """Test loading config when the file exists."""
        mock_path = '/mock/home/.config/graphiti/repo_path.txt'
        mock_repo_path = '/mock/repo/path'
        
        with patch('graphiti_cli.utils.config.get_config_path', return_value=Path(mock_path)):
            with patch('pathlib.Path.is_file', return_value=True):
                with patch('builtins.open', mock_open(read_data=f"{mock_repo_path}\n")):
                    result = config.load_config()
                    assert result == mock_repo_path
    
    def test_load_config_not_exists(self):
        """Test loading config when the file doesn't exist."""
        with patch('graphiti_cli.utils.config.get_config_path', return_value=Path('/nonexistent/path')):
            with patch('pathlib.Path.is_file', return_value=False):
                result = config.load_config()
                assert result is None
    
    def test_load_config_error(self):
        """Test loading config when there's an error."""
        with patch('graphiti_cli.utils.config.get_config_path', return_value=Path('/mock/path')):
            with patch('pathlib.Path.is_file', return_value=True):
                with patch('builtins.open', side_effect=Exception("Test error")):
                    result = config.load_config()
                    assert result is None
    
    def test_save_config(self):
        """Test saving config to file."""
        mock_path = '/mock/home/.config/graphiti/repo_path.txt'
        mock_repo_path = '/mock/repo/path'
        
        with patch('graphiti_cli.utils.config.get_config_path', return_value=Path(mock_path)):
            with patch('pathlib.Path.parent.mkdir') as mock_mkdir:
                with patch('builtins.open', mock_open()) as mock_file:
                    config.save_config(mock_repo_path)
                    
                    # Verify directory was created
                    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
                    
                    # Verify file was written with correct content
                    mock_file.assert_called_once_with(Path(mock_path), 'w')
                    mock_file().write.assert_called_once_with(f"{mock_repo_path}\n")

class TestRepoRootDetection:
    """Tests for repository root detection."""
    
    def setup_method(self):
        """Set up test environment variables."""
        # Save original environment
        self.original_env = os.environ.copy()
    
    def teardown_method(self):
        """Restore environment variables."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_get_repo_root_env_var(self):
        """Test repo root detection using environment variable."""
        mock_path = '/mock/repo/path'
        os.environ[ENV_REPO_PATH] = mock_path
        
        # Mock validation to return True
        with patch('graphiti_cli.utils.paths._validate_repo_path', return_value=True):
            result = config._find_repo_root()
            assert result == Path(mock_path).resolve()
    
    def test_get_repo_root_config_file(self):
        """Test repo root detection using config file."""
        # Remove env var if exists
        if ENV_REPO_PATH in os.environ:
            del os.environ[ENV_REPO_PATH]
        
        mock_path = '/mock/repo/path'
        
        # Mock validation to return False for env var path (in case it exists)
        # but True for config file path
        with patch('graphiti_cli.utils.config._get_validated_path_from_config', return_value=Path(mock_path)):
            result = config._find_repo_root()
            assert result == Path(mock_path)
    
    def test_get_repo_root_from_relative_path(self):
        """Test repo root detection using relative path guessing."""
        # Remove env var if exists
        if ENV_REPO_PATH in os.environ:
            del os.environ[ENV_REPO_PATH]
        
        # Mock config file to return None
        with patch('graphiti_cli.utils.config._get_validated_path_from_config', return_value=None):
            # Mock __file__ resolution
            mock_file_path = Path('/mock/repo/path/graphiti_cli/utils/config.py')
            mock_repo_path = Path('/mock/repo/path')
            
            with patch('pathlib.Path.resolve', return_value=mock_file_path):
                # Mock validation to return True for the guessed path
                with patch('graphiti_cli.utils.paths._validate_repo_path') as mock_validate:
                    def validate_side_effect(path):
                        return path == mock_repo_path
                    
                    mock_validate.side_effect = validate_side_effect
                    
                    with patch('pathlib.Path.parents', new_callable=MagicMock) as mock_parents:
                        # Setup mock_parents to return [parent0, parent1, parent2]
                        # where parent1 is our repo root
                        mock_parents.__getitem__.return_value = mock_repo_path
                        
                        result = config._find_repo_root()
                        assert result == mock_repo_path
    
    def test_get_repo_root_prompt(self):
        """Test repo root detection using user prompt."""
        # Remove env var if exists
        if ENV_REPO_PATH in os.environ:
            del os.environ[ENV_REPO_PATH]
        
        # Mock config file to return None
        with patch('graphiti_cli.utils.config._get_validated_path_from_config', return_value=None):
            # Mock all guessing methods to fail
            with patch('pathlib.Path.__init__', side_effect=Exception("No __file__")):
                with patch('pathlib.Path.cwd', return_value=Path('/mock/cwd')):
                    # Mock validation to return False for guessed paths
                    with patch('graphiti_cli.utils.paths._validate_repo_path', return_value=False):
                        # Mock prompt to return a path
                        mock_prompt_path = Path('/mock/prompt/path')
                        with patch('graphiti_cli.utils.config._prompt_and_save_repo_path', return_value=mock_prompt_path):
                            result = config._find_repo_root()
                            assert result == mock_prompt_path
    
    def test_get_repo_root_fail(self):
        """Test repo root detection failure with sys.exit."""
        # Remove env var if exists
        if ENV_REPO_PATH in os.environ:
            del os.environ[ENV_REPO_PATH]
        
        # Mock config file to return None
        with patch('graphiti_cli.utils.config._get_validated_path_from_config', return_value=None):
            # Mock all guessing methods to fail
            with patch('pathlib.Path.__init__', side_effect=Exception("No __file__")):
                with patch('pathlib.Path.cwd', return_value=Path('/mock/cwd')):
                    # Mock validation to return False for guessed paths
                    with patch('graphiti_cli.utils.paths._validate_repo_path', return_value=False):
                        # Mock prompt to return None (user cancelled)
                        with patch('graphiti_cli.utils.config._prompt_and_save_repo_path', return_value=None):
                            with pytest.raises(SystemExit):
                                config.get_repo_root()

    def test_validate_path_from_config(self):
        """Test _get_validated_path_from_config with valid path."""
        mock_path = '/mock/repo/path'
        
        with patch('graphiti_cli.utils.config.load_config', return_value=mock_path):
            with patch('graphiti_cli.utils.paths._validate_repo_path', return_value=True):
                result = config._get_validated_path_from_config()
                assert result == Path(mock_path).resolve()
    
    def test_validate_path_from_config_invalid(self):
        """Test _get_validated_path_from_config with invalid path."""
        mock_path = '/mock/repo/path'
        
        with patch('graphiti_cli.utils.config.load_config', return_value=mock_path):
            with patch('graphiti_cli.utils.paths._validate_repo_path', return_value=False):
                result = config._get_validated_path_from_config()
                assert result is None 