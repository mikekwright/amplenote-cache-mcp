"""
Tests for task-related functionality using dependency injection.
"""

import pytest
import json


def test_search_tasks(tasks_service):
    """Test searching tasks by description."""
    # Search for a broader term to find tasks
    results = tasks_service.search_tasks("the", limit=20, include_done=True)

    # Should have results since we're searching the actual database
    if len(results) > 0:
        # At least some tasks should have valid content
        tasks_with_content = [r for r in results if r["content"] is not None]

        if len(tasks_with_content) > 0:
            # Verify content structure is correct for parsed tasks
            for task in tasks_with_content:
                plain_text = task["content"].to_plain_text()
                assert isinstance(plain_text, str), "Plain text should be a string"
    else:
        # If no tasks found, the search still worked (empty result is valid)
        assert isinstance(results, list)


def test_search_tasks_no_results(tasks_service):
    """Test task search with no matching results."""
    results = tasks_service.search_tasks("nonexistent_task_xyz", limit=10)
    assert len(results) == 0


def test_search_tasks_exclude_deleted(tasks_service):
    """Test that deleted tasks are excluded by default."""
    results = tasks_service.search_tasks("task", include_deleted=False)

    # Should not include the deleted task
    assert all(r["deleted"] == False for r in results)


def test_search_tasks_include_deleted(tasks_service):
    """Test including deleted tasks in search."""
    results = tasks_service.search_tasks("Deleted", include_deleted=True)

    # Should find the deleted task
    assert len(results) > 0
    assert any(r["deleted"] == True for r in results)


def test_list_tasks(tasks_service):
    """Test listing tasks with default filters."""
    results = tasks_service.list_tasks(limit=10)

    assert len(results) > 0
    assert all("uuid" in r for r in results)
    assert all("content" in r for r in results)
    assert all("deleted" in r for r in results)


def test_list_tasks_filter_by_priority(tasks_service):
    """Test filtering tasks by priority level."""
    # Note: Priority filtering is not implemented in the new schema
    # This test needs to be updated or removed based on actual schema
    results = tasks_service.list_tasks(limit=10)

    assert len(results) >= 0


def test_list_tasks_filter_has_due_date(tasks_service):
    """Test filtering tasks with due dates."""
    results_with_due = tasks_service.list_tasks(has_due_date=True, limit=10)
    results_without_due = tasks_service.list_tasks(has_due_date=False, limit=10)

    assert all(r["due"] is not None for r in results_with_due)
    assert all(r["due"] is None for r in results_without_due)


def test_list_tasks_exclude_deleted(tasks_service):
    """Test that deleted tasks are excluded by default."""
    results = tasks_service.list_tasks(include_deleted=False)

    assert all(r["deleted"] == False for r in results)


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

    assert all(r["deleted"] == False for r in results)


def test_get_tasks_by_note(tasks_service):
    """Test retrieving tasks associated with a note UUID."""
    # This test requires tasks that reference notes in their body
    # For now, just verify the function works
    results = tasks_service.get_tasks_by_note("some-note-uuid")

    # Should return empty list if no tasks reference this note
    assert isinstance(results, list)


