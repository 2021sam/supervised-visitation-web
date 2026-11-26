"""Resolve acquisition records to website supervisor identities."""

from backend.importers.cleanup import SOURCE_SYSTEM


def resolve_supervisor_id(connection, source_id, name):
    existing = connection.execute("""
        SELECT supervisor_id
        FROM supervisor_sources
        WHERE source_system = ?
          AND source_id = ?
    """, (SOURCE_SYSTEM, source_id)).fetchone()

    if existing:
        return existing[0]

    cursor = connection.execute("""
        INSERT INTO supervisors (name)
        VALUES (?)
    """, (name,))

    supervisor_id = cursor.lastrowid

    connection.execute("""
        INSERT INTO supervisor_sources (
            source_system, source_id, supervisor_id
        )
        VALUES (?, ?, ?)
    """, (SOURCE_SYSTEM, source_id, supervisor_id))

    return supervisor_id
