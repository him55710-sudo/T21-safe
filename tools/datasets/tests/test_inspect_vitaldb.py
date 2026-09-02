import json
import unittest

from tools.datasets.inspect_vitaldb import parse_payload


class InspectVitalDBTests(unittest.TestCase):
    def test_json_is_limited(self):
        payload = json.dumps([{"caseid": 1}, {"caseid": 2}, {"caseid": 3}]).encode()
        self.assertEqual(parse_payload(payload, 2), [{"caseid": 1}, {"caseid": 2}])

    def test_csv_is_limited(self):
        payload = b"caseid,age\n1,30\n2,40\n"
        self.assertEqual(parse_payload(payload, 1), [{"caseid": "1", "age": "30"}])


if __name__ == "__main__":
    unittest.main()
