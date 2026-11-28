import sqlite3
import unittest

from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.registration.database import initialize, connect
from backend.registration.travel_rates import save_travel_rates
from backend.publication.rebuild import rebuild_directory


class TestDirectoryRebuild(unittest.TestCase):

    def test_registration_lifecycle(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            destination = root / "directory.db"
            registration = root / "registration.db"

            initialize(registration)

            def rebuild():
                return rebuild_directory(
                    destination_path=destination,
                    registration_path=registration,
                )

            rebuild()

            with closing(sqlite3.connect(destination)) as db:
                email, = db.execute("""
                    SELECT email
                    FROM supervisors
                    WHERE TRIM(email) != ''
                    GROUP BY LOWER(TRIM(email))
                    HAVING COUNT(*) = 1
                    LIMIT 1
                """).fetchone()

                original = db.execute("""
                    SELECT supervisor_id, name, phone, email
                    FROM supervisors
                    WHERE email = ?
                """, (email,)).fetchone()

            supervisor_id = original[0]

            with closing(connect(registration)) as db:
                with db:
                    db.execute("""
                        INSERT INTO registrations (
                            account_email, email_verified_at,
                            first_name, last_name,
                            status, last_published_at,
                            phone, phone_visibility,
                            typed_reports, is_smoker
                        )
                        VALUES (
                            ?, CURRENT_TIMESTAMP,
                            'Updated', 'Provider',
                            'active', CURRENT_TIMESTAMP,
                            '9255550100', 'hidden',
                            1, 0
                        )
                    """, (email,))

                    save_travel_rates(db, 1, {
                        "price_per_mile": 725,
                        "driving_hourly_rate": 50000,
                    })

                    db.execute("""
                        INSERT INTO registrations (
                            account_email, email_verified_at,
                            first_name, last_name,
                            state_code, county, status
                        )
                        VALUES (
                            'independent@example.invalid',
                            CURRENT_TIMESTAMP,
                            'Independent', 'Provider',
                            'CA', 'Alameda', 'active'
                        )
                    """)

            private_before = registration.read_bytes()

            for _ in range(2):
                rebuild()

                with closing(sqlite3.connect(destination)) as db:
                    updated = db.execute("""
                        SELECT name, phone, email,
                               typed_reports, is_smoker,
                               price_per_mile,
                               driving_hourly_rate
                        FROM supervisors
                        WHERE supervisor_id = ?
                    """, (supervisor_id,)).fetchone()

                    self.assertEqual(updated, (
                        "Updated Provider", "", "",
                        1, 0, 725, 50000,
                    ))

                    self.assertEqual(db.execute("""
                        SELECT name FROM supervisors
                        WHERE supervisor_id = -2
                    """).fetchone(), ("Independent Provider",))

            self.assertEqual(
                registration.read_bytes(), private_before
            )

            print("Repeated publication and stable IDs: PASSED")
            print("Registered data precedence: PASSED")
            print("Restricted contact protection: PASSED")
            print("Travel rates: PASSED")

            with closing(connect(registration)) as db:
                with db:
                    db.execute("""
                        UPDATE registrations
                        SET status = 'hidden'
                        WHERE registration_id = 1
                    """)

                    db.execute("""
                        UPDATE registrations
                        SET status = 'deleted'
                        WHERE registration_id = 2
                    """)

            rebuild()

            with closing(sqlite3.connect(destination)) as db:
                self.assertEqual(db.execute("""
                    SELECT name, phone, email
                    FROM supervisors
                    WHERE supervisor_id = ?
                """, (supervisor_id,)).fetchone(), ("", "", ""))

                self.assertEqual(db.execute("""
                    SELECT COUNT(*)
                    FROM supervisor_courts
                    WHERE supervisor_id = ?
                """, (supervisor_id,)).fetchone()[0], 0)

                self.assertEqual(db.execute("""
                    SELECT COUNT(*)
                    FROM supervisors
                    WHERE supervisor_id = -2
                """).fetchone()[0], 0)

            print("Hidden acquired listing: PASSED")
            print("Deleted independent listing: PASSED")

            with closing(connect(registration)) as db:
                with db:
                    db.execute("""
                        UPDATE registrations
                        SET status = 'active',
                            first_name = 'Restored',
                            typed_reports = NULL
                        WHERE registration_id = 1
                    """)

                    save_travel_rates(db, 1, {
                        "price_per_mile": None,
                        "driving_hourly_rate": 0,
                    })

            rebuild()

            with closing(sqlite3.connect(destination)) as db:
                self.assertEqual(db.execute("""
                    SELECT name, typed_reports,
                           price_per_mile, driving_hourly_rate
                    FROM supervisors
                    WHERE supervisor_id = ?
                """, (supervisor_id,)).fetchone(), (
                    "Restored Provider", None, None, 0,
                ))

                self.assertGreater(db.execute("""
                    SELECT COUNT(*)
                    FROM supervisor_courts
                    WHERE supervisor_id = ?
                """, (supervisor_id,)).fetchone()[0], 0)

                self.assertEqual(
                    db.execute("PRAGMA integrity_check").fetchone()[0],
                    "ok",
                )

                self.assertEqual(
                    db.execute("PRAGMA foreign_key_check").fetchall(),
                    [],
                )

            print("Hidden provider restoration: PASSED")
            print("Original provider ID preservation: PASSED")
            print("Cleared field preservation: PASSED")
            print("Database integrity: PASSED")
            print("Production data modified: NO")


if __name__ == "__main__":
    unittest.main()
