import sqlite3
from typing import List, Tuple


class ConversationMemory:
    """Prosta pamięć konwersacyjna oparta o SQLite"""

    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS messages(
            session TEXT,
            role TEXT,
            content TEXT
        )""")
        self.conn.commit()

    def add(self, session: str, role: str, content: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO messages(session, role, content) VALUES(?,?,?)",
            (session, role, content)
        )
        self.conn.commit()

    def get(self, session: str) -> List[Tuple[str, str]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT role, content FROM messages WHERE session=? ORDER BY rowid",
            (session,)
        )
        return cur.fetchall()
