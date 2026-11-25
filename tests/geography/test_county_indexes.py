import unittest

from backend.geography.county_indexes import build_county_indexes


class TestCountyIndexes(unittest.TestCase):

    def setUp(self):
        self.records = [
            {
                "geoid": "06013",
                "state_code": "CA",
                "county_name": "Contra Costa County",
            },
            {
                "geoid": "06001",
                "state_code": "CA",
                "county_name": "Alameda County",
            },
            {
                "geoid": "32031",
                "state_code": "NV",
                "county_name": "Washoe County",
            },
        ]

        self.indexes = build_county_indexes(self.records)

    def test_geoid_lookup(self):
        self.assertEqual(
            self.indexes["by_geoid"]["06013"],
            self.records[0],
        )

    def test_counties_by_state(self):
        self.assertEqual(len(self.indexes["by_state"]["CA"]), 2)
        self.assertEqual(len(self.indexes["by_state"]["NV"]), 1)

    def test_alphabetical_order(self):
        names = [
            record["county_name"]
            for record in self.indexes["by_state"]["CA"]
        ]

        self.assertEqual(
            names,
            ["Alameda County", "Contra Costa County"],
        )

    def test_duplicate_geoid_rejected(self):
        with self.assertRaises(ValueError):
            build_county_indexes([self.records[0], self.records[0]])

    def test_empty_input(self):
        self.assertEqual(
            build_county_indexes([]),
            {"by_geoid": {}, "by_state": {}},
        )

    def test_input_order_preserved(self):
        self.assertEqual(self.records[0]["geoid"], "06013")


if __name__ == "__main__":
    unittest.main()
