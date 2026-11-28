"""Save provider changes and refresh published listings."""

import logging
import os

from backend.importers.supervisors import SOURCE, DESTINATION
from backend.registration.database import DATABASE_PATH
from backend.registration.profiles import get_profile
from backend.publication.locking import publication_lock
from backend.publication.rebuild import _rebuild_directory


def update_registration(
    email,
    save,
    registration_path=DATABASE_PATH,
    source_path=SOURCE,
    destination_path=DESTINATION,
):
    with publication_lock(destination_path):
        result = save()
        profile = get_profile(email, registration_path)

        if profile is None or profile["status"] != "active":
            return result, None

        if os.environ.get("PROFILE_PUBLICATION_ENABLED") != "1":
            return result, False

        try:
            _rebuild_directory(
                source_path=source_path,
                destination_path=destination_path,
                registration_path=registration_path,
            )
        except Exception:
            logging.getLogger(__name__).exception(
                "Directory refresh failed"
            )
            return result, False

        return result, True
