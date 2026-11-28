import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor

from backend.auth.database import initialize
from backend.auth.verification_tokens import issue_token
from backend.auth.rate_limits import RateLimitExceeded


class RateLimitTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "auth.db"
        initialize(self.path)

    def issue(self, timestamp, email="provider@example.com"):
        with patch(
            "backend.auth.verification_tokens.time.time",
            return_value=timestamp
        ):
            return issue_token(email, self.path)

    def test_first_request_allowed(self):
        self.assertTrue(self.issue(100000))

    def test_immediate_repeat_blocked(self):
        self.issue(100000)

        with self.assertRaises(RateLimitExceeded):
            self.issue(100001)

    def test_request_after_one_minute(self):
        self.issue(100000)
        self.assertTrue(self.issue(100060))

    def test_hourly_limit(self):
        for i in range(5):
            self.issue(100000 + i * 60)

        with self.assertRaises(RateLimitExceeded):
            self.issue(100300)

    def test_hourly_limit_resets(self):
        for i in range(5):
            self.issue(100000 + i * 60)

        self.assertTrue(self.issue(103600))

    def test_daily_limit(self):
        for hour in range(4):
            for i in range(5):
                self.issue(
                    100000 + hour * 3600 + i * 60
                )

        with self.assertRaises(RateLimitExceeded):
            self.issue(114400)

    def test_daily_limit_resets(self):
        for hour in range(4):
            for i in range(5):
                self.issue(
                    100000 + hour * 3600 + i * 60
                )

        self.assertTrue(self.issue(186400))

    def test_independent_email_addresses(self):
        self.issue(100000, "first@example.com")
        self.assertTrue(
            self.issue(100001, "second@example.com")
        )

    def test_case_insensitive_limit(self):
        self.issue(100000, "Provider@example.com")

        with self.assertRaises(RateLimitExceeded):
            self.issue(100001, "provider@example.com")

    def test_simultaneous_requests(self):
        def request(_):
            try:
                issue_token(
                    "provider@example.com", self.path
                )
                return True
            except RateLimitExceeded:
                return False

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(request, range(2)))

        self.assertEqual(results.count(True), 1)
        self.assertEqual(results.count(False), 1)


if __name__ == "__main__":
    unittest.main()
