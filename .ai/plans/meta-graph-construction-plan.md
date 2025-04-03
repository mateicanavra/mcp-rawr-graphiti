# Meta-Graph Entities Implementation Plan

## 1. Overview

**Status: Phase 1, 2, and 3 Completed. Ready for Phase 4.**

1. **Goal:** Implement the 14 Pydantic models defined in `ai/resources/meta-graph-draft.md` within the `entity_types` directory.
2. **Design Guidelines:** Follow the patterns in `ai/resources/entity-design-guidelines.md` and `ai/resources/entity-design-example.md` (using `pydantic.BaseModel`, `Field` with descriptions).

## 2. Target Structure (from `meta-graph-draft.md`)

```
entity_types/
├── actions/
│   └── procedure.py
├── constraints/
│   └── requirement.py
├── interaction/
│   ├── interaction_model.py
│   ├── preference.py
│   └── feedback.py
├── connectors/
│   ├── agent.py
│   ├── project.py
│   ├── resource.py
│   ├── goal.py
│   ├── developer.py
│   └── context_bundle.py
└── resources/
    ├── documentation.py
    ├── artifact.py
    └── tool.py
```

## 3. Existing Structure (`entity_types/`)

Contains `__init__.py`, `entity_registry.py`, and a `base/` directory with `preferences.py`, `procedures.py`, `requirements.py`.

## 4. Registration

`entity_types/entity_registry.py` provides `register_entity_type` for adding models to a central registry.

## 5. Discrepancy

The target structure differs from the existing `base/` directory content.

## 6. Implementation Plan

Here is a step-by-step plan to implement the meta-graph entities:

### Phase 1: Setup and Structure [COMPLETED]

1. **Create Directory Structure:** [COMPLETED]
    - Create the following directories under `entity_types/`:
        - `actions`
        - `constraints`
        - `interaction`
        - `connectors`
        - `resources`
    - Create `__init__.py` files within each of these new directories to mark them as Python packages. [COMPLETED]

### Phase 2: Entity Implementation [COMPLETED]

2. **Implement `actions/procedure.py`:** [COMPLETED]
    - Create the file `entity_types/actions/procedure.py`.
    - Define the `Procedure` Pydantic model as specified in `meta-graph-draft.md`, ensuring imports (`BaseModel`, `Field` from `pydantic`).
3. **Implement `constraints/requirement.py`:** [COMPLETED]
    - Create the file `entity_types/constraints/requirement.py`.
    - Define the `Requirement` Pydantic model.
4. **Implement `interaction` Models:** [COMPLETED]
    - Create `entity_types/interaction/interaction_model.py` and define `InteractionModel`.
    - Create `entity_types/interaction/preference.py` and define `Preference`.
    - Create `entity_types/interaction/feedback.py` and define `Feedback`.
5. **Implement `connectors` Models:** [COMPLETED]
    - Create `entity_types/connectors/agent.py` and define `Agent`.
    - Create `entity_types/connectors/project.py` and define `Project`.
    - Create `entity_types/connectors/resource.py` and define `Resource`.
    - Create `entity_types/connectors/goal.py` and define `Goal`.
    - Create `entity_types/connectors/developer.py` and define `Developer`.
    - Create `entity_types/connectors/context_bundle.py` and define `ContextBundle`.
6. **Implement `resources` Models:** [COMPLETED]
    - Create `entity_types/resources/documentation.py` and define `Documentation`.
    - Create `entity_types/resources/artifact.py` and define `Artifact`.
    - Create `entity_types/resources/tool.py` and define `Tool`.

### Phase 3: Registration [COMPLETED]

7. **Centralize Imports and Registration:** [COMPLETED]
    - Modify `entity_types/__init__.py`.
    - Import all 14 newly defined entity models from their respective modules (`actions.procedure`, `constraints.requirement`, etc.).
    - Import `register_entity_type` from `.entity_registry`.
    - Call `register_entity_type` for each imported model, using a suitable string name (e.g., `"Procedure"`, `"Requirement"`). Consider using the class name (`Model.__name__`) as the key for consistency.
    - Ensure the existing exports (`register_entity_type`, `get_entity_types`, `get_entity_type_subset`) are maintained.

### Phase 4: Cleanup and Verification [PENDING]

8. **Address Existing `base/` Directory:**
    - **Decision Point:** Determine the fate of `entity_types/base/preferences.py`, `procedures.py`, and `requirements.py`.
        - **Option A (Replace):** If the new models in `interaction/`, `actions/`, `constraints/` fully supersede these, delete the `base/` directory and its contents.
        - **Option B (Refactor/Merge):** If the existing files contain valuable logic or variations, refactor them to fit the new structure or merge their functionality.
        - **Option C (Defer):** Leave the `base/` directory for now and create a follow-up task to reconcile it.
    - *(This plan assumes Option C for now, leaving cleanup as a separate task).*

9. **Linting and Type Checking:**
    - Run appropriate linting (e.g., `ruff`, `flake8`) and type checking (e.g., `mypy`) tools over the `entity_types` directory to ensure code quality and correctness. Fix any reported issues.

## 7. Acceptance Criteria

- All 14 entity types from `meta-graph-draft.md` are implemented as Pydantic models in the specified directory structure under `entity_types/`.
- Each model file includes necessary imports and follows the design guidelines.
- All 14 models are successfully registered upon importing the `entity_types` package.
- Calling `get_entity_types()` after import returns a dictionary containing all 14 registered types.
- The code passes configured linting and type checking rules.
- The existing files in `entity_types/base/` are consciously addressed (even if deferred).

## 8. Potential Risks/Dependencies

- **Pydantic Version:** Ensure compatibility with the project's Pydantic version.
- **Naming Conflicts:** Ensure the chosen registration names (e.g., `"Procedure"`) don't conflict with other existing or future types. Using `Model.__name__` mitigates this.
- **Circular Dependencies:** Avoid creating circular import dependencies between entity modules during registration setup. Centralizing registration in `entity_types/__init__.py` should help prevent this.
- **Cleanup Complexity:** Reconciling the old `base/` directory might be more complex than initially anticipated (Risk associated with Deferral - Option C).