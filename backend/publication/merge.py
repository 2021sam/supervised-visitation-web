"""Apply registration overrides to a candidate directory."""

from backend.publication.merge_plan import build_merge_plan
from backend.publication.public_fields import public_profile
from backend.publication.schema import PUBLIC_COLUMNS


def remove_listing(db, supervisor_id):
    db.execute(
        "DELETE FROM supervisor_courts WHERE supervisor_id = ?",
        (supervisor_id,),
    )

    fields = {
        "name": "",
        "phone": "",
        "email": "",
        "website": "",
        "address": "",
        "city": "",
        "state_code": "",
        "zip_code": "",
        "latitude": None,
        "longitude": None,
        "service_area": None,
        "service_zip_code": None,
        "languages": None,
        "service_counties": None,
        "additional_info": None,
    }

    fields.update(dict.fromkeys(PUBLIC_COLUMNS))

    update_listing(db, supervisor_id, fields)


def update_listing(db, supervisor_id, profile):
    assignments = ", ".join(
        f"{field} = ?" for field in profile
    )

    db.execute(
        f"UPDATE supervisors SET {assignments} "
        "WHERE supervisor_id = ?",
        (*profile.values(), supervisor_id),
    )


def insert_listing(db, profile, registration_id):
    if type(registration_id) is not int or registration_id <= 0:
        raise ValueError("Invalid registration ID.")

    profile = {
        "supervisor_id": -registration_id,
        **profile,
    }

    columns = ", ".join(profile)
    placeholders = ", ".join("?" for _ in profile)

    cursor = db.execute(
        f"INSERT INTO supervisors ({columns}) "
        f"VALUES ({placeholders})",
        tuple(profile.values()),
    )

    return cursor.lastrowid


def update_counties(db, supervisor_id, registration):
    state = (registration.get("state_code") or "").strip().upper()

    counties = {
        name.strip()
        for name in [
            registration.get("county") or "",
            *(registration.get("service_counties") or "").split(","),
        ]
        if name.strip()
    }

    if not state or not counties:
        return

    db.execute(
        "DELETE FROM supervisor_courts WHERE supervisor_id = ?",
        (supervisor_id,),
    )

    db.executemany("""
        INSERT INTO supervisor_courts (
            supervisor_id, state_code, county
        )
        VALUES (?, ?, ?)
    """, [
        (supervisor_id, state, county)
        for county in sorted(counties)
    ])


def apply_merge_plan(db, plan):
    counts = {"updated": 0, "inserted": 0, "suppressed": 0}

    for item in plan:
        matched_ids = item["matched_ids"]

        if item["action"] == "suppress":
            for supervisor_id in matched_ids:
                remove_listing(db, supervisor_id)
                counts["suppressed"] += 1

            continue

        profile = public_profile(item["registration"])

        if not profile["name"].strip():
            raise ValueError("Active registration requires a name.")

        if matched_ids:
            for supervisor_id in matched_ids:
                update_listing(db, supervisor_id, profile)
                update_counties(
                    db, supervisor_id, item["registration"]
                )
                counts["updated"] += 1
        else:
            registration = item["registration"]

            supervisor_id = insert_listing(
                db,
                profile,
                registration["registration_id"],
            )
            if not registration.get("state_code") or not registration.get("county"):
                raise ValueError(
                    "New public listing requires a state and county."
                )

            update_counties(db, supervisor_id, registration)

            counts["inserted"] += 1

    return counts
