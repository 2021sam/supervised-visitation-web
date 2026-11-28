"""Independent SMTP email sender."""

import mimetypes
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path


def send_email(
    recipient: str,
    subject: str,
    body: str,
    *,
    html: bool = False,
    attachments: tuple = (),
) -> None:
    """Send an email. Raise an exception on failure."""

    username = os.environ["EMAIL_HOST_USER"]
    password = os.environ["EMAIL_HOST_PASSWORD"]

    message = EmailMessage()
    message["From"] = os.environ.get("EMAIL_FROM", username)
    message["To"] = recipient
    message["Subject"] = subject

    if html:
        message.set_content("Please view this email in HTML format.")
        message.add_alternative(body, subtype="html")
    else:
        message.set_content(body)

    for attachment in attachments:
        path = Path(attachment)
        content_type, _ = mimetypes.guess_type(path.name)
        maintype, subtype = (
            content_type or "application/octet-stream"
        ).split("/", 1)

        message.add_attachment(
            path.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=path.name,
        )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        context=ssl.create_default_context(),
        timeout=30,
    ) as smtp:
        smtp.login(username, password)
        smtp.send_message(message)
