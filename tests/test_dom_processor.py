import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_processing.preprocessor.dom_processor import DOMProcessor

class TestDOMProcessor(unittest.TestCase):
    def test_custom_valid_actions(self):
        config = {'valid_actions': ['paste'], 'log_dir': 'logs'}
        proc = DOMProcessor(config)
        step_valid = {'type': 'paste', 'value': 'x', 'path': 'body>input'}
        self.assertTrue(proc._validate_action(step_valid))
        step_invalid = {'type': 'click', 'value': '', 'path': 'body>div'}
        self.assertFalse(proc._validate_action(step_invalid))

if __name__ == '__main__':
    unittest.main()
