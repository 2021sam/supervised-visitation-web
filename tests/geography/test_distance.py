import unittest

from backend.geography.distance import distance_miles


class TestDistance(unittest.TestCase):

    def test_same_location(self):
        self.assertEqual(
            distance_miles(37.8321, -121.9167, 37.8321, -121.9167),
            0.0,
        )

    def test_one_degree_at_equator(self):
        self.assertAlmostEqual(
            distance_miles(0, 0, 0, 1),
            69.09,
            delta=0.1,
        )

    def test_symmetry(self):
        forward = distance_miles(37.7749, -122.4194, 40.7128, -74.0060)
        reverse = distance_miles(40.7128, -74.0060, 37.7749, -122.4194)

        self.assertAlmostEqual(forward, reverse, places=8)

    def test_short_distance(self):
        self.assertAlmostEqual(
            distance_miles(37.8321, -121.9167, 37.7749, -122.4194),
            27.73,
            delta=0.1,
        )

    def test_cross_country_distance(self):
        self.assertAlmostEqual(
            distance_miles(37.7749, -122.4194, 40.7128, -74.0060),
            2565.72,
            delta=1.0,
        )

    def test_international_date_line(self):
        self.assertAlmostEqual(
            distance_miles(0, 179, 0, -179),
            138.19,
            delta=0.1,
        )

    def test_opposite_sides_of_earth(self):
        self.assertAlmostEqual(
            distance_miles(0, 0, 0, 180),
            12436.94,
            delta=1.0,
        )


if __name__ == "__main__":
    unittest.main()
