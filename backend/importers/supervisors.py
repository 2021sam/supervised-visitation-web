"""Import validated California supervisor records."""

import sqlite3
from pathlib import Path

from backend.importers.cleanup import remove_obsolete_supervisors
from backend.importers.source_mapping import resolve_supervisor_id

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT.parent / "supervised-visitation" / "registry.db"
DESTINATION = ROOT / "data" / "directory.db"


def import_supervisors(source_path=SOURCE, destination_path=DESTINATION):
    with sqlite3.connect(
        Path(source_path).resolve().as_uri() + "?mode=ro", uri=True
    ) as source:
        source.row_factory = sqlite3.Row

        records = source.execute("""
            SELECT
                s.supervisor_id,
                s.name,
                s.phone,
                s.email,
                s.website,
                s.zip_code,
                s.service_area,
                s.service_counties,
                s.languages,
                s.additional_info,
                c.county,
                c.court_url,
                r.url AS source_url
            FROM supervisors s
            JOIN courts c ON c.court_id = s.court_id
            JOIN search_results r ON r.result_id = s.result_id
            WHERE r.validation_status = 'VALIDATED'
              AND r.court_id = s.court_id
              AND TRIM(s.name) != ''
              AND (
                  TRIM(s.phone) != ''
                  OR TRIM(s.email) != ''
              )
        """).fetchall()

    with sqlite3.connect(destination_path) as destination:
        destination.execute("PRAGMA foreign_keys = ON")

        from backend.publication.source_schema import extend_source_schema
        extend_source_schema(destination)

        if not records:
            raise RuntimeError("Refusing to synchronize an empty acquisition dataset")

        active_sources = {
            record["supervisor_id"]: record["name"]
            for record in records
        }

        removed = remove_obsolete_supervisors(
            destination, active_sources
        )

        for record in records:
            supervisor_id = resolve_supervisor_id(
                destination,
                record["supervisor_id"],
                record["name"],
            )
            destination.execute("""
                INSERT INTO supervisors (
                    supervisor_id, name, phone, email, website,
                    zip_code, service_area, service_counties,
                    languages, additional_info
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(supervisor_id) DO UPDATE SET
                    name = excluded.name,
                    phone = excluded.phone,
                    email = excluded.email,
                    website = excluded.website,
                    zip_code = excluded.zip_code,
                    service_area = excluded.service_area,
                    service_counties = excluded.service_counties,
                    languages = excluded.languages,
                    additional_info = excluded.additional_info
            """, (
                supervisor_id,
                record["name"],
                record["phone"],
                record["email"],
                record["website"],
                record["zip_code"],
                record["service_area"],
                record["service_counties"],
                record["languages"],
                record["additional_info"],
            ))

            destination.execute("""
                INSERT INTO supervisor_courts (
                    supervisor_id, state_code, county,
                    court_url, source_url
                )
                VALUES (?, 'CA', ?, ?, ?)
                ON CONFLICT(supervisor_id, state_code, county)
                DO UPDATE SET
                    court_url = excluded.court_url,
                    source_url = excluded.source_url
            """, (
                supervisor_id,
                record["county"],
                record["court_url"],
                record["source_url"],
            ))

    print(f"Obsolete supervisors removed: {removed}")
    return len(records)


if __name__ == "__main__":
    print(f"Supervisor records imported: {import_supervisors()}")
