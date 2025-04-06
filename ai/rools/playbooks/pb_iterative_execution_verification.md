# Playbook: Iterative Execution & Verification

**Purpose:** To reliably execute complex tasks involving modifications by incorporating structured planning, execution, verification, and feedback-driven iteration loops.

**Key Roles (Generic):**
*   **Orchestrator:** Manages the process, dispatches agents, interprets results, guides iteration.
*   **Planner (Optional/Implicit):** Defines the initial strategy.
*   **Executor:** Performs the core modification tasks *as defined by the plan or instructions*.
*   **Verifier:** Assesses the Executor's work against *the defined objective, requirements, and/or quality standards*.
*   **Feedback Source (Optional):** Provides input on plans or results.

**Workflow Steps:**
1.  **Initiation & Planning:** Define objective, formulate plan (optional plan review for robustness).
2.  **Execution:** Dispatch Executor agent to perform planned actions.
3.  **Verification:** Dispatch Verifier agent to assess results *against defined criteria* and report findings.
4.  **Evaluation & Decision:** Orchestrator/User evaluates verification report.
    *   If Success -> Proceed to Step 6 (Completion).
    *   If Issues -> Proceed to Step 5 (Iteration).
5.  **Iteration Loop:**
    *   Synthesize feedback *and verification findings* into corrective instructions.
    *   Dispatch Executor for revision.
    *   Return to Step 3 (Verification).
6.  **Completion:** Orchestrator confirms successful task completion.

This pattern provides a structured approach for tasks requiring modification and quality assurance through iterative refinement.