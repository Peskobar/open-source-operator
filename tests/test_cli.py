import unittest
from unittest.mock import patch
import sys, types, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if 'playwright.async_api' not in sys.modules:
    fake_api = types.ModuleType('playwright.async_api')
    fake_api.async_playwright = lambda: None
    sys.modules['playwright.async_api'] = fake_api
    sys.modules['playwright'] = types.ModuleType('playwright')

if 'openai' not in sys.modules:
    fake_openai = types.ModuleType('openai')
    class _Client:
        def __init__(self, *a, **k):
            pass
    fake_openai.OpenAI = _Client
    sys.modules['openai'] = fake_openai

if 'torch' not in sys.modules:
    sys.modules['torch'] = types.ModuleType('torch')

if 'transformers' not in sys.modules:
    fake_tr = types.ModuleType('transformers')
    fake_tr.AutoModelForCausalLM = object
    fake_tr.AutoTokenizer = object
    fake_tr.pipeline = lambda *a, **k: None
    sys.modules['transformers'] = fake_tr

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

import cli

class TestCLI(unittest.TestCase):
    @patch('cli.run_agent')
    def test_run_command(self, ra):
        ra.return_value = None
        with patch('sys.argv', ['oss-op', 'run', '--url', 'http://x', '--task', 'hi']):
            cli.main()
        ra.assert_called_once()

if __name__ == '__main__':
    unittest.main()
