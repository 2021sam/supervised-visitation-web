"""Validate Census county dataset integrity."""

import hashlib
import json
import unittest
from pathlib import Path

from backend.geography.county_loader import load_counties


DATA_DIR = (
    Path(__file__).resolve().parents[2]
    / "backend"
    / "geography"
    / "data"
    / "census"
)


class TestCountyMetadata(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.metadata = json.loads(
            (DATA_DIR / "source.json").read_text(
                encoding="utf-8"
            )
        )

        cls.records = load_counties()

    def test_source_file_exists(self):
        source_file = DATA_DIR / self.metadata["active_filename"]
        self.assertTrue(source_file.is_file())

    def test_record_count(self):
        self.assertEqual(
            len(self.records),
            self.metadata["record_count"],
        )

    def test_dataset_checksum(self):
        source_file = DATA_DIR / self.metadata["active_filename"]

        checksum = hashlib.sha256(
            source_file.read_bytes()
        ).hexdigest()

        self.assertEqual(
            checksum,
            self.metadata["sha256"],
        )

    def test_unique_geoid_count(self):
        self.assertEqual(
            len({record["geoid"] for record in self.records}),
            self.metadata["record_count"],
        )


if __name__ == "__main__":
    unittest.main()
