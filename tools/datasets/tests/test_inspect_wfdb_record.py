import unittest

from tools.datasets.inspect_wfdb_record import parse_header


class InspectWFDBTests(unittest.TestCase):
    def test_parses_synthetic_header_and_honors_signal_limit(self):
        header = "synthetic 2 125 1000\nsynthetic.dat 16 200/mV 16 0 0 0 0 ECG\nsynthetic.dat 16 1000/NU 16 0 0 0 0 PLETH\n"
        result = parse_header(header, 1)
        self.assertEqual(result["record"], "synthetic")
        self.assertEqual(result["signal_count"], 2)
        self.assertEqual(result["sampling_frequency_hz"], 125.0)
        self.assertEqual(result["returned_signals"], 1)
        self.assertEqual(result["signals"][0]["description"], "ECG")


if __name__ == "__main__":
    unittest.main()
