import unittest
import os
import sys
import types
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if 'requests_toolbelt' not in sys.modules:
    requests_toolbelt = types.ModuleType('requests_toolbelt')
    multipart = types.ModuleType('requests_toolbelt.multipart')
    encoder = types.ModuleType('requests_toolbelt.multipart.encoder')
    class Dummy:
        def __init__(self, *args, **kwargs):
            pass
    encoder.MultipartEncoder = Dummy
    multipart.encoder = encoder
    requests_toolbelt.multipart = multipart
    sys.modules['requests_toolbelt'] = requests_toolbelt
    sys.modules['requests_toolbelt.multipart'] = multipart
    sys.modules['requests_toolbelt.multipart.encoder'] = encoder

if 'requests' not in sys.modules:
    requests = types.ModuleType('requests')
    def _post(*a, **k):
        class Resp:
            status_code = 200
            def json(self):
                return {'data': {'pwdLogin': 'token'}}
            text = ''
        return Resp()
    requests.post = _post
    sys.modules['requests'] = requests

from data_processing.downloader.dataset_io import GraphQLClient

class TestGraphQLClientEnv(unittest.TestCase):
    def tearDown(self):
        os.environ.pop('IMEAN_USERNAME', None)
        os.environ.pop('IMEAN_PASSWORD', None)

    def test_missing_credentials_raises(self):
        os.environ.pop('IMEAN_USERNAME', None)
        os.environ.pop('IMEAN_PASSWORD', None)
        with self.assertRaises(ValueError):
            GraphQLClient()

    def test_credentials_loaded(self):
        os.environ['IMEAN_USERNAME'] = 'user'
        os.environ['IMEAN_PASSWORD'] = 'pass123'
        client = GraphQLClient()
        self.assertEqual(client.username, 'user')
        self.assertEqual(client.password, 'pass123')

if __name__ == '__main__':
    unittest.main()
