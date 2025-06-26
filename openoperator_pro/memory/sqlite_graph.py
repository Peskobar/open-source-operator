import sqlite3
from langgraph.graph import MessageGraphMemory


class MemoryManager:
    def __init__(self, path: str):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self._ensure()
        self.mem = MessageGraphMemory()

    def _ensure(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY, msg TEXT)")
        self.conn.commit()

    def add(self, msg: str):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO history(msg) VALUES (?)", (msg,))
        self.conn.commit()
        self.mem.add_user_message(msg)

    def plan(self, prompt: str) -> str:
        self.add(prompt)
        # placeholder for planning, using previous messages
        return '{"type": "noop"}'
