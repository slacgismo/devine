import datetime
import unittest
from powerflex.ingest import *

class TestDataIngest(unittest.TestCase):
    def test_base_headers(self):
        expected_headers = {
            "cache-control": "no-cache", 
            "content-type": "application/json"
        }
        result = get_request_base_headers()
        self.assertDictEqual(result, expected_headers)

    def test_set_authentication_headers(self):
        expected_headers = {
            "cache-control": "no-cache", 
            "content-type": "application/json", 
            "Authorization": "Bearer token_1234"
        }
        result = set_authentication_headers("token_1234")
        self.assertDictEqual(result, expected_headers)

    def test_get_formatted_date_components(self):
        expected_date_components = "01", "11", "2020"
        d = datetime.datetime(year=2020, month=1, day=11)
        result = get_formatted_date_components(d)
        self.assertTupleEqual(result, expected_date_components)

    def test_get_timestamp(self):
        start_hour = 0
        end_hour = 23
        d = datetime.datetime(year=2020, month=1, day=11)
        d = d.replace(tzinfo=datetime.timezone.utc)
        result = get_timestamp(d, start_hour, end_hour)
        expected_timestamps = (1578700800, 1578783600)
        self.assertTupleEqual(result, expected_timestamps)

    def test_generate_filename(self):
        expected_filename = "debug/prefix/data_type/2020-01-11-01.csv"
        d = datetime.datetime(year=2020, month=1, day=11)
        result = generate_filename_and_path("prefix", "data_type", d, "csv", "-01")
        self.assertEquals(result, expected_filename)