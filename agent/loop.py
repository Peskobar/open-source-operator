import asyncio
import json
import os
import re
import time
from typing import Dict, Optional

from playwright.async_api import async_playwright
from openai import OpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from vision.llava_client import VisionModel
from memory.sqlite_graph import ConversationMemory
from inference.logs import logger
from plugins import load_plugins

MAX_STEPS = 20
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# load optional plugins on import
load_plugins()

_LOCAL_MODEL_PATH = os.getenv("LOCAL_LLM_PATH")
_local_pipeline = None
if _LOCAL_MODEL_PATH:
    try:
        tok = AutoTokenizer.from_pretrained(_LOCAL_MODEL_PATH)
        model = AutoModelForCausalLM.from_pretrained(
            _LOCAL_MODEL_PATH,
            device_map="auto",
            torch_dtype="auto",
            load_in_4bit=True,
        )
        _local_pipeline = pipeline("text-generation", model=model, tokenizer=tok)
        logger.info("Loaded local LLM from %s", _LOCAL_MODEL_PATH)
    except Exception as e:  # pragma: no cover - environment dependent
        logger.warning("Failed to load local model: %s", e)
        _local_pipeline = None


def contains_sensitive(dom: str) -> bool:
    keywords = [
        '<input type="password"',
        'credit card',
        'ssn',
        'social security',
        'cvv',
    ]
    dom_l = dom.lower()
    return any(k in dom_l for k in keywords)


async def execute_action(page, action: Dict[str, str]):
    if action["type"] == "click":
        await page.click(action["selector"])
    elif action["type"] == "type":
        await page.fill(action["selector"], action.get("text", ""))
    elif action["type"] == "press":
        await page.keyboard.press(action["key"])


def parse_action(text: str) -> Dict[str, str]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in model output")
    return json.loads(match.group(0))


async def run_agent(
    url: str,
    instruction: str,
    model_name: str,
    memory: ConversationMemory,
    session_id: str = "default",
    max_steps: int = MAX_STEPS,
    vision_checkpoint: Optional[str] = os.getenv("VISION_MODEL_PATH"),
) -> Dict[str, Optional[str]]:
    """Główna pętla Plan-Act-Observe"""
    vision = VisionModel(model_name, checkpoint_path=vision_checkpoint)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        steps = 0
        while steps < max_steps:
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
            use_openai = _local_pipeline is None
            action = None
            if _local_pipeline:
                try:
                    out = _local_pipeline(prompt, max_new_tokens=256)[0]["generated_text"]
                    action = parse_action(out)
                except Exception as e:  # pragma: no cover - runtime dependant
                    logger.warning("Local pipeline failed: %s", e)
                    use_openai = True
            if use_openai:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
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
