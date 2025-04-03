# Critical Areas for Test Coverage

Based on the codebase and our previous conversations, these are the most critical areas for test coverage:

1. **Docker Command Operations** - High priority due to recent regressions
   - `docker_up`, `docker_down`, `docker_restart`, `docker_reload` functions
   - `ensure_docker_compose_file()` and interaction with compose generation

2. **Compose Generation Logic**
   - YAML handling/merging functionality in `compose_generator.py`
   - Service definitions and volume path generation

3. **Configuration Handling**
   - `get_repo_root()` and config utilities
   - Loading/validation of configuration files (mcp-config.yaml)

4. **CLI Command Interface**
   - Entry points and argument validation
   - Error handling in commands

5. **Environment Setup Verification**
   - `check_setup()` functionality

## Implementation Progress

### ✅ Step 1: Create and Push Feature Branch
- Created branch `feature/setup-testing`
- Pushed branch to remote

### ✅ Step 2: Add Testing Dependencies
- Updated `pyproject.toml` with:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-mock>=3.11.1", 
    "pytest-cov>=4.1.0",
]
```

### ✅ Step 3: Create Test Directory Structure
- Created basic test directory structure:
```
tests/
├── unit/
├── functional/
└── conftest.py
```

### ✅ Step 4: Create Common Test Fixtures
- Created `tests/conftest.py` with:
  - `temp_repo_root` fixture for creating a temporary directory with necessary subdirectories
  - `mock_repo_root` fixture for mocking the repository root

### ✅ Step 5: Create Unit Tests for Docker Module
- Created `tests/unit/test_docker.py` with tests for:
  - `ensure_docker_compose_file()` - tests for file exists, missing, and error cases
  - `docker_up()`, `docker_down()`, `docker_restart()`, `docker_reload()` - verifying correct function calls
  - Added parametrized test for detached mode in `docker_up()`

### ✅ Step 6: Create Unit Tests for Compose Generator
- Created `tests/unit/test_compose_generator.py` with tests for:
  - Basic compose file generation with minimal config
  - Compose generation with projects from registry
  - Error handling for missing base compose file
  - Error handling for invalid base compose structure
  - Error handling for missing custom base anchor
  - Handling of missing projects registry

### ✅ Step 7: Create Unit Tests for Config Utilities
- Created `tests/unit/test_config.py` with tests for:
  - Config path resolution (`get_config_path()`)
  - Config loading/saving operations
  - Repository root detection via various methods (env var, config file, path guessing, user prompt)
  - Error handling for repo root detection

### ✅ Step 8: Create Functional Tests for CLI Commands
- Created `tests/functional/test_cli_commands.py` with tests for:
  - Basic CLI functionality (help, missing command, unknown command)
  - Docker-related commands (`up`, `down`, `restart`, `reload`, `compose`)
  - Project-related commands (`init`, `entity`, `rules`)
  - Utility commands (`check-setup`)
  - Error handling for missing arguments

### ✅ Step 9: Create GitHub Actions Workflow
- Created `.github/workflows/tests.yml` for:
  - Running tests on push and pull requests to main and develop branches
  - Testing on Python 3.10 and 3.11
  - Setting up Python, installing dependencies
  - Running pytest with coverage reports
  - Optional integration with Codecov
  - Basic linting with flake8

### ✅ Step 10: Add Documentation on Running Tests
- Added documentation on how to run tests:
  - Created `tests/README.md` with detailed instructions on test setup, running tests, and writing new tests
  - Added a testing section to the main `README.md` file with basic instructions
  - Included information about the CI workflow and coverage reporting

## Implementation Complete!

All planned steps have been completed successfully. The testing infrastructure is now in place with:

1. **Comprehensive test coverage** for critical areas identified
2. **Test organization** with separate unit and functional test directories
3. **Common test fixtures** for shared testing functionality
4. **GitHub Actions workflow** for continuous integration
5. **Documentation** on running and writing tests

This testing infrastructure will help prevent regressions and ensure the reliability of the Graphiti MCP Server.

## Recommended Testing Approach

Based on your pyproject.toml and codebase structure, I recommend using pytest with the following setup:

```bash
which pytest
```
### 1. Add Testing Dependencies to `pyproject.toml`

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-mock>=3.11.1",
    "pytest-cov>=4.1.0",
]
```

