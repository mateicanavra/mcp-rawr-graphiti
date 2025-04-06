# Playbook: Development Logging

## Purpose

This playbook outlines the standard process for generating development logs, ensuring consistency and clarity in documenting development tasks.

## Key Roles/Modes

*   **Architect:** Defines log storage path and filename conventions.
*   **Analyze:** Reviews conversation history and generates a detailed summary of the development task, then formats the summary into a structured Markdown log entry.
*   **Code:** Writes the formatted log entry to the file system according to the defined conventions.
*   **Git:** Commits the newly created log file to the repository.

## Workflow Steps

1.  **Define Log Convention:**
    *   Use `architect` mode to determine the log storage path and filename convention. This ensures logs are stored in a consistent and easily accessible manner.
2.  **Summarize History:**
    *   Use `analyze` mode to review the conversation history related to the development task.
    *   Generate a detailed summary of the task, including the problem addressed, the solution implemented, and any challenges encountered.
3.  **Format Log Entry:**
    *   Use `analyze` mode to format the summary into a structured Markdown log entry.
    *   Include relevant details such as the date, task description, and key steps taken.
4.  **Write Log File:**
    *   Use `code` mode to write the formatted log entry to the file system.
    *   Adhere to the log storage path and filename convention defined in step 1.
5.  **Commit Log File:**
    *   Use `git` mode to commit the newly created log file to the repository.
    *   Include a descriptive commit message that clearly identifies the task being logged.