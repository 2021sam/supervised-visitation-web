"""Verification request limits."""

MINIMUM_INTERVAL = 60
HOURLY_LIMIT = 5
DAILY_LIMIT = 20
IP_HOURLY_LIMIT = 20
GLOBAL_HOURLY_LIMIT = 100


class RateLimitExceeded(Exception):
    """Verification request limit exceeded."""


def check_rate_limit(db, email, now):
    row = db.execute("""
        SELECT
            MAX(created_at) AS latest,
            COUNT(CASE
                WHEN created_at > ? THEN 1
            END) AS hourly_count,
            COUNT(*) AS daily_count
        FROM verification_tokens
        WHERE email = ?
        AND created_at > ?
    """, (
        now - 3600,
        email,
        now - 86400,
    )).fetchone()

    if (
        row["latest"] is not None
        and now - row["latest"] < MINIMUM_INTERVAL
    ):
        raise RateLimitExceeded(
            "Please wait before requesting another link."
        )

    if row["hourly_count"] >= HOURLY_LIMIT:
        raise RateLimitExceeded(
            "Hourly verification request limit reached."
        )

    if row["daily_count"] >= DAILY_LIMIT:
        raise RateLimitExceeded(
            "Daily verification request limit reached."
        )


def check_network_limits(db, client_ip, now):
    cutoff = now - 3600

    if client_ip:
        count = db.execute(
            """
            SELECT COUNT(*)
            FROM verification_tokens
            WHERE client_ip = ?
            AND created_at > ?
            """,
            (client_ip, cutoff),
        ).fetchone()[0]

        if count >= IP_HOURLY_LIMIT:
            raise RateLimitExceeded(
                "IP verification request limit reached."
            )

    count = db.execute(
        """
        SELECT COUNT(*)
        FROM verification_tokens
        WHERE created_at > ?
        """,
        (cutoff,),
    ).fetchone()[0]

    if count >= GLOBAL_HOURLY_LIMIT:
        raise RateLimitExceeded(
            "Global verification request limit reached."
        )
