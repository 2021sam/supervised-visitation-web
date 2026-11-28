"""Manage provider profile publication status."""

from contextlib import closing

from backend.registration.database import DATABASE_PATH, connect


def validate_publication(profile):
    required = [
        "first_name",
        "last_name",
        "phone",
        "zip_code",
        "state_code",
        "county",
    ]

    if profile["provider_type"] not in ("individual", "agency"):
        raise ValueError("Select a provider type.")

    if profile["provider_type"] == "agency":
        required.append("business_name")

    missing = [
        field for field in required
        if not str(profile[field] or "").strip()
    ]

    if missing:
        raise ValueError(
            "Complete the following fields: "
            + ", ".join(field.replace("_", " ") for field in missing)
        )

    if not profile["email_verified_at"]:
        raise ValueError("Email verification is required.")


def change_status(email, action, database_path=DATABASE_PATH):
    statuses = {
        "publish": "active",
        "hide": "hidden",
        "delete": "deleted",
    }

    if action not in statuses:
        raise ValueError("Invalid profile action.")

    email = email.strip().lower()

    with closing(connect(database_path)) as db, db:
        db.execute("BEGIN IMMEDIATE")

        profile = db.execute("""
            SELECT *
            FROM registrations
            WHERE account_email = ?
        """, (email,)).fetchone()

        if profile is None:
            raise ValueError("Save your profile first.")

        if profile["status"] == "deleted":
            raise ValueError("This profile has been deleted.")

        if action == "publish":
            validate_publication(profile)

        db.execute("""
            UPDATE registrations
            SET status = ?,
                updated_at = CURRENT_TIMESTAMP,
                deleted_at = CASE
                    WHEN ? = 'delete' THEN CURRENT_TIMESTAMP
                    ELSE deleted_at
                END
            WHERE account_email = ?
        """, (statuses[action], action, email))

    return statuses[action]
