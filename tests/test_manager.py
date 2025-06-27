import unittest
from unittest.mock import patch
import sys, types, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if 'openai' not in sys.modules:
    fake_openai = types.ModuleType('openai')
    fake_openai.OpenAI = object
    sys.modules['openai'] = fake_openai

if 'playwright.async_api' not in sys.modules:
    fake_api = types.ModuleType('playwright.async_api')
    fake_api.async_playwright = lambda: None
    sys.modules['playwright.async_api'] = fake_api
    sys.modules['playwright'] = types.ModuleType('playwright')

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

from agent.manager import AgentManager

class TestManager(unittest.TestCase):
    @patch('agent.manager.run_agent')
    def test_parallel(self, ra):
        ra.return_value = {'result': 'ok'}
        m = AgentManager(':memory:')
        tasks = [{'url': 'x', 'instruction': 'y'} for _ in range(2)]
        results = m.run_parallel(tasks)
        self.assertEqual(len(results), 2)

if __name__ == '__main__':
    unittest.main()
