import unittest

from backend.geography.radius import search_radius


class TestRadius(unittest.TestCase):

    def setUp(self):
        self.records = [
            {
                "id": 1,
                "latitude": 0,
                "longitude": 2,
                "state_code": "CA",
            },
            {
                "id": 2,
                "latitude": 0,
                "longitude": 0,
                "state_code": "CA",
            },
            {
                "id": 3,
                "latitude": 0,
                "longitude": 1,
                "state_code": "NV",
            },
        ]

    def test_radius_filter(self):
        results = search_radius(self.records, 0, 0, 100)
        self.assertEqual(len(results), 2)

    def test_nearest_first(self):
        results = search_radius(self.records, 0, 0, 200)
        self.assertEqual(
            [r["id"] for r in results],
            [2, 3, 1],
        )

    def test_cross_state_search(self):
        results = search_radius(self.records, 0, 0, 100)
        self.assertEqual(
            {r["state_code"] for r in results},
            {"CA", "NV"},
        )

    def test_zero_radius(self):
        results = search_radius(self.records, 0, 0, 0)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 2)

    def test_boundary_included(self):
        results = search_radius(self.records, 0, 0, 200)
        boundary = results[1]["distance_miles"]

        results = search_radius(self.records, 0, 0, boundary)

        self.assertEqual(
            [r["id"] for r in results],
            [2, 3],
        )

    def test_original_records_unchanged(self):
        search_radius(self.records, 0, 0, 200)

        for record in self.records:
            self.assertNotIn("distance_miles", record)

    def test_invalid_radius(self):
        for radius in [-1, float("nan"), float("inf")]:
            with self.subTest(radius=radius):
                with self.assertRaises(ValueError):
                    search_radius(self.records, 0, 0, radius)

    def test_invalid_origin(self):
        for lat, lon in [(91, 0), (0, 181), (float("nan"), 0)]:
            with self.subTest(lat=lat, lon=lon):
                with self.assertRaises(ValueError):
                    search_radius(self.records, lat, lon, 100)

    def test_empty_input(self):
        self.assertEqual(search_radius([], 0, 0, 100), [])


if __name__ == "__main__":
    unittest.main()