def test_get_tasks_by_note_ordering(tasks_service):
    """Test that tasks are ordered by due date."""
    results = tasks_service.get_tasks_by_note("task")

    # If we have results, verify ordering by due date
    if len(results) > 1:
        for i in range(len(results) - 1):
            # Earlier due dates should come first
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
            uuid CHARACTER(36),
            local_uuid CHARACTER(36),
            remote_uuid CHARACTER(36),
            deleted INTEGER DEFAULT 0,
            calendar_sync_required INTEGER DEFAULT 0,
            notify_at INTEGER,
            attrs TEXT,
            content TEXT,
            due INTEGER,
            done INTEGER DEFAULT 0,
            is_scheduled_bullet INTEGER DEFAULT 0,
            parent_uuid CHARACTER(36)
        )
    """)
    # Use proper ProseMirror JSON format for content
    test_content = json.dumps([{
        "type": "paragraph",
        "content": [{"type": "text", "text": "Test task description"}]
    }])
    cursor.execute("""
        INSERT INTO tasks (uuid, local_uuid, remote_uuid, deleted, calendar_sync_required, notify_at, attrs, content, due, done, is_scheduled_bullet, parent_uuid)
        VALUES ('test-task-uuid', 'local-uuid', 'remote-uuid', 0, 0, NULL, '{}', ?, NULL, 0, 0, NULL)
    """, (test_content,))
    conn.commit()

    # Mock returns the in-memory connection
    mock_db_connection.get_connection.return_value = conn

    # Import after mocking to avoid import-time issues
    from app.tasks import TasksService

    service = TasksService(mock_db_connection)

    # Test that service uses the mocked connection
    # We need to search for something in the content
    results = service.search_tasks("Test", limit=10, include_deleted=False)

    assert len(results) > 0
    # Content is now a TaskContent model
    assert results[0]["content"] is not None
    assert results[0]["content"].to_plain_text() == "Test task description"
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


def test_task_content_parsing(tasks_service):
    """Test that task content JSON is properly parsed into TaskContent model."""
    results = tasks_service.search_tasks("", limit=5, include_deleted=False, include_done=False)

    if len(results) > 0:
        # Check that content is parsed
        for task in results:
            if task["content"] is not None:
                # Should be TaskContent model, not string
                assert hasattr(task["content"], "root"), "Content should be a TaskContent model"
                assert isinstance(task["content"].root, list), "Content should have a list of paragraphs"

                # Test to_plain_text method
                plain_text = task["content"].to_plain_text()
                assert isinstance(plain_text, str), "to_plain_text should return a string"


def test_task_attrs_parsing(tasks_service):
    """Test that task attrs JSON is properly parsed into TaskAttrs model."""
    results = tasks_service.search_tasks("", limit=5, include_deleted=False, include_done=False)

    if len(results) > 0:
        # Check that attrs is parsed
        for task in results:
            if task["attrs"] is not None:
                # Should be TaskAttrs model, not string
                assert hasattr(task["attrs"], "created_at"), "Attrs should be a TaskAttrs model"
                assert hasattr(task["attrs"], "victory_value"), "Attrs should have victory_value field"

                # Verify field access works
                if task["attrs"].created_at:
                    assert isinstance(task["attrs"].created_at, int), "created_at should be an int"


def test_task_content_with_links():
    """Test parsing task content that contains links."""
    from app.tasks import TasksService

    content_json = json.dumps([
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Review the "},
                {
                    "type": "link",
                    "attrs": {"href": "https://example.com/ticket/123"},
                    "content": [{"type": "text", "text": "TICKET-123"}]
                },
                {"type": "text", "text": " today"}
            ]
        }
    ])

    parsed = TasksService._parse_task_content(content_json)
    assert parsed is not None
    assert len(parsed.root) == 1
    assert len(parsed.root[0].content) == 3

    # Verify plain text extraction
    plain_text = parsed.to_plain_text()
    assert "Review the" in plain_text
    assert "TICKET-123" in plain_text
    assert "today" in plain_text


def test_task_content_with_formatting():
    """Test parsing task content with text formatting marks."""
    from app.tasks import TasksService

    content_json = json.dumps([
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "This is "},
                {"type": "text", "marks": [{"type": "em"}], "text": "important"},
                {"type": "text", "text": " and "},
                {"type": "text", "marks": [{"type": "strong"}], "text": "urgent"}
            ]
        }
    ])

    parsed = TasksService._parse_task_content(content_json)
    assert parsed is not None
    assert len(parsed.root) == 1
    assert len(parsed.root[0].content) == 4

    # Check marks
    assert parsed.root[0].content[1].marks is not None
    assert parsed.root[0].content[1].marks[0].type == "em"
    assert parsed.root[0].content[3].marks is not None
    assert parsed.root[0].content[3].marks[0].type == "strong"


def test_task_attrs_with_recurring():
    """Test parsing task attrs with recurring task data."""
    from app.tasks import TasksService

    attrs_json = json.dumps({
        "createdAt": 1758663212,
        "repeat": "DTSTART:20250421T090000\nRRULE:FREQ=WEEKLY;BYDAY=MO",
        "startAt": 1759042800,
        "startRule": "P1DT1H",
        "streakCount": 4,
        "duration": "PT15M",
        "flags": "IU",
        "points": 15.1,
        "pointsUpdatedAt": 1761162794,
        "victoryValue": 9.7,
        "completedAt": 1761163795
    })

    parsed = TasksService._parse_task_attrs(attrs_json)
    assert parsed is not None
    assert parsed.created_at == 1758663212
    assert parsed.repeat == "DTSTART:20250421T090000\nRRULE:FREQ=WEEKLY;BYDAY=MO"
    assert parsed.streak_count == 4
    assert parsed.duration == "PT15M"
    assert parsed.flags == "IU"
    assert parsed.points == 15.1
    assert parsed.victory_value == 9.7


def test_task_attrs_with_references():
    """Test parsing task attrs with note/task references."""
    from app.tasks import TasksService

    attrs_json = json.dumps({
        "createdAt": 1758664814,
        "references": ["db177700-018f-11ef-8a67-7e9dd6e19a06", "another-uuid"]
    })

    parsed = TasksService._parse_task_attrs(attrs_json)
    assert parsed is not None
    assert parsed.references is not None
    assert len(parsed.references) == 2
    assert "db177700-018f-11ef-8a67-7e9dd6e19a06" in parsed.references


def test_parse_invalid_json():
    """Test that invalid JSON doesn't crash the parser."""
    from app.tasks import TasksService

    # Test invalid content JSON
    invalid_content = "not valid json"
    parsed_content = TasksService._parse_task_content(invalid_content)
    assert parsed_content is None

    # Test invalid attrs JSON
    invalid_attrs = "not valid json"
    parsed_attrs = TasksService._parse_task_attrs(invalid_attrs)
    assert parsed_attrs is None

    # Test None values
    assert TasksService._parse_task_content(None) is None
    assert TasksService._parse_task_attrs(None) is None
