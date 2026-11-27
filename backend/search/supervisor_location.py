"""Resolve a supervisor's location for mileage searches."""

from backend.geography.lookup import (
    get_zip_records,
    get_city_zip_codes,
)


def resolve_supervisor_location(
    supervisor,
    zip_indexes,
    state_code,
):
    for field in ("service_zip_code", "zip_code"):
        zip_code = (supervisor.get(field) or "").strip()

        if zip_code:
            records = get_zip_records(zip_indexes, zip_code)

            if records:
                return {
                    **records[0],
                    "distance_basis": field,
                }

    service_area = (supervisor.get("service_area") or "").strip()

    if not service_area:
        return None

    first_city = service_area.split(",")[0].strip()

    if first_city.casefold().endswith(
        (" county", " counties", " parish", " borough")
    ):
        return None

    zip_codes = get_city_zip_codes(
        zip_indexes,
        state_code,
        first_city,
    )

    if not zip_codes:
        return None

    records = get_zip_records(zip_indexes, zip_codes[0])

    if not records:
        return None

    return {
        **records[0],
        "distance_basis": "service_area_city",
    }
