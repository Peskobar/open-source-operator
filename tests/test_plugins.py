import unittest
from plugins import load_plugins, Plugin

class TestPlugins(unittest.TestCase):
    def test_load_sample(self):
        plugins = load_plugins()
        self.assertTrue(any(isinstance(p, Plugin) for p in plugins))

if __name__ == '__main__':
    unittest.main()
