"""
Tests for note-related functionality using dependency injection.
"""

import pytest


def test_search_notes(notes_service):
    """Test full-text search of notes."""
    results = notes_service.search_notes("project", limit=10)

    assert len(results) > 0
    assert any("Project Planning" in r["name"] for r in results)


def test_search_notes_no_results(notes_service):
    """Test search with no matching results."""
    results = notes_service.search_notes("nonexistent_keyword_xyz", limit=10)
    assert len(results) == 0


def test_get_note_by_uuid(notes_service):
    """Test retrieving a note by UUID."""
    note = notes_service.get_note_by_uuid("uuid-1")

    assert note is not None
    assert note["remote_uuid"] == "uuid-1"
    assert note["name"] == "Project Planning"
    assert "project planning note" in note["text"].lower()


def test_get_note_by_uuid_not_found(notes_service):
    """Test retrieving a non-existent note."""
    note = notes_service.get_note_by_uuid("nonexistent-uuid")
    assert note is None


def test_get_note_by_name(notes_service):
    """Test retrieving a note by name."""
    note = notes_service.get_note_by_name("Meeting")

    assert note is not None
    assert "Meeting Notes" in note["name"]


def test_get_note_by_name_not_found(notes_service):
    """Test retrieving a note with non-matching name."""
    note = notes_service.get_note_by_name("Nonexistent Note Title")
    assert note is None


def test_list_notes(notes_service):
    """Test listing notes with pagination."""
    results = notes_service.list_notes(limit=2, offset=0)

    assert len(results) <= 2
    assert all("remote_uuid" in r for r in results)
    assert all("name" in r for r in results)


def test_list_notes_pagination(notes_service):
    """Test note pagination works correctly."""
    first_page = notes_service.list_notes(limit=1, offset=0)
    second_page = notes_service.list_notes(limit=1, offset=1)

    assert len(first_page) == 1
    assert len(second_page) == 1
    assert first_page[0]["remote_uuid"] != second_page[0]["remote_uuid"]


def test_get_note_references(notes_service):
    """Test retrieving note references."""
    references = notes_service.get_note_references("local-uuid-1")

    assert "referenced_by" in references
    assert "references" in references
    assert isinstance(references["referenced_by"], list)
    assert isinstance(references["references"], list)


def test_get_note_references_no_references(notes_service):
    """Test note with no references."""
    references = notes_service.get_note_references("local-uuid-3")

    # local-uuid-3 is referenced by local-uuid-2
    assert len(references["referenced_by"]) >= 1
    # But doesn't reference anything
    assert len(references["references"]) == 0


def test_notes_service_with_mock_db():
    """Test that NotesService can work with a mocked DatabaseConnection."""
    from unittest.mock import Mock
    import sqlite3

    # Create an in-memory database with test data
    mock_db_connection = Mock()
    conn = sqlite3.connect(":memory:")

    # Set up complete schema for testing
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE notes (
            rowid INTEGER PRIMARY KEY,
            remote_uuid TEXT,
            local_uuid TEXT,
            name TEXT,
            metadata TEXT,
            text TEXT,
            remote_content TEXT,
            remote_digest TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO notes (remote_uuid, local_uuid, name, metadata, text, remote_content, remote_digest)
        VALUES ('test-uuid', 'test-local-uuid', 'Test Note', '{}', 'Test content', '{}', 'digest')
    """)
    conn.commit()

    # Mock returns the in-memory connection
    mock_db_connection.get_readonly_connection.return_value = conn

    # Import after mocking to avoid import-time issues
    from app.notes import NotesService

    service = NotesService(mock_db_connection)

    # Test that service uses the mocked connection
    note = service.get_note_by_uuid("test-uuid")

    assert note["name"] == "Test Note"
    assert note["remote_uuid"] == "test-uuid"

    conn.close()
