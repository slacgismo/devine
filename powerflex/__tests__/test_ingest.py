import unittest
from powerflex.ingest import *

class TestDataIngest(unittest.TestCase):
    def test_base_headers(self):
        expected_headers = {"cache-control": "no-cache", "content-type": "application/json"}
        result = get_request_base_headers()
        self.assertDictEqual(result, expected_headers)
