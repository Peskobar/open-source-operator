import asyncio
import multiprocessing as mp
from typing import List, Dict

from .loop import run_agent
from memory import get_memory


def _worker(task: Dict):
    mem = get_memory({"path": task.get("db_path", "openoperator.db")})
    return asyncio.run(
        run_agent(
            task["url"],
            task["instruction"],
            task.get("model", "llava-next"),
            mem,
            session_id=task.get("session_id", str(mp.current_process().pid)),
        )
    )


class AgentManager:
    """Coordinate multiple agents concurrently."""

    def __init__(self, db_path: str = "openoperator.db"):
        self.memory_cfg = {"path": db_path}
        self.memory = get_memory(self.memory_cfg)

    async def run_agents(self, tasks: List[Dict]):
        coros = [
            run_agent(
                t["url"],
                t["instruction"],
                t.get("model", "llava-next"),
                self.memory,
                session_id=t.get("session_id", str(i)),
            )
            for i, t in enumerate(tasks)
        ]
        return await asyncio.gather(*coros)

    def run_parallel(self, tasks: List[Dict]):
        for t in tasks:
            t["db_path"] = self.memory_cfg["path"]
        with mp.Pool(len(tasks)) as pool:
            return pool.map(_worker, tasks)
