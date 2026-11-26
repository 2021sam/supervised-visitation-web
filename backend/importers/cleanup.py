"""Remove obsolete acquisition-owned supervisor records."""

SOURCE_SYSTEM = "court_acquisition"


def remove_obsolete_supervisors(connection, active_sources):
    mappings = connection.execute("""
        SELECT m.source_id, m.supervisor_id, s.name
        FROM supervisor_sources m
        JOIN supervisors s
          ON s.supervisor_id = m.supervisor_id
        WHERE m.source_system = ?
    """, (SOURCE_SYSTEM,)).fetchall()

    removed = 0

    for source_id, supervisor_id, name in mappings:
        active_name = active_sources.get(source_id)

        if (
            active_name is not None
            and active_name.strip().casefold()
            == name.strip().casefold()
        ):
            continue

        connection.execute("""
            DELETE FROM supervisor_sources
            WHERE source_system = ?
              AND source_id = ?
        """, (SOURCE_SYSTEM, source_id))

        remaining = connection.execute("""
            SELECT 1
            FROM supervisor_sources
            WHERE supervisor_id = ?
            LIMIT 1
        """, (supervisor_id,)).fetchone()

        if remaining:
            continue

        connection.execute("""
            DELETE FROM supervisor_courts
            WHERE supervisor_id = ?
        """, (supervisor_id,))

        connection.execute("""
            DELETE FROM supervisors
            WHERE supervisor_id = ?
        """, (supervisor_id,))

        removed += 1

    return removed
