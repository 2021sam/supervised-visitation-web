"""Send passwordless email verification links."""

from urllib.parse import urlencode, urlsplit

from backend.auth.database import DATABASE_PATH
from backend.auth.verification_tokens import issue_token
from backend.email.sender import send_email


def send_verification_email(
    email,
    base_url,
    database_path=DATABASE_PATH,
    *,
    client_ip=None,
):
    email = email.strip().lower()
    base_url = base_url.rstrip("/")

    parsed = urlsplit(base_url)

    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path
    ):
        raise ValueError("A trusted HTTPS website origin is required")

    token = issue_token(
        email, database_path, client_ip=client_ip
    )

    query = urlencode({"token": token})
    verification_url = f"{base_url}/verify#{query}"

    subject = "Your secure sign-in link"

    body = (
        "Supervised Visitation Directory\n\n"
        "Use the following link to verify your email "
        "address and sign in:\n\n"
        f"{verification_url}\n\n"
        "This link expires in 15 minutes and can "
        "only be used once.\n\n"
        "If you did not request this email, "
        "you can safely ignore it."
    )

    send_email(email, subject, body)
