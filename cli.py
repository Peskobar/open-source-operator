import argparse
import asyncio
from agent.loop import run_agent
from memory.sqlite_graph import ConversationMemory


def main():
    parser = argparse.ArgumentParser(description="Run OpenOperator in CLI mode")
    parser.add_argument("--url", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--vision_model", default="llava-next")
    parser.add_argument("--max_steps", type=int, default=20)
    args = parser.parse_args()

    mem = ConversationMemory("openoperator.db")
    asyncio.run(
        run_agent(
            args.url,
            args.task,
            args.vision_model,
            mem,
            session_id="cli",
            max_steps=args.max_steps,
        )
    )


if __name__ == "__main__":
    main()
