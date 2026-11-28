import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.email.sender import send_email


class TestEmailSender(unittest.TestCase):

    def setUp(self):
        env = patch.dict(os.environ, {
            "EMAIL_HOST_USER": "sender@example.com",
            "EMAIL_HOST_PASSWORD": "test-password",
            "EMAIL_FROM": "sender@example.com",
        })
        env.start()
        self.addCleanup(env.stop)

        smtp = patch("backend.email.sender.smtplib.SMTP_SSL")
        self.smtp_class = smtp.start()
        self.addCleanup(smtp.stop)
        self.smtp = self.smtp_class.return_value.__enter__.return_value

    def message(self):
        return self.smtp.send_message.call_args.args[0]

    def test_plain_text(self):
        send_email("recipient@example.com", "Test", "Hello")

        self.smtp.login.assert_called_once_with(
            "sender@example.com", "test-password"
        )
        self.assertEqual(self.message()["Subject"], "Test")
        self.assertEqual(
            self.message()["To"], "recipient@example.com"
        )
        self.assertEqual(self.message().get_content().strip(), "Hello")

    def test_html(self):
        send_email(
            "recipient@example.com",
            "Test HTML",
            "<h1>Hello</h1>",
            html=True,
        )
        self.assertEqual(
            self.message().get_body(
                preferencelist=("html",)
            ).get_content().strip(),
            "<h1>Hello</h1>",
        )

    def test_attachment(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "backup.db.age"
            path.write_bytes(b"test backup")

            send_email(
                "recipient@example.com",
                "Backup",
                "Database backup",
                attachments=(path,),
            )

            attachments = list(self.message().iter_attachments())
            self.assertEqual(len(attachments), 1)
            self.assertEqual(
                attachments[0].get_filename(), "backup.db.age"
            )
            self.assertEqual(
                attachments[0].get_payload(decode=True),
                b"test backup",
            )

    def test_smtp_failure(self):
        self.smtp.send_message.side_effect = OSError("SMTP failed")

        with self.assertRaisesRegex(OSError, "SMTP failed"):
            send_email("recipient@example.com", "Test", "Hello")


if __name__ == "__main__":
    unittest.main()
