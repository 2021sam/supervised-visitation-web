"""Issue and consume single-use email verification tokens."""

import time
from contextlib import closing

from backend.auth.database import connect, DATABASE_PATH
from backend.auth.tokens import generate_token, hash_token
from backend.auth.rate_limits import (
    check_rate_limit,
    check_network_limits,
)


TOKEN_LIFETIME_SECONDS = 15 * 60


def issue_token(
    email,
    database_path=DATABASE_PATH,
    *,
    client_ip=None,
):
    email = email.strip().lower()

    if not email:
        raise ValueError("Email is required")

    token = generate_token()
    now = int(time.time())

    with closing(connect(database_path)) as db:
        with db:
            db.execute("BEGIN IMMEDIATE")
            now = int(time.time())
            check_rate_limit(db, email, now)
            check_network_limits(db, client_ip, now)

            db.execute("""
                INSERT INTO verification_tokens (
                    token_hash,
                    email,
                    created_at,
                    expires_at,
                    client_ip
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                hash_token(token),
                email,
                now,
                now + TOKEN_LIFETIME_SECONDS,
                client_ip,
            ))

    return token


def consume_token(token, database_path=DATABASE_PATH):
    if not token:
        return None

    now = int(time.time())
    digest = hash_token(token)

    with closing(connect(database_path)) as db:
        with db:
            cursor = db.execute("""
                UPDATE verification_tokens
                SET consumed_at = ?
                WHERE token_hash = ?
                AND consumed_at IS NULL
                AND expires_at > ?
            """, (now, digest, now))

            if cursor.rowcount != 1:
                return None

            row = db.execute("""
                SELECT email
                FROM verification_tokens
                WHERE token_hash = ?
            """, (digest,)).fetchone()

            return row["email"]
