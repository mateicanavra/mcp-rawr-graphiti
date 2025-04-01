Okay, let's refine the architecture proposal for migrating the `graphiti` Bash script to Python, integrating existing Python helpers (`_yaml_helper.py`, `generate_compose.py`), and ensuring it aligns well with your current setup.

We'll aim for a clean, maintainable Python CLI tool using **Typer** for the interface, **ruamel.yaml** for config file handling (as already established), and standard Python libraries (`subprocess`, `pathlib`, `os`, `shutil`) for orchestration.

**Consolidation Strategy:**

1.  **Integrate YAML Logic:** The core logic from `generate_compose.py` (@LINE:1-191) and `_yaml_helper.py` (@LINE:1-111) will be moved into functions within a dedicated `yaml_utils.py` module as part of the new CLI tool package. This eliminates executing them as separate scripts.
2.  **Retain Server Logic:** `graphiti_mcp_server.py` (@LINE:1-780) remains the server application. Its `argparse` logic handles arguments passed _inside_ the container (via `entrypoint.sh`). The new Python CLI tool will _not_ replicate this internal server argument parsing; it focuses on orchestrating Docker and project setup from the host.
3.  **Entity Registry:** `entity_registry.py` (@LINE:1-41) remains part of the server's domain, used during entity loading within the server runtime. The CLI tool doesn't interact with it directly.

**Proposed Python CLI Architecture:**

1.  **New Package Structure (Example):**
    We'll create a dedicated package for the CLI tool. This could live at the repository root or within the existing `scripts/` directory. Let's assume we create `graphiti_cli/` at the root for clarity.

    ```
    mcp-graphiti/
    ├── mcp_server/
    │   ├── entity_types/
    │   ├── rules/
    │   ├── Dockerfile
    │   ├── entrypoint.sh
    │   ├── base-compose.yaml
    │   ├── mcp-projects.yaml
    │   ├── docker-compose.yml  # (Generated)
    │   ├── graphiti_mcp_server.py
    │   ├── entity_registry.py
    │   └── ... (other server files)
    ├── graphiti_cli/           # <--- NEW CLI Package
    │   ├── __init__.py
    │   ├── main.py             # Typer app definition, command entry points
    │   ├── core.py             # Core logic: finding paths, running subprocesses
    │   ├── commands.py         # Command implementations (init, up, down, etc.)
    │   └── yaml_utils.py       # Integrated YAML handling logic
    ├── pyproject.toml          # <--- Modified
    ├── .env.example
    └── ... (other repo files)
    ```

