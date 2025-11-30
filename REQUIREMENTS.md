Amplenote cache MCP
===========================================

This is an mcp that was quickly setup for local usage as no mcp solution
for amplenote exists, and amplenote is just much better for task management
compared to notion.

Core Features
--------------------------------------------

Core features include:
* Ability to search all notes by name and content.
* Ability to search all tasks by description and get their duration, dates, urgent and important level.
* Ability to get the most recently modified notes.
* Ability to get the most recently created tasks (sorted by createdAt from attrs JSON).
* Ability to get the most recent tasks and not have to be restarted.
* Ability to select tasks by the date they were created (stored in attrs JSON).
* Ability to select tasks ordered by their point values.
* Ability to filter tasks by priority flags (urgent, important, none, or both).

MCP Tool Features:
* `search_tasks` and `list_tasks` support advanced filtering parameters:
  - `min_points` and `max_points`: Filter tasks by point value range
  - `flags_filter`: Filter by priority flags ("urgent", "important", "both", "none")
  - `sort_by`: Sort results by "due" (default), "points", or "created" date
* `get_recently_created_tasks`: Renamed from `get_recently_modified_tasks` to accurately reflect that it uses createdAt from attrs JSON instead of the non-existent updated_at field.
* **NEW: `query_tasks`** - Advanced task querying with comprehensive filtering capabilities:
  - Uses a structured TaskQuery model instead of simple string queries
  - Supports filtering on ALL task fields including all attrs metadata
  - Range capabilities for numeric and timestamp fields (min/max, before/after)
  - Content/Text Search: Full-text search in task content
  - Points Filtering: `min_points`, `max_points`
  - Victory Value Filtering: `minVictoryValue`, `maxVictoryValue`
  - Streak Count Filtering: `minStreakCount`, `maxStreakCount`
  - Timestamp Filtering (range, Unix timestamps):
    - `createdAfter`, `createdBefore`: Filter by creation date
    - `completedAfter`, `completedBefore`: Filter by completion date
    - `startAfter`, `startBefore`: Filter by start date
    - `due_before`, `due_after`: Filter by due date
  - Flag Filtering:
    - `flagsFilter`: "urgent" (U only), "important" (I only), "both" (I and U), "none" (neither), "any" (has at least one)
    - `hasFlags`: Must have all specified flags (e.g., "IU" for both important and urgent)
  - Duration Filtering:
    - `hasDuration`: Filter tasks with/without duration
    - `durationEquals`: Exact duration match (ISO 8601 format, e.g., "PT30M")
  - Recurring Filtering: `isRecurring` - Filter recurring/non-recurring tasks
  - Reference Filtering:
    - `hasReferences`: Filter tasks with/without references
    - `referencesUuid`: Tasks that reference a specific UUID
  - Sorting: `sortBy` supports "due", "points", "created", "completed", "victory_value", "streak_count"
    - `sortDescending`: Control sort direction
  - Pagination: `limit` (1-1000) and `offset` for result pagination

Development Requirements
-----------------------------------------------

The final solution must:
* Have unit tests to verify the flow
* Be able to target a different location for amplenote database.
* Be very idiomatic in the python code
* Support smaller functions and more modules to make the solution clean.

