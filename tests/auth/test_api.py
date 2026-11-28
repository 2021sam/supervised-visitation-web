"""HTTP tests for passwordless authentication."""

import os
import tempfile
import unittest

from pathlib import Path
from functools import partial
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from backend.auth.database import initialize
from backend.auth.verification_tokens import (
    issue_token,
    consume_token,
)
from backend.auth.sessions import (
    create_session,
    get_session_email,
    revoke_session,
)
from backend.auth.rate_limits import RateLimitExceeded


class AuthAPITests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)

        self.path = Path(temp.name) / "auth.db"
        initialize(self.path)

        self.origin = "https://directory.example.com"
        self.email = "provider@example.com"

        env = patch.dict(os.environ, {
            "AUTH_BASE_URL": self.origin,
            "AUTH_EMAIL_ENABLED": "0",
        })
        env.start()
        self.addCleanup(env.stop)

        for function in (
            consume_token,
            create_session,
            get_session_email,
            revoke_session,
        ):
            mock = patch(
                f"backend.api.auth.{function.__name__}",
                partial(function, database_path=self.path),
            )
            mock.start()
            self.addCleanup(mock.stop)

        self.client = TestClient(
            app,
            base_url=self.origin,
        )
        self.addCleanup(self.client.close)

        self.headers = {"Origin": self.origin}

    def verify(self, token):
        return self.client.post(
            "/api/auth/verify",
            json={"token": token},
            headers=self.headers,
        )

    def sign_in(self):
        token = issue_token(self.email, self.path)
        return self.verify(token)

    def test_unauthenticated_session(self):
        response = self.client.get("/api/auth/session")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "authenticated": False,
            "email": None,
        })

    @patch("backend.api.auth.send_verification_email")
    def test_email_disabled(self, sender):
        response = self.client.post(
            "/api/auth/request",
            json={"email": self.email},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 503)
        sender.assert_not_called()

    @patch("backend.api.auth.send_verification_email")
    def test_request_verification(self, sender):
        with patch.dict(os.environ, {
            "AUTH_EMAIL_ENABLED": "1",
        }):
            response = self.client.post(
                "/api/auth/request",
                json={"email": "Provider@Example.com"},
                headers=self.headers,
            )

        self.assertEqual(response.status_code, 200)
        sender.assert_called_once_with(
            self.email, self.origin,
            client_ip="testclient",
        )

    @patch("backend.api.auth.send_verification_email")
    def test_invalid_email(self, sender):
        response = self.client.post(
            "/api/auth/request",
            json={"email": "not-an-email"},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 422)
        sender.assert_not_called()

    @patch("backend.api.auth.send_verification_email")
    def test_rate_limit(self, sender):
        sender.side_effect = RateLimitExceeded()

        with patch.dict(os.environ, {
            "AUTH_EMAIL_ENABLED": "1",
        }):
            response = self.client.post(
                "/api/auth/request",
                json={"email": self.email},
                headers=self.headers,
            )

        self.assertEqual(response.status_code, 429)

    @patch("backend.api.auth.send_verification_email")
    def test_smtp_failure(self, sender):
        sender.side_effect = RuntimeError("SMTP failure")

        with patch.dict(os.environ, {
            "AUTH_EMAIL_ENABLED": "1",
        }):
            response = self.client.post(
                "/api/auth/request",
                json={"email": self.email},
                headers=self.headers,
            )

        self.assertEqual(response.status_code, 503)
        self.assertNotIn("SMTP failure", response.text)

    def test_missing_origin(self):
        response = self.client.post(
            "/api/auth/request",
            json={"email": self.email},
        )

        self.assertEqual(response.status_code, 403)

    def test_wrong_origin(self):
        response = self.client.post(
            "/api/auth/request",
            json={"email": self.email},
            headers={"Origin": "https://other.example.com"},
        )

        self.assertEqual(response.status_code, 403)

    def test_valid_verification(self):
        response = self.sign_in()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "authenticated": True,
            "email": self.email,
        })

    def test_secure_session_cookie(self):
        response = self.sign_in()
        cookie = response.headers["set-cookie"].lower()

        self.assertIn("sv_session=", cookie)
        self.assertIn("httponly", cookie)
        self.assertIn("secure", cookie)
        self.assertIn("samesite=lax", cookie)
        self.assertIn("max-age=2592000", cookie)
        self.assertNotIn("sv_session", response.json())

    def test_authenticated_session(self):
        self.sign_in()

        response = self.client.get("/api/auth/session")

        self.assertEqual(response.json(), {
            "authenticated": True,
            "email": self.email,
        })

    def test_invalid_token(self):
        response = self.verify("a" * 43)
        self.assertEqual(response.status_code, 400)

    def test_single_use_token(self):
        token = issue_token(self.email, self.path)

        self.assertEqual(
            self.verify(token).status_code, 200
        )
        self.assertEqual(
            self.verify(token).status_code, 400
        )

    def test_expired_token(self):
        with patch(
            "backend.auth.verification_tokens.time.time",
            return_value=100000,
        ):
            token = issue_token(self.email, self.path)

        response = self.verify(token)
        self.assertEqual(response.status_code, 400)

    def test_logout(self):
        self.sign_in()

        token = self.client.cookies.get("sv_session")

        response = self.client.post(
            "/api/auth/logout",
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(
            get_session_email(token, self.path)
        )

        response = self.client.get("/api/auth/session")
        self.assertFalse(response.json()["authenticated"])

    def test_logout_requires_origin(self):
        self.sign_in()

        response = self.client.post("/api/auth/logout")

        self.assertEqual(response.status_code, 403)

        response = self.client.get("/api/auth/session")
        self.assertTrue(response.json()["authenticated"])

    def test_session_not_cached(self):
        response = self.client.get("/api/auth/session")

        self.assertEqual(
            response.headers["cache-control"],
            "no-store",
        )

    def test_verification_requires_post(self):
        response = self.client.get("/api/auth/verify")
        self.assertEqual(response.status_code, 405)

    def test_session_rotation(self):
        self.sign_in()
        old_token = self.client.cookies.get("sv_session")

        token = issue_token(
            "second@example.com", self.path
        )

        response = self.verify(token)
        self.assertEqual(response.status_code, 200)

        new_token = self.client.cookies.get("sv_session")

        self.assertNotEqual(old_token, new_token)
        self.assertIsNone(
            get_session_email(old_token, self.path)
        )
        self.assertEqual(
            get_session_email(new_token, self.path),
            "second@example.com",
        )


if __name__ == "__main__":
    unittest.main()
