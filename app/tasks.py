"""
Task-related tools for Amplenote MCP Server.
"""

from typing import Optional
from datetime import datetime
import json
from pydantic import ValidationError

from .database import DatabaseConnection
from .models import Task, TaskWithTimestamp, TaskAttrs, TaskContent


class TasksService:
    """
    Service class for task-related operations.

    This class encapsulates all task-related business logic and database queries.
    It follows dependency injection principles by accepting a DatabaseConnection
    instance rather than creating database connections directly.


    Task Schema (2025-11-29):
        sqlite> PRAGMA table_info(tasks);
        0|id|INTEGER|0||1
        1|uuid|CHARACTER(36)|1||0
        2|local_uuid|CHARACTER(36)|0||0
        3|remote_uuid|CHARACTER(36)|0||0
        4|deleted|INTEGER|1|0|0
        5|calendar_sync_required|INTEGER|1|0|0
        6|notify_at|INTEGER|0||0
        7|attrs|TEXT|0||0
        8|content|TEXT|0||0
        9|due|INTEGER|0||0
        10|done|INTEGER|1|0|0
        11|is_scheduled_bullet|INTEGER|1|0|0
        12|parent_uuid|CHARACTER(36)|0||0
    """
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection

    @staticmethod
    def _parse_task_attrs(attrs_json: str | None) -> TaskAttrs | None:
        """Parse task attributes JSON string into TaskAttrs model."""
        if not attrs_json:
            return None
        try:
            data = json.loads(attrs_json)
            return TaskAttrs(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            # Log error but don't fail - return None for invalid data
            print(f"Warning: Failed to parse task attrs: {e}")
            return None

    @staticmethod
    def _parse_task_content(content_json: str | None) -> TaskContent | None:
        """Parse task content JSON string into TaskContent model."""
        if not content_json:
            return None
        try:
            data = json.loads(content_json)
            return TaskContent.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            # Log error but don't fail - return None for invalid data
            print(f"Warning: Failed to parse task content: {e}")
            return None

    def search_tasks(self, query: str, limit: int = 20, include_deleted: bool = False, include_done: bool = False) -> list[Task]:
        """
        Search tasks by description/body text and return list of matched tasks.
        """
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()

        sql_query = """
            SELECT
              id, uuid, local_uuid, remote_uuid, deleted, calendar_sync_required, notify_at, attrs,
              content, due, done, is_scheduled_bullet, parent_uuid
            FROM tasks
            WHERE content LIKE ?
        """
        params = [f"%{query}%"]

        if not include_deleted:
            sql_query += " AND (deleted IS NULL OR deleted = 0)"

        if not include_done:
            sql_query += " AND (done IS NULL OR done = 0)"

        sql_query += " ORDER BY due ASC LIMIT ?"
        params.append(limit)

        cursor.execute(sql_query, params)

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "uuid": row[1],
                "local_uuid": row[2],
                "remote_uuid": row[3],
                "deleted": False if row[4] == 0 else True,
                "calendar_sync_required": False if row[5] == 0 else True,
                "notify_at": None if row[6] is None or row[6] == 0 else datetime.fromtimestamp(row[6]),
                "attrs": self._parse_task_attrs(row[7]),
                "content": self._parse_task_content(row[8]),
                "due": None if row[9] is None or row[9] == 0 else datetime.fromtimestamp(row[9]),
                "done": False if row[10] == 0 else True,
                "is_scheduled_bullet": False if row[11] == 0 else True,
                "parent_uuid": row[12],
            })

        conn.close()
        return results

    def list_tasks(
        self,
        limit: int = 20,
        include_deleted: bool = False,
        include_done: bool = False,
        has_due_date: Optional[bool] = None
    ) -> list[Task]:
        """
        List tasks with optional filtering.

        Args:
            limit: Maximum number of tasks to return (default: 20)
            include_deleted: Whether to include deleted tasks (default: False)
            include_done: Whether to include completed tasks (default: False)
            has_due_date: Filter tasks with/without due dates (optional)

        Returns:
            List of tasks with details
        """
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT
              id, uuid, local_uuid, remote_uuid, deleted, calendar_sync_required, notify_at, attrs,
              content, due, done, is_scheduled_bullet, parent_uuid
            FROM tasks
            WHERE 1=1
        """
        params = []

        if not include_deleted:
            query += " AND (deleted IS NULL OR deleted = 0)"

        if not include_done:
            query += " AND (done IS NULL OR done = 0)"

        if has_due_date is not None:
            if has_due_date:
                query += " AND due IS NOT NULL"
            else:
                query += " AND due IS NULL"

        query += " ORDER BY due ASC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "uuid": row[1],
                "local_uuid": row[2],
                "remote_uuid": row[3],
                "deleted": False if row[4] == 0 else True,
                "calendar_sync_required": False if row[5] == 0 else True,
                "notify_at": None if row[6] is None or row[6] == 0 else datetime.fromtimestamp(row[6]),
                "attrs": self._parse_task_attrs(row[7]),
                "content": self._parse_task_content(row[8]),
                "due": None if row[9] is None or row[9] == 0 else datetime.fromtimestamp(row[9]),
                "done": False if row[10] == 0 else True,
                "is_scheduled_bullet": False if row[11] == 0 else True,
                "parent_uuid": row[12],
            })

        conn.close()
        return results

    def get_recently_modified_tasks(self, limit: int = 20, include_deleted: bool = False, include_done: bool = False) -> list[TaskWithTimestamp]:
        """
        Get the most recently modified tasks.

        Args:
            limit: Maximum number of tasks to return (default: 20)
            include_deleted: Whether to include deleted tasks (default: False)
            include_done: Whether to include completed tasks (default: False)

        Returns:
            List of recently modified tasks with details
        """
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT
              id, uuid, local_uuid, remote_uuid, deleted, calendar_sync_required, notify_at, attrs,
              content, due, done, is_scheduled_bullet, parent_uuid, updated_at
            FROM tasks
            WHERE 1=1
        """
        params = []

        if not include_deleted:
            query += " AND (deleted IS NULL OR deleted = 0)"

        if not include_done:
            query += " AND (done IS NULL OR done = 0)"

        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "uuid": row[1],
                "local_uuid": row[2],
                "remote_uuid": row[3],
                "deleted": False if row[4] == 0 else True,
                "calendar_sync_required": False if row[5] == 0 else True,
                "notify_at": None if row[6] is None or row[6] == 0 else datetime.fromtimestamp(row[6]),
                "attrs": self._parse_task_attrs(row[7]),
                "content": self._parse_task_content(row[8]),
                "due": None if row[9] is None or row[9] == 0 else datetime.fromtimestamp(row[9]),
                "done": False if row[10] == 0 else True,
                "is_scheduled_bullet": False if row[11] == 0 else True,
                "parent_uuid": row[12],
                "updated_at": row[13]
            })

        conn.close()
        return results

    def get_tasks_by_note(self, note_uuid: str, include_deleted: bool = False, include_done: bool = False) -> list[Task]:
        """
        Get all tasks associated with a specific note.
        Note: This searches for the note UUID in the task content.

        Args:
            note_uuid: The UUID of the note
            include_deleted: Whether to include deleted tasks (default: False)
            include_done: Whether to include completed tasks (default: False)

        Returns:
            List of tasks that mention this note
        """
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT
              id, uuid, local_uuid, remote_uuid, deleted, calendar_sync_required, notify_at, attrs,
              content, due, done, is_scheduled_bullet, parent_uuid
            FROM tasks
            WHERE content LIKE ?
        """
        params = [f"%{note_uuid}%"]

        if not include_deleted:
            query += " AND (deleted IS NULL OR deleted = 0)"

        if not include_done:
            query += " AND (done IS NULL OR done = 0)"

        query += " ORDER BY due ASC"

        cursor.execute(query, params)

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "uuid": row[1],
                "local_uuid": row[2],
                "remote_uuid": row[3],
                "deleted": False if row[4] == 0 else True,
                "calendar_sync_required": False if row[5] == 0 else True,
                "notify_at": None if row[6] is None or row[6] == 0 else datetime.fromtimestamp(row[6]),
                "attrs": self._parse_task_attrs(row[7]),
                "content": self._parse_task_content(row[8]),
                "due": None if row[9] is None or row[9] == 0 else datetime.fromtimestamp(row[9]),
                "done": False if row[10] == 0 else True,
                "is_scheduled_bullet": False if row[11] == 0 else True,
                "parent_uuid": row[12],
            })

        conn.close()
        return results


# Legacy functions for backward compatibility during migration
# These will be removed once all code is migrated to use DI
def search_tasks(query: str, limit: int = 20, include_deleted: bool = False) -> list[Task]:
    """DEPRECATED: Use TasksService.search_tasks instead."""
    from .database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    sql_query = "SELECT id, uuid, body, due, duration, notify, points, priority, start_at, deleted FROM tasks WHERE body LIKE ?"
    params = [f"%{query}%"]
    if not include_deleted:
        sql_query += " AND (deleted IS NULL OR deleted = 0)"
    sql_query += " ORDER BY priority DESC, due ASC LIMIT ?"
    params.append(limit)
    cursor.execute(sql_query, params)
    results = []
    for row in cursor.fetchall():
        results.append({
            "id": row[0], "uuid": row[1], "body": row[2], "due": row[3], "duration": row[4],
            "notify": row[5], "points": row[6], "priority": row[7], "start_at": row[8], "deleted": row[9]
        })
    conn.close()
    return results


def list_tasks(
    limit: int = 20,
    include_deleted: bool = False,
    priority: Optional[int] = None,
    has_due_date: Optional[bool] = None
) -> list[Task]:
    """DEPRECATED: Use TasksService.list_tasks instead."""
    from .database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT id, uuid, body, due, duration, notify, points, priority, start_at, deleted FROM tasks WHERE 1=1"
    params = []
    if not include_deleted:
        query += " AND (deleted IS NULL OR deleted = 0)"
    if priority is not None:
        query += " AND priority = ?"
        params.append(priority)
    if has_due_date is not None:
        if has_due_date:
            query += " AND due IS NOT NULL"
        else:
            query += " AND due IS NULL"
    query += " ORDER BY priority DESC, due ASC LIMIT ?"
    params.append(limit)
    cursor.execute(query, params)
    results = []
    for row in cursor.fetchall():
        results.append({
            "id": row[0], "uuid": row[1], "body": row[2], "due": row[3], "duration": row[4],
            "notify": row[5], "points": row[6], "priority": row[7], "start_at": row[8], "deleted": row[9]
        })
    conn.close()
    return results


def get_recently_modified_tasks(limit: int = 20, include_deleted: bool = False) -> list[TaskWithTimestamp]:
    """DEPRECATED: Use TasksService.get_recently_modified_tasks instead."""
    from .database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT id, uuid, body, due, duration, notify, points, priority, start_at, deleted, updated_at FROM tasks WHERE 1=1"
    params = []
    if not include_deleted:
        query += " AND (deleted IS NULL OR deleted = 0)"
    query += " ORDER BY updated_at DESC LIMIT ?"
    params.append(limit)
    cursor.execute(query, params)
    results = []
    for row in cursor.fetchall():
        results.append({
            "id": row[0], "uuid": row[1], "body": row[2], "due": row[3], "duration": row[4],
            "notify": row[5], "points": row[6], "priority": row[7], "start_at": row[8],
            "deleted": row[9], "updated_at": row[10]
        })
    conn.close()
    return results


def get_tasks_by_note(note_uuid: str) -> list[Task]:
    """DEPRECATED: Use TasksService.get_tasks_by_note instead."""
    from .database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, uuid, body, due, duration, notify, points, priority, start_at, deleted
        FROM tasks
        WHERE body LIKE ?
        ORDER BY priority DESC, due ASC
    """, (f"%{note_uuid}%",))
    results = []
    for row in cursor.fetchall():
        results.append({
            "id": row[0], "uuid": row[1], "body": row[2], "due": row[3], "duration": row[4],
            "notify": row[5], "points": row[6], "priority": row[7], "start_at": row[8], "deleted": row[9]
        })
    conn.close()
    return results
