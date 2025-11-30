"""
Amplenote MCP Server

A FastMCP server that provides access to your Amplenote SQLite database cache.
"""
import logging

from fastmcp import FastMCP

from .models import Note, NoteBasic, NoteReferences, NoteSearchResult, Task, TaskQuery
from .notes import NotesService
from .tasks import TasksService


logger = logging.getLogger(__name__)


class MCPApp:
    def __init__(self, notes_service: NotesService, tasks_service: TasksService):
        self._notes_service = notes_service
        self._tasks_service = tasks_service
        self._mcp = FastMCP("Amplenote Cache")

    def _setup_note_tools(self):
        mcp = self._mcp

        @mcp.tool()
        def search_notes(query: str, limit: int = 10, offset: int = 0) -> list[NoteSearchResult]:
            return self._notes_service.search_notes(query, limit)

        @mcp.tool()
        def get_note_by_uuid(uuid: str) -> Note | None:
            return self._notes_service.get_note_by_uuid(uuid)

        @mcp.tool()
        def get_note_by_name(name: str) -> Note | None:
            return self._notes_service.get_note_by_name(name)

        @mcp.tool()
        def list_notes(limit: int = 20, offset: int = 0) -> list[NoteBasic]:
            return self._notes_service.list_notes(limit, offset)

        @mcp.tool()
        def get_note_references(uuid: str) -> NoteReferences:
            return self._notes_service.get_note_references(uuid)

    def _setup_task_tools(self):
        mcp = self._mcp
        
        @mcp.tool()
        def search_tasks(query: str, limit: int = 20, offset: int = 0) -> list[Task]:
            return self._tasks_service.search_tasks(query, limit, offset)

        @mcp.tool()
        def list_tasks(
            limit: int = 20,
            offset: int = 0,
            include_deleted: bool = False,
            include_done: bool = False,
        ) -> list[Task]:
            return self._tasks_service.list_tasks(limit, offset, include_deleted, include_done)

        @mcp.tool()
        def get_tasks_by_note(
            note_uuid: str,
            include_deleted: bool = False,
            include_done: bool = False
        ) -> list[Task]:
            return self._tasks_service.get_tasks_by_note(note_uuid, include_deleted, include_done)

        @mcp.tool()
        def query_tasks(query: dict) -> list[Task]:
            task_query = TaskQuery(**query)
            return self._tasks_service.query_tasks(task_query)

    def run(self):
        logger.debug('Initializing MCP Server note tools')
        self._setup_note_tools()

        logger.debug('Initializing MCP Server task tools')
        self._setup_task_tools()

        logger.info('Starting MCP Server')
        self._mcp.run()
