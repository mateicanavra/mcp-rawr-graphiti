# Public Repository Preparation Plan: mcp-rawr-graphiti

**Date:** 2025-04-04

## 1. Summary of Findings

The codebase review identified several issues requiring attention before public release. The most critical issues involve hardcoded secrets (Neo4j password, OpenAI API key) in the `.env` file, which must be removed and the file excluded from the repository history if previously committed. Major issues include hardcoded absolute file paths in configuration (`docker-compose.yml`, `mcp-projects.yaml`) and documentation/examples (`README.md`, `CONFIGURATION.md`, generated files), hindering portability. Minor issues involve potential PII exposure (`tools@matei.work` email in Git history) and less critical absolute path usage in tests and the virtual environment (`.venv`). The project structure, dependency management, and general naming conventions are good, but standard repository files like `LICENSE` and `CONTRIBUTING.md` appear to be missing.

## 2. Prioritized Remediation Plan

### Critical Issues (Highest Priority)

1.  **Issue:** Hardcoded Neo4j Password in `.env`
    *   **Location:** `.env` @LINE:7
    *   **Action:**
        *   Verify `.env` is listed in `.gitignore`.
        *   If `.env` was ever committed, remove it from the Git history using appropriate tools (e.g., `git filter-repo` or BFG Repo-Cleaner). **Caution:** Rewriting history is destructive.
        *   Ensure developers rely solely on `.env.example` for setup guidance and manage their own `.env` files locally.
2.  **Issue:** Hardcoded OpenAI API Key in `.env`
    *   **Location:** `.env` @LINE:11
    *   **Action:**
        *   Verify `.env` is listed in `.gitignore`.
        *   If `.env` was ever committed, remove it from the Git history (see caution above).
        *   **Immediately revoke the exposed OpenAI API key (`sk-proj-gRW...`) and generate a new one.**
        *   Ensure developers manage their keys locally via their `.env` file.

### Major Issues (Medium Priority)

1.  **Issue:** Hardcoded Absolute Paths in Configuration Files
    *   **Locations:** `docker-compose.yml` (@LINE:119, @LINE:133), `mcp-projects.yaml` (@LINE:16, @LINE:18, @LINE:21, @LINE:23)
    *   **Action:**
        *   Refactor configurations to use relative paths (e.g., `./data` instead of `/Users/mateicanavra/.../data`) or environment variables defined in `.env.example` (e.g., `${PROJECT_DATA_DIR:-./data}`).
        *   Update `CONFIGURATION.md` and any related documentation/examples to reflect the new configuration method.
2.  **Issue:** Hardcoded Absolute Paths in Documentation/Examples
    *   **Locations:** `README.md` (@LINE:93, @LINE:105), `CONFIGURATION.md` (@LINE:23, @LINE:24, @LINE:27, @LINE:28), `rawr_mcp_graphiti.egg-info/PKG-INFO` (generated), `rawr-mcp-graphiti-repo.md` (@LINE:4351, @LINE:4363)
    *   **Action:**
        *   Replace specific user paths (e.g., `/Users/mateicanavra/...`, `/Users/your_user/...`) in `README.md` and `CONFIGURATION.md` examples with generic placeholders like `/path/to/your/project`, `<your-data-directory>`, or relative paths (e.g., `data/`).
        *   Ensure changes to `README.md` (and potentially `pyproject.toml` description) propagate to generated files like `PKG-INFO` upon the next build.
        *   Review the purpose of `rawr-mcp-graphiti-repo.md`. If it's a generated artifact or outdated, consider removing it or updating its generation process. If necessary, update paths within it.

### Minor Issues (Lowest Priority)

1.  **Issue:** PII (Email Address) in Git Commit History
    *   **Location:** `.git/logs/` (affecting commit history)
    *   **Content:** `tools@matei.work`
    *   **Action:**
        *   **Confirm Sensitivity:** Determine if the `tools@matei.work` email address is considered sensitive or if its public exposure is acceptable.
        *   **If Sensitive:** Choose a remediation strategy:
            *   **(Recommended if feasible):** Squash commits on feature branches before merging into the main public branch to consolidate history under a desired author/email.
            *   **(Use with extreme caution):** Use tools like `git filter-repo` to rewrite the entire repository history, replacing the email address. This is complex and can cause issues for collaborators.
        *   **If Not Sensitive:** Document this decision and accept the exposure.
2.  **Issue:** Hardcoded Absolute Paths in Test Examples
    *   **Locations:** `tests/unit/test_config.py` (@LINE:25, @LINE:32, @LINE:58)
    *   **Action:** (Low priority) Consider refactoring tests during future maintenance to use `pathlib`, relative paths, or pytest fixtures like `tmp_path` for creating test files/directories instead of potentially brittle absolute paths like `/mock/home/...`. No immediate action required.
3.  **Issue:** Absolute Paths in `.venv`
    *   **Location:** Various files within `.venv/`
    *   **Action:**
        *   Verify `.venv` is correctly listed in `.gitignore`. (This is standard practice but should be confirmed).
        *   No code changes needed; these files are local environment artifacts and should not be committed.

## 3. Repository Gap Analysis & Recommendations

Based on standard practices for public repositories, the following gaps and actions are identified:

1.  **Missing `LICENSE` File:**
    *   **Gap:** No `LICENSE` file found defining the terms under which the software can be used, modified, and distributed.
    *   **Recommendation:** Choose an appropriate open-source license (e.g., MIT, Apache 2.0, GPL) based on project goals and add a `LICENSE` file to the repository root containing the chosen license text. Consult legal advice if unsure.
2.  **Missing `CONTRIBUTING.md` File:**
    *   **Gap:** No file outlining guidelines for potential contributors (e.g., how to report bugs, suggest features, submit pull requests, coding standards).
    *   **Recommendation:** Create a `CONTRIBUTING.md` file in the repository root detailing the contribution process.
3.  **Missing `CODE_OF_CONDUCT.md` File:**
    *   **Gap:** No file establishing community standards and expectations for behavior.
    *   **Recommendation:** Adopt a standard Code of Conduct (e.g., Contributor Covenant) and add a `CODE_OF_CONDUCT.md` file to the repository root.
4.  **Verification of `.gitignore`:**
    *   **Gap:** Report assumes `.env` and `.venv` are ignored.
    *   **Recommendation:** Explicitly check the `.gitignore` file to confirm that `.env` and `venv/` (or similar patterns) are present. Add them if missing.
5.  **Review `rawr-mcp-graphiti-repo.md`:**
    *   **Gap:** Purpose and necessity of this large file are unclear.
    *   **Recommendation:** Investigate the origin and purpose of `rawr-mcp-graphiti-repo.md`. If it's an unnecessary generated file or archive, remove it. If it's required, ensure it doesn't contain sensitive information or outdated absolute paths.

## 4. Next Steps

Execute the remediation plan, starting with Critical issues, followed by Major, and then Minor/Gap Analysis items. Track progress against this plan.