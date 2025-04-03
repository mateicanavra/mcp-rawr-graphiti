# Graphiti MCP Server Testing

This directory contains tests for the Graphiti MCP Server project.

## Test Structure

The tests are organized as follows:

```
tests/
├── unit/             # Unit tests for individual modules
│   ├── test_docker.py
│   ├── test_compose_generator.py
│   └── test_config.py
├── functional/       # Functional tests for CLI commands
│   └── test_cli_commands.py
├── conftest.py       # Shared test fixtures
└── README.md         # This file
```

## Setup and Installation

To run the tests, you'll need to install the development dependencies:

```bash
# Install the package with development dependencies
pip install -e ".[dev]"
```

## Running Tests

### Running All Tests

To run all tests:

```bash
pytest
```

### Running Unit Tests Only

To run only the unit tests:

```bash
pytest tests/unit/
```

### Running Functional Tests Only

To run only the functional tests:

```bash
pytest tests/functional/
```

### Running Specific Test Files

To run tests from a specific file:

```bash
pytest tests/unit/test_docker.py
```

### Running Specific Test Functions

To run a specific test function:

```bash
pytest tests/unit/test_docker.py::TestDockerCommands::test_docker_up_regenerates_compose_file
```

## Running Tests with Coverage

To run tests with coverage reporting:

```bash
# Run tests with coverage
pytest --cov=graphiti_cli

# Generate HTML coverage report
pytest --cov=graphiti_cli --cov-report=html
```

After running with HTML coverage reporting, open `htmlcov/index.html` in your browser to view the coverage details.

## Continuous Integration

This project uses GitHub Actions to automatically run tests on each push and pull request.

The workflow is defined in `.github/workflows/tests.yml` and includes:

- Testing on multiple Python versions (3.10, 3.11)
- Code coverage reporting
- Basic linting with flake8

## Writing New Tests

When adding new features or fixing bugs, please add appropriate tests:

1. **Unit Tests:** For testing individual functions and classes in isolation
   - Place in the `tests/unit/` directory
   - Focus on a single module or functionality
   - Use mocks to avoid external dependencies

2. **Functional Tests:** For testing CLI commands and end-to-end functionality
   - Place in the `tests/functional/` directory
   - Test the CLI interface using the Typer test client
   - Focus on user-facing functionality

3. **Fixtures:** For reusable test components
   - Place in `conftest.py` if they should be available to all tests
   - Place in test module if only needed for that module

### Mocking Guidelines

- Use `unittest.mock.patch` for mocking functions and methods
- Use `pytest-mock` fixtures for simpler mocking when appropriate
- Mock at the appropriate level (usually the boundary of the unit being tested)
- Use `mock_repo_root` fixture for tests that need a repository root path 