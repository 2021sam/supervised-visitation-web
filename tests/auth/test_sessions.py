import tempfile
import unittest
from pathlib import Path
from contextlib import closing
from unittest.mock import patch

from backend.auth.database import connect, initialize
from backend.auth.tokens import hash_token
from backend.auth.sessions import (
    create_session,
    get_session_email,
    revoke_session,
    SESSION_LIFETIME_SECONDS,
)


class SessionTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "auth.db"
        initialize(self.path)

    def test_create_session(self):
        token = create_session(
            "provider@example.com", self.path
        )
        self.assertEqual(len(token), 43)

    def test_valid_session(self):
        token = create_session(
            "provider@example.com", self.path
        )
        self.assertEqual(
            get_session_email(token, self.path),
            "provider@example.com"
        )

    def test_email_normalization(self):
        token = create_session(
            " Provider@Example.com ", self.path
        )
        self.assertEqual(
            get_session_email(token, self.path),
            "provider@example.com"
        )

    def test_empty_email(self):
        with self.assertRaises(ValueError):
            create_session(" ", self.path)

    def test_only_hash_is_stored(self):
        token = create_session(
            "provider@example.com", self.path
        )

        with closing(connect(self.path)) as db:
            row = db.execute("""
                SELECT token_hash FROM sessions
            """).fetchone()

        self.assertEqual(row["token_hash"], hash_token(token))
        self.assertNotEqual(row["token_hash"], token)

    def test_unknown_session(self):
        self.assertIsNone(
            get_session_email("unknown", self.path)
        )

    def test_empty_session(self):
        self.assertIsNone(
            get_session_email("", self.path)
        )

    def test_expired_session(self):
        with patch(
            "backend.auth.sessions.time.time",
            return_value=1000
        ):
            token = create_session(
                "provider@example.com", self.path
            )

        with patch(
            "backend.auth.sessions.time.time",
            return_value=1000 + SESSION_LIFETIME_SECONDS
        ):
            self.assertIsNone(
                get_session_email(token, self.path)
            )

    def test_valid_before_expiration(self):
        with patch(
            "backend.auth.sessions.time.time",
            return_value=1000
        ):
            token = create_session(
                "provider@example.com", self.path
            )

        with patch(
            "backend.auth.sessions.time.time",
            return_value=1000 + SESSION_LIFETIME_SECONDS - 1
        ):
            self.assertEqual(
                get_session_email(token, self.path),
                "provider@example.com"
            )

    def test_revoke_session(self):
        token = create_session(
            "provider@example.com", self.path
        )

        self.assertTrue(
            revoke_session(token, self.path)
        )
        self.assertIsNone(
            get_session_email(token, self.path)
        )

    def test_revoke_twice(self):
        token = create_session(
            "provider@example.com", self.path
        )

        self.assertTrue(revoke_session(token, self.path))
        self.assertFalse(revoke_session(token, self.path))

    def test_revoke_unknown_session(self):
        self.assertFalse(
            revoke_session("unknown", self.path)
        )

    def test_multiple_independent_sessions(self):
        first = create_session(
            "provider@example.com", self.path
        )
        second = create_session(
            "provider@example.com", self.path
        )

        self.assertNotEqual(first, second)

        revoke_session(first, self.path)

        self.assertIsNone(
            get_session_email(first, self.path)
        )
        self.assertEqual(
            get_session_email(second, self.path),
            "provider@example.com"
        )


if __name__ == "__main__":
    unittest.main()
