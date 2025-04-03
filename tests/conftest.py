"""
Common test fixtures and configuration for pytest.
"""
import os
import sys
import tempfile
from pathlib import Path
import pytest

# Add the repository root to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def temp_repo_root():
    """
    Create a temporary directory simulating a repository root.
    This provides an isolated environment for tests that need to write files.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create any necessary subdirectories that would exist in a real repo
        (tmp_path / "ai" / "graph").mkdir(parents=True, exist_ok=True)
        (tmp_path / "entity_types" / "base").mkdir(parents=True, exist_ok=True)
        
        original_dir = os.getcwd()
        os.chdir(tmp_path)  # Change to temp dir for duration of test
        
        yield tmp_path
        
        os.chdir(original_dir)  # Change back to original dir

@pytest.fixture
def mock_repo_root(monkeypatch):
    """
    Mock the repo root without creating actual directories.
    Useful for unit tests that only need to patch the get_repo_root function.
    """
    mock_path = Path("/mock/repo/root")
    
    def mock_get_repo_root():
        return mock_path
    
    # Patch the get_repo_root function
    monkeypatch.setattr("graphiti_cli.utils.config.get_repo_root", mock_get_repo_root)
    
    return mock_path 