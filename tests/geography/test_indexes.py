import unittest

from backend.geography.indexes import build_indexes


class TestIndexes(unittest.TestCase):

    def setUp(self):
        self.records = [
            {
                "zip_code": "94506",
                "state_code": "CA",
                "city": "Danville",
                "county_code": "013",
            },
            {
                "zip_code": "94526",
                "state_code": "CA",
                "city": "Danville",
                "county_code": "013",
            },
            {
                "zip_code": "89501",
                "state_code": "NV",
                "city": "Reno",
                "county_code": "031",
            },
        ]

        self.indexes = build_indexes(self.records)

    def test_zip_lookup(self):
        self.assertEqual(
            self.indexes["by_zip"]["94506"],
            [self.records[0]],
        )

    def test_state_lookup(self):
        self.assertEqual(len(self.indexes["by_state"]["CA"]), 2)

    def test_city_lookup(self):
        self.assertEqual(
            len(self.indexes["by_city"][("CA", "danville")]), 2
        )

    def test_county_lookup(self):
        self.assertEqual(
            len(self.indexes["by_county"][("CA", "013")]), 2
        )

    def test_duplicate_zip_preserved(self):
        indexes = build_indexes([self.records[0], self.records[0]])
        self.assertEqual(len(indexes["by_zip"]["94506"]), 2)

    def test_missing_state(self):
        record = dict(self.records[0], state_code="")
        indexes = build_indexes([record])

        self.assertIn("94506", indexes["by_zip"])
        self.assertEqual(indexes["by_state"], {})
        self.assertEqual(indexes["by_city"], {})
        self.assertEqual(indexes["by_county"], {})

    def test_empty_input(self):
        indexes = build_indexes([])
        self.assertTrue(all(not index for index in indexes.values()))


if __name__ == "__main__":
    unittest.main()
