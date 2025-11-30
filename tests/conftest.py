"""
Pytest configuration and fixtures for Amplenote MCP tests.
"""

import os
import sqlite3
import tempfile

from pathlib import Path
from unittest.mock import Mock

import pytest

from app.config import Settings
from app.container import Container
from app.database import DatabaseConnection
from app.notes import NotesService
from app.tasks import TasksService


@pytest.fixture
def test_db_path():
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db') as f:
        db_path = f.name

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def populated_db(test_db_path):
    """Create and populate a test database with sample data."""
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Create notes table
    cursor.execute("""
        CREATE TABLE notes (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            remote_uuid TEXT,
            local_uuid TEXT,
            name TEXT,
            metadata TEXT,
            text TEXT,
            remote_content TEXT,
            remote_digest TEXT,
            updated_at TEXT
        )
    """)

    # Create tasks table
    cursor.execute("""
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT,
            body TEXT,
            due TEXT,
            duration INTEGER,
            notify TEXT,
            points INTEGER,
            priority INTEGER,
            start_at TEXT,
            deleted INTEGER,
            updated_at TEXT
        )
    """)

    # Create note_references table
    cursor.execute("""
        CREATE TABLE note_references (
            local_uuid TEXT,
            referenced_uuid TEXT
        )
    """)

    # Create FTS4 virtual table for notes search
    cursor.execute("""
        CREATE VIRTUAL TABLE notes_search_index USING fts4(
            content='notes',
            name,
            text
        )
    """)

    # Insert sample notes
    notes_data = [
        ('uuid-1', 'local-uuid-1', 'Project Planning', '{}', 'This is a project planning note with tasks.',
         '{}', 'digest-1', '2024-01-15 10:00:00'),
        ('uuid-2', 'local-uuid-2', 'Meeting Notes', '{}', 'Important meeting about the quarterly review.',
         '{}', 'digest-2', '2024-01-16 11:00:00'),
        ('uuid-3', 'local-uuid-3', 'Ideas', '{}', 'Random ideas and thoughts for future projects.',
         '{}', 'digest-3', '2024-01-14 09:00:00'),
    ]

    for note in notes_data:
        cursor.execute("""
            INSERT INTO notes (remote_uuid, local_uuid, name, metadata, text, remote_content, remote_digest, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, note)

    # Populate FTS index
    cursor.execute("""
        INSERT INTO notes_search_index (docid, name, text)
        SELECT rowid, name, text FROM notes
    """)

    # Insert sample tasks
    tasks_data = [
        ('task-uuid-1', 'Complete project documentation', '2024-02-01', 120, None, 5, 1, None, None, '2024-01-15 10:30:00'),
        ('task-uuid-2', 'Review pull requests', '2024-01-20', 60, None, 3, 2, None, None, '2024-01-16 12:00:00'),
        ('task-uuid-3', 'Update dependencies', None, 30, None, 2, 0, None, None, '2024-01-14 08:00:00'),
        ('task-uuid-4', 'Deleted task', '2024-01-25', 45, None, 1, 1, None, 1, '2024-01-13 15:00:00'),
    ]

    for task in tasks_data:
        cursor.execute("""
            INSERT INTO tasks (uuid, body, due, duration, notify, points, priority, start_at, deleted, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, task)

    # Insert note references
    cursor.execute("""
        INSERT INTO note_references (local_uuid, referenced_uuid)
        VALUES ('local-uuid-1', 'local-uuid-2')
    """)

    cursor.execute("""
        INSERT INTO note_references (local_uuid, referenced_uuid)
        VALUES ('local-uuid-2', 'local-uuid-3')
    """)

    conn.commit()
    conn.close()

    return test_db_path


@pytest.fixture
def test_settings(populated_db):
    """Create test settings with the populated database path."""
    return Settings(db_path=Path(populated_db))


@pytest.fixture
def db_connection(test_settings):
    """Create a DatabaseConnection instance for testing."""
    return DatabaseConnection(test_settings)


@pytest.fixture
def notes_service(db_connection):
    """Create a NotesService instance with dependency injection."""
    return NotesService(db_connection)


@pytest.fixture
def tasks_service(db_connection):
    """Create a TasksService instance with dependency injection."""
    return TasksService(db_connection)


@pytest.fixture
def container(populated_db):
    """
    Create and configure a DI container for testing.

    This fixture provides a fully wired container with all dependencies
    configured to use the test database.
    """
    test_container = Container()

    # Override settings to use test database
    test_container.settings.override(
        Settings(db_path=Path(populated_db))
    )

    return test_container


# Legacy fixture for backward compatibility
# This should be gradually phased out in favor of service fixtures
@pytest.fixture
def set_test_db_env(populated_db, monkeypatch):
    """
    DEPRECATED: Use service fixtures (notes_service, tasks_service) instead.

    Set the AMPLENOTE_DB_PATH environment variable to the test database.
    This fixture is kept for backward compatibility but should not be used
    in new tests.
    """
    monkeypatch.setenv('AMPLENOTE_DB_PATH', populated_db)

    # Force reload of the database module to pick up the new env var
    import app.database
    import importlib
    importlib.reload(app.database)

    yield populated_db

    # Reload again to reset
    importlib.reload(app.database)
