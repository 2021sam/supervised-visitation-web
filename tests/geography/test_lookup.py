import unittest

from backend.geography.lookup import (
    get_zip_records,
    get_state_cities,
    get_city_zip_codes,
    get_state_counties,
    get_county,
)


class TestLookup(unittest.TestCase):

    def setUp(self):
        first = {"zip_code": "94506", "city": "Danville"}
        second = {"zip_code": "94526", "city": "Danville"}
        third = {"zip_code": "94507", "city": "Alamo"}

        self.indexes = {
            "by_zip": {
                "94506": [first],
                "94526": [second],
                "94507": [third],
            },
            "by_state": {
                "CA": [first, second, third],
            },
            "by_city": {
                ("CA", "danville"): [first, second],
                ("CA", "alamo"): [third],
            },
        }

        county = {
            "geoid": "06013",
            "state_code": "CA",
            "county_name": "Contra Costa County",
        }

        self.county_indexes = {
            "by_geoid": {"06013": county},
            "by_state": {"CA": [county]},
        }

    def test_zip_lookup(self):
        records = get_zip_records(self.indexes, "94506")
        self.assertEqual(records[0]["city"], "Danville")

    def test_unknown_zip(self):
        self.assertEqual(
            get_zip_records(self.indexes, "00000"), []
        )

    def test_unique_sorted_cities(self):
        self.assertEqual(
            get_state_cities(self.indexes, "CA"),
            ["Alamo", "Danville"],
        )

    def test_city_zip_codes(self):
        self.assertEqual(
            get_city_zip_codes(self.indexes, "CA", "Danville"),
            ["94506", "94526"],
        )

    def test_case_and_whitespace_normalization(self):
        self.assertEqual(
            get_city_zip_codes(self.indexes, " ca ", " DANVILLE "),
            ["94506", "94526"],
        )

    def test_unknown_state_and_city(self):
        self.assertEqual(
            get_state_cities(self.indexes, "XX"), []
        )
        self.assertEqual(
            get_city_zip_codes(self.indexes, "CA", "Unknown"), []
        )

    def test_state_counties(self):
        counties = get_state_counties(self.county_indexes, "ca")
        self.assertEqual(counties[0]["geoid"], "06013")

    def test_county_lookup(self):
        county = get_county(self.county_indexes, "06013")
        self.assertEqual(
            county["county_name"], "Contra Costa County"
        )

    def test_unknown_county(self):
        self.assertIsNone(
            get_county(self.county_indexes, "00000")
        )

    def test_unknown_county_state(self):
        self.assertEqual(
            get_state_counties(self.county_indexes, "XX"), []
        )


if __name__ == "__main__":
    unittest.main()
