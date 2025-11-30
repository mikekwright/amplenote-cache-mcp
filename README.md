# Amplenote MCP Server

A Model Context Protocol (MCP) server that provides access to your Amplenote SQLite database cache.

## Features

### Note Operations
- **search_notes**: Search notes using full-text search (FTS4)
- **get_note_by_uuid**: Retrieve complete note content by UUID
- **get_note_by_name**: Find notes by name (partial match)
- **list_notes**: List all notes with pagination
- **get_recently_modified_notes**: Get the most recently modified notes
- **get_note_references**: Get bidirectional note references

### Task Operations
- **search_tasks**: Search tasks by description/body text with duration, dates, and priority
- **list_tasks**: List and filter tasks (by priority, due date, etc.)
- **get_recently_modified_tasks**: Get the most recently modified tasks
- **get_tasks_by_note**: Find tasks associated with a specific note

## Installation

The solution uses nix, so you just need to use nix to develop.

```bash
nix develop --no-pure-eval
```

## Running commands

There are two different commands to help, one for starting mcp and one for Running tests.

```bash
nix develop --no-pure-eval --command mcp-start
```

```bash
nix develop --no-pure-eval --command run-tests
```

## Configuration

The database path can be configured via environment variable. By default, it uses:
`~/.config/ample-electron/amplenote.db` which is not a valid database file, update
with your local configuration.

### Automatic Setup for Claude Desktop

The easiest way to configure Claude Desktop is to use the built-in setup script:

```bash
# Use default database path
nix develop --no-pure-eval --command setup-claude-desktop

# Or specify a custom database path
nix develop --no-pure-eval --command setup-claude-desktop /path/to/your/amplenote.db
```

This will automatically:
- Detect your OS and locate the Claude Desktop config directory
- Create or update the MCP server configuration
- Configure the server to use nix for running
- Set the database path

After running the setup script, restart Claude Desktop for the changes to take effect.

### Manual Configuration

If you prefer to configure manually, add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "amplenote_cache": {
      "command": "nix",
      "args": ["develop", "--no-pure-eval", "--command", "mcp-start"],
      "cwd": "/path/to/amplenote_cache_mcp",
      "env": {
        "AMPLENOTE_DB_PATH": "~/.config/ample-electron/<some-file>.db"
      }
    }
  }
}
```

## Available Tools

### Note Tools

#### search_notes
Search your notes using full-text search.
- `query` (str): Search query
- `limit` (int): Max results (default: 10)

**Example**: Search for notes containing "project planning"

#### get_note_by_uuid
Get complete note content by UUID.
- `uuid` (str): Remote or local UUID

**Example**: Retrieve the full content of a specific note

#### get_note_by_name
Find a note by name (case-insensitive partial match).
- `name` (str): Note name to search for

**Example**: Find a note with "Meeting" in its title

#### list_notes
List all notes with pagination.
- `limit` (int): Max results (default: 20)
- `offset` (int): Skip N notes (default: 0)

**Example**: Get the first 20 notes sorted alphabetically

#### get_recently_modified_notes
Get the most recently modified notes.
- `limit` (int): Max results (default: 20)

**Example**: See what notes were updated recently

#### get_note_references
Get bidirectional references for a note.
- `uuid` (str): Note UUID

**Example**: Find all notes that link to or from a specific note

### Task Tools

#### search_tasks
Search tasks by description/body text.
- `query` (str): Search query to match in task body
- `limit` (int): Max results (default: 20)
- `include_deleted` (bool): Include deleted tasks (default: false)

**Returns**: Tasks with duration, due dates, priority (urgent/important level), and other details

**Example**: Find all tasks related to "documentation"

#### list_tasks
List tasks with filtering options.
- `limit` (int): Max results (default: 20)
- `include_deleted` (bool): Include deleted tasks (default: false)
- `priority` (int): Filter by priority level (0-3, where higher is more important)
- `has_due_date` (bool): Filter tasks with/without due dates

**Example**: Get all high-priority tasks with due dates

#### get_recently_modified_tasks
Get the most recently modified tasks.
- `limit` (int): Max results (default: 20)
- `include_deleted` (bool): Include deleted tasks (default: false)

**Returns**: Recently updated tasks with all details including timestamps

**Example**: See what tasks were recently updated

#### get_tasks_by_note
Get tasks associated with a specific note.
- `note_uuid` (str): Note UUID

**Example**: Find all tasks mentioned in a specific note

## Database Schema

The server reads from these Amplenote tables:
- `notes`: Note content and metadata (including `updated_at` timestamp)
- `tasks`: Task details (including priority, duration, due dates, and `updated_at` timestamp)
- `note_references`: Note-to-note references
- `notes_search_index`: FTS4 full-text search index

## Testing

The project includes a comprehensive test suite. To run tests:

```bash
nix develop --no-pure-eval --command run-tests
```

```bash
poetry run pytest
```

To run tests with coverage:

```bash
poetry run coverage run -m pytest
poetry run coverage report
```

## Development

This project follows idiomatic Python practices:
- Modular architecture with separate files for database, models, notes, and tasks
- Type hints throughout the codebase
- Comprehensive docstrings
- Small, focused functions with single responsibilities
- Proper error handling

### Code Style

The project uses `ruff` for linting and formatting:

```bash
poetry run ruff format app/
poetry run ruff check app/
```

## Architecture

The codebase is organized into focused modules:

- `app/database.py`: Database connection and configuration
- `app/models.py`: TypedDict models for data structures
- `app/notes.py`: Note-related functionality
- `app/tasks.py`: Task-related functionality
- `app/__main__.py`: FastMCP server and tool registration

This modular design makes the code easier to maintain, test, and extend.
