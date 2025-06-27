import asyncio
from typing import List, Dict
from .loop import run_agent
from memory.sqlite_graph import ConversationMemory


class AgentManager:
    """Coordinate multiple agents concurrently."""

    def __init__(self, db_path: str = "openoperator.db"):
        self.memory = ConversationMemory(db_path)

    async def run_agents(self, tasks: List[Dict]):
        coros = [
            run_agent(t["url"], t["instruction"], t.get("model", "llava-next"), self.memory, session_id=t.get("session_id", str(i)))
            for i, t in enumerate(tasks)
        ]
        return await asyncio.gather(*coros)