2.  **`pyproject.toml` Modifications:**
    Update your main `pyproject.toml` (@LINE:1-16) (or create one at the root if it doesn't exist there) to include the CLI tool dependencies and define the script entry point.

    ```toml
    # pyproject.toml

    [build-system]
    requires = ["setuptools>=61.0"]
    build-backend = "setuptools.build_meta"

    [project]
    name = "graphiti-mcp-tools" # Name for the installable package containing the CLI
    version = "0.1.0" # Consider syncing with server version or managing independently
    description = "CLI Tools for Graphiti MCP Server Management"
    readme = "README.md"
    requires-python = ">=3.10"
    dependencies = [
        # CLI specific dependencies:
        "typer[all]>=0.9.0", # [all] includes rich for better tracebacks/output
        "ruamel.yaml>=0.17.21",
        "python-dotenv>=1.0.0", # Useful for potentially reading .env in CLI too
        # Add other CLI-specific needs here
    ]
    # Note: Dependencies for the *server* itself (mcp, openai, graphiti-core)
    # might be listed here if you install both server and CLI from the same
    # pyproject.toml, or they could remain separate if the server has its own.
    # For simplicity now, assuming they might be installed together.
    # If separating, remove server deps from here.

    [project.scripts]
    # This makes the 'graphiti' command available after 'pip install .'
    graphiti = "graphiti_cli.main:app"
    ```

    _(Self-correction: Added `build-system` section for modern packaging)_

3.  **`graphiti_cli/main.py` (Entry Point & Typer App):**

    ```python
    # graphiti_cli/main.py
    import typer
    from pathlib import Path
    from typing_extensions import Annotated # Preferred for Typer >= 0.9

    # Import command functions and core utilities
    from . import commands
    from .core import LogLevel, get_repo_root

    # Initialize Typer app
    app = typer.Typer(
        help="CLI for managing Graphiti MCP Server projects and Docker environment.",
        no_args_is_help=True, # Show help if no command is given
        rich_markup_mode="markdown" # Nicer help text formatting
    )

    # --- Callback to ensure repo path is found early ---
    @app.callback()
    def main_callback(ctx: typer.Context):
        """
        Main callback to perform setup before any command runs.
        Ensures the MCP_GRAPHITI_REPO_PATH is found.
        """
        # Ensure repo root is detected/set early.
        # get_repo_root() will print messages and exit if not found.
        _ = get_repo_root()


    # --- Define Commands (delegating to functions in commands.py) ---

    @app.command()
    def init(
        project_name: Annotated[str, typer.Argument(help="Name of the target project.")],
        target_dir: Annotated[Path, typer.Argument(
            ".", # Default to current directory
            help="Target project root directory.",
            exists=False, # Allow creating the directory
            file_okay=False,
            dir_okay=True,
            writable=True,
            resolve_path=True # Convert to absolute path
        )] = Path(".")
    ):
        """
        Initialize a project: create ai/graph structure with config, entities dir, and rules. ✨
        """
        commands.init_project(project_name, target_dir)

    @app.command()
    def entity(
        set_name: Annotated[str, typer.Argument(help="Name for the new entity type set (e.g., 'my-entities').")],
        target_dir: Annotated[Path, typer.Argument(
            ".",
            help="Target project root directory containing ai/graph/mcp-config.yaml.",
            exists=True, # Must exist for entity creation
            file_okay=False,
            dir_okay=True,
            resolve_path=True
        )] = Path(".")
    ):
        """
        Create a new entity type set directory and template file within a project's ai/graph/entities directory. 📄
        """
        commands.create_entity_set(set_name, target_dir)

    @app.command()
    def rules(
        project_name: Annotated[str, typer.Argument(help="Name of the target project for rule setup.")],
        target_dir: Annotated[Path, typer.Argument(
            ".",
            help="Target project root directory.",
            exists=True, # Must exist for rules setup
            file_okay=False,
            dir_okay=True,
            resolve_path=True
        )] = Path(".")
    ):
        """
        Setup/update Cursor rules symlinks and schema template for a project. 🔗
        """
        commands.setup_rules(project_name, target_dir)

    @app.command()
    def up(
        detached: Annotated[bool, typer.Option("--detached", "-d", help="Run containers in detached mode.")] = False,
        log_level: Annotated[LogLevel, typer.Option("--log-level", help="Set logging level for containers.", case_sensitive=False)] = LogLevel.info
    ):
        """
        Start all containers using Docker Compose (builds first). 🚀
        """
        commands.docker_up(detached, log_level.value)

    @app.command()
    def down(
        log_level: Annotated[LogLevel, typer.Option("--log-level", help="Set logging level for Docker Compose execution.", case_sensitive=False)] = LogLevel.info
    ):
        """
        Stop and remove all containers using Docker Compose. 🛑
        """
        commands.docker_down(log_level.value)

    @app.command()
    def restart(
        detached: Annotated[bool, typer.Option("--detached", "-d", help="Run 'up' in detached mode after 'down'.")] = False,
        log_level: Annotated[LogLevel, typer.Option("--log-level", help="Set logging level for containers.", case_sensitive=False)] = LogLevel.info
    ):
        """
        Restart all containers: runs 'down' then 'up'. 🔄
        """
        commands.docker_restart(detached, log_level.value)

    @app.command()
    def reload(
        service_name: Annotated[str, typer.Argument(help="Name of the service to reload (e.g., 'mcp-test-project-1-main').")]
    ):
        """
        Restart a specific running service container. ⚡
        """
        commands.docker_reload(service_name)

    @app.command()
    def compose():
        """
        Generate docker-compose.yml from base and project configs. ⚙️
        """
        commands.docker_compose_generate()


    # Allow running the script directly for development/testing
    if __name__ == "__main__":
        app()
    ```

    _(Self-correction: Using `Annotated` for Typer arguments/options as it's the modern approach. Added `no_args_is_help=True`. Added emojis for fun.)_

4.  **`graphiti_cli/core.py` (Core Utilities):**
    (Similar to the previous proposal, containing `get_repo_root`, `get_mcp_server_dir`, `run_command`, `LogLevel` enum, ANSI colors, etc. No major changes needed here from the previous draft.)

5.  **`graphiti_cli/yaml_utils.py` (Consolidated YAML Logic):**

    ```python
    # graphiti_cli/yaml_utils.py
    import sys
    from pathlib import Path
    from ruamel.yaml import YAML
    from ruamel.yaml.comments import CommentedMap
    import os
    from typing import Optional, List, Dict, Any

    from .core import get_mcp_server_dir, CONTAINER_ENTITY_PATH, DEFAULT_PORT_START, DEFAULT_MCP_CONTAINER_PORT_VAR # Import constants

    # --- YAML Instances ---
    yaml_rt = YAML() # Round-Trip for preserving structure/comments
    yaml_rt.preserve_quotes = True
    yaml_rt.indent(mapping=2, sequence=4, offset=2)

    yaml_safe = YAML(typ='safe') # Safe loader for reading untrusted/simple config

    # --- File Handling ---
    def load_yaml_file(file_path: Path, safe: bool = False) -> Optional[Any]:
        """Loads a YAML file, handling errors."""
        yaml_loader = yaml_safe if safe else yaml_rt
        if not file_path.is_file():
            print(f"Warning: YAML file not found or is not a file: {file_path}")
            return None
        try:
            with file_path.open('r') as f:
                return yaml_loader.load(f)
        except Exception as e:
            print(f"Error parsing YAML file '{file_path}': {e}")
            return None # Or raise specific exception

    def write_yaml_file(data: Any, file_path: Path, header: Optional[List[str]] = None):
         """Writes data to a YAML file using round-trip dumper."""
         try:
             # Ensure parent directory exists
             file_path.parent.mkdir(parents=True, exist_ok=True)
             with file_path.open('w') as f:
                 if header:
                     f.write("\n".join(header) + "\n\n") # Add extra newline
                 yaml_rt.dump(data, f)
         except IOError as e:
             print(f"Error writing YAML file '{file_path}': {e}")
             raise # Re-raise after printing
         except Exception as e:
             print(f"An unexpected error occurred during YAML dumping to '{file_path}': {e}")
             raise

    # --- Logic from _yaml_helper.py ---
    def update_registry_logic(
        registry_file: Path,
        project_name: str,
        root_dir: Path, # Expecting resolved absolute path
        config_file: Path, # Expecting resolved absolute path
        enabled: bool = True
    ) -> bool:
        """
        Updates the central project registry file (mcp-projects.yaml).
        Corresponds to the logic in the old _yaml_helper.py.
        """
        print(f"Updating registry '{registry_file}' for project '{project_name}'")
        if not root_dir.is_absolute() or not config_file.is_absolute():
             print("Error: Project root_dir and config_file must be absolute paths.")
             return False

        if not config_file.exists():
             print(f"Warning: Project config file '{config_file}' does not exist.")
             # Allow continuing for init scenarios

        # Create registry file with header if it doesn't exist
        if not registry_file.exists():
            print(f"Creating new registry file: {registry_file}")
            header = [
                "# !! WARNING: This file is managed by the 'graphiti init' command. !!",
                "# !! Avoid manual edits unless absolutely necessary.                 !!",
                "#",
                "# Maps project names to their configuration details.",
                "# Paths should be absolute for reliability.",
            ]
            initial_data = CommentedMap({'projects': CommentedMap()})
            try:
                write_yaml_file(initial_data, registry_file, header=header)
            except Exception:
                 return False # Error handled in write_yaml_file

        # Load existing registry data using round-trip loader
        data = load_yaml_file(registry_file, safe=False)
        if data is None:
             print(f"Error: Could not load registry file {registry_file}")
             return False

        if not isinstance(data, dict) or 'projects' not in data:
            print(f"Error: Invalid registry file format in {registry_file}. Missing 'projects' key.")
            return False

        # Ensure 'projects' key exists and is a map
        if data.get('projects') is None:
             data['projects'] = CommentedMap()
        elif not isinstance(data['projects'], dict):
              print(f"Error: 'projects' key in {registry_file} is not a dictionary.")
              return False


        # Add or update the project entry (convert Paths to strings for YAML)
        project_entry = CommentedMap({
            'root_dir': str(root_dir),
            'config_file': str(config_file),
            'enabled': enabled
        })
        data['projects'][project_name] = project_entry

        # Write back to the registry file
        try:
            # Preserve header by reading first few lines if necessary (complex)
            # Simpler: Assume header is managed manually or re-added if file recreated.
            # We rewrite the whole file here.
            write_yaml_file(data, registry_file)
            print(f"Successfully updated registry for project '{project_name}'")
            return True
        except Exception:
             return False # Error handled in write_yaml_file


    # --- Logic from generate_compose.py ---
    def generate_compose_logic(mcp_server_dir: Path):
        """
        Generates the final docker-compose.yml by merging base and project configs.
        Corresponds to the logic in the old generate_compose.py.
        """
        print("Generating docker-compose.yml...")
        base_compose_path = mcp_server_dir / 'base-compose.yaml'
        projects_registry_path = mcp_server_dir / 'mcp-projects.yaml'
        output_compose_path = mcp_server_dir / 'docker-compose.yml'

        # Load base compose file
        compose_data = load_yaml_file(base_compose_path, safe=False)
        if compose_data is None or not isinstance(compose_data, dict):
            print(f"Error: Failed to load or parse base compose file: {base_compose_path}")
            sys.exit(1)

        if 'services' not in compose_data or not isinstance(compose_data.get('services'), dict):
            print(f"Error: Invalid structure in '{base_compose_path}'. Missing 'services' dictionary.")
            sys.exit(1)

        # Load project registry safely
        projects_registry = load_yaml_file(projects_registry_path, safe=True)
        if projects_registry is None:
            print(f"Warning: Project registry file '{projects_registry_path}' not found or failed to parse. No custom services will be added.")
            projects_registry = {'projects': {}}
        elif 'projects' not in projects_registry or not isinstance(projects_registry['projects'], dict):
            print(f"Warning: Invalid format or missing 'projects' key in '{projects_registry_path}'. No custom services will be added.")
            projects_registry = {'projects': {}}

        # --- Generate Custom Service Definitions ---
        services_map = compose_data['services'] # Should be CommentedMap

        # Find the anchor object for merging
        custom_base_anchor_obj = compose_data.get('x-graphiti-mcp-custom-base')
        if not custom_base_anchor_obj:
            print(f"{RED}Error: Could not find 'x-graphiti-mcp-custom-base' definition in {base_compose_path}.{NC}")
            sys.exit(1)

        overall_service_index = 0
        # Iterate through projects from the registry
        for project_name, project_data in projects_registry.get('projects', {}).items():
            if not isinstance(project_data, dict) or not project_data.get('enabled', False):
                continue # Skip disabled or invalid projects

            project_config_path_str = project_data.get('config_file')
            project_root_dir_str = project_data.get('root_dir')

            if not project_config_path_str or not project_root_dir_str:
                print(f"Warning: Skipping project '{project_name}' due to missing 'config_file' or 'root_dir'.")
                continue

            project_config_path = Path(project_config_path_str)
            project_root_dir = Path(project_root_dir_str)

            # Load the project's specific mcp-config.yaml
            project_config = load_yaml_file(project_config_path, safe=True)
            if project_config is None:
                print(f"Warning: Skipping project '{project_name}' because config file '{project_config_path}' could not be loaded.")
                continue

            if 'services' not in project_config or not isinstance(project_config['services'], list):
                print(f"Warning: Skipping project '{project_name}' due to missing or invalid 'services' list in '{project_config_path}'.")
                continue

            # Iterate through services defined in the project's config
            for server_conf in project_config['services']:
                if not isinstance(server_conf, dict):
                    print(f"Warning: Skipping invalid service entry in '{project_config_path}': {server_conf}")
                    continue

                server_id = server_conf.get('id')
                entity_type_dir = server_conf.get('entity_dir') # Relative path within project

                if not server_id or not entity_type_dir:
                    print(f"Warning: Skipping service in '{project_name}' due to missing 'id' or 'entity_dir': {server_conf}")
                    continue

                # --- Determine Service Configuration ---
                service_name = f"mcp-{server_id}"
                container_name = server_conf.get('container_name', service_name) # Default to service_name
                port_default = server_conf.get('port_default', DEFAULT_PORT_START + overall_service_index + 1)
                port_mapping = f"{port_default}:${{{DEFAULT_MCP_CONTAINER_PORT_VAR}}}" # Use f-string

                # --- Build Service Definition using CommentedMap ---
                new_service = CommentedMap()
                # Add the merge key first using the anchor object
                new_service.add_yaml_merge([(0, custom_base_anchor_obj)]) # Merge base config

                new_service['container_name'] = container_name
                new_service['ports'] = [port_mapping] # Ports must be a list

                # --- Environment Variables ---
                env_vars = CommentedMap() # Use CommentedMap to preserve order if needed
                mcp_group_id = server_conf.get('group_id', project_name) # Default group_id to project_name
                env_vars['MCP_GROUP_ID'] = mcp_group_id
                env_vars['MCP_USE_CUSTOM_ENTITIES'] = 'true' # Assume true if defined here

                # Calculate absolute host path for entity volume mount
                abs_host_entity_path = (project_root_dir / entity_type_dir).resolve()
                if not abs_host_entity_path.is_dir():
                     print(f"Warning: Entity directory '{abs_host_entity_path}' for service '{service_name}' does not exist. Volume mount might fail.")
                     # Continue anyway, Docker will create an empty dir inside container if host path doesn't exist

                # Set container path for entity directory env var
                env_vars['MCP_ENTITY_TYPE_DIR'] = CONTAINER_ENTITY_PATH

                # Add project-specific environment variables from mcp-config.yaml
                project_environment = server_conf.get('environment', {})
                if isinstance(project_environment, dict):
                     env_vars.update(project_environment)
                else:
                     print(f"Warning: Invalid 'environment' section for service '{service_name}' in '{project_config_path}'. Expected a dictionary.")

                new_service['environment'] = env_vars

                # --- Volumes ---
                # Ensure volumes list exists (might be added by anchor merge, check needed?)
                # setdefault is safer if anchor doesn't guarantee 'volumes'
                if 'volumes' not in new_service:
                     new_service['volumes'] = []
                elif not isinstance(new_service['volumes'], list):
                     print(f"Warning: 'volumes' merged from anchor for service '{service_name}' is not a list. Overwriting.")
                     new_service['volumes'] = []

                # Append the entity volume mount (read-only)
                new_service['volumes'].append(f"{abs_host_entity_path}:{CONTAINER_ENTITY_PATH}:ro")

                # --- Add to Services Map ---
                services_map[service_name] = new_service
                overall_service_index += 1

        # --- Write Output File ---
        header = [
            "# Generated by graphiti CLI",
            "# Do not edit this file directly. Modify base-compose.yaml or project-specific mcp-config.yaml files instead.",
            "",
            "# --- Custom MCP Services Info ---",
            f"# Default Ports: Assigned sequentially starting from {DEFAULT_PORT_START + 1}",
            "#              Can be overridden by specifying 'port_default' in project's mcp-config.yaml.",
        ]
        try:
            write_yaml_file(compose_data, output_compose_path, header=header)
            print(f"Successfully generated '{output_compose_path}'.")
        except Exception:
            # Error already printed by write_yaml_file
             sys.exit(1)

    ```

    _(Self-correction: Added explicit checks for file existence and type before loading YAML. Ensured paths passed to `update_registry_logic` are absolute. Handled potential non-existence of 'volumes' key after merge. Defaulted `group_id` to `project_name`.)_

6.  **`graphiti_cli/commands.py` (Command Implementations):**
    (This file contains the actual logic called by `main.py`. It imports helpers from `core.py` and `yaml_utils.py`).

        ```python
        # graphiti_cli/commands.py
        import sys
        import shutil
        from pathlib import Path
        import os
        import re # For entity name validation

        from . import core
        from . import yaml_utils

        # --- Docker Commands ---

        def docker_up(detached: bool, log_level: str):
        	core.ensure_docker_compose_file()
        	core.ensure_dist_for_build()
        	cmd = ["up", "--build", "--force-recreate"]
        	core.run_docker_compose(cmd, log_level, detached)
        	print(f"{core.GREEN}Docker compose up completed.{core.NC}")

        def docker_down(log_level: str):
        	core.ensure_docker_compose_file() # Needed for compose to find project
        	core.run_docker_compose(["down"], log_level)
        	print(f"{core.GREEN}Docker compose down completed.{core.NC}")

        def docker_restart(detached: bool, log_level: str):
        	print(f"{core.BOLD}Restarting Graphiti containers: first down, then up...{core.NC}")
        	docker_down(log_level) # Run down first
        	docker_up(detached, log_level) # Then run up
        	print(f"{core.GREEN}Restart sequence completed.{core.NC}")

        def docker_reload(service_name: str):
        	core.ensure_docker_compose_file()
        	print(f"{core.BOLD}Attempting to restart service '{core.CYAN}{service_name}{core.NC}'...{core.NC}")
        	try:
        		# Use check=True to let run_command handle the error printing on failure
        		core.run_docker_compose(["restart", service_name], check=True)
        		print(f"{core.GREEN}Service '{service_name}' restarted successfully.{core.NC}")
        	except SystemExit: # run_command exits on error if check=True
        		# Error message already printed by run_command via CalledProcessError handling
        		print(f"{core.RED}Failed to restart service '{service_name}'. Check service name and if stack is running.{core.NC}")
        		# No need to exit again, run_command already did

        def docker_compose_generate():
        	print(f"{core.BOLD}Generating docker-compose.yml from templates...{core.NC}")
        	mcp_server_dir = core.get_mcp_server_dir()
        	try:
        		yaml_utils.generate_compose_logic(mcp_server_dir)
        		# Success message printed within generate_compose_logic
        	except Exception as e:
        		print(f"{core.RED}Error: Failed to generate docker-compose.yml file: {e}{core.NC}")
        		sys.exit(1)

        # --- Project/File Management Commands ---

        def init_project(project_name: str, target_dir: Path):
            """
            Initialize a Graphiti project.

            Args:
                project_name (str): Name of the project
                target_dir (Path): Target directory for the project
            """
            # Basic validation
            if not re.fullmatch(r'^[a-zA-Z0-9_-]+$', project_name):
                print(f"{core.RED}Error: Invalid PROJECT_NAME '{project_name}'. Use only letters, numbers, underscores, and hyphens.{core.NC}")
                sys.exit(1)

            print(f"Initializing Graphiti project '{core.CYAN}{project_name}{core.NC}' in '{core.CYAN}{target_dir}{core.NC}'...")

            # Create ai/graph directory structure
            graph_dir = target_dir / "ai" / "graph"
            try:
                graph_dir.mkdir(parents=True, exist_ok=True)
                print(f"Created directory structure: {core.CYAN}{graph_dir}{core.NC}")
            except OSError as e:
                print(f"{core.RED}Error creating directory structure {graph_dir}: {e}{core.NC}")
                sys.exit(1)

            # Create mcp-config.yaml in ai/graph directory
            config_path = graph_dir / "mcp-config.yaml"
            config_content = f"""# Configuration for project: {project_name}

    services:
      - id: {project_name}-main  # Service ID (used for default naming) # container_name: "custom-name" # Optional: Specify custom container name # port_default: 8001 # Optional: Specify custom host port
        group_id: "{project_name}"  # Graph group ID
        entity_dir: "entities"  # Relative path to entity definitions within ai/graph # environment: # Optional: Add non-secret env vars here # MY_FLAG: "true"
    """
    try:
    target_dir.mkdir(parents=True, exist_ok=True) # Ensure target dir exists
    config_path.write_text(config_content)
    print(f"Created template {core.CYAN}{config_path}{core.NC}")
    except OSError as e:
    print(f"{core.RED}Error creating config file {config_path}: {e}{core.NC}")
    sys.exit(1)

            # Create entities directory within ai/graph
            entities_dir = graph_dir / "entities"
            try:
                entities_dir.mkdir(exist_ok=True)
                (entities_dir / ".gitkeep").touch(exist_ok=True) # Create or update timestamp
                print(f"Created entities directory: {core.CYAN}{entities_dir}{core.NC}")
            except OSError as e:
                print(f"{core.RED}Error creating entities directory {entities_dir}: {e}{core.NC}")
                sys.exit(1)

            # Set up rules
            setup_rules(project_name, target_dir) # Call the rules setup logic

            # Update central registry
            mcp_server_dir = core.get_mcp_server_dir()
            registry_path = mcp_server_dir / "mcp-projects.yaml"
            print(f"Updating central project registry: {core.CYAN}{registry_path}{core.NC}")
            try:
                # Ensure paths are absolute before passing
                success = yaml_utils.update_registry_logic(
                    registry_file=registry_path,
                    project_name=project_name,
                    root_dir=target_dir.resolve(),
                    config_file=config_path.resolve(),
                    enabled=True
                )
                if not success:
                    print(f"{core.RED}Error: Failed to update project registry (see previous errors).{core.NC}")
                    sys.exit(1)
            except Exception as e:
                print(f"{core.RED}Error updating project registry: {e}{core.NC}")
                sys.exit(1)

            print(f"{core.GREEN}Graphiti project '{project_name}' initialization complete.{core.NC}")


        def setup_rules(project_name: str, target_dir: Path):
        	"""Sets up the .cursor/rules directory and symlinks."""
        	print(f"Setting up Graphiti Cursor rules for project '{core.CYAN}{project_name}{core.NC}' in {core.CYAN}{target_dir}{core.NC}")
        	mcp_server_dir = core.get_mcp_server_dir()
        	rules_source_dir = mcp_server_dir / "rules"
        	templates_source_dir = rules_source_dir / "templates"
        	cursor_rules_dir = target_dir / ".cursor" / "rules" / "graphiti"

        	try:
        		cursor_rules_dir.mkdir(parents=True, exist_ok=True)
        		print(f"Created/verified rules directory: {core.CYAN}{cursor_rules_dir}{core.NC}")

        		core_rule_src = rules_source_dir / "graphiti-mcp-core-rules.md"
        		maint_rule_src = rules_source_dir / "graphiti-knowledge-graph-maintenance.md"
        		schema_template_src = templates_source_dir / "project_schema_template.md"

        		core_rule_link = cursor_rules_dir / "graphiti-mcp-core-rules.mdc"
        		maint_rule_link = cursor_rules_dir / "graphiti-knowledge-graph-maintenance.mdc"
        		target_schema_file = cursor_rules_dir / f"graphiti-{project_name}-schema.mdc"

        		# Check source files
        		missing_files = []
        		if not core_rule_src.is_file(): missing_files.append(core_rule_src)
        		if not maint_rule_src.is_file(): missing_files.append(maint_rule_src)
        		if not schema_template_src.is_file(): missing_files.append(schema_template_src)
        		if missing_files:
        			print(f"{core.RED}Error: Source rule/template files not found:{core.NC}")
        			for f in missing_files: print(f"  - {f}")
        			sys.exit(1)

        		# Create/Update symlinks using relative paths for better portability
        		try:
        			core_rel_path = os.path.relpath(core_rule_src.resolve(), start=cursor_rules_dir.resolve())
        			maint_rel_path = os.path.relpath(maint_rule_src.resolve(), start=cursor_rules_dir.resolve())
        		except ValueError:
        			# Handle case where paths are on different drives (Windows) - fall back to absolute
        			print(f"{core.YELLOW}Warning: Cannot create relative symlink paths (different drives?). Using absolute paths.{core.NC}")
        			core_rel_path = core_rule_src.resolve()
        			maint_rel_path = maint_rule_src.resolve()

        		# Unlink if it exists and is not the correct link target
        		if core_rule_link.is_symlink():
        			if core_rule_link.readlink() != Path(core_rel_path):
        				core_rule_link.unlink()
        		elif core_rule_link.exists(): # It exists but isn't a symlink
        			core_rule_link.unlink()

        		if not core_rule_link.exists():
        			core_rule_link.symlink_to(core_rel_path)
        			print(f"Linking core rule: {core.CYAN}{core_rule_link.name}{core.NC} -> {core.CYAN}{core_rel_path}{core.NC}")
        		else:
        			print(f"Core rule link already exists: {core.CYAN}{core_rule_link.name}{core.NC}")


        		if maint_rule_link.is_symlink():
        			if maint_rule_link.readlink() != Path(maint_rel_path):
        				maint_rule_link.unlink()
        		elif maint_rule_link.exists():
        			maint_rule_link.unlink()

        		if not maint_rule_link.exists():
        			maint_rule_link.symlink_to(maint_rel_path)
        			print(f"Linking maintenance rule: {core.CYAN}{maint_rule_link.name}{core.NC} -> {core.CYAN}{maint_rel_path}{core.NC}")
        		else:
        			print(f"Maintenance rule link already exists: {core.CYAN}{maint_rule_link.name}{core.NC}")

        		# Generate schema file from template
        		if target_schema_file.exists():
        			print(f"{core.YELLOW}Warning: Project schema file already exists, skipping template generation: {target_schema_file}{core.NC}")
        		else:
        			print(f"Generating template project schema file: {core.CYAN}{target_schema_file}{core.NC}")
        			template_content = schema_template_src.read_text()
        			schema_content = template_content.replace("__PROJECT_NAME__", project_name)
        			target_schema_file.write_text(schema_content)

        		print(f"{core.GREEN}Graphiti Cursor rules setup complete for project '{project_name}'.{core.NC}")

        	except OSError as e:
        		print(f"{core.RED}Error setting up rules: {e}{core.NC}")
        		sys.exit(1)
        	except Exception as e:
        		print(f"{core.RED}An unexpected error occurred during rule setup: {e}{core.NC}")
        		sys.exit(1)


        def _to_pascal_case(snake_str: str) -> str:
        	"""Converts snake_case or kebab-case to PascalCase."""
        	parts = re.split('_|-', snake_str)
        	return "".join(part.capitalize() for part in parts)

        def create_entity_set(set_name: str, target_dir: Path):
            """Creates a new directory and example entity file for an entity set within a project's ai/graph directory."""
            # Validate SET_NAME format
            if not re.fullmatch(r'^[a-zA-Z0-9_-]+$', set_name):
                print(f"{core.RED}Error: Invalid SET_NAME '{set_name}'. Use only letters, numbers, underscores, and hyphens.{core.NC}")
                sys.exit(1)

            # Load project configuration from ai/graph directory
            graph_dir = target_dir / "ai" / "graph"
            config_path = graph_dir / "mcp-config.yaml"
            if not config_path.is_file():
                print(f"{core.RED}Error: Project configuration file not found: {config_path}{core.NC}")
                print(f"Make sure the project has been initialized with 'graphiti init' first.")
                sys.exit(1)

            project_config = yaml_utils.load_yaml_file(config_path, safe=True)
            if project_config is None:
                print(f"{core.RED}Error: Failed to load project configuration from: {config_path}{core.NC}")
                sys.exit(1)

            # Validate project config structure
            if 'services' not in project_config or not isinstance(project_config['services'], list) or not project_config['services']:
                print(f"{core.RED}Error: Invalid or missing 'services' section in project configuration: {config_path}{core.NC}")
                sys.exit(1)

            # Extract the entity directory name from the first service entry
            entity_dir_name = project_config.get('services', [{}])[0].get('entity_dir', 'entities')

            # Calculate paths - use graph_dir as base
            project_entity_base_dir = graph_dir / entity_dir_name
            new_set_dir = project_entity_base_dir / set_name

            if new_set_dir.exists():
                print(f"{core.RED}Error: Entity type set '{set_name}' already exists at: {new_set_dir}{core.NC}")
                sys.exit(1)

            try:
                new_set_dir.mkdir(parents=True)
                print(f"Created entity type set directory: {core.CYAN}{new_set_dir}{core.NC}")

                class_name = _to_pascal_case(set_name) + "Entity" # Add suffix convention
                # Use set_name for lowercase replacements, class_name for class definition
                entity_file_path = new_set_dir / f"{class_name}.py" # Name file after class

                if not example_template_path.is_file():
                    print(f"{core.YELLOW}Warning: Template file not found: {example_template_path}{core.NC}")
                    print("Creating a minimal entity file instead.")
                    minimal_content = f"""from pydantic import BaseModel, Field

        class {class_name}(BaseModel):
        	\"\"\"Example entity for the '{set_name}' set.\"\"\"

        	example_field: str = Field(
        		...,
        		description='An example field.',
        	)
        """
                    entity_file_path.write_text(minimal_content)
                else:
                    template_content = example_template_path.read_text()
                    # Perform replacements carefully
                    content = template_content.replace("class Product(BaseModel):", f"class {class_name}(BaseModel):")
                    # Replace descriptions, trying to be specific
                    content = content.replace("A Product represents", f"A {class_name} represents")
                    content = content.replace("about Products mentioned", f"about {class_name} entities mentioned")
                    content = content.replace("product names", f"{set_name} names")
                    content = content.replace("the product belongs", f"the {set_name} belongs")
                    content = content.replace("description of the product", f"description of the {set_name}")
                    # Add more replacements if needed based on the template content

                    entity_file_path.write_text(content)
                    print(f"Created entity file using template: {core.CYAN}{entity_file_path}{core.NC}")

                print(f"{core.GREEN}Entity set '{set_name}' successfully created.{core.NC}")

            except OSError as e:
                print(f"{core.RED}Error creating entity set '{set_name}': {e}{core.NC}")
                sys.exit(1)
            except Exception as e:
                print(f"{core.RED}An unexpected error occurred creating entity set '{set_name}': {e}{core.NC}")
                sys.exit(1)

        ```

This completes the `commands.py` file, providing the implementation logic for all the commands defined in `main.py`. Each function orchestrates the necessary steps, calling helpers from `core.py` for process execution and path management, and `yaml_utils.py` for configuration file handling. Error handling is included using `try...except` blocks and checking subprocess results.
