import hashlib
import tempfile
import unittest
from pathlib import Path

from tools.datasets.generate_data_manifest import build_manifest


class GenerateManifestTests(unittest.TestCase):
    def test_synthetic_file_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            sample = Path(directory) / "synthetic.txt"
            sample.write_bytes(b"synthetic-not-patient-data")
            manifest = build_manifest(sample, 1, "https://physionet.org/example", "1.0", "TEST")
            expected = hashlib.sha256(sample.read_bytes()).hexdigest()
            self.assertEqual(manifest["file_count"], 1)
            self.assertEqual(manifest["files"][0]["sha256"], expected)


if __name__ == "__main__":
    unittest.main()
