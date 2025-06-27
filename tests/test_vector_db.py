import unittest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memory.vector_db import VectorDB
import importlib

class TestVectorDB(unittest.TestCase):
    def test_add_search(self):
        if importlib.util.find_spec('faiss') is None:
            self.skipTest('faiss not available')
        db = VectorDB(3)
        db.add([0.0, 0.1, 0.2], "a")
        res = db.search([0.0, 0.1, 0.2], k=1)
        self.assertEqual(res[0], "a")

if __name__ == '__main__':
    unittest.main()
