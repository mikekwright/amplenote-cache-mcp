import sqlite3

from .config import Settings


class DatabaseConnection:
    def __init__(self, settings: Settings):
        self.settings = settings

    def get_readonly_connection(self) -> sqlite3.Connection:
        db_path = self.settings.db_path.expanduser()
        if not db_path.exists():
            raise FileNotFoundError(f"Amplenote database not found at: {db_path}")

        # Open database in read-only mode using URI syntax
        return sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

