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
    include_deleted: bool = False
) -> list[dict]:
    """
    Search tasks by description/body text.

    Args:
        query: Search query to match in task body
        limit: Maximum number of tasks to return (default: 20)
        include_deleted: Whether to include deleted tasks (default: False)

    Returns:
        List of matching tasks with details including duration, dates, and priority
    """
    return tasks_service.search_tasks(query, limit, include_deleted)


@mcp.tool()
def list_tasks(
    limit: int = 20,
    include_deleted: bool = False,
    priority: Optional[int] = None,
    has_due_date: Optional[bool] = None
) -> list[dict]:
    """
    List tasks with optional filtering.

    Args:
        limit: Maximum number of tasks to return (default: 20)
        include_deleted: Whether to include deleted tasks (default: False)
        priority: Filter by priority level (optional)
        has_due_date: Filter tasks with/without due dates (optional)

    Returns:
        List of tasks with details
    """
    return tasks_service.list_tasks(limit, include_deleted, priority, has_due_date)


@mcp.tool()
def get_recently_modified_tasks(
    limit: int = 20,
    include_deleted: bool = False
) -> list[dict]:
    """
    Get the most recently modified tasks.

    Args:
        limit: Maximum number of tasks to return (default: 20)
        include_deleted: Whether to include deleted tasks (default: False)

    Returns:
        List of recently modified tasks with details
    """
    return tasks_service.get_recently_modified_tasks(limit, include_deleted)


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
