import hashlib
import json
import unittest
from pathlib import Path

from backend.geography.loader import load_states, load_zip_records


DATA_DIR = (
    Path(__file__).resolve().parents[2]
    / "backend"
    / "geography"
    / "data"
)


class TestLoader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.states = load_states()
        cls.records = load_zip_records()

        cls.metadata = json.loads(
            (DATA_DIR / "source.json").read_text(
                encoding="utf-8"
            )
        )

    def test_state_count(self):
        self.assertEqual(len(self.states), 51)

    def test_record_count(self):
        self.assertEqual(
            len(self.records),
            self.metadata["record_count"],
        )

    def test_unique_zip_count(self):
        self.assertEqual(
            len({r["zip_code"] for r in self.records}),
            self.metadata["unique_zip_count"],
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

    def test_leading_zeros_preserved(self):
        self.assertTrue(
            any(r["zip_code"].startswith("0") for r in self.records)
        )

    def test_coordinates(self):
        for record in self.records:
            self.assertTrue(-90 <= record["latitude"] <= 90)
            self.assertTrue(-180 <= record["longitude"] <= 180)

    def test_zip_format(self):
        for record in self.records:
            zip_code = record["zip_code"]

            self.assertEqual(len(zip_code), 5)
            self.assertTrue(zip_code.isascii())
            self.assertTrue(zip_code.isdigit())

    def test_minimum_dataset_coverage(self):
        self.assertGreaterEqual(len(self.records), 40000)


if __name__ == "__main__":
    unittest.main()
