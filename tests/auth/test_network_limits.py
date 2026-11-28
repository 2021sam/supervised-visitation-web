"""Independent tests for network verification limits."""

import tempfile
import unittest

from pathlib import Path
from contextlib import closing
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor

from backend.auth.database import initialize, connect
from backend.auth.verification_tokens import issue_token
from backend.auth.rate_limits import RateLimitExceeded


class NetworkLimitTests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "auth.db"
        initialize(self.path)

    def issue(self, number, ip, timestamp=100000):
        with patch(
            "backend.auth.verification_tokens.time.time",
            return_value=timestamp,
        ):
            return issue_token(
                f"provider{number}@example.com",
                self.path,
                client_ip=ip,
            )

    def test_ip_is_stored(self):
        self.issue(1, "192.0.2.1")

        with closing(connect(self.path)) as db:
            row = db.execute("""
                SELECT client_ip
                FROM verification_tokens
            """).fetchone()

        self.assertEqual(row["client_ip"], "192.0.2.1")

    def test_ip_hourly_limit(self):
        for i in range(20):
            self.issue(i, "192.0.2.1")

        with self.assertRaises(RateLimitExceeded):
            self.issue(20, "192.0.2.1")

    def test_independent_ip_addresses(self):
        for i in range(20):
            self.issue(i, "192.0.2.1")

        self.assertTrue(
            self.issue(20, "192.0.2.2")
        )

    def test_ip_limit_resets(self):
        for i in range(20):
            self.issue(i, "192.0.2.1")

        self.assertTrue(
            self.issue(20, "192.0.2.1", 103600)
        )

    def test_global_hourly_limit(self):
        for i in range(100):
            self.issue(i, f"192.0.2.{i + 1}")

        with self.assertRaises(RateLimitExceeded):
            self.issue(100, "192.0.2.101")

    def test_global_limit_resets(self):
        for i in range(100):
            self.issue(i, f"192.0.2.{i + 1}")

        self.assertTrue(
            self.issue(100, "192.0.2.101", 103600)
        )

    def test_missing_ip_still_subject_to_global_limit(self):
        for i in range(100):
            self.issue(i, None)

        with self.assertRaises(RateLimitExceeded):
            self.issue(100, None)

    def test_rejected_request_does_not_create_token(self):
        for i in range(20):
            self.issue(i, "192.0.2.1")

        with self.assertRaises(RateLimitExceeded):
            self.issue(20, "192.0.2.1")

        with closing(connect(self.path)) as db:
            count = db.execute("""
                SELECT COUNT(*)
                FROM verification_tokens
            """).fetchone()[0]

        self.assertEqual(count, 20)

    def test_simultaneous_ip_requests(self):
        for i in range(19):
            self.issue(i, "192.0.2.1")

        def request(number):
            try:
                issue_token(
                    f"provider{number}@example.com",
                    self.path,
                    client_ip="192.0.2.1",
                )
                return True
            except RateLimitExceeded:
                return False

        with patch(
            "backend.auth.verification_tokens.time.time",
            return_value=100000,
        ):
            with ThreadPoolExecutor(max_workers=2) as executor:
                results = list(
                    executor.map(request, (19, 20))
                )

        self.assertEqual(results.count(True), 1)
        self.assertEqual(results.count(False), 1)


if __name__ == "__main__":
    unittest.main()
