import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import json5  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover - fallback for offline testing
    import json as json5
    sys.modules['json5'] = json5

from inference.agent.Memory.short_memory.history import HistoryMemory

class TestHistoryMemory(unittest.TestCase):
    def test_construct_cache_returns_recent_steps(self):
        data = [{'step': i} for i in range(10)]
        cache = HistoryMemory.construct_cache(data, max_steps=3)
        self.assertEqual(cache, data[-3:])

    def test_construct_cache_invalid_input(self):
        with self.assertRaises(ValueError):
            HistoryMemory.construct_cache('notalist')

if __name__ == '__main__':
    unittest.main()
