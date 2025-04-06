# Standard Operating Procedures

## Git Workflow

All development work (features, fixes, refactoring) MUST be done on a dedicated feature branch created from the `main` branch.

Work MUST be committed incrementally to the feature branch.

Before merging, the work SHOULD be reviewed/verified (details may depend on the task).

Once complete and verified, the feature branch MUST be merged back into the `main` branch.

## Development Logging

Upon successful completion and merging of any significant development task, a development log entry MUST be created.

The process outlined in `agents/orchestrate/playbooks/playbook_development_logging.md` MUST be followed to generate and commit this log entry to the `main` branch.

## Plan Review

For complex or large-scale plans involving multiple agents or significant modifications, the Orchestrator SHOULD first submit the proposed plan to an `analyze` or `ask` agent for review and feedback before presenting it to the user or initiating the first step. The Orchestrator MUST incorporate feedback before finalizing the plan.

## General Workflow Principles

1.  **Define Conventions:** Before generating artifacts (logs, code, documentation), establish and adhere to clear conventions (e.g., naming, storage paths, formats).
2.  **Specify Before Execution:** Synthesize research findings or plans into a clear specification or set of instructions before initiating the main execution step.
3.  **Verify & Iterate:** Verify task outputs against defined objectives, requirements, or specifications. Iterate based on verification results and feedback, refining the approach or output until criteria are met.
4.  **Mode Switching for Content Generation:** Agents generating substantial content (e.g., Markdown, code) SHOULD switch to an appropriate mode (like `code` or `document`) within their task loop. After successful generation, they MUST return only the path to the created file.