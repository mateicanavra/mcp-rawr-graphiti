# Playbook: Discovery-Driven Execution

## Purpose

This playbook outlines a generic workflow for tasks where execution depends on first understanding external systems, APIs, file formats, or conventions. It emphasizes a research-driven approach to ensure successful task completion when faced with initial unknowns.

## Key Roles

*   **Researcher:** Gathers information about unknown conventions/constraints. Employs `search`, `read_file`, etc.
*   **Analyzer:** Synthesizes research findings into a clear execution specification.
*   **Executor:** Performs the task according to the derived specification. Employs `code`, `implement`, etc.
*   **Verifier:** Assesses results against the objective *and* the derived specification. Employs `review`, `test`.

## Workflow Steps

1.  **Initiation & Planning:**
    *   Define the objective of the task.
    *   Identify potential unknowns regarding the execution method or conventions.
2.  **Research/Discovery:**
    *   Dispatch Researcher agent(s) to gather information about the unknown conventions/constraints.
    *   Utilize tools like `search`, `read_file`, etc., to explore external systems, APIs, file formats, or conventions.
3.  **Analysis & Specification:**
    *   Dispatch Analyzer agent(s) to synthesize research findings into a clear execution specification.
    *   Define the required format, API calls, file paths, or any other relevant details for successful execution.
4.  **Execution:**
    *   Dispatch Executor agent(s) to perform the task *according to the derived specification*.
    *   Ensure the execution adheres to the identified conventions and constraints.
5.  **Verification:**
    *   Dispatch Verifier agent(s) to assess the results against the objective *and* the derived specification.
    *   Check for adherence to the defined format, API calls, file paths, etc.
6.  **Iteration Loop:**
    *   If verification fails, analyze the reasons for failure.
    *   Refine understanding/specification (back to Research or Analysis) or execution.
    *   Re-verify the results.
7.  **Completion:**
    *   Confirm successful task completion based on the objective and the derived specification.