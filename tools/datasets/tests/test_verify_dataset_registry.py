import csv
import unittest
from pathlib import Path

from tools.datasets._common import load_registry
from tools.datasets.verify_dataset_registry import validate_registry


REPO_ROOT = Path(__file__).resolve().parents[3]


class VerifyRegistryTests(unittest.TestCase):
    def test_repository_registry_pair_is_valid(self):
        yaml_path = REPO_ROOT / "research" / "dataset_registry.yaml"
        csv_path = REPO_ROOT / "research" / "dataset_registry.csv"
        payload = load_registry(yaml_path)
        with csv_path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(validate_registry(payload, rows, 20), [])


if __name__ == "__main__":
    unittest.main()
