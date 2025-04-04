---
description: Filesystem MCP Tools: Quick start guide for using the filesystem MCP server tools (reading, writing, searching, JSON/XML operations). Use when planning filesystem interactions.
globs: 
alwaysApply: false
---

# Filesystem MCP Tools: Quick Start Guide

This guide provides concise rules and workflows for using the filesystem MCP server tools effectively.

## Core Concepts

1.  **Allowed Directories**: All operations are restricted to specific directories configured when the server starts. Use `list_allowed_directories` to see them. All paths provided to tools MUST be relative to the project root or absolute paths within these allowed directories.
2.  **Permissions**: The server might be read-only or have specific write operations enabled (`create`, `edit`, `move`, `delete`, `rename`).
    *   **ALWAYS check permissions first** using `get_permissions` before attempting any write operation (create, modify, edit, move, rename, delete, `xml_to_json` with save).
    *   If required permissions are missing, inform the user; do not attempt the operation.
3.  **Path Handling**: Paths are handled internally for robustness (normalization, home expansion, validation). Ensure paths passed to tools are correct and intended for allowed directories. Symlink behavior depends on the `--no-follow-symlinks` server flag.
4.  **Size Limits**: Many tools (especially read/query tools) require a `maxBytes` or similar parameter to prevent excessive memory usage. Use sensible defaults (e.g., 10KB-1MB) unless otherwise specified or dealing with known large files.

## Common Workflows

### Exploring Filesystem Structure

1.  **Initial Overview**: Use `list_directory` for a top-level view of a directory.
2.  **Deeper Dive**: Use `directory_tree` with a controlled `maxDepth` (e.g., 2 or 3) to understand nested structures. Use `excludePatterns` (e.g., `node_modules`, `*.log`) to filter noise.
3.  **Specific Item Info**: Use `get_file_info` to get metadata (size, type, dates) for a specific file or directory.

### Searching for Files/Content

1.  **By Name/Pattern**: Use `search_files` for general pattern matching (case-insensitive, partial names). Requires `maxDepth`, `maxResults`.
2.  **By Extension**: Use `find_files_by_extension` for finding specific file types (e.g., `.ts`, `.json`). Requires `maxDepth`, `maxResults`.
3.  **JSON Key/Value**: Use `json_search_kv` to find specific key-value pairs within JSON files in a directory. Requires `maxBytes`, `maxDepth`, `maxResults`.
4.  **XML Content**: Use `xml_query` with XPath for targeted searches within XML files. Requires `maxBytes`.
5.  **JSON Content**: Use `json_query` with JSONPath for targeted searches within JSON files. Requires `maxBytes`.

### Reading File Content

1.  **Single File**: Use `read_file`. Requires `maxBytes`.
2.  **Multiple Files**: Use `read_multiple_files` for efficiency when reading several files. Requires `maxBytesPerFile`.

### Modifying Files (Requires Permissions!)

*   **Check Permissions First**: Use `get_permissions`.

1.  **Creating New Files**: Use `create_file`. Fails if the file already exists.
2.  **Targeted Edits (Small Changes)**:
    *   Read the relevant section using `read_file` (if needed).
    *   Use `edit_file` with specific `oldText` and `newText`. Requires `maxBytes`. This is preferred for small, precise changes as it preserves the rest of the file and returns a diff.
3.  **Overwriting Entire File**: Use `modify_file`. Replaces all content. Use when rewriting the whole file. Fails if the file doesn't exist.
4.  **Creating Directories**: Use `create_directory`. Creates parent directories if needed.
5.  **Moving/Renaming**:
    *   Use `move_file` to move/rename files *or* directories to a *different* location. Destination parent must exist.
    *   Use `rename_file` to rename a file *within* its current directory.
6.  **Deleting**:
    *   Use `delete_file` for single files.
    *   Use `delete_directory` for directories (use `recursive: true` for non-empty ones).

### Working with JSON (Requires `maxBytes` for most)

*   **Understand Structure**: Use `json_structure` first on unknown files.
*   **Query Data**: Use `json_query` (JSONPath).
*   **Get Specific Value**: Use `json_get_value`.
*   **Filter Arrays**: Use `json_filter`.
*   **Transform Data**: Use `json_transform`.
*   **Sample Data**: Use `json_sample`.
*   **Validate**: Use `json_validate` against a schema file.
*   **Search Key/Value**: Use `json_search_kv` across multiple files.

### Working with XML (Requires `maxBytes` for most)

*   **Understand Structure**: Use `xml_structure` first on unknown files.
*   **Query Data**: Use `xml_query` (XPath).
*   **Convert to JSON**:
    *   Use `xml_to_json_string` to get JSON as text (read-only).
    *   Use `xml_to_json` to save JSON to a file (requires `create`/`edit` permission).

## Tool Selection Quick Reference

*   **Read one file?** -> `read_file`
*   **Read many files?** -> `read_multiple_files`
*   **List dir contents?** -> `list_directory`
*   **See nested structure?** -> `directory_tree`
*   **Find file by name/pattern?** -> `search_files`
*   **Find file by extension?** -> `find_files_by_extension`
*   **Get file size/date/type?** -> `get_file_info`
*   **Create a new file?** -> `create_file` (Check Perms!)
*   **Make small change in existing file?** -> `edit_file` (Check Perms!)
*   **Replace entire file content?** -> `modify_file` (Check Perms!)
*   **Create directory?** -> `create_directory` (Check Perms!)
*   **Move/Rename file/dir?** -> `move_file` (Check Perms!)
*   **Rename file in place?** -> `rename_file` (Check Perms!)
*   **Delete file?** -> `delete_file` (Check Perms!)
*   **Delete directory?** -> `delete_directory` (Check Perms!)
*   **Query XML?** -> `xml_query`
*   **Query JSON?** -> `json_query`
*   **Convert XML to JSON (string)?** -> `xml_to_json_string`
*   **Convert XML to JSON (file)?** -> `xml_to_json` (Check Perms!)
*   **Check permissions?** -> `get_permissions`
*   **See allowed paths?** -> `list_allowed_directories`