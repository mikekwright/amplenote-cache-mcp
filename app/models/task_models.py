from datetime import datetime

from typing import TypedDict, Literal
from pydantic import BaseModel, Field, ConfigDict

from .task_attrs import TaskAttrs
from .task_content import TaskContent


class Task(TypedDict):
    """Task data model."""
    id: int
    uuid: str
    local_uuid: str
    remote_uuid: str
    deleted: bool
    calendar_sync_required: int
    notify_at: datetime | None
    attrs: TaskAttrs | None  # Parsed from JSON
    content: TaskContent | None  # Parsed from JSON
    due: datetime | None
    done: bool
    is_scheduled_bullet: bool
    parent_uuid: str


class TaskWithTimestamp(TypedDict):
    """Task with modification timestamp."""
    id: int
    uuid: str
    local_uuid: str
    remote_uuid: str
    deleted: bool
    calendar_sync_required: bool
    notify_at: datetime | None
    attrs: TaskAttrs | None  # Parsed from JSON
    content: TaskContent | None  # Parsed from JSON
    due: datetime | None
    done: bool
    is_scheduled_bullet: bool
    parent_uuid: str
    updated_at: str


# ============================================================================
# Task Query Models (Advanced Filtering)
# ============================================================================

class TaskQuery(BaseModel):
    """
    Comprehensive query model for filtering tasks.

    Supports filtering on all task fields including attrs metadata with range capabilities.
    All fields are optional - omitted fields are not used in filtering.
    """
    model_config = ConfigDict(populate_by_name=True)

    # Content/text search
    content_search: str | None = Field(None, description="Full-text search in task content")

    # Basic task fields
    include_deleted: bool = Field(False, description="Include deleted tasks")
    include_done: bool = Field(False, description="Include completed tasks")
    has_due_date: bool | None = Field(None, description="Filter tasks with/without due dates")
    due_before: int | None = Field(None, description="Unix timestamp - tasks due before this date")
    due_after: int | None = Field(None, description="Unix timestamp - tasks due after this date")

    # Points filtering (range)
    min_points: float | None = Field(None, description="Minimum points value")
    max_points: float | None = Field(None, description="Maximum points value")

    # Victory value filtering (range)
    min_victory_value: float | None = Field(None, alias="minVictoryValue", description="Minimum victory value")
    max_victory_value: float | None = Field(None, alias="maxVictoryValue", description="Maximum victory value")

    # Streak count filtering (range)
    min_streak_count: int | None = Field(None, alias="minStreakCount", description="Minimum streak count")
    max_streak_count: int | None = Field(None, alias="maxStreakCount", description="Maximum streak count")

    # Timestamp filtering (range) - Unix timestamps
    created_after: int | None = Field(None, alias="createdAfter", description="Unix timestamp - created after this date")
    created_before: int | None = Field(None, alias="createdBefore", description="Unix timestamp - created before this date")
    completed_after: int | None = Field(None, alias="completedAfter", description="Unix timestamp - completed after this date")
    completed_before: int | None = Field(None, alias="completedBefore", description="Unix timestamp - completed before this date")
    start_after: int | None = Field(None, alias="startAfter", description="Unix timestamp - starts after this date")
    start_before: int | None = Field(None, alias="startBefore", description="Unix timestamp - starts before this date")

    # Flag filtering
    flags_filter: Literal["urgent", "important", "both", "none", "any"] | None = Field(
        None,
        alias="flagsFilter",
        description="Filter by priority flags: 'urgent' (U only), 'important' (I only), 'both' (I and U), 'none' (neither), 'any' (has at least one)"
    )
    has_flags: str | None = Field(None, alias="hasFlags", description="Tasks must have all specified flags (e.g., 'IU', 'D')")

    # Duration filtering
    has_duration: bool | None = Field(None, alias="hasDuration", description="Filter tasks with/without duration")
    duration_equals: str | None = Field(None, alias="durationEquals", description="Exact duration match (ISO 8601 format)")

    # Repeat/recurring filtering
    is_recurring: bool | None = Field(None, alias="isRecurring", description="Filter recurring/non-recurring tasks")

    # Reference filtering
    has_references: bool | None = Field(None, alias="hasReferences", description="Filter tasks with/without references")
    references_uuid: str | None = Field(None, alias="referencesUuid", description="Tasks that reference this UUID")

    # Sorting
    sort_by: Literal["due", "points", "created", "completed", "victory_value", "streak_count"] | None = Field(
        None,
        alias="sortBy",
        description="Sort order: 'due', 'points', 'created', 'completed', 'victory_value', 'streak_count'"
    )
    sort_descending: bool = Field(False, alias="sortDescending", description="Sort in descending order (default: False)")

    # Pagination
    limit: int = Field(20, ge=1, le=1000, description="Maximum number of results (1-1000)")
    offset: int = Field(0, ge=0, description="Number of results to skip")
