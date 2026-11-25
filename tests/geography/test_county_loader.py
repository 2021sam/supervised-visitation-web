import tempfile
import unittest
from pathlib import Path

from backend.geography.county_loader import load_counties


class TestCountyLoader(unittest.TestCase):

    def load_sample(self, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "counties.txt"
            path.write_text(
                "USPS|GEOID|NAME|INTPTLAT|INTPTLONG\n" + rows,
                encoding="utf-8",
            )
            return load_counties(path)

    def test_valid_record(self):
        records = self.load_sample(
            "CA|06013|Contra Costa County|37.9|-121.9\n"
        )

        record = records[0]

        self.assertEqual(record["geoid"], "06013")
        self.assertEqual(record["state_fips"], "06")
        self.assertEqual(record["county_code"], "013")
        self.assertEqual(record["state_code"], "CA")
        self.assertEqual(record["county_name"], "Contra Costa County")

    def test_duplicate_geoid_rejected(self):
        row = "CA|06013|Contra Costa County|37.9|-121.9\n"

        with self.assertRaises(ValueError):
            self.load_sample(row + row)

    def test_invalid_geoid_rejected(self):
        with self.assertRaises(ValueError):
            self.load_sample("CA|6013|Example|37.9|-121.9\n")

    def test_invalid_coordinates_rejected(self):
        with self.assertRaises(ValueError):
            self.load_sample("CA|06013|Example|100|-121.9\n")

    def test_missing_name_rejected(self):
        with self.assertRaises(ValueError):
            self.load_sample("CA|06013||37.9|-121.9\n")

    def test_official_dataset(self):
        records = load_counties()

        self.assertGreater(len(records), 3000)
        self.assertEqual(
            len(records),
            len({r["geoid"] for r in records}),
        )

        states = {r["state_code"] for r in records}
        self.assertGreaterEqual(len(states), 51)


if __name__ == "__main__":
    unittest.main()
