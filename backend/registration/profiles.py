"""Read and save provider-owned registration profiles."""

from contextlib import closing

from backend.registration.database import DATABASE_PATH, connect
from backend.registration.travel_rates import (
    RATE_UNITS,
    read_travel_rates,
    save_travel_rates,
)


EDITABLE_FIELDS = (
    "first_name",
    "middle_name",
    "last_name",
    "provider_type",
    "business_name",
    "professional_title",
    "phone",
    "phone_is_cell",
    "email",
    "website",
    "zip_code",
    "city",
    "state_code",
    "county",
    "service_start_year",
    "languages",
    "service_counties",
    "service_area",
    "additional_info",
    "accepting_new_clients",
    "supervised_visitation",
    "supervised_exchange",
    "transportation",
    "virtual_visitation",
    "on_site_visitation",
    "off_site_visitation",
    "handwritten_reports",
    "typed_reports",
    "is_smoker",
    "uses_vape",
    "calendar_url",
    "calendar_visibility",
    "reference_point",
    "charges_roundtrip_mileage",
    "charges_roundtrip_driving_time",
)


def get_profile(email, database_path=DATABASE_PATH):
    email = email.strip().lower()

    with closing(connect(database_path)) as db:
        row = db.execute(
            """
            SELECT *
            FROM registrations
            WHERE account_email = ?
            """,
            (email,),
        ).fetchone()

        if row is None:
            return None

        return {
            **dict(row),
            **read_travel_rates(db, row["registration_id"]),
        }


def save_profile(email, values, database_path=DATABASE_PATH):
    email = email.strip().lower()

    if not email:
        raise ValueError("Verified account email is required.")

    unknown = set(values) - set(EDITABLE_FIELDS) - set(RATE_UNITS)

    if unknown:
        raise ValueError(
            f"Unsupported profile fields: {sorted(unknown)}"
        )

    rates = {
        field: value
        for field, value in values.items()
        if field in RATE_UNITS
    }

    values = {
        field: value
        for field, value in values.items()
        if field in EDITABLE_FIELDS
    }

    with closing(connect(database_path)) as db, db:
        db.execute(
            """
            INSERT INTO registrations (
                account_email,
                email_verified_at
            )
            VALUES (?, CURRENT_TIMESTAMP)
            ON CONFLICT(account_email) DO NOTHING
            """,
            (email,),
        )

        registration = db.execute(
            "SELECT registration_id, status FROM registrations "
            "WHERE account_email = ?",
            (email,),
        ).fetchone()

        if registration["status"] == "deleted":
            raise ValueError("Registration has been deleted.")

        save_travel_rates(
            db, registration["registration_id"], rates
        )

        if values:
            assignments = ", ".join(
                f"{field} = ?" for field in values
            )

            db.execute(
                f"""
                UPDATE registrations
                SET {assignments},
                    updated_at = CURRENT_TIMESTAMP
                WHERE account_email = ?
                  AND status != 'deleted'
                """,
                (*values.values(), email),
            )

    return get_profile(email, database_path)
