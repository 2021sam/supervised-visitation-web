"""Build and validate a replacement public directory database."""

import os
import sqlite3

from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.importers.supervisors import (
    SOURCE,
    DESTINATION,
    import_supervisors,
)
from backend.registration.database import DATABASE_PATH
from backend.publication.reset import reset_registration_overrides
from backend.publication.registrations import read_registrations
from backend.publication.merge_plan import build_merge_plan
from backend.publication.merge import apply_merge_plan

SCHEMA = Path(__file__).resolve().parents[1] / "database" / "schema.sql"


def rebuild_directory(
    source_path=SOURCE,
    destination_path=DESTINATION,
    registration_path=DATABASE_PATH,
):
    destination = Path(destination_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory(dir=destination.parent) as directory:
        candidate = Path(directory) / "directory.db"

        with closing(sqlite3.connect(candidate)) as target:
            if destination.exists():
                with closing(sqlite3.connect(
                    destination.as_uri() + "?mode=ro", uri=True
                )) as existing:
                    existing.backup(target)

            target.executescript(SCHEMA.read_text())
            target.execute("PRAGMA foreign_keys = ON")

            with target:
                reset_registration_overrides(target)

        count = import_supervisors(
            source_path=source_path,
            destination_path=candidate,
        )

        registrations = read_registrations(registration_path)

        with closing(sqlite3.connect(candidate)) as db:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA foreign_keys = ON")

            acquired = [
                dict(row)
                for row in db.execute("SELECT * FROM supervisors")
            ]

            plan = build_merge_plan(acquired, registrations)

            with db:
                counts = apply_merge_plan(db, plan)

            integrity = db.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0]

            violations = db.execute(
                "PRAGMA foreign_key_check"
            ).fetchall()

            if integrity != "ok" or violations:
                raise RuntimeError("Directory validation failed.")

        os.replace(candidate, destination)

    print("Registration overrides:", counts)
    return count
