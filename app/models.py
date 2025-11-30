"""
Data models and type definitions for Amplenote MCP Server.
"""

from typing import TypedDict


class Note(TypedDict):
    """Note data model."""
    remote_uuid: str
    local_uuid: str
    name: str
    metadata: str | None
    text: str | None
    remote_content: str | None
    remote_digest: str | None


class NoteBasic(TypedDict):
    """Basic note information without full content."""
    remote_uuid: str
    local_uuid: str
    name: str


class NoteWithTimestamp(TypedDict):
    """Note with modification timestamp."""
    remote_uuid: str
    local_uuid: str
    name: str
    updated_at: str


class NoteSearchResult(TypedDict):
    """Search result for notes."""
    uuid: str
    name: str
    snippet: str


class Task(TypedDict):
    """Task data model."""
    id: int
    uuid: str
    body: str
    due: str | None
    duration: int | None
    notify: str | None
    points: int | None
    priority: int | None
    start_at: str | None
    deleted: int | None


class TaskWithTimestamp(TypedDict):
    """Task with modification timestamp."""
    id: int
    uuid: str
    body: str
    due: str | None
    duration: int | None
    notify: str | None
    points: int | None
    priority: int | None
    start_at: str | None
    deleted: int | None
    updated_at: str


class NoteReference(TypedDict):
    """Note reference data."""
    uuid: str
    name: str | None


class NoteReferences(TypedDict):
    """Bidirectional note references."""
    referenced_by: list[NoteReference]
    references: list[NoteReference]
