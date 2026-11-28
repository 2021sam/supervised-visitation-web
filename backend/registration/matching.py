"""Find existing directory information by verified email."""

import sqlite3
from contextlib import closing

from backend.registration.database import PROJECT_ROOT

DIRECTORY_PATH = PROJECT_ROOT / "data" / "directory.db"

MATCH_FIELDS = (
    "name",
    "phone",
    "email",
    "website",
    "city",
    "state_code",
    "zip_code",
    "languages",
    "service_counties",
    "service_area",
    "additional_info",
)


def find_existing_provider(email, database_path=DIRECTORY_PATH):
    email = email.strip().lower()

    if not email:
        return None

    with closing(sqlite3.connect(
        f"file:{database_path}?mode=ro",
        uri=True,
    )) as db:
        db.row_factory = sqlite3.Row

        rows = db.execute(
            """
            SELECT *
            FROM supervisors
            WHERE LOWER(TRIM(email)) = ?
            """,
            (email,),
        ).fetchall()

    if not rows:
        return None

    result = {}

    for field in MATCH_FIELDS:
        values = {
            str(row[field]).strip()
            for row in rows
            if row[field] is not None
            and str(row[field]).strip()
        }

        if len(values) == 1:
            result[field] = values.pop()

    return result
