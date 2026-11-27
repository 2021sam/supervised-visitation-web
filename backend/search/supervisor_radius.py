"""Search supervisors by ZIP code and radius."""

from backend.geography.lookup import get_zip_records
from backend.geography.radius import search_radius
from backend.search.supervisor_location import (
    resolve_supervisor_location,
)


def search_supervisors_by_radius(
    supervisors,
    zip_indexes,
    state_code,
    zip_code,
    radius_miles,
):
    state_code = state_code.strip().upper()

    origins = [
        record
        for record in get_zip_records(zip_indexes, zip_code)
        if record["state_code"] == state_code
    ]

    if not origins:
        raise ValueError(
            "ZIP code does not belong to the selected state"
        )

    origin = origins[0]
    candidates = []

    for supervisor in supervisors:
        location = resolve_supervisor_location(
            supervisor,
            zip_indexes,
            state_code,
        )

        if location is None:
            continue

        candidates.append({
            **supervisor,
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "resolved_zip_code": location["zip_code"],
            "distance_basis": location["distance_basis"],
        })

    return search_radius(
        candidates,
        origin["latitude"],
        origin["longitude"],
        radius_miles,
    )
