import unittest

from tools.datasets._common import DatasetToolError, validate_open_https_url
from tools.datasets.download_open_sample import validate_dataset


class DownloadOpenSampleTests(unittest.TestCase):
    def test_open_registry_row_with_bounded_download_is_accepted(self):
        validate_dataset(
            {
                "dataset_id": "open",
                "access_type": "OPEN",
                "immediate_download_possible": "Yes with sample limit",
            }
        )

    def test_restricted_registry_row_is_rejected(self):
        with self.assertRaisesRegex(DatasetToolError, "will not bypass"):
            validate_dataset({"dataset_id": "restricted", "access_type": "CREDENTIAL_REQUIRED"})

    def test_non_allowlisted_or_non_https_url_is_rejected(self):
        with self.assertRaises(DatasetToolError):
            validate_open_https_url("http://physionet.org/file")
        with self.assertRaises(DatasetToolError):
            validate_open_https_url("https://example.invalid/file")


if __name__ == "__main__":
    unittest.main()
