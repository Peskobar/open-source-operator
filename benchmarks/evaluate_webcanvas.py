import argparse
import csv
import json
import time
from pathlib import Path

import yaml
from playwright.sync_api import sync_playwright

from agent.loop import parse_action, contains_sensitive
from vision.llava_client import VisionModel
from memory.sqlite_graph import ConversationMemory
from inference.logs import logger
from openai import OpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import os

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

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def execute_action_sync(page, action):
    if action["type"] == "click":
        page.click(action["selector"])
    elif action["type"] == "type":
        page.fill(action["selector"], action.get("text", ""))
    elif action["type"] == "press":
        page.keyboard.press(action["key"])


class Agent:
    browser = None

    def __init__(self, headless: bool = True, model_name: str = "llava-next", vision_checkpoint: str | None = None):
        self.headless = headless
        self.model_name = model_name
        self.vision = VisionModel(model_name, checkpoint_path=vision_checkpoint)
        self.memory = ConversationMemory(":memory:")

    def _prompt(self, instruction: str, dom: str, vision_desc: str, session_id: str) -> str:
        history = self.memory.get(session_id)
        return (
            "You are a browser automation agent.\nTask: {task}\n{history}\nDOM:\n{dom}\nVISION:\n{vision}\nReply with a JSON action.".format(
                task=instruction,
                history="\n".join(f"{r}:{c}" for r, c in history),
                dom=dom,
                vision=vision_desc,
            )
        )

    def _predict_action(self, prompt: str) -> dict:
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
        return action

    def plan_act_observe(self, page, instruction: str, session_id: str) -> dict:
        dom = page.content()
        screenshot_path = f"/tmp/shot_{int(time.time()*1000)}.png"
        page.screenshot(path=screenshot_path)
        if contains_sensitive(dom):
            return {"handoff": screenshot_path}
        vision_desc = self.vision.describe(screenshot_path)
        prompt = self._prompt(instruction, dom[:2000], vision_desc, session_id)
        action = self._predict_action(prompt)
        self.memory.add(session_id, "assistant", json.dumps(action))
        execute_action_sync(page, action)
        return action


def load_scenarios(path: str):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def evaluate_scenarios(scenarios, output_path: str):
    results = []
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        Agent.browser = pw.chromium
        browser = pw.chromium.launch(headless=True)
        for sc in scenarios:
            context = browser.new_context()
            page = context.new_page()
            start = time.time()
            page.goto(sc["url"])
            cred = sc.get("credentials")
            if cred:
                page.fill("input[type=text]", cred["username"])
                page.fill("input[type=password]", cred["password"])
                page.press("input[type=password]", "Enter")
            agent = Agent(headless=True)
            steps = 0
            success = False
            while steps < sc["max_steps"]:
                agent.plan_act_observe(page, sc.get("description", sc["name"]), sc["name"])
                steps += 1
                if page.query_selector(sc["success_selector"]):
                    success = True
                    break
            duration = time.time() - start
            results.append({
                "name": sc["name"],
                "success": success,
                "steps": steps,
                "duration": round(duration, 2)
            })
            context.close()
        browser.close()
    if output_path.endswith(".json"):
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
    else:
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "success", "steps", "duration"])
            writer.writeheader()
            writer.writerows(results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()
    scenarios = load_scenarios(args.scenarios)
    evaluate_scenarios(scenarios, args.output)


if __name__ == "__main__":
    main()
