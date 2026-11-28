"""Save or remove a provider's processed profile photo."""

from contextlib import closing

from backend.registration.database import DATABASE_PATH, connect


def save_photo(email, photo, database_path=DATABASE_PATH):
    with closing(connect(database_path)) as db, db:
        result = db.execute("""
            UPDATE registrations
            SET profile_photo = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE account_email = ?
              AND status != 'deleted'
        """, (photo, email.strip().lower()))

        if result.rowcount != 1:
            raise ValueError("Save your profile before adding a photo.")

    return photo
