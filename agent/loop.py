import asyncio
import json
import os
import time
from typing import Dict, Optional

from playwright.async_api import async_playwright
from openai import OpenAI

from vision.llava_client import VisionModel
from memory.sqlite_graph import ConversationMemory

MAX_STEPS = 20
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def contains_sensitive(dom: str) -> bool:
    return "<input type=\"password\"" in dom or "credit card" in dom


async def execute_action(page, action: Dict[str, str]):
    if action["type"] == "click":
        await page.click(action["selector"])
    elif action["type"] == "type":
        await page.fill(action["selector"], action.get("text", ""))
    elif action["type"] == "press":
        await page.keyboard.press(action["key"])


async def run_agent(url: str, instruction: str, model_name: str, memory: ConversationMemory,
                    session_id: str = "default") -> Dict[str, Optional[str]]:
    """Główna pętla Plan-Act-Observe"""
    vision = VisionModel(model_name)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        steps = 0
        while steps < MAX_STEPS:
            dom = await page.content()
            screenshot_path = f"/tmp/shot_{int(time.time()*1000)}.png"
            await page.screenshot(path=screenshot_path)
            if contains_sensitive(dom):
                await browser.close()
                return {"handoff": screenshot_path}
            vision_desc = vision.describe(screenshot_path)
            history = memory.get(session_id)
            prompt = """You are a browser automation agent.\nTask: {task}\n{history}\nDOM:\n{dom}\nVISION:\n{vision}\nReply with a JSON action.""".format(
                task=instruction,
                history="\n".join(f"{r}:{c}" for r, c in history),
                dom=dom[:2000],
                vision=vision_desc,
            )
            response = client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "action",
                        "description": "Browser action",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "selector": {"type": "string"},
                                "text": {"type": "string"},
                                "key": {"type": "string"}
                            }
                        }
                    }
                }]
            )
            tool_call = response.choices[0].message.tool_calls[0]
            action = json.loads(tool_call.function.arguments)
            memory.add(session_id, "assistant", json.dumps(action))
            await execute_action(page, action)
            steps += 1
        await browser.close()
        return {"result": "completed", "steps": str(steps)}
