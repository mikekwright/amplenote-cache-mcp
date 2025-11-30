"""
Tests for task-related functionality using dependency injection.
"""

import pytest


def test_search_tasks(tasks_service):
    """Test searching tasks by description."""
    results = tasks_service.search_tasks("documentation", limit=10)

    assert len(results) > 0
    assert any("documentation" in r["body"].lower() for r in results)


def test_search_tasks_no_results(tasks_service):
    """Test task search with no matching results."""
    results = tasks_service.search_tasks("nonexistent_task_xyz", limit=10)
    assert len(results) == 0


def test_search_tasks_exclude_deleted(tasks_service):
    """Test that deleted tasks are excluded by default."""
    results = tasks_service.search_tasks("task", include_deleted=False)

    # Should not include the deleted task
    assert all(r["deleted"] is None or r["deleted"] == 0 for r in results)


def test_search_tasks_include_deleted(tasks_service):
    """Test including deleted tasks in search."""
    results = tasks_service.search_tasks("Deleted", include_deleted=True)

    # Should find the deleted task
    assert len(results) > 0
    assert any(r["deleted"] == 1 for r in results)


def test_list_tasks(tasks_service):
    """Test listing tasks with default filters."""
    results = tasks_service.list_tasks(limit=10)

    assert len(results) > 0
    assert all("uuid" in r for r in results)
    assert all("body" in r for r in results)
    assert all("priority" in r for r in results)


def test_list_tasks_filter_by_priority(tasks_service):
    """Test filtering tasks by priority level."""
    results = tasks_service.list_tasks(priority=1, limit=10)

    assert all(r["priority"] == 1 for r in results)


def test_list_tasks_filter_has_due_date(tasks_service):
    """Test filtering tasks with due dates."""
    results_with_due = tasks_service.list_tasks(has_due_date=True, limit=10)
    results_without_due = tasks_service.list_tasks(has_due_date=False, limit=10)

    assert all(r["due"] is not None for r in results_with_due)
    assert all(r["due"] is None for r in results_without_due)


def test_list_tasks_exclude_deleted(tasks_service):
    """Test that deleted tasks are excluded by default."""
    results = tasks_service.list_tasks(include_deleted=False)

    assert all(r["deleted"] is None or r["deleted"] == 0 for r in results)


def test_get_recently_modified_tasks(tasks_service):
    """Test retrieving recently modified tasks."""
    results = tasks_service.get_recently_modified_tasks(limit=5)

    assert len(results) > 0
    assert all("updated_at" in r for r in results)

    # Verify sorted by updated_at descending
    if len(results) > 1:
        for i in range(len(results) - 1):
            assert results[i]["updated_at"] >= results[i + 1]["updated_at"]


def test_get_recently_modified_tasks_exclude_deleted(tasks_service):
    """Test that recently modified excludes deleted tasks by default."""
    results = tasks_service.get_recently_modified_tasks(include_deleted=False)

    assert all(r["deleted"] is None or r["deleted"] == 0 for r in results)


def test_get_tasks_by_note(tasks_service):
    """Test retrieving tasks associated with a note UUID."""
    # This test requires tasks that reference notes in their body
    # For now, just verify the function works
    results = tasks_service.get_tasks_by_note("some-note-uuid")

    # Should return empty list if no tasks reference this note
    assert isinstance(results, list)


def test_get_tasks_by_note_ordering(tasks_service):
    """Test that tasks are ordered by priority and due date."""
    results = tasks_service.get_tasks_by_note("task")

    # If we have results, verify ordering
    if len(results) > 1:
        for i in range(len(results) - 1):
            # Higher priority should come first, or if same priority, earlier due date
            if results[i]["priority"] == results[i + 1]["priority"]:
                if results[i]["due"] and results[i + 1]["due"]:
                    assert results[i]["due"] <= results[i + 1]["due"]


def test_tasks_service_with_mock_db():
    """Test that TasksService can work with a mocked DatabaseConnection."""
    from unittest.mock import Mock
    import sqlite3

    # Create an in-memory database with test data
    mock_db_connection = Mock()
    conn = sqlite3.connect(":memory:")

    # Set up complete schema for testing
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            uuid TEXT,
            body TEXT,
            due TEXT,
            duration INTEGER,
            notify TEXT,
            points INTEGER,
            priority INTEGER,
            start_at TEXT,
            deleted INTEGER
        )
    """)
    cursor.execute("""
        INSERT INTO tasks (uuid, body, due, duration, notify, points, priority, start_at, deleted)
        VALUES ('test-task-uuid', 'Test task description', NULL, 60, NULL, 3, 1, NULL, 0)
    """)
    conn.commit()

    # Mock returns the in-memory connection
    mock_db_connection.get_connection.return_value = conn

    # Import after mocking to avoid import-time issues
    from app.tasks import TasksService

    service = TasksService(mock_db_connection)

    # Test that service uses the mocked connection
    # We need to search for something in the body
    results = service.search_tasks("Test", limit=10, include_deleted=False)

    assert len(results) > 0
    assert results[0]["body"] == "Test task description"
    assert results[0]["uuid"] == "test-task-uuid"

    conn.close()


def test_tasks_service_dependency_injection():
    """Test that TasksService properly receives injected dependencies."""
    from unittest.mock import Mock
    from app.tasks import TasksService

    mock_db_connection = Mock()
    service = TasksService(mock_db_connection)

    # Verify the dependency was injected
    assert service.db_connection is mock_db_connection
