"""Remove previous registration overrides before regeneration."""

from backend.publication.schema import PUBLIC_COLUMNS, extend_schema


def reset_registration_overrides(db):
    extend_schema(db)

    for table in ("supervisor_sources", "supervisor_courts"):
        db.execute(f"""
            DELETE FROM {table}
            WHERE supervisor_id < 0
        """)

    db.execute("""
        DELETE FROM supervisors
        WHERE supervisor_id < 0
    """)

    assignments = [
        f"{field} = NULL"
        for field in PUBLIC_COLUMNS
    ]

    assignments.extend([
        "address = ''",
        "city = ''",
        "state_code = ''",
        "latitude = NULL",
        "longitude = NULL",
        "service_zip_code = NULL",
    ])

    db.execute(
        "UPDATE supervisors SET " + ", ".join(assignments)
    )
