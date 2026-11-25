"""Calculate great-circle distances in miles."""

import math

EARTH_RADIUS_MILES = 3958.8


def distance_miles(lat1, lon1, lat2, lon2):
    """Return the great-circle distance between two coordinates."""

    lat1, lon1, lat2, lon2 = map(
        math.radians, (lat1, lon1, lat2, lon2)
    )

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    a = max(0.0, min(1.0, a))

    return 2 * EARTH_RADIUS_MILES * math.asin(math.sqrt(a))
