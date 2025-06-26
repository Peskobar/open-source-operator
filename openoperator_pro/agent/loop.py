import os
import json
import asyncio
from typing import Generator

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from guardrails import Guard

from ..vision.llava_client import describe_image
from ..vision.dom_aligner import match_bbox_to_dom

POLICY_PATH = os.path.join(os.path.dirname(__file__), '..', 'policy.yaml')

def run_agent(url: str, task: str, model: str, memory) -> Generator[str, None, None]:
    guard = Guard.from_policies([POLICY_PATH])
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        yield f"Otworzono {url}"

        for step in range(20):
            dom = page.content()
            soup = BeautifulSoup(dom, 'html.parser')
            if soup.find('input', {'type': 'password'}) or 'credit card' in dom.lower():
                yield 'HANDOFF_REQUIRED'
                page.pause()
            screenshot = page.screenshot(path=f"s_{step}.png")
            desc = describe_image(f"s_{step}.png", model=model)
            prompt = f"TASK:{task}\nDESC:{desc}"
            action = memory.plan(prompt)
            checked = guard(action)
            if not checked.valid:
                yield 'Action blocked by policy'
                break
            try:
                a = json.loads(action)
                if a['type'] == 'click':
                    page.click(a['selector'])
                elif a['type'] == 'type':
                    page.fill(a['selector'], a['text'])
                elif a['type'] == 'press':
                    page.keyboard.press(a['key'])
                else:
                    break
            except Exception as e:
                yield f'Error: {e}'
                break
            yield f'Step {step}: {action}'
        browser.close()
        yield 'Zakończono'
