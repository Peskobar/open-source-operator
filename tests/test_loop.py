import unittest
from unittest.mock import AsyncMock, patch
import sys, os, types
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if 'playwright.async_api' not in sys.modules:
    fake_api = types.ModuleType('playwright.async_api')
    fake_api.async_playwright = lambda: None
    sys.modules['playwright.async_api'] = fake_api
    sys.modules['playwright'] = types.ModuleType('playwright')

if 'openai' not in sys.modules:
    fake_openai = types.ModuleType('openai')
    class _Client:
        def __init__(self, *args, **kwargs):
            pass
    fake_openai.OpenAI = _Client
    sys.modules['openai'] = fake_openai

if 'transformers' not in sys.modules:
    fake_tr = types.ModuleType('transformers')
    fake_tr.AutoModelForCausalLM = object
    fake_tr.AutoTokenizer = object
    fake_tr.pipeline = lambda *a, **k: None
    sys.modules['transformers'] = fake_tr

if 'torch' not in sys.modules:
    sys.modules['torch'] = types.ModuleType('torch')

if 'numpy' not in sys.modules:
    sys.modules['numpy'] = types.ModuleType('numpy')

if 'colorlog' not in sys.modules:
    fake_cl = types.ModuleType('colorlog')
    class CF:
        def __init__(self, *a, **k):
            pass
        def format(self, record):
            return ''
    fake_cl.ColoredFormatter = CF
    sys.modules['colorlog'] = fake_cl

from agent.loop import parse_action, run_agent
from memory import get_memory


class TestParseAction(unittest.TestCase):
    def test_parse_valid_json(self):
        text = 'some preamble {"type": "click", "selector": "#id"} extra'
        action = parse_action(text)
        self.assertEqual(action["type"], "click")

    def test_parse_invalid_json(self):
        with self.assertRaises(ValueError):
            parse_action("no json here")


class TestRunAgent(unittest.IsolatedAsyncioTestCase):
    async def test_run_agent_mock_playwright(self):
        memory = get_memory({"path": ":memory:"})
        fake_page = AsyncMock()
        fake_page.content.return_value = "<html></html>"
        fake_page.screenshot = AsyncMock()
        async def goto(url):
            return None
        fake_page.goto = AsyncMock(side_effect=goto)
        fake_browser = AsyncMock()
        fake_browser.new_page.return_value = fake_page
        pw_context = AsyncMock()
        pw_context.chromium.launch.return_value = fake_browser
        pw = AsyncMock()
        pw.__aenter__.return_value = pw_context
        pw.__aexit__.return_value = False
        with patch('agent.loop.async_playwright', return_value=pw):
            with patch('agent.loop.VisionModel') as VM:
                VM.return_value.describe.return_value = "image"
                with patch('agent.loop._local_pipeline', None):
                    with patch('agent.loop.client') as oc:
                        class ToolCall:
                            def __init__(self):
                                self.function = type('f', (), {'arguments': '{"type": "click", "selector": "#id"}'})
                        oc.chat.completions.create.return_value.choices=[type('x', (), {'message': type('m', (), {'tool_calls':[ToolCall()]})})]
                        result = await run_agent('http://x', 'task', 'model', memory, max_steps=1)
                        self.assertEqual(result['result'], 'completed')


if __name__ == '__main__':
    unittest.main()
