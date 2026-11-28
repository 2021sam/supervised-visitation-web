"""Independent authentication database."""

import os
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "auth.db"
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect(database_path=DATABASE_PATH):
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize(database_path=DATABASE_PATH):
    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    fd = os.open(
        database_path,
        os.O_CREAT | os.O_WRONLY,
        0o600
    )
    os.close(fd)
    database_path.chmod(0o600)

    connection = connect(database_path)

    try:
        connection.executescript(
            SCHEMA_PATH.read_text(encoding="utf-8")
        )
        connection.commit()
    finally:
        connection.close()

    return database_path


if __name__ == "__main__":
    print(initialize())
