from typing import Optional, Literal
from datetime import datetime
import json
from pydantic import ValidationError

from .database import DatabaseConnection
from .models import Task, TaskAttrs, TaskContent, TaskQuery


class TasksService:
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection

    @staticmethod
    def _parse_task_attrs(attrs_json: str | None) -> TaskAttrs | None:
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
        if not content_json:
            return None
        try:
            data = json.loads(content_json)
            return TaskContent.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            # Log error but don't fail - return None for invalid data
            print(f"Warning: Failed to parse task content: {e}")
            return None

    def search_tasks(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Task]:
        conn = self.db_connection.get_readonly_connection()
        cursor = conn.cursor()

        sql_query = """
            SELECT
              id, uuid, local_uuid, remote_uuid, deleted, calendar_sync_required, notify_at, attrs,
              content, due, done, is_scheduled_bullet, parent_uuid
            FROM tasks
            WHERE content LIKE ?
        """
        params = [f"%{query}%"]

        # if not include_deleted:
        #     sql_query += " AND (deleted IS NULL OR deleted = 0)"
        #
        # if not include_done:
        #     sql_query += " AND (done IS NULL OR done = 0)"

        sql_query += "LIMIT ? OFFSET ?"
        params.extend([str(limit), str(offset)])
        cursor.execute(sql_query, params)

        # Fetch and parse results
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
        offset: int = 0,
        include_deleted: bool = False,
        include_done: bool = False,
    ) -> list[Task]:
        conn = self.db_connection.get_readonly_connection()
        cursor = conn.cursor()

        query = """
            SELECT
              id, uuid, local_uuid, remote_uuid, deleted, calendar_sync_required, notify_at, attrs,
              content, due, done, is_scheduled_bullet, parent_uuid
            FROM tasks
            WHERE 1=1
        """

        if not include_deleted:
            query += " AND (deleted IS NULL OR deleted = 0)"

        if not include_done:
            query += " AND (done IS NULL OR done = 0)"

        query += "ORDER BY attrs->>'createdAt' LIMIT ? OFFSET ?"
        params = [limit, offset]

        cursor.execute(query, params)

        # Fetch and parse results with filtering
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
        conn = self.db_connection.get_readonly_connection()
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

    def get_tasks_by_created_date(
        self,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        limit: int = 20,
        include_deleted: bool = False,
        include_done: bool = False
    ) -> list[Task]:
        """
        Get tasks filtered by creation date from the attrs JSON field.

        Args:
            start_date: Unix timestamp for start of date range (inclusive)
            end_date: Unix timestamp for end of date range (inclusive)
            limit: Maximum number of tasks to return (default: 20)
            include_deleted: Whether to include deleted tasks (default: False)
            include_done: Whether to include completed tasks (default: False)

        Returns:
            List of tasks created within the date range, ordered by creation date descending
        """
        conn = self.db_connection.get_readonly_connection()
        cursor = conn.cursor()

        query = """
            SELECT
              id, uuid, local_uuid, remote_uuid, deleted, calendar_sync_required, notify_at, attrs,
              content, due, done, is_scheduled_bullet, parent_uuid
            FROM tasks
            WHERE attrs IS NOT NULL
        """
        params = []

        if not include_deleted:
            query += " AND (deleted IS NULL OR deleted = 0)"

        if not include_done:
            query += " AND (done IS NULL OR done = 0)"

        cursor.execute(query, params)

        # Post-process to filter by creation date from JSON
        results = []
        for row in cursor.fetchall():
            attrs = self._parse_task_attrs(row[7])

            # Skip if attrs parsing failed or no created_at
            if not attrs or attrs.created_at is None:
                continue

            # Apply date range filters
            if start_date is not None and attrs.created_at < start_date:
                continue
            if end_date is not None and attrs.created_at > end_date:
                continue

            results.append({
                "id": row[0],
                "uuid": row[1],
                "local_uuid": row[2],
                "remote_uuid": row[3],
                "deleted": False if row[4] == 0 else True,
                "calendar_sync_required": False if row[5] == 0 else True,
                "notify_at": None if row[6] is None or row[6] == 0 else datetime.fromtimestamp(row[6]),
                "attrs": attrs,
                "content": self._parse_task_content(row[8]),
                "due": None if row[9] is None or row[9] == 0 else datetime.fromtimestamp(row[9]),
                "done": False if row[10] == 0 else True,
                "is_scheduled_bullet": False if row[11] == 0 else True,
                "parent_uuid": row[12],
            })

        # Sort by creation date descending (most recent first)
        results.sort(key=lambda x: x["attrs"].created_at if x["attrs"] else 0, reverse=True)

        # Apply limit
        results = results[:limit]

        conn.close()
        return results

    def get_tasks_ordered_by_points(
        self,
        limit: int = 20,
        include_deleted: bool = False,
        include_done: bool = False,
        ascending: bool = False
    ) -> list[Task]:
        """
        Get tasks ordered by their point values from the attrs JSON field.

        Args:
            limit: Maximum number of tasks to return (default: 20)
            include_deleted: Whether to include deleted tasks (default: False)
            include_done: Whether to include completed tasks (default: False)
            ascending: Sort order - True for ascending, False for descending (default: False)

        Returns:
            List of tasks ordered by points
        """
        conn = self.db_connection.get_readonly_connection()
        cursor = conn.cursor()

        query = """
            SELECT
              id, uuid, local_uuid, remote_uuid, deleted, calendar_sync_required, notify_at, attrs,
              content, due, done, is_scheduled_bullet, parent_uuid
            FROM tasks
            WHERE attrs IS NOT NULL
        """
        params = []

        if not include_deleted:
            query += " AND (deleted IS NULL OR deleted = 0)"

        if not include_done:
            query += " AND (done IS NULL OR done = 0)"

        cursor.execute(query, params)

        # Post-process to extract and sort by points
        results = []
        for row in cursor.fetchall():
            attrs = self._parse_task_attrs(row[7])

            # Skip if attrs parsing failed or no points
            if not attrs or attrs.points is None:
                continue

            results.append({
                "id": row[0],
                "uuid": row[1],
                "local_uuid": row[2],
                "remote_uuid": row[3],
                "deleted": False if row[4] == 0 else True,
                "calendar_sync_required": False if row[5] == 0 else True,
                "notify_at": None if row[6] is None or row[6] == 0 else datetime.fromtimestamp(row[6]),
                "attrs": attrs,
                "content": self._parse_task_content(row[8]),
                "due": None if row[9] is None or row[9] == 0 else datetime.fromtimestamp(row[9]),
                "done": False if row[10] == 0 else True,
                "is_scheduled_bullet": False if row[11] == 0 else True,
                "parent_uuid": row[12],
            })

        # Sort by points
        results.sort(key=lambda x: x["attrs"].points if x["attrs"] else 0, reverse=not ascending)

        # Apply limit
        results = results[:limit]

        conn.close()
        return results

    def get_tasks_by_priority_flags(
        self,
        priority_filter: Literal["urgent", "important", "both", "none"],
        limit: int = 20,
        include_deleted: bool = False,
        include_done: bool = False
    ) -> list[Task]:
        """
        Get tasks filtered by priority flags (urgent, important) from the attrs JSON field.

        Args:
            priority_filter: Filter type:
                - "urgent": Tasks with U flag only (not I)
                - "important": Tasks with I flag only (not U)
                - "both": Tasks with both I and U flags
                - "none": Tasks with neither I nor U flags
            limit: Maximum number of tasks to return (default: 20)
            include_deleted: Whether to include deleted tasks (default: False)
            include_done: Whether to include completed tasks (default: False)

        Returns:
            List of tasks matching the priority filter criteria
        """
        conn = self.db_connection.get_readonly_connection()
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

        cursor.execute(query, params)

        # Post-process to filter by flags
        results = []
        for row in cursor.fetchall():
            attrs = self._parse_task_attrs(row[7])

            # Check flags
            flags = attrs.flags if attrs and attrs.flags else ""
            has_urgent = "U" in flags
            has_important = "I" in flags

            # Apply priority filter
            should_include = False
            if priority_filter == "urgent":
                should_include = has_urgent and not has_important
            elif priority_filter == "important":
                should_include = has_important and not has_urgent
            elif priority_filter == "both":
                should_include = has_urgent and has_important
            elif priority_filter == "none":
                should_include = not has_urgent and not has_important

            if not should_include:
                continue

            results.append({
                "id": row[0],
                "uuid": row[1],
                "local_uuid": row[2],
                "remote_uuid": row[3],
                "deleted": False if row[4] == 0 else True,
                "calendar_sync_required": False if row[5] == 0 else True,
                "notify_at": None if row[6] is None or row[6] == 0 else datetime.fromtimestamp(row[6]),
                "attrs": attrs,
                "content": self._parse_task_content(row[8]),
                "due": None if row[9] is None or row[9] == 0 else datetime.fromtimestamp(row[9]),
                "done": False if row[10] == 0 else True,
                "is_scheduled_bullet": False if row[11] == 0 else True,
                "parent_uuid": row[12],
            })

        # Apply limit
        results = results[:limit]

        conn.close()
        return results

    def query_tasks(self, query: TaskQuery) -> list[Task]:
        """
        Advanced task querying with comprehensive filtering capabilities.

        Uses the TaskQuery model to support filtering on all task fields including
        attrs metadata with range capabilities.

        Args:
            query: TaskQuery model with filter criteria

        Returns:
            List of tasks matching the query criteria
        """
        conn = self.db_connection.get_readonly_connection()
        cursor = conn.cursor()

        # Build base SQL query
        sql_query = """
            SELECT
              id, uuid, local_uuid, remote_uuid, deleted, calendar_sync_required, notify_at, attrs,
              content, due, done, is_scheduled_bullet, parent_uuid
            FROM tasks
            WHERE 1=1
        """
        params = []

        # Apply basic filters
        if not query.include_deleted:
            sql_query += " AND (deleted IS NULL OR deleted = 0)"

        if not query.include_done:
            sql_query += " AND (done IS NULL OR done = 0)"

        # Apply has_due_date filter
        if query.has_due_date is not None:
            if query.has_due_date:
                sql_query += " AND due IS NOT NULL"
            else:
                sql_query += " AND due IS NULL"

        # Apply due date range filters
        if query.due_after is not None:
            sql_query += " AND due >= ?"
            params.append(query.due_after)

        if query.due_before is not None:
            sql_query += " AND due <= ?"
            params.append(query.due_before)

        # Apply content search if specified
        if query.content_search:
            sql_query += " AND content LIKE ?"
            params.append(f"%{query.content_search}%")

        cursor.execute(sql_query, params)

        # Fetch all results and apply attrs-based filters
        results = []
        for row in cursor.fetchall():
            attrs = self._parse_task_attrs(row[7])
            content = self._parse_task_content(row[8])

            # Apply points filters
            if query.min_points is not None:
                if not attrs or attrs.points is None or attrs.points < query.min_points:
                    continue
            if query.max_points is not None:
                if not attrs or attrs.points is None or attrs.points > query.max_points:
                    continue

            # Apply victory value filters
            if query.min_victory_value is not None:
                if not attrs or attrs.victory_value is None or attrs.victory_value < query.min_victory_value:
                    continue
            if query.max_victory_value is not None:
                if not attrs or attrs.victory_value is None or attrs.victory_value > query.max_victory_value:
                    continue

            # Apply streak count filters
            if query.min_streak_count is not None:
                if not attrs or attrs.streak_count is None or attrs.streak_count < query.min_streak_count:
                    continue
            if query.max_streak_count is not None:
                if not attrs or attrs.streak_count is None or attrs.streak_count > query.max_streak_count:
                    continue

            # Apply created_at filters
            if query.created_after is not None:
                if not attrs or attrs.created_at is None or attrs.created_at < query.created_after:
                    continue
            if query.created_before is not None:
                if not attrs or attrs.created_at is None or attrs.created_at > query.created_before:
                    continue

            # Apply completed_at filters
            if query.completed_after is not None:
                if not attrs or attrs.completed_at is None or attrs.completed_at < query.completed_after:
                    continue
            if query.completed_before is not None:
                if not attrs or attrs.completed_at is None or attrs.completed_at > query.completed_before:
                    continue

            # Apply start_at filters
            if query.start_after is not None:
                if not attrs or attrs.start_at is None or attrs.start_at < query.start_after:
                    continue
            if query.start_before is not None:
                if not attrs or attrs.start_at is None or attrs.start_at > query.start_before:
                    continue

            # Apply flags filter
            if query.flags_filter is not None:
                flags = attrs.flags if attrs and attrs.flags else ""
                has_urgent = "U" in flags
                has_important = "I" in flags

                should_include = False
                if query.flags_filter == "urgent":
                    should_include = has_urgent and not has_important
                elif query.flags_filter == "important":
                    should_include = has_important and not has_urgent
                elif query.flags_filter == "both":
                    should_include = has_urgent and has_important
                elif query.flags_filter == "none":
                    should_include = not has_urgent and not has_important
                elif query.flags_filter == "any":
                    should_include = has_urgent or has_important

                if not should_include:
                    continue

            # Apply has_flags filter (must have all specified flags)
            if query.has_flags is not None:
                flags = attrs.flags if attrs and attrs.flags else ""
                if not all(flag in flags for flag in query.has_flags):
                    continue

            # Apply duration filters
            if query.has_duration is not None:
                has_duration = attrs and attrs.duration is not None
                if query.has_duration != has_duration:
                    continue

            if query.duration_equals is not None:
                if not attrs or attrs.duration != query.duration_equals:
                    continue

            # Apply is_recurring filter
            if query.is_recurring is not None:
                is_recurring = attrs and attrs.repeat is not None
                if query.is_recurring != is_recurring:
                    continue

            # Apply has_references filter
            if query.has_references is not None:
                has_references = attrs and attrs.references is not None and len(attrs.references) > 0
                if query.has_references != has_references:
                    continue

            # Apply references_uuid filter
            if query.references_uuid is not None:
                if not attrs or not attrs.references or query.references_uuid not in attrs.references:
                    continue

            # Build task result
            results.append({
                "id": row[0],
                "uuid": row[1],
                "local_uuid": row[2],
                "remote_uuid": row[3],
                "deleted": False if row[4] == 0 else True,
                "calendar_sync_required": False if row[5] == 0 else True,
                "notify_at": None if row[6] is None or row[6] == 0 else datetime.fromtimestamp(row[6]),
                "attrs": attrs,
                "content": content,
                "due": None if row[9] is None or row[9] == 0 else datetime.fromtimestamp(row[9]),
                "done": False if row[10] == 0 else True,
                "is_scheduled_bullet": False if row[11] == 0 else True,
                "parent_uuid": row[12],
            })

        # Apply sorting
        if query.sort_by == "points":
            results.sort(
                key=lambda x: x["attrs"].points if x["attrs"] and x["attrs"].points else 0,
                reverse=query.sort_descending
            )
        elif query.sort_by == "created":
            results.sort(
                key=lambda x: x["attrs"].created_at if x["attrs"] and x["attrs"].created_at else 0,
                reverse=query.sort_descending
            )
        elif query.sort_by == "completed":
            results.sort(
                key=lambda x: x["attrs"].completed_at if x["attrs"] and x["attrs"].completed_at else 0,
                reverse=query.sort_descending
            )
        elif query.sort_by == "victory_value":
            results.sort(
                key=lambda x: x["attrs"].victory_value if x["attrs"] and x["attrs"].victory_value else 0,
                reverse=query.sort_descending
            )
        elif query.sort_by == "streak_count":
            results.sort(
                key=lambda x: x["attrs"].streak_count if x["attrs"] and x["attrs"].streak_count else 0,
                reverse=query.sort_descending
            )
        else:  # Default to "due" or when sort_by is None
            results.sort(
                key=lambda x: x["due"].timestamp() if x["due"] else float('inf'),
                reverse=query.sort_descending
            )

        # Apply pagination
        start_idx = query.offset
        end_idx = start_idx + query.limit
        results = results[start_idx:end_idx]

        conn.close()
        return results
