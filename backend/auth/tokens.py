"""Secure random tokens and token hashing."""

import hashlib
import secrets


def generate_token() -> str:
    """Generate a cryptographically secure 256-bit token."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Return the SHA-256 hash used for database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
