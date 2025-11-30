"""
Task-related tools for Amplenote MCP Server.
"""

from typing import Optional

from .database import DatabaseConnection
from .models import Task, TaskWithTimestamp


class TasksService:
    """
    Service class for task-related operations.

    This class encapsulates all task-related business logic and database queries.
    It follows dependency injection principles by accepting a DatabaseConnection
    instance rather than creating database connections directly.
    """
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection

    def search_tasks(self, query: str, limit: int = 20, include_deleted: bool = False) -> list[Task]:
        """
        Search tasks by description/body text and return list of matched tasks.
        """
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()

        sql_query = """
            SELECT id, uuid, body, due, duration, notify, points, priority, start_at, deleted
            FROM tasks
            WHERE body LIKE ?
        """
        params = [f"%{query}%"]

        if not include_deleted:
            sql_query += " AND (deleted IS NULL OR deleted = 0)"

        sql_query += " ORDER BY priority DESC, due ASC LIMIT ?"
        params.append(limit)

        cursor.execute(sql_query, params)

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "uuid": row[1],
                "body": row[2],
                "due": row[3],
                "duration": row[4],
                "notify": row[5],
                "points": row[6],
                "priority": row[7],
                "start_at": row[8],
                "deleted": row[9]
            })

        conn.close()
        return results

    def list_tasks(
        self,
        limit: int = 20,
        include_deleted: bool = False,
        priority: Optional[int] = None,
        has_due_date: Optional[bool] = None
    ) -> list[Task]:
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
        conn = self.db_connection.get_connection()
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
                "id": row[0],
                "uuid": row[1],
                "body": row[2],
                "due": row[3],
                "duration": row[4],
                "notify": row[5],
                "points": row[6],
                "priority": row[7],
                "start_at": row[8],
                "deleted": row[9]
            })

        conn.close()
        return results

    def get_recently_modified_tasks(self, limit: int = 20, include_deleted: bool = False) -> list[TaskWithTimestamp]:
        """
        Get the most recently modified tasks.

        Args:
            limit: Maximum number of tasks to return (default: 20)
            include_deleted: Whether to include deleted tasks (default: False)

        Returns:
            List of recently modified tasks with details
        """
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, uuid, body, due, duration, notify, points, priority, start_at, deleted, updated_at
            FROM tasks
            WHERE 1=1
        """
        params = []

        if not include_deleted:
            query += " AND (deleted IS NULL OR deleted = 0)"

        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "uuid": row[1],
                "body": row[2],
                "due": row[3],
                "duration": row[4],
                "notify": row[5],
                "points": row[6],
                "priority": row[7],
                "start_at": row[8],
                "deleted": row[9],
                "updated_at": row[10]
            })

        conn.close()
        return results

    def get_tasks_by_note(self, note_uuid: str) -> list[Task]:
        """
        Get all tasks associated with a specific note.
        Note: This searches for the note UUID in the task body.

        Args:
            note_uuid: The UUID of the note

        Returns:
            List of tasks that mention this note
        """
        conn = self.db_connection.get_connection()
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
                "id": row[0],
                "uuid": row[1],
                "body": row[2],
                "due": row[3],
                "duration": row[4],
                "notify": row[5],
                "points": row[6],
                "priority": row[7],
                "start_at": row[8],
                "deleted": row[9]
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
