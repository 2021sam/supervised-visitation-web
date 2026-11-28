"""Read supervisor listings from the directory database."""

import sqlite3
from pathlib import Path

from backend.publication.schema import PUBLIC_COLUMNS

DATABASE = Path(__file__).resolve().parents[2] / "data" / "directory.db"


def list_supervisors(state_code=None, county=None):
    public_fields = ", ".join(
        f"s.{field}" for field in PUBLIC_COLUMNS
    )

    query = f"""
        SELECT DISTINCT
            s.supervisor_id,
            s.name,
            s.phone,
            s.email,
            s.website,
            s.address,
            s.city,
            s.state_code,
            s.zip_code,
            s.latitude,
            s.longitude,
            s.service_area,
            s.service_zip_code,
            s.languages,
            s.service_counties,
            s.additional_info,
            {public_fields}
        FROM supervisors s
        JOIN supervisor_courts c
            ON c.supervisor_id = s.supervisor_id
        WHERE 1 = 1
    """

    parameters = []

    if state_code:
        query += " AND c.state_code = ?"
        parameters.append(state_code.strip().upper())

    if county:
        query += " AND c.county = ? COLLATE NOCASE"
        parameters.append(county.strip())

    query += " ORDER BY s.name COLLATE NOCASE, s.supervisor_id"

    with sqlite3.connect(
        DATABASE.as_uri() + "?mode=ro", uri=True
    ) as connection:
        connection.row_factory = sqlite3.Row
        return [
            dict(row)
            for row in connection.execute(query, parameters)
        ]
