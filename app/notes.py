"""
Note-related tools for Amplenote MCP Server.
"""
import logging

from .database import DatabaseConnection
from .models import Note, NoteBasic, NoteReference, NoteReferences, NoteSearchResult, NoteWithTimestamp


logger = logging.getLogger(__name__)


class NotesService:
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection

    def search_notes(self, query: str, limit: int = 10, offset: int = 0) -> list[NoteSearchResult]:
        conn = self.db_connection.get_readonly_connection()
        cursor = conn.cursor()

        # Use FTS4 virtual table for full-text search
        cursor.execute("""
            SELECT n.remote_uuid, n.name, snippet(notes_search_index, '[', ']', '...', -1, 32) as snippet
            FROM notes_search_index
            JOIN notes n ON notes_search_index.docid = n.rowid
            WHERE notes_search_index MATCH ?
            LIMIT ? OFFSET ?
        """, (query, limit, offset))

        results = []
        for row in cursor.fetchall():
            results.append({
                "uuid": row[0],
                "name": row[1],
                "snippet": row[2]
            })

        conn.close()
        return results

    def get_note_by_uuid(self, uuid: str) -> Note | None:
        conn = self.db_connection.get_readonly_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT remote_uuid, local_uuid, name, metadata, text, remote_content, remote_digest
            FROM notes
            WHERE remote_uuid = ? OR local_uuid = ?
        """, (uuid, uuid))

        row = cursor.fetchone()
        conn.close()

        if not row:
            logger.info("Note with UUID %s not found", uuid)
            return None

        return {
            "remote_uuid": row[0],
            "local_uuid": row[1],
            "name": row[2],
            "metadata": row[3],
            "text": row[4],
            "remote_content": row[5],
            "remote_digest": row[6]
        }

    def get_note_by_name(self, name: str) -> Note | None:
        conn = self.db_connection.get_readonly_connection()
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
            logger.info("Note with name containing %s not found", name)
            return None

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
        List all notes with pagination ordered by last change.
        """
        conn = self.db_connection.get_readonly_connection()
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

    def get_note_references(self, reference_note_uuid: str) -> NoteReferences:
        conn = self.db_connection.get_readonly_connection()
        cursor = conn.cursor()

        # Notes that reference this note
        cursor.execute("""
            SELECT nr.local_uuid, n.name
            FROM note_references nr
            LEFT JOIN notes n ON nr.local_uuid = n.local_uuid
            WHERE nr.referenced_uuid = ?
        """, (reference_note_uuid,))

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
        """, (reference_note_uuid,))

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