### 2. Test Directory Structure

```
tests/
├── unit/
│   ├── test_docker.py
│   ├── test_compose_generator.py
│   └── test_config.py
├── functional/
│   ├── test_cli_commands.py
│   └── test_docker_integration.py
└── conftest.py
```

### 3. Testing Strategy by Component

#### Docker Module Testing (`test_docker.py`)

```python
import pytest
from unittest.mock import patch, MagicMock
from graphiti_cli.commands import docker

def test_ensure_docker_compose_file_exists(tmp_path):
    """Test that ensure_docker_compose_file works when file exists"""
    with patch('pathlib.Path.is_file', return_value=True):
        with patch('graphiti_cli.utils.config.get_repo_root', return_value=tmp_path):
            # Should not raise or attempt to generate
            docker.ensure_docker_compose_file()

def test_docker_up_regenerates_compose_file():
    """Test that docker_up always regenerates compose file"""
    with patch('graphiti_cli.commands.docker.ensure_dist_for_build') as mock_ensure:
        with patch('graphiti_cli.commands.docker.get_repo_root') as mock_root:
            with patch('graphiti_cli.commands.docker.compose_generator.generate_compose_logic') as mock_gen:
                with patch('graphiti_cli.commands.docker.run_docker_compose') as mock_run:
                    docker.docker_up(detached=True, log_level="info")
                    
                    # Verify compose file was regenerated
                    mock_gen.assert_called_once()
                    # Verify docker compose was called with right args
                    mock_run.assert_called_once()
```

#### Compose Generator Testing (`test_compose_generator.py`)

```python
import pytest
import tempfile
from pathlib import Path
from graphiti_cli.logic import compose_generator

def test_generate_compose_yaml_structure():
    """Test that generated compose YAML has correct structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create minimal config files needed
        # ...setup test files...
        
        # Generate compose file
        compose_generator.generate_compose_logic(tmp_path)
        
        # Verify file exists
        compose_file = tmp_path / "docker-compose.yml"
        assert compose_file.exists()
        
        # Verify content has required sections
        with open(compose_file, 'r') as f:
            content = f.read()
            assert "version:" in content
            assert "services:" in content
            # Verify merge keys are present
            assert "<<:" in content
```

### 4. GitHub Actions CI Workflow

Create `.github/workflows/test.yml`:

```yaml
name: Python Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    - name: Test with pytest
      run: |
        pytest --cov=graphiti_cli tests/
```

### 5. Docker-Specific Testing Approach

For testing Docker operations, I recommend:

1. **Unit tests with mocking**: Test the logic of Docker commands with mocked subprocess calls
2. **Integration tests in CI**: Use Docker-in-Docker in GitHub Actions to test actual Docker operations
3. **Isolated test environments**: Create temporary directories with minimal configs for testing Docker command generation

Example mock pattern for Docker commands:

```python
@pytest.mark.parametrize("detached", [True, False])
def test_docker_up_command_formatting(detached):
    """Test that docker_up generates proper command with/without detached flag"""
    with patch('graphiti_cli.utils.process.run_command') as mock_run:
        docker.docker_up(detached=detached, log_level="info")
        
        # Extract the command that would be run
        cmd_args = mock_run.call_args[0][0]
        
        # Verify command structure
        assert cmd_args[0:2] == ["docker", "compose"]
        assert "up" in cmd_args
        assert "--build" in cmd_args
        
        # Check for -d flag presence based on detached parameter
        if detached:
            assert "-d" in cmd_args
        else:
            assert "-d" not in cmd_args
```

This testing approach balances thoroughness with practicality for your CLI tool and would help prevent the regression issues you've experienced.

Python: Check out the cli-test-helpers package mentioned on StackOverflow for CLI testing
