"""
Amplenote MCP Server

A FastMCP server that provides access to your Amplenote SQLite database cache.
"""

from typing import Optional

from fastmcp import FastMCP

from .container import Container


# Initialize DI container and services
container = Container()
notes_service = container.notes_service()
tasks_service = container.tasks_service()

# Initialize FastMCP server
mcp = FastMCP("Amplenote Cache")


@mcp.tool()
def search_notes(query: str, limit: int = 10) -> list[dict]:
    """
    Search notes using full-text search.

    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 10)

    Returns:
        List of matching notes with uuid, name, and snippet
    """
    return notes_service.search_notes(query, limit)


@mcp.tool()
def get_note_by_uuid(uuid: str) -> dict:
    """
    Get the full content of a note by its UUID.

    Args:
        uuid: The remote_uuid of the note

    Returns:
        Note details including name, text, and metadata
    """
    return notes_service.get_note_by_uuid(uuid)


@mcp.tool()
def get_note_by_name(name: str) -> dict:
    """
    Get the full content of a note by its name.

    Args:
        name: The name of the note (case-insensitive partial match)

    Returns:
        Note details including uuid, text, and metadata
    """
    return notes_service.get_note_by_name(name)


@mcp.tool()
def list_notes(limit: int = 20, offset: int = 0) -> list[dict]:
    """
    List all notes with pagination.

    Args:
        limit: Maximum number of notes to return (default: 20)
        offset: Number of notes to skip (default: 0)

    Returns:
        List of notes with uuid and name
    """
    return notes_service.list_notes(limit, offset)


@mcp.tool()
def get_recently_modified_notes(limit: int = 20) -> list[dict]:
    """
    Get the most recently modified notes.

    Args:
        limit: Maximum number of notes to return (default: 20)

    Returns:
        List of recently modified notes with uuid, name, and modification timestamp
    """
    return notes_service.get_recently_modified_notes(limit)


@mcp.tool()
def search_tasks(
    query: str,
    limit: int = 20,
    include_deleted: bool = False,
    include_done: bool = False,
    min_points: Optional[float] = None,
    max_points: Optional[float] = None,
    flags_filter: Optional[str] = None,
    sort_by: Optional[str] = None
) -> list[dict]:
    """
    Search tasks by description/content text with advanced filtering.

    Args:
        query: Search query to match in task content
        limit: Maximum number of tasks to return (default: 20)
        include_deleted: Whether to include deleted tasks (default: False)
        include_done: Whether to include completed tasks (default: False)
        min_points: Minimum points value to filter by (optional)
        max_points: Maximum points value to filter by (optional)
        flags_filter: Filter by priority flags - "urgent", "important", "both", or "none" (optional)
        sort_by: Sort order - "due" (default), "points", or "created" (optional)

    Returns:
        List of matching tasks with details including dates and metadata
    """
    return tasks_service.search_tasks(
        query, limit, include_deleted, include_done,
        min_points, max_points, flags_filter, sort_by
    )


@mcp.tool()
def list_tasks(
    limit: int = 20,
    include_deleted: bool = False,
    include_done: bool = False,
    has_due_date: Optional[bool] = None,
    min_points: Optional[float] = None,
    max_points: Optional[float] = None,
    flags_filter: Optional[str] = None,
    sort_by: Optional[str] = None
) -> list[dict]:
    """
    List tasks with optional filtering and sorting.

    Args:
        limit: Maximum number of tasks to return (default: 20)
        include_deleted: Whether to include deleted tasks (default: False)
        include_done: Whether to include completed tasks (default: False)
        has_due_date: Filter tasks with/without due dates (optional)
        min_points: Minimum points value to filter by (optional)
        max_points: Maximum points value to filter by (optional)
        flags_filter: Filter by priority flags - "urgent", "important", "both", or "none" (optional)
        sort_by: Sort order - "due" (default), "points", or "created" (optional)

    Returns:
        List of tasks with details
    """
    return tasks_service.list_tasks(
        limit, include_deleted, include_done, has_due_date,
        min_points, max_points, flags_filter, sort_by
    )


@mcp.tool()
def get_recently_created_tasks(
    limit: int = 20,
    include_deleted: bool = False,
    include_done: bool = False
) -> list[dict]:
    """
    Get the most recently created tasks (sorted by creation date).

    Note: Previously named get_recently_modified_tasks. Now uses createdAt from attrs
    instead of the non-existent updated_at field.

    Args:
        limit: Maximum number of tasks to return (default: 20)
        include_deleted: Whether to include deleted tasks (default: False)
        include_done: Whether to include completed tasks (default: False)

    Returns:
        List of recently created tasks with details, ordered by creation date descending
    """
    return tasks_service.get_recently_modified_tasks(limit, include_deleted, include_done)


@mcp.tool()
def get_note_references(uuid: str) -> dict:
    """
    Get all notes that reference a given note, and all notes it references.

    Args:
        uuid: The UUID of the note to check references for

    Returns:
        Dictionary with 'referenced_by' and 'references' lists
    """
    return notes_service.get_note_references(uuid)


@mcp.tool()
def get_tasks_by_note(note_uuid: str) -> list[dict]:
    """
    Get all tasks associated with a specific note.
    Note: This searches for the note UUID in the task body.

    Args:
        note_uuid: The UUID of the note

    Returns:
        List of tasks that mention this note
    """
    return tasks_service.get_tasks_by_note(note_uuid)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
