# Amplenote Database Schema

Database File: `~/.config/ample-electron/eea3554e-27f8-11ee-8a5a-4e62ba9bf71c.db`

## Tables Overview

1. [notes](#notes)
2. [notes_search_index](#notes_search_index)
3. [notes_search_index_segments](#notes_search_index_segments)
4. [notes_search_index_segdir](#notes_search_index_segdir)
5. [notes_search_index_docsize](#notes_search_index_docsize)
6. [notes_search_index_stat](#notes_search_index_stat)
7. [reducers](#reducers)
8. [note_references](#note_references)
9. [tasks](#tasks)
10. [task_references](#task_references)
11. [search_tokenizer](#search_tokenizer)
12. [sqlite_sequence](#sqlite_sequence)

---

## Table Schemas

### notes

Main table storing note data.

```sql
CREATE TABLE notes(
    remote_uuid CHARACTER(36),
    local_uuid CHARACTER(36),
    name TEXT DEFAULT '' NOT NULL,
    metadata TEXT,
    text TEXT DEFAULT '' NOT NULL,
    remote_content TEXT,
    remote_digest TEXT,
    remote_key TEXT
);
```

**Indexes:**
- `notes_remote_uuid` - UNIQUE INDEX ON notes(remote_uuid)
- `notes_local_uuid` - UNIQUE INDEX ON notes(local_uuid)

**Triggers:**
- `notes_after_insert` - Inserts into notes_search_index after note creation
- `notes_before_delete` - Removes from notes_search_index before note deletion
- `notes_before_update_name` - Removes old entry from search index before name update
- `notes_after_update_name` - Inserts new entry into search index after name update
- `notes_before_update_text` - Removes old entry from search index before text update
- `notes_after_update_text` - Inserts new entry into search index after text update

---

### notes_search_index

Virtual FTS4 (Full-Text Search) table for searching note names and text content.

```sql
CREATE VIRTUAL TABLE notes_search_index USING fts4(
    content='notes',
    name,
    text,
    tokenize=porter
);
```

**Purpose:** Enables full-text search on note names and content using Porter stemming algorithm.

---

### notes_search_index_segments

Internal FTS4 table storing search index segments.

```sql
CREATE TABLE IF NOT EXISTS 'notes_search_index_segments'(
    blockid INTEGER PRIMARY KEY,
    block BLOB
);
```

**Purpose:** Stores the actual FTS index data in blocks.

---

### notes_search_index_segdir

Internal FTS4 table managing search index directory structure.

```sql
CREATE TABLE IF NOT EXISTS 'notes_search_index_segdir'(
    level INTEGER,
    idx INTEGER,
    start_block INTEGER,
    leaves_end_block INTEGER,
    end_block INTEGER,
    root BLOB,
    PRIMARY KEY(level, idx)
);
```

**Purpose:** Directory structure for FTS index segments.

---

### notes_search_index_docsize

Internal FTS4 table tracking document sizes.

```sql
CREATE TABLE IF NOT EXISTS 'notes_search_index_docsize'(
    docid INTEGER PRIMARY KEY,
    size BLOB
);
```

**Purpose:** Stores size information for documents in the FTS index.

---

### notes_search_index_stat

Internal FTS4 table storing index statistics.

```sql
CREATE TABLE IF NOT EXISTS 'notes_search_index_stat'(
    id INTEGER PRIMARY KEY,
    value BLOB
);
```

**Purpose:** Statistical information about the FTS index.

---

### reducers

Stores application state/reducer data.

```sql
CREATE TABLE reducers(
    name TEXT NOT NULL,
    value TEXT
);
```

**Indexes:**
- `reducers_name` - UNIQUE INDEX ON reducers(name)

**Purpose:** Key-value store for application state management.

---

### note_references

Tracks references between notes.

```sql
CREATE TABLE note_references(
    local_uuid CHARACTER(36),
    remote_uuid CHARACTER(36),
    referenced_uuid CHARACTER(38)
);
```

**Indexes:**
- `note_references_remote_uuid` - INDEX ON note_references(remote_uuid)
- `note_references_local_uuid` - INDEX ON note_references(local_uuid)
- `note_references_referenced_uuid` - INDEX ON note_references(referenced_uuid)

**Purpose:** Maps relationships between notes (e.g., when one note links to another).

---

### tasks

Main table storing task/todo items.

```sql
CREATE TABLE tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid CHARACTER(36) NOT NULL,
    local_uuid CHARACTER(36),
    remote_uuid CHARACTER(36),
    deleted INTEGER DEFAULT 0 NOT NULL,
    calendar_sync_required INTEGER DEFAULT 0 NOT NULL,
    notify_at INTEGER,
    attrs TEXT,
    content TEXT,
    due INTEGER,
    done INTEGER DEFAULT 0 NOT NULL,
    is_scheduled_bullet INTEGER DEFAULT 0 NOT NULL,
    parent_uuid CHARACTER(36)
);
```

**Indexes:**
- `tasks_uuid` - UNIQUE INDEX ON tasks(uuid)
- `tasks_local_uuid` - INDEX ON tasks(local_uuid)
- `tasks_remote_uuid` - INDEX ON tasks(remote_uuid)
- `tasks_notify_at` - INDEX ON tasks(notify_at)
- `tasks_due` - INDEX ON tasks(due)

**Purpose:** Stores all task data including completion status, due dates, notifications, and hierarchy.

#### JSON Schema for `content` Column

The `content` column stores the task description as a ProseMirror document structure (JSON array).

**Structure:**
```typescript
[
  {
    "type": "paragraph",
    "content": [
      {
        "type": "text",
        "text": "Task description text",
        "marks": [                    // Optional text formatting
          {"type": "em"},             // Italic
          {"type": "strong"},         // Bold
          {"type": "code"}            // Inline code
        ]
      },
      {
        "type": "link",
        "attrs": {
          "href": "https://example.com",
          "description": "",          // Optional
          "media": null              // Optional
        },
        "content": [
          {"type": "text", "text": "Link text"}
        ]
      },
      {
        "type": "hard_break"         // Line break within paragraph
      }
    ]
  }
]
```

**Node Types:**
- `paragraph` - Container for inline content
- `text` - Plain text node
- `link` - Hyperlink with href and optional description/media
- `hard_break` - Line break within a paragraph

**Text Marks (formatting):**
- `em` - Italic/emphasis
- `strong` - Bold
- `code` - Inline code formatting

**Example:**
```json
[
  {
    "type": "paragraph",
    "content": [
      {"type": "text", "text": "Review the "},
      {"type": "text", "marks": [{"type": "em"}], "text": "important"},
      {"type": "text", "text": " ticket "},
      {
        "type": "link",
        "attrs": {"href": "https://example.com/ticket/123"},
        "content": [{"type": "text", "text": "TICKET-123"}]
      }
    ]
  }
]
```

#### JSON Schema for `attrs` Column

The `attrs` column stores task metadata and attributes (JSON object).

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `createdAt` | integer | Unix timestamp (seconds) when task was created |
| `completedAt` | integer | Unix timestamp when task was completed (if done) |
| `crossedOutAt` | integer | Unix timestamp when task was crossed out |
| `startAt` | integer | Unix timestamp for scheduled start time |
| `notify` | string | ISO 8601 duration for notification timing (e.g., `"PT5M"` = 5 minutes) |
| `duration` | string | ISO 8601 duration for task length (e.g., `"PT30M"` = 30 minutes, `"PT1H"` = 1 hour) |
| `repeat` | string | Recurrence rule in iCalendar RRULE format or ISO 8601 duration |
| `startRule` | string | ISO 8601 duration offset for start time calculation |
| `dueDayPart` | string | Part of day for due date (e.g., `"M"` = morning) |
| `flags` | string | Single-character flags combined (e.g., `"IU"`, `"DIU"`) |
| `points` | number | Point value/score for task (can be decimal) |
| `pointsUpdatedAt` | integer | Unix timestamp when points were last updated |
| `victoryValue` | number | Victory/completion value (can be decimal) |
| `streakCount` | integer | Number of consecutive completions for recurring tasks |
| `references` | array | Array of UUIDs for referenced notes/tasks |

**Flag Characters:**
- `I` - Important
- `U` - Urgent
- `D` - Delegated (or other domain-specific meaning)

**Repeat Formats:**

1. iCalendar RRULE format:
```
DTSTART:20250421T090000
RRULE:FREQ=WEEKLY;BYDAY=MO
```

2. ISO 8601 Duration (relative repeat):
```
P7DT9H      // 7 days and 9 hours
P1MT9H      // 1 month and 9 hours
P30DT9H     // 30 days and 9 hours
```

**Example - Simple completed task:**
```json
{
  "createdAt": 1760477809,
  "victoryValue": 1,
  "completedAt": 1761163010
}
```

**Example - Recurring scheduled task:**
```json
{
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
}
```

**Example - Task with references:**
```json
{
  "createdAt": 1758664814,
  "repeat": "P1MT9H",
  "startRule": "PT0H",
  "duration": "PT30M",
  "flags": "DI",
  "points": 0.5,
  "pointsUpdatedAt": 1761162794,
  "victoryValue": 10.4,
  "completedAt": 1761163890,
  "references": ["00000000-000f-11ef-8a67-7e9dd6e19a06"]
}
```

---

### task_references

Tracks relationships between tasks.

```sql
CREATE TABLE task_references(
    source_uuid CHARACTER(36),
    target_uuid CHARACTER(36),
    task_relation TEXT
);
```

**Purpose:** Maps relationships between tasks (e.g., dependencies, subtasks).

---

### search_tokenizer

Virtual FTS3 tokenizer table for search functionality.

```sql
CREATE VIRTUAL TABLE search_tokenizer USING fts3tokenize('porter');
```

**Purpose:** Provides Porter stemming tokenization for search queries.

---

### sqlite_sequence

SQLite internal table for AUTOINCREMENT counters.

```sql
CREATE TABLE sqlite_sequence(
    name,
    seq
);
```

**Purpose:** Tracks the next AUTOINCREMENT value for tables (e.g., tasks.id).

---

## Key Observations

### UUID System
- **remote_uuid**: UUID from the Amplenote server
- **local_uuid**: UUID for local-only or offline items
- The system supports both local and remote synchronization

### Full-Text Search
- Uses SQLite FTS4 extension with Porter stemming
- Automatically maintained via triggers on the notes table
- Searches both note names and content

### Task Management
- Tasks support hierarchy via `parent_uuid`
- Soft deletion via `deleted` flag
- Calendar integration via `calendar_sync_required`
- Scheduled bullets via `is_scheduled_bullet`
- Notifications via `notify_at` timestamp

### Synchronization
- Separate tracking of local and remote UUIDs
- `remote_content`, `remote_digest`, and `remote_key` fields suggest content versioning/syncing
