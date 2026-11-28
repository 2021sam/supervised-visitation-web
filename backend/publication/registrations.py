"""Read provider registrations for directory publication."""

import sqlite3

from contextlib import closing
from pathlib import Path

from backend.registration.database import DATABASE_PATH
from backend.registration.travel_rates import read_travel_rates
from backend.publication.registration_status import publication_action


def read_registrations(database_path=DATABASE_PATH):
    uri = Path(database_path).resolve().as_uri() + "?mode=ro"

    with closing(sqlite3.connect(uri, uri=True)) as db:
        db.row_factory = sqlite3.Row
        db.execute("BEGIN")

        registrations = []

        for row in db.execute("""
            SELECT *
            FROM registrations
            ORDER BY registration_id
        """):
            registration = dict(row)

            if publication_action(registration) == "ignore":
                continue

            registration.update(
                read_travel_rates(
                    db,
                    registration["registration_id"],
                )
            )

            registrations.append(registration)

        return registrations
