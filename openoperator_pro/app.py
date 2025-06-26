import os
import asyncio
from multiprocessing import Process, Queue
from typing import List

import gradio as gr

from .agent.loop import run_agent
from .memory.sqlite_graph import MemoryManager

MODEL_OPTIONS = {
    "llava": "LLaVA-Next-13B-RAG",
    "fuyu": "Fuyu-8B",
    "gpt4o": "GPT-4o-Vision"
}

memory = MemoryManager("agent_memory.db")


def start_agent(url: str, task: str, model: str):
    queue: Queue = Queue()

    def _run(q: Queue):
        for log in run_agent(url, task, model, memory):
            q.put(log)
        q.put("__done__")

    p = Process(target=_run, args=(queue,))
    p.start()
    logs: List[str] = []
    while True:
        msg = queue.get()
        if msg == "__done__":
            break
        logs.append(msg)
    p.join()
    return "\n".join(logs)


def main():
    with gr.Blocks(title="OpenOperator-Pro") as demo:
        url = gr.Textbox(label="URL", value="https://example.com")
        task = gr.Textbox(label="Polecenie")
        model = gr.Dropdown(label="Model wizji", choices=list(MODEL_OPTIONS.keys()), value="llava")
        out = gr.Textbox(label="Log")
        btn = gr.Button("Start")

        btn.click(fn=start_agent, inputs=[url, task, model], outputs=out)

    demo.launch()


if __name__ == "__main__":
    main()
