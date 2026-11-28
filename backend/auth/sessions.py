"""Create, validate and revoke authenticated sessions."""

import time
from contextlib import closing

from backend.auth.database import connect, DATABASE_PATH
from backend.auth.tokens import generate_token, hash_token


SESSION_LIFETIME_SECONDS = 30 * 24 * 60 * 60


def create_session(email, database_path=DATABASE_PATH):
    email = email.strip().lower()

    if not email:
        raise ValueError("Email is required")

    token = generate_token()
    now = int(time.time())

    with closing(connect(database_path)) as db:
        with db:
            db.execute("""
                INSERT INTO sessions (
                    token_hash,
                    email,
                    created_at,
                    expires_at
                )
                VALUES (?, ?, ?, ?)
            """, (
                hash_token(token),
                email,
                now,
                now + SESSION_LIFETIME_SECONDS,
            ))

    return token


def get_session_email(token, database_path=DATABASE_PATH):
    if not token:
        return None

    now = int(time.time())

    with closing(connect(database_path)) as db:
        row = db.execute("""
            SELECT email
            FROM sessions
            WHERE token_hash = ?
            AND revoked_at IS NULL
            AND expires_at > ?
        """, (hash_token(token), now)).fetchone()

        return row["email"] if row else None


def revoke_session(token, database_path=DATABASE_PATH):
    if not token:
        return False

    now = int(time.time())

    with closing(connect(database_path)) as db:
        with db:
            cursor = db.execute("""
                UPDATE sessions
                SET revoked_at = ?
                WHERE token_hash = ?
                AND revoked_at IS NULL
            """, (now, hash_token(token)))

            return cursor.rowcount == 1
