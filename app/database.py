"""
Database connection utilities for Amplenote MCP Server.
"""

import sqlite3

from .config import Settings


class DatabaseConnection:
    """
    Database connection factory that manages SQLite connections.

    This class is responsible for creating read-only database connections to the
    Amplenote SQLite database. All connections are opened in read-only mode to
    prevent accidental modifications to the Amplenote database.

    Args:
        settings: Application settings containing database configuration
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    def get_connection(self) -> sqlite3.Connection:
        """
        Create and return a read-only database connection.

        The connection is opened with SQLite's read-only mode (mode=ro) to ensure
        the application cannot modify the Amplenote database.

        Returns:
            sqlite3.Connection: Read-only connection to the Amplenote database

        Raises:
            FileNotFoundError: If the database file does not exist
        """
        db_path = self.settings.db_path.expanduser()
        if not db_path.exists():
            raise FileNotFoundError(f"Amplenote database not found at: {db_path}")

        # Open database in read-only mode using URI syntax
        return sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

