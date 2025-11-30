"""
Tests for database connection utilities.
"""

import os
import sqlite3

from pathlib import Path
from unittest.mock import Mock

import pytest

from app.config import Settings
from app.database import DatabaseConnection


def test_database_connection_success(test_settings):
    """Test successful database connection using dependency injection."""
    db_conn = DatabaseConnection(test_settings)
    conn = db_conn.get_readonly_connection()
    assert conn is not None

    # Verify we can execute a query
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    assert result == (1,)

    conn.close()


def test_database_connection_missing_file():
    """Test that FileNotFoundError is raised when database doesn't exist."""
    settings = Settings(db_path=Path('/nonexistent/path/to/db.sqlite'))
    db_conn = DatabaseConnection(settings)

    with pytest.raises(FileNotFoundError) as exc_info:
        db_conn.get_readonly_connection()

    assert "Amplenote database not found" in str(exc_info.value)


def test_database_connection_with_mock():
    """Test database connection can be mocked for unit tests."""
    # Create a mock database connection
    mock_connection = Mock(spec=DatabaseConnection)
    mock_connection.get_connection.return_value = sqlite3.connect(":memory:")

    # Verify the mock works
    conn = mock_connection.get_connection()
    assert conn is not None

    cursor = conn.cursor()
    cursor.execute("SELECT 42")
    result = cursor.fetchone()
    assert result == (42,)

    conn.close()


def test_database_connection_settings_injection():
    """Test that Settings are properly injected into DatabaseConnection."""
    test_path = Path("/test/path/db.sqlite")
    settings = Settings(db_path=test_path)
    db_conn = DatabaseConnection(settings)

    assert db_conn.settings.db_path == test_path


def test_database_connection_readonly_mode(test_settings):
    """Test that database connections are opened in read-only mode."""
    db_conn = DatabaseConnection(test_settings)
    conn = db_conn.get_readonly_connection()

    # Try to create a table - this should fail in read-only mode
    cursor = conn.cursor()
    with pytest.raises(sqlite3.OperationalError) as exc_info:
        cursor.execute("CREATE TABLE test_table (id INTEGER)")

    assert "attempt to write a readonly database" in str(exc_info.value)
    conn.close()
