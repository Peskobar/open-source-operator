import argparse
import asyncio
import subprocess

from agent.loop import run_agent
from memory import get_memory


def cmd_run(args):
    mem = get_memory()
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


def cmd_monitor(args):
    from tools.monitor_resources import monitor
    monitor(args.output)


def cmd_test(args):
    subprocess.call(["pytest"])  # pragma: no cover - CLI passthrough


def main():
    parser = argparse.ArgumentParser(description="OpenOperator command line")
    sub = parser.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="Run an agent")
    r.add_argument("--url", required=True)
    r.add_argument("--task", required=True)
    r.add_argument("--vision_model", default="llava-next")
    r.add_argument("--max_steps", type=int, default=20)
    r.set_defaults(func=cmd_run)

    m = sub.add_parser("monitor", help="Monitor system resources")
    m.add_argument("--output", default="resources.csv")
    m.set_defaults(func=cmd_monitor)

    t = sub.add_parser("test", help="Run unit tests")
    t.set_defaults(func=cmd_test)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
