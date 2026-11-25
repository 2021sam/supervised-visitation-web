"""Find geographic records within a specified radius."""

import math

from backend.geography.distance import distance_miles


def search_radius(records, latitude, longitude, radius_miles):
    """Return matching records ordered by distance."""

    if not (
        math.isfinite(latitude)
        and math.isfinite(longitude)
        and -90 <= latitude <= 90
        and -180 <= longitude <= 180
    ):
        raise ValueError("Invalid origin coordinates")

    if not math.isfinite(radius_miles) or radius_miles < 0:
        raise ValueError("Invalid search radius")

    results = []

    for record in records:
        distance = distance_miles(
            latitude,
            longitude,
            record["latitude"],
            record["longitude"],
        )

        if distance <= radius_miles:
            results.append({
                **record,
                "distance_miles": distance,
            })

    return sorted(
        results,
        key=lambda record: record["distance_miles"],
    )
