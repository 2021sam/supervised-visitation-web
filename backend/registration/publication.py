"""Coordinate provider status changes and directory publication."""

from contextlib import closing

from backend.importers.supervisors import SOURCE, DESTINATION
from backend.registration.database import DATABASE_PATH, connect
from backend.registration.profiles import get_profile
from backend.registration.status import change_status
from backend.publication.locking import publication_lock
from backend.publication.rebuild import _rebuild_directory


def publish_action(
    email,
    action,
    registration_path=DATABASE_PATH,
    source_path=SOURCE,
    destination_path=DESTINATION,
):
    email = email.strip().lower()

    with publication_lock(destination_path):
        previous = get_profile(email, registration_path)

        if previous is None:
            raise ValueError("Save your profile first.")

        change_status(email, action, registration_path)

        try:
            _rebuild_directory(
                source_path=source_path,
                destination_path=destination_path,
                registration_path=registration_path,
            )
        except Exception:
            with closing(connect(registration_path)) as db, db:
                db.execute("""
                    UPDATE registrations
                    SET status = ?,
                        updated_at = ?,
                        deleted_at = ?,
                        last_published_at = ?
                    WHERE account_email = ?
                """, (
                    previous["status"],
                    previous["updated_at"],
                    previous["deleted_at"],
                    previous["last_published_at"],
                    email,
                ))
            raise

        if action == "publish":
            with closing(connect(registration_path)) as db, db:
                db.execute("""
                    UPDATE registrations
                    SET last_published_at = CURRENT_TIMESTAMP
                    WHERE account_email = ?
                """, (email,))

        return get_profile(email, registration_path)
