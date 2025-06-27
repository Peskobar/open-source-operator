import asyncio
import argparse
import json
import random

from agent.loop import run_agent
from memory.sqlite_graph import ConversationMemory

TASKS = [
    ("https://webarena.dev/shop", "Dodaj najtańszą żarówkę E27 do koszyka"),
    ("https://webarena.dev/calendar", "Zaplanuj spotkanie jutro o 15"),
    ("https://webarena.dev/docs", "Znajdź sekcję FAQ")
]


def main(episodes: int, report: str):
    memory = ConversationMemory("/tmp/bench.db")
    results = []
    for i in range(episodes):
        url, task = random.choice(TASKS)
        res = asyncio.run(run_agent(url, task, "llava-next", memory, session_id=str(i)))
        success = "result" in res
        steps = int(res.get("steps", 0)) if success else 0
        results.append({"success": success, "steps": steps})
    success_rate = sum(r["success"] for r in results) / episodes
    avg_steps = sum(r["steps"] for r in results) / max(1, sum(r["success"] for r in results))
    with open(report, "w") as f:
        json.dump({"success_rate": success_rate, "avg_steps": avg_steps}, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=5)
    parser.add_argument("--report", type=str, default="report.json")
    args = parser.parse_args()
    main(args.episodes, args.report)
