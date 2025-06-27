import multiprocessing as mp
import asyncio
import os
import gradio as gr

from agent.loop import run_agent
from memory.sqlite_graph import ConversationMemory


def start(url: str, task: str, model: str):
    memory = ConversationMemory("openoperator.db")
    max_steps = int(os.getenv("MAX_STEPS", "20"))
    p = mp.Process(target=lambda: asyncio.run(run_agent(url, task, model, memory, max_steps=max_steps)))
    p.start()
    p.join()
    return "Zadanie wykonane"


def main():
    with gr.Blocks(title="OpenOperator-Pro") as demo:
        gr.Markdown("## OpenOperator-Pro")
        url = gr.Textbox(value="https://webarena.dev", label="URL startowy")
        task = gr.Textbox(label="Polecenie")
        model = gr.Dropdown(["llava-next", "fuyu-8b", "gpt-4o-vision"], value="llava-next", label="Model wizji")
        out = gr.Textbox(label="Wynik")
        btn = gr.Button("Start")
        btn.click(start, inputs=[url, task, model], outputs=out)
    demo.launch(server_name="0.0.0.0", server_port=7860, auth=("user", "pass"), share=False)


if __name__ == "__main__":
    main()
