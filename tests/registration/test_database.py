import sqlite3
import tempfile
import unittest
from pathlib import Path

from backend.registration.database import connect, initialize


class RegistrationDatabaseTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.path = Path(self.temp.name) / "registration.db"
        initialize(self.path)

        self.db = connect(self.path)
        self.addCleanup(self.db.close)

        cursor = self.db.execute("""
            INSERT INTO registrations (account_email)
            VALUES (?)
        """, ("provider@example.com",))

        self.provider_id = cursor.lastrowid

    def test_tables_and_field_count(self):
        expected = {
            "registrations": 175,
            "registration_availability": 5,
            "registration_rates": 8,
        }

        for table, count in expected.items():
            columns = self.db.execute(
                f"PRAGMA table_info({table})"
            ).fetchall()

            self.assertEqual(len(columns), count)

    def test_integrity(self):
        result = self.db.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

        self.assertEqual(result, "ok")

    def test_foreign_keys_enabled(self):
        result = self.db.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0]

        self.assertEqual(result, 1)

    def test_registration_defaults(self):
        row = self.db.execute("""
            SELECT *
            FROM registrations
            WHERE registration_id = ?
        """, (self.provider_id,)).fetchone()

        self.assertEqual(row["status"], "hidden")
        self.assertEqual(row["country_code"], "US")
        self.assertEqual(row["address_visibility"], "hidden")
        self.assertEqual(row["terms_accepted"], 0)
        self.assertEqual(row["privacy_acknowledged"], 0)
        self.assertIsNone(row["is_smoker"])
        self.assertIsNone(row["phone_is_cell"])

    def test_unique_email_case_insensitive(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""
                INSERT INTO registrations (account_email)
                VALUES (?)
            """, ("PROVIDER@example.com",))

    def test_boolean_values(self):
        for value in (0, 1, None):
            self.db.execute("""
                UPDATE registrations
                SET is_smoker = ?
                WHERE registration_id = ?
            """, (value, self.provider_id))

            result = self.db.execute("""
                SELECT is_smoker
                FROM registrations
                WHERE registration_id = ?
            """, (self.provider_id,)).fetchone()[0]

            self.assertEqual(result, value)

        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""
                UPDATE registrations
                SET is_smoker = 2
                WHERE registration_id = ?
            """, (self.provider_id,))

    def test_multiple_daily_time_ranges(self):
        ranges = [
            ("08:00", "11:00"),
            ("14:00", "16:00"),
            ("18:00", "21:00"),
        ]

        self.db.executemany("""
            INSERT INTO registration_availability (
                registration_id,
                day_of_week,
                start_time,
                end_time
            )
            VALUES (?, 0, ?, ?)
        """, [
            (self.provider_id, start, end)
            for start, end in ranges
        ])

        rows = self.db.execute("""
            SELECT start_time, end_time
            FROM registration_availability
            WHERE registration_id = ?
            AND day_of_week = 0
            ORDER BY start_time
        """, (self.provider_id,)).fetchall()

        self.assertEqual(
            [tuple(row) for row in rows],
            ranges
        )

    def test_invalid_availability(self):
        invalid = [
            (7, "09:00", "17:00"),
            (0, "25:00", "26:00"),
            (0, "17:00", "09:00"),
            (0, "09:00", "09:00"),
            (0, "09:60", "17:00"),
        ]

        for day, start, end in invalid:
            with self.subTest(day=day, start=start, end=end):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.db.execute("""
                        INSERT INTO registration_availability (
                            registration_id,
                            day_of_week,
                            start_time,
                            end_time
                        )
                        VALUES (?, ?, ?, ?)
                    """, (self.provider_id, day, start, end))

    def test_independent_travel_rates(self):
        rates = [
            ("hourly_rate", 100000, "hour"),
            ("price_per_mile", 725, "mile"),
            ("driving_hourly_rate", 60000, "hour"),
        ]

        self.db.executemany("""
            INSERT INTO registration_rates (
                registration_id,
                rate_type,
                amount,
                billing_unit
            )
            VALUES (?, ?, ?, ?)
        """, [
            (self.provider_id, kind, amount, unit)
            for kind, amount, unit in rates
        ])

        rows = self.db.execute("""
            SELECT rate_type, amount
            FROM registration_rates
            WHERE registration_id = ?
        """, (self.provider_id,)).fetchall()

        result = {
            row["rate_type"]: row["amount"]
            for row in rows
        }

        self.assertEqual(result["hourly_rate"], 100000)
        self.assertEqual(result["price_per_mile"], 725)
        self.assertEqual(result["driving_hourly_rate"], 60000)

    def test_zero_price(self):
        self.db.execute("""
            INSERT INTO registration_rates (
                registration_id,
                rate_type,
                amount,
                billing_unit
            )
            VALUES (?, 'consultation_fee', 0, 'consultation')
        """, (self.provider_id,))

        amount = self.db.execute("""
            SELECT amount
            FROM registration_rates
            WHERE registration_id = ?
        """, (self.provider_id,)).fetchone()[0]

        self.assertEqual(amount, 0)

    def test_invalid_rates(self):
        invalid = [
            ("hourly_rate", -1000, "hour"),
            ("price_per_mile", 760, "hour"),
            ("driving_hourly_rate", 60000, "mile"),
            ("unknown_rate", 1000, "hour"),
            ("hourly_rate", 1000.5, "hour"),
        ]

        for kind, amount, unit in invalid:
            with self.subTest(kind=kind, amount=amount, unit=unit):
                with self.assertRaises(sqlite3.IntegrityError):
                    self.db.execute("""
                        INSERT INTO registration_rates (
                            registration_id,
                            rate_type,
                            amount,
                            billing_unit
                        )
                        VALUES (?, ?, ?, ?)
                    """, (self.provider_id, kind, amount, unit))

    def test_contact_visibility(self):
        for visibility in ("public", "verified", "hidden"):
            self.db.execute("""
                UPDATE registrations
                SET phone_visibility = ?
                WHERE registration_id = ?
            """, (visibility, self.provider_id))

        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""
                UPDATE registrations
                SET phone_visibility = 'invalid'
                WHERE registration_id = ?
            """, (self.provider_id,))

    def test_invalid_foreign_key(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("""
                INSERT INTO registration_rates (
                    registration_id,
                    rate_type,
                    amount,
                    billing_unit
                )
                VALUES (999999, 'hourly_rate', 100000, 'hour')
            """)

    def test_cascade_delete(self):
        self.db.execute("""
            INSERT INTO registration_availability (
                registration_id,
                day_of_week,
                start_time,
                end_time
            )
            VALUES (?, 0, '09:00', '17:00')
        """, (self.provider_id,))

        self.db.execute("""
            INSERT INTO registration_rates (
                registration_id,
                rate_type,
                amount,
                billing_unit
            )
            VALUES (?, 'hourly_rate', 100000, 'hour')
        """, (self.provider_id,))

        self.db.execute("""
            DELETE FROM registrations
            WHERE registration_id = ?
        """, (self.provider_id,))

        for table in (
            "registration_availability",
            "registration_rates",
        ):
            count = self.db.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            self.assertEqual(count, 0)

    def test_initialize_is_idempotent(self):
        self.db.commit()
        initialize(self.path)

        count = self.db.execute("""
            SELECT COUNT(*) FROM registrations
        """).fetchone()[0]

        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
