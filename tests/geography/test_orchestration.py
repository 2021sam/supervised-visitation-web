import unittest

from backend.geography.orchestration import initialize_geography
from backend.geography.lookup import (
    get_zip_records,
    get_state_counties,
    get_city_zip_codes,
)
from backend.geography.radius import search_radius


class TestOrchestration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.geo = initialize_geography()

    def test_required_components(self):
        self.assertEqual(
            set(self.geo),
            {
                "states",
                "zip_records",
                "counties",
                "zip_indexes",
                "county_indexes",
            },
        )

    def test_nationwide_state_coverage(self):
        states = {
            record["state_code"]
            for record in self.geo["states"]
        }

        self.assertEqual(len(states), 51)
        self.assertIn("DC", states)

        for state in states:
            self.assertIn(state, self.geo["zip_indexes"]["by_state"])
            self.assertIn(state, self.geo["county_indexes"]["by_state"])

    def test_zip_index_consistency(self):
        indexed_count = sum(
            len(records)
            for records in self.geo["zip_indexes"]["by_zip"].values()
        )

        self.assertEqual(
            indexed_count,
            len(self.geo["zip_records"]),
        )

    def test_county_index_consistency(self):
        self.assertEqual(
            len(self.geo["county_indexes"]["by_geoid"]),
            len(self.geo["counties"]),
        )

    def test_county_lookup_integration(self):
        counties = get_state_counties(
            self.geo["county_indexes"], "CA"
        )

        self.assertTrue(counties)

        self.assertTrue(
            all(record["state_code"] == "CA" for record in counties)
        )

    def test_city_lookup_integration(self):
        zip_codes = get_city_zip_codes(
            self.geo["zip_indexes"], "CA", "Danville"
        )

        self.assertIn("94506", zip_codes)

    def test_radius_search_integration(self):
        origin = get_zip_records(
            self.geo["zip_indexes"], "94506"
        )[0]

        results = search_radius(
            self.geo["zip_records"],
            origin["latitude"],
            origin["longitude"],
            25,
        )

        self.assertTrue(results)

        distances = [
            record["distance_miles"]
            for record in results
        ]

        self.assertEqual(distances, sorted(distances))
        self.assertEqual(distances[0], 0)
        self.assertTrue(all(d <= 25 for d in distances))


if __name__ == "__main__":
    unittest.main()
