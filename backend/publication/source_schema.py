"""Preserve original acquisition identity metadata."""


def extend_source_schema(db):
    columns = {
        row[1]
        for row in db.execute(
            "PRAGMA table_info(supervisor_sources)"
        )
    }

    if "source_name" not in columns:
        db.execute("""
            ALTER TABLE supervisor_sources
            ADD COLUMN source_name TEXT
        """)

        db.execute("""
            UPDATE supervisor_sources
            SET source_name = (
                SELECT name
                FROM supervisors
                WHERE supervisors.supervisor_id =
                      supervisor_sources.supervisor_id
            )
        """)
