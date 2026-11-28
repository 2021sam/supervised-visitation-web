import tempfile
import unittest
from pathlib import Path
from contextlib import closing
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor

from backend.auth.database import connect, initialize
from backend.auth.tokens import hash_token
from backend.auth.verification_tokens import (
    issue_token,
    consume_token,
    TOKEN_LIFETIME_SECONDS,
)


class VerificationTokenTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "auth.db"
        initialize(self.path)

    def test_issue_token(self):
        token = issue_token("provider@example.com", self.path)
        self.assertEqual(len(token), 43)

    def test_only_hash_is_stored(self):
        token = issue_token("provider@example.com", self.path)

        with closing(connect(self.path)) as db:
            row = db.execute("""
                SELECT token_hash
                FROM verification_tokens
            """).fetchone()

        self.assertEqual(row["token_hash"], hash_token(token))
        self.assertNotEqual(row["token_hash"], token)

    def test_email_normalization(self):
        token = issue_token(" Provider@Example.com ", self.path)

        self.assertEqual(
            consume_token(token, self.path),
            "provider@example.com"
        )

    def test_empty_email(self):
        with self.assertRaises(ValueError):
            issue_token(" ", self.path)

    def test_valid_token(self):
        token = issue_token("provider@example.com", self.path)

        self.assertEqual(
            consume_token(token, self.path),
            "provider@example.com"
        )

    def test_token_is_single_use(self):
        token = issue_token("provider@example.com", self.path)

        self.assertIsNotNone(consume_token(token, self.path))
        self.assertIsNone(consume_token(token, self.path))

    def test_unknown_token(self):
        self.assertIsNone(
            consume_token("unknown-token", self.path)
        )

    def test_empty_token(self):
        self.assertIsNone(consume_token("", self.path))

    def test_expired_token(self):
        with patch(
            "backend.auth.verification_tokens.time.time",
            return_value=1000
        ):
            token = issue_token(
                "provider@example.com", self.path
            )

        with patch(
            "backend.auth.verification_tokens.time.time",
            return_value=1000 + TOKEN_LIFETIME_SECONDS
        ):
            self.assertIsNone(
                consume_token(token, self.path)
            )

    def test_token_valid_before_expiration(self):
        with patch(
            "backend.auth.verification_tokens.time.time",
            return_value=1000
        ):
            token = issue_token(
                "provider@example.com", self.path
            )

        with patch(
            "backend.auth.verification_tokens.time.time",
            return_value=1000 + TOKEN_LIFETIME_SECONDS - 1
        ):
            self.assertEqual(
                consume_token(token, self.path),
                "provider@example.com"
            )

    def test_simultaneous_consumption(self):
        token = issue_token("provider@example.com", self.path)

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(
                lambda _: consume_token(token, self.path),
                range(2)
            ))

        self.assertEqual(
            results.count("provider@example.com"), 1
        )
        self.assertEqual(results.count(None), 1)


if __name__ == "__main__":
    unittest.main()
