"""
Note-related tools for Amplenote MCP Server.
"""

from .database import DatabaseConnection
from .models import Note, NoteBasic, NoteReference, NoteReferences, NoteSearchResult, NoteWithTimestamp


class NotesService:
    """
    Service class for note-related operations.

    This class encapsulates all note-related business logic and database queries.
    It follows dependency injection principles by accepting a DatabaseConnection
    instance rather than creating database connections directly.

    Args:
        db_connection: Database connection factory for creating connections
    """

    def __init__(self, db_connection: DatabaseConnection):
        """
        Initialize the notes service.

        Args:
            db_connection: Database connection factory
        """
        self.db_connection = db_connection

    def search_notes(self, query: str, limit: int = 10) -> list[NoteSearchResult]:
        """
        Search notes using full-text search.

        Args:
            query: Search query string
            limit: Maximum number of results to return (default: 10)

        Returns:
            List of matching notes with uuid, name, and snippet
        """
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()

        # Use FTS4 virtual table for full-text search
        cursor.execute("""
            SELECT n.remote_uuid, n.name, snippet(notes_search_index, '[', ']', '...', -1, 32) as snippet
            FROM notes_search_index
            JOIN notes n ON notes_search_index.docid = n.rowid
            WHERE notes_search_index MATCH ?
            LIMIT ?
        """, (query, limit))

        results = []
        for row in cursor.fetchall():
            results.append({
                "uuid": row[0],
                "name": row[1],
                "snippet": row[2]
            })

        conn.close()
        return results

    def get_note_by_uuid(self, uuid: str) -> Note | dict[str, str]:
        """
        Get the full content of a note by its UUID.

        Args:
            uuid: The remote_uuid of the note

        Returns:
            Note details including name, text, and metadata
        """
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT remote_uuid, local_uuid, name, metadata, text, remote_content, remote_digest
            FROM notes
            WHERE remote_uuid = ? OR local_uuid = ?
        """, (uuid, uuid))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return {"error": f"Note with UUID {uuid} not found"}

        return {
            "remote_uuid": row[0],
            "local_uuid": row[1],
            "name": row[2],
            "metadata": row[3],
            "text": row[4],
            "remote_content": row[5],
            "remote_digest": row[6]
        }

    def get_note_by_name(self, name: str) -> Note | dict[str, str]:
        """
        Get the full content of a note by its name.

        Args:
            name: The name of the note (case-insensitive partial match)

        Returns:
            Note details including uuid, text, and metadata
        """
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT remote_uuid, local_uuid, name, metadata, text, remote_content, remote_digest
            FROM notes
            WHERE name LIKE ?
            LIMIT 1
        """, (f"%{name}%",))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return {"error": f"Note with name containing '{name}' not found"}

        return {
            "remote_uuid": row[0],
            "local_uuid": row[1],
            "name": row[2],
            "metadata": row[3],
            "text": row[4],
            "remote_content": row[5],
            "remote_digest": row[6]
        }

    def list_notes(self, limit: int = 20, offset: int = 0) -> list[NoteBasic]:
        """
        List all notes with pagination.

        Args:
            limit: Maximum number of notes to return (default: 20)
            offset: Number of notes to skip (default: 0)

        Returns:
            List of notes with uuid and name
        """
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT remote_uuid, local_uuid, name
            FROM notes
            ORDER BY name
            LIMIT ? OFFSET ?
        """, (limit, offset))

        results = []
        for row in cursor.fetchall():
            results.append({
                "remote_uuid": row[0],
                "local_uuid": row[1],
                "name": row[2]
            })

        conn.close()
        return results

    def get_recently_modified_notes(self, limit: int = 20) -> list[NoteWithTimestamp]:
        """
        Get the most recently modified notes.

        Args:
            limit: Maximum number of notes to return (default: 20)

        Returns:
            List of recently modified notes with uuid, name, and modification timestamp
        """
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT remote_uuid, local_uuid, name, updated_at
            FROM notes
            ORDER BY updated_at DESC
            LIMIT ?
        """, (limit,))

        results = []
        for row in cursor.fetchall():
            results.append({
                "remote_uuid": row[0],
                "local_uuid": row[1],
                "name": row[2],
                "updated_at": row[3]
            })

        conn.close()
        return results

    def get_note_references(self, uuid: str) -> NoteReferences:
        """
        Get all notes that reference a given note, and all notes it references.

        Args:
            uuid: The UUID of the note to check references for

        Returns:
            Dictionary with 'referenced_by' and 'references' lists
        """
        conn = self.db_connection.get_connection()
        cursor = conn.cursor()

        # Notes that reference this note
        cursor.execute("""
            SELECT nr.local_uuid, n.name
            FROM note_references nr
            LEFT JOIN notes n ON nr.local_uuid = n.local_uuid
            WHERE nr.referenced_uuid = ?
        """, (uuid,))

        referenced_by = []
        for row in cursor.fetchall():
            referenced_by.append({
                "uuid": row[0],
                "name": row[1]
            })

        # Notes that this note references
        cursor.execute("""
            SELECT nr.referenced_uuid, n.name
            FROM note_references nr
            LEFT JOIN notes n ON nr.referenced_uuid = n.local_uuid
            WHERE nr.local_uuid = ?
        """, (uuid,))

        references = []
        for row in cursor.fetchall():
            references.append({
                "uuid": row[0],
                "name": row[1]
            })

        conn.close()

        return {
            "referenced_by": referenced_by,
            "references": references
        }
