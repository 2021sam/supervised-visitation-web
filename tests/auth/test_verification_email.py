import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit, parse_qs

from backend.auth.database import initialize
from backend.auth.verification_tokens import consume_token
from backend.auth.verification_email import send_verification_email


class VerificationEmailTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.path = Path(self.temp.name) / "auth.db"
        initialize(self.path)

        self.base_url = "https://directory.example.com"

    @patch("backend.auth.verification_email.send_email")
    def test_email_recipient(self, sender):
        send_verification_email(
            " Provider@Example.com ",
            self.base_url,
            self.path
        )

        sender.assert_called_once()
        self.assertEqual(
            sender.call_args.args[0],
            "provider@example.com"
        )

    @patch("backend.auth.verification_email.send_email")
    def test_email_subject(self, sender):
        send_verification_email(
            "provider@example.com",
            self.base_url,
            self.path
        )

        self.assertEqual(
            sender.call_args.args[1],
            "Your secure sign-in link"
        )

    @patch("backend.auth.verification_email.send_email")
    def test_verification_link(self, sender):
        send_verification_email(
            "provider@example.com",
            self.base_url,
            self.path
        )

        body = sender.call_args.args[2]

        url = next(
            line for line in body.splitlines()
            if line.startswith("https://")
        )

        parsed = urlsplit(url)

        self.assertEqual(
            parsed.hostname,
            "directory.example.com"
        )
        self.assertEqual(parsed.path, "/verify")
        self.assertEqual(parsed.query, "")

        token = parse_qs(parsed.fragment)["token"][0]

        self.assertEqual(
            consume_token(token, self.path),
            "provider@example.com"
        )

    @patch("backend.auth.verification_email.send_email")
    def test_expiration_notice(self, sender):
        send_verification_email(
            "provider@example.com",
            self.base_url,
            self.path
        )

        body = sender.call_args.args[2]
        self.assertIn("15 minutes", body)
        self.assertIn("only be used once", body)

    @patch("backend.auth.verification_email.send_email")
    def test_invalid_base_url(self, sender):
        for url in (
            "",
            "http://directory.example.com",
            "https://",
            "https://user@example.com",
            "https://example.com?redirect=other",
            "https://example.com/path",
        ):
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    send_verification_email(
                        "provider@example.com",
                        url,
                        self.path
                    )

        sender.assert_not_called()

    @patch("backend.auth.verification_email.send_email")
    def test_email_failure_propagates(self, sender):
        sender.side_effect = RuntimeError("SMTP failure")

        with self.assertRaises(RuntimeError):
            send_verification_email(
                "provider@example.com",
                self.base_url,
                self.path
            )


if __name__ == "__main__":
    unittest.main()
